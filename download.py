import requests
import os
import hashlib
from datetime import datetime


def download_file(url):
    """
    下载远程文件并保存到本地指定路径。

    :param url: 远程文件的 URL
    """
    try:
        # 获取本地保存目录，目录名为 'video'
        save_path = get_local_dir('video')
        # 生成保存文件的完整路径，文件名是 URL 的 MD5 值加上 ".mp4" 后缀
        save_path = os.path.join(save_path, get_md5(url) + ".mp4")

        # 发起 GET 请求下载文件，设置 stream=True 以便分块下载
        response = requests.get(url, stream=True)
        # 检查请求是否成功，如果失败则抛出异常
        response.raise_for_status()

        # 确保保存路径的目录存在，如果目录不存在则创建
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 以二进制写模式打开文件并写入内容
        with open(save_path, 'wb') as file:
            # 遍历响应内容的分块，每次写入 8192 字节
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        # 返回保存文件的路径
        return save_path
    except requests.exceptions.RequestException as e:
        raise Exception(f"下载文件时发生错误: {e}")
    except Exception as e:
        raise Exception(f"下载文件时发生未知错误: {e}")


def get_local_dir(dir_name):
    """
    获取本地目录路径，并确保目录存在且权限为777。

    :param dir_name: 目录名称
    :return: 本地目录的完整路径
    """
    # 获取当前日期
    current_date = datetime.now()
    # 格式化日期为 YYYYMMDD 的形式
    formatted_date = current_date.strftime('%Y%m%d')

    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(__file__)
    # 拼接目录名称和当前日期，形成完整的目录路径
    save_directory = os.path.join(current_dir, dir_name)
    save_directory = os.path.join(save_directory, formatted_date)

    # 确保目录存在，如果目录已存在，不会抛出异常
    os.makedirs(save_directory, exist_ok=True)

    # 设置目录权限为可读、可写、可执行（777）
    os.chmod(save_directory, 0o777)

    # 返回目录的完整路径
    return save_directory


def get_md5(text):
    """
    计算文本的 MD5 值。

    :param text: 要计算 MD5 的文本
    :return: 文本的 MD5 值（十六进制字符串）
    """
    # 创建一个 MD5 哈希对象
    md5_hash = hashlib.md5()

    # 更新哈希对象的内容（需要将文本转换为字节）
    md5_hash.update(text.encode('utf-8'))

    # 获取十六进制格式的哈希值
    md5_value = md5_hash.hexdigest()

    return md5_value


def get_current_hour():
    """
    获取当前时间的小时（24小时制）。
    """
    # 获取当前时间
    current_time = datetime.now()

    # 获取当前小时（24小时制）
    current_hour = current_time.hour

    return str(current_hour)
