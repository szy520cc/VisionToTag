from flask import Flask, request
from custom_log import write_log
from gemini2 import get_video_tag
from download import download_file

app = Flask(__name__)


# 接受参数
def receive_parameter():
    """
    接收并解析请求参数。

    根据请求的方法（GET或POST）和内容类型，从请求中提取参数。

    :return: 解析后的请求参数
    """
    # 检查请求方法是否为GET
    if request.method == "GET":
        # 如果是GET请求，从请求的查询字符串中获取参数
        data = request.args
    # 检查请求方法是否为POST
    elif request.method == "POST":
        # 检查请求的内容类型是否以'application/json'开头
        if request.content_type.startswith('application/json'):
            # 如果是JSON格式，从请求的JSON数据中获取参数
            data = request.json
        # 检查请求的内容类型是否以'multipart/form-data'开头
        elif request.content_type.startswith('multipart/form-data'):
            # 如果是表单数据，从请求的表单中获取参数
            data = request.form
        else:
            # 如果内容类型不匹配，从请求的所有值中获取参数
            data = request.values
    # 返回解析后的参数
    return data


@app.route('/index', methods=['GET'])
def index():
    return 'hello world!'

@app.route('/vision_to_tag', methods=['GET'])
def vision_to_tag():
    """
    将视觉内容转换为标签。

    该函数通过接收一个包含URL的POST请求，下载该URL对应的文件，并生成文件的标签。
    使用场景：当需要根据视觉内容（如视频）自动生成描述性标签时。

    方法：POST
    输入：一个包含'url'字段的JSON对象。
    输出：下载文件后的标签信息。
    """

    try:
        # 接收传入的参数
        data = receive_parameter()

        # 从参数中提取url，默认为空字符串
        url = data.get('url', '')

        # 检查url是否为空
        if not url:
            # 如果url为空，记录错误日志并返回错误信息
            raise Exception('URL不能为空')

        # 记录url日志信息
        write_log('info', {'请求参数url': url})

        # 下载文件并获取保存路径
        save_path = download_file(url)
        write_log('info', {'文件下载成功,保存路径': save_path})

        # 根据下载文件的路径获取视频标签
        return get_video_tag(save_path)
    except Exception as e:
        # 记录错误日志并返回错误信息
        write_log('error', str(e))
        return str(e)

if __name__ == '__main__':
    app.run()
