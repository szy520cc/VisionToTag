import requests

def can_access_google():
    """
    验证是否可以访问谷歌官网。
    """
    url = "https://www.google.com"
    try:
        # 发送 GET 请求
        response = requests.get(url, timeout=10)  # 设置超时时间为 10 秒
        # 检查响应状态码
        if response.status_code == 200:
            print("可以访问谷歌官网。")
            return True
        else:
            print(f"无法访问谷歌官网，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        # 捕获请求异常
        print(f"无法访问谷歌官网，错误信息: {e}")
        return False

if __name__ == "__main__":
    can_access_google()
