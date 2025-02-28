import requests
from bs4 import BeautifulSoup
import time

# 通用请求头，模拟浏览器
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
}

# 用于提取电影信息的函数
def get_data(baseurl, max_pages=10):
    datalist = []  # 用来存储爬取的网页信息
    for i in range(max_pages):
        url = f"{baseurl}{i * 25}"
        print(f"正在爬取第 {i+1} 页：{url}")  # 打印当前页的URL
        html = ask_url(url)  # 获取网页源码
        if html:  # 如果网页请求成功
            soup = BeautifulSoup(html, "html.parser")
            items = soup.find_all('div', class_="item")
            print(f"共找到 {len(items)} 部电影")  # 打印当前页面的电影数量

            for item in items:
                data = []  # 保存一部电影所有信息

                # 获取电影的详情链接
                link = item.find('a')['href']
                data.append(link)

                # 获取电影的标题（可能有中文和英文名）
                title = item.find('span', class_="title").get_text()
                data.append(title)

                # 获取电影的简介（如果存在）
                inq = item.find('span', class_="inq")
                data.append(inq.get_text() if inq else '暂无简介')

                # 获取电影的评分
                rating = item.find('span', class_="rating_num")
                data.append(rating.get_text() if rating else '暂无评分')

                # 获取电影的详细信息（如导演、主演等）
                bd = item.find('p', class_="")
                data.append(bd.get_text().strip() if bd else '暂无详细信息')

                datalist.append(data)
                print(data)  # 打印当前电影的信息

            # 防止爬得过快，被网站封锁，适当延迟
            time.sleep(1)
        else:
            print(f"警告：无法获取第 {i+1} 页的数据。")
    return datalist

# 获取网页内容的函数
def ask_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # 如果请求失败，抛出异常
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None


# 示例主函数
if __name__ == "__main__":
    baseurl = "https://movie.douban.com/top250?start="
    datalist = get_data(baseurl)
    print(f"总共爬取了 {len(datalist)} 条数据。")

