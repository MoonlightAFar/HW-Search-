import requests
import json
import re
from lxml import etree
from elasticsearch import Elasticsearch
import ssl
import concurrent.futures

# 忽略SSL验证（如果需要）
ssl._create_default_https_context = ssl._create_unverified_context

# Elasticsearch配置
es = Elasticsearch(
    hosts=["http://localhost:9200"],  # Elasticsearch的地址和端口
    request_timeout=3600  # 使用request_timeout代替timeout
)

proxies = {"http": None, "https": None}

# 创建索引
index_name = 'music'

# 通用请求头
HEADERS = {
    'Referer': 'http://music.163.com',
    'Host': 'music.163.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
}


# 获取歌词的函数
def get_lyrics(music_id):
    url = f'http://music.163.com/api/song/lyric?id={music_id}&lv=1&kv=1&tv=-1'
    try:
        response = requests.get(url, headers=HEADERS, proxies=proxies, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        lyrics = data['lrc']['lyric']

        # 使用正则去掉时间戳
        pattern = r'\[.*?\]'  # 改进正则，直接匹配时间戳
        lyrics = re.sub(pattern, '', lyrics).strip()  # 去掉时间戳并去除前后空格

        return lyrics
    except requests.exceptions.RequestException as e:
        print(f"Error fetching lyrics for song ID {music_id}: {e}")
        return ""


# 获取歌手的歌曲列表
def get_songs(artist_id, page=1):
    page_url = f'https://music.163.com/artist?id={artist_id}&page={page}'
    try:
        res = requests.get(page_url, headers=HEADERS, proxies=proxies)
        res.raise_for_status()  # Raise an exception for HTTP errors
        html = etree.HTML(res.text)

        href_xpath = "//*[@id='hotsong-list']//a/@href"
        name_xpath = "//*[@id='hotsong-list']//a/text()"

        hrefs = html.xpath(href_xpath)
        names = html.xpath(name_xpath)

        song_ids = [href[9:] for href in hrefs]  # 提取歌曲ID
        song_names = names

        return song_ids, song_names
    except requests.exceptions.RequestException as e:
        print(f"Error fetching songs for artist ID {artist_id} on page {page}: {e}")
        return [], []


# 批量插入数据到Elasticsearch
def save_to_es(datalist):
    try:
        # 使用bulk API进行批量插入
        actions = [
            {
                "_op_type": "index",
                "_index": index_name,
                "_id": idx + 11020,
                "_source": {
                    'link': data[0],
                    'title': data[1],
                    'text': data[2]
                }
            }
            for idx, data in enumerate(datalist)
        ]
        # 批量插入
        es.bulk(actions)
        print(f"Successfully inserted {len(datalist)} documents into Elasticsearch.")
    except Exception as e:
        print(f"Error inserting data into Elasticsearch: {e}")


# 主程序，获取歌手歌曲并存储到Elasticsearch
def main(artist_id):
    song_list = []
    page = 1
    # 获取歌曲直到数量达到100
    while len(song_list) < 100:
        current_songs, _ = get_songs(artist_id, page)
        if not current_songs:
            break  # 如果没有更多歌曲了，停止抓取
        song_list.extend(current_songs)
        page += 1

    print(f"Found {len(song_list)} songs.")
    if len(song_list) == 0:
        print("No songs found.")
        return

    datalist = []
    # 使用ThreadPoolExecutor进行并发请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_song = {executor.submit(get_lyrics, song_id): song_id for song_id in song_list[:100]}

        for future in concurrent.futures.as_completed(future_to_song):
            song_id = future_to_song[future]
            try:
                lyrics = future.result()
                if lyrics:  # 只处理有歌词的歌曲
                    link = f"https://music.163.com/#/song?id={song_id}"
                    song_name = song_list[song_list.index(song_id)]
                    datalist.append([link, song_name, lyrics])
                    print([link, song_name, lyrics[:50]])  # 打印歌词的前50个字符
            except Exception as e:
                print(f"Error processing song ID: {song_id}: {e}")

    # 保存数据到Elasticsearch
    if datalist:
        save_to_es(datalist)


if __name__ == "__main__":
    artist_id = '12487174'  # 示例歌手ID
    main(artist_id)

