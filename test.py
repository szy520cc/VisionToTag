from download import download_file
from custom_log import write_log
from gemini2 import get_video_tag

def test(url):
    try:
        save_path = download_file(url)
        write_log('info', {'文件下载成功,保存路径': save_path})

        # 根据下载文件的路径获取视频标签
        res = get_video_tag(save_path)
        write_log('info', {'视频标签': res})
        return res
    except Exception as e:
        write_log('error', {'获取视频标签失败': str(e)})


if __name__ == "__main__":
    url = "https://aigc-miaobi.tos-cn-guangzhou.volces.com/parse_video/2025-02-11/951ab7a0-e840-11ef-9a95-b384e50e5459.mp4"
    test(url)