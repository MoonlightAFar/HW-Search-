from urllib.parse import urlparse
from collections import Counter


def get_interest(file_path="search_history.txt"):
    """
    读取浏览历史文件，分析用户的兴趣并返回排名前几个的主机名。

    :param file_path: 包含浏览历史 URL 的文件路径，默认为 'search_history.txt'
    :return: 按照点击频次排序的主机名及其出现次数的列表
    """
    # 读取文件并提取主机名
    with open(file_path, 'r') as file:
        # 提取每个 URL 的主机名
        host_names = [urlparse(url.strip()).netloc for url in file.readlines()]

    # 统计每个主机名的点击频次
    host_counts = Counter(host_names)

    # 将结果按点击次数降序排序
    sorted_clicks = host_counts.most_common()

    return sorted_clicks


# 示例用法
if __name__ == "__main__":
    interests = get_interest()
    print("用户兴趣（按点击频次排序）：")
    for host, count in interests:
        print(f"{host}: {count}")

