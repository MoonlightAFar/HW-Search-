import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse
import os

# 提示用户输入图片的网址
# 比如：https://www.w3schools.com/html/pic_trulli.jpg
url = input("请输入图片的网址: ")

# 发送HTTP请求获取图片内容
response = requests.get(url)

# 确保请求成功
if response.status_code == 200:
    try:
        # 通过Pillow库加载图片
        img = Image.open(BytesIO(response.content))

        # 从URL中提取文件名
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)

        # 如果 URL 中没有文件名（例如网址是一个目录），我们可以使用域名作为文件名
        if not file_name:
            file_name = parsed_url.netloc + ".jpg"  # 默认以 .jpg 结尾

        # 创建'snapshots'文件夹，如果它不存在的话
        folder_name = "snapshots"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # 设置文件保存路径
        file_path = os.path.join(folder_name, file_name)

        # 保存图片到'snapshots'文件夹
        img.save(file_path)
        img.show()
        print(f"图片已保存为 '{file_path}' 并显示。")

    except Exception as e:
        print("无法处理该文件，可能不是有效的图片格式:", e)
else:
    print(f"请求失败，状态码：{response.status_code}")


