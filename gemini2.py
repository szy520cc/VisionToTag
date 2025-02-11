import os
import time
import google.generativeai as genai

from custom_log import write_log
from rate_limiter import get_rate_limiter


def get_api_key():
    rate_limiter = get_rate_limiter()
    api_key = rate_limiter.get_available_api_key()

    if api_key is None:
        raise Exception("没有可用的API密钥")

    return api_key['api_key']['key']


def configure_genai():
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    return api_key


def upload_to_gemini(path, mime_type=None):
    """将指定文件上传到 Gemini。

    参考文档：https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    try:
        api_key = configure_genai()
        file = genai.upload_file(path, mime_type=mime_type)
        write_log("info", f"文件 '{file.display_name}' 已上传，URI: {file.uri}")

        # 更新使用计数
        rate_limiter = get_rate_limiter()
        rate_limiter.increment_usage_count(api_key)

        return file
    except Exception as e:
        # 如果API调用失败，标记key为不可用
        rate_limiter = get_rate_limiter()
        rate_limiter.update_api_key_status(api_key, 'inactive')
        raise e


def wait_for_files_active(files):
    """等待指定文件变为可用状态。

    上传到 Gemini API 的某些文件在用作提示输入之前需要进行处理。
    可以通过查询文件的 "state" 字段来查看状态。

    此实现使用简单的阻塞轮询循环。生产环境中应该使用更优化的方法。
    """
    write_log("info", "等待文件处理中...")
    try:
        api_key = configure_genai()
        for name in (file.name for file in files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(10)
                file = genai.get_file(name)
            if file.state.name != "ACTIVE":
                raise Exception(f"文件 {file.name} 处理失败")
        write_log("info", "所有文件已就绪")

        # 更新使用计数
        rate_limiter = get_rate_limiter()
        rate_limiter.increment_usage_count(api_key)
    except Exception as e:
        # 如果API调用失败，标记key为不可用
        rate_limiter = get_rate_limiter()
        rate_limiter.update_api_key_status(api_key, 'inactive')
        raise e


# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}


def create_model():
    try:
        api_key = configure_genai()
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config,
            system_instruction="你是一位专业的多模态视频内容分析专家。你的任务是从多个维度深入分析视频内容，生成全面的标签描述。\n\n一、视觉元素分析\n    1. 人物维度\n        - 主要人物特征（性别、年龄、着装、职业特征）\n        - 人物数量与关系\n        - 表情与肢体语言\n        - 互动方式\n        - 身份角色（主持人、演员、素人等）\n    2. 场景维度\n        - 场景类型（自然、城市、室内外等）\n        - 场景功能（商业、居住、娱乐等）\n        - 场景氛围\n        - 地理特征\n        - 文化元素\n    3. 画面维度\n        - 构图方式（对称、三分法等）\n        - 镜头语言（特写、全景、运镜等）\n        - 视觉风格（明快、复古、极简等）\n        - 色彩运用\n        - 光线效果\n        - 画面质量\n        - 后期处理特征\n\n二、听觉元素分析\n    1. 语音维度\n        - 说话人特征（性别、年龄、口音等）\n        - 语气语调\n        - 情感表达\n        - 语速节奏\n        - 语言类型（普通话、方言、外语等）\n    2. 音乐维度\n        - 音乐类型\n        - 情感基调\n        - 节奏特点\n        - 配乐作用（背景、主题、衬托等）\n    3. 环境音维度\n        - 自然音效\n        - 人为音效\n        - 音频质量\n        - 混音特点\n\n三、文字元素分析\n    1. 视频文字\n        - 字幕类型（同步字幕、解说字幕等）\n        - 文字样式\n        - 排版布局\n        - 动效设计\n        - 多语言支持\n    2. 文案内容\n        - 核心信息\n        - 话题标签\n        - 品牌元素\n        - 文案风格\n        - 互动引导\n\n四、内容语义分析\n    1. 主题维度\n        - 内容类别（教育、娱乐、广告等）\n        - 目标受众\n        - 传播目的\n        - 价值导向\n    2. 叙事维度\n        - 故事结构\n        - 情节发展\n        - 冲突设置\n        - 高潮转折\n    3. 情感维度\n        - 主要情绪\n        - 氛围营造\n        - 情感共鸣点\n        - 感染力\n\n五、商业价值分析\n    1. 产品维度\n        - 产品类别\n        - 品牌露出\n        - 产品展示方式\n        - 价值主张\n        - 目标人群\n    2. 营销维度\n        - 营销诉求点\n        - 说服力要素\n        - 购买引导\n        - 互动转化设计\n\n六、内容质量评估\n    1. 专业度\n        - 内容专业性\n        - 表达准确性\n        - 信息可信度\n    2. 制作质量\n        - 画面质量\n        - 音频质量\n        - 后期制作\n    3. 传播价值\n        - 内容吸引力\n        - 互动潜力\n        - 传播价值\n\n七、受众特征分析\n    1. 目标人群画像\n        - 年龄段\n        - 性别倾向\n        - 兴趣特征\n        - 消费能力\n    2. 内容匹配度\n        - 内容适配性\n        - 需求匹配度\n        - 价值匹配度\n\n输出格式：\n{\n    \"visual_analysis\": {\n        \"characters\": {\n            \"tags\": [],\n            \"confidence\": {}\n        },\n        \"scene\": {\n            \"tags\": [],\n            \"confidence\": {}\n        },\n        \"cinematography\": {\n            \"tags\": [],\n            \"confidence\": {}\n        }\n    },\n    \"audio_analysis\": {\n        \"speech\": {\n            \"tags\": [],\n            \"confidence\": {}\n        },\n        \"music\": {\n            \"tags\": [],\n            \"confidence\": {}\n        },\n        \"sound_effects\": {\n            \"tags\": [],\n            \"confidence\": {}\n        }\n    },\n    \"text_analysis\": {\n        \"subtitles\": {\n            \"tags\": [],\n            \"confidence\": {}\n        },\n        \"copywriting\": {\n            \"tags\": [],\n            \"confidence\": {}\n        }\n    },\n    \"semantic_analysis\": {\n        \"theme\": {\n            \"tags\": [],\n            \"confidence\": {}\n        },\n        \"narrative\": {\n            \"tags\": [],\n            \"confidence\": {}\n        },\n        \"emotion\": {\n            \"tags\": [],\n            \"confidence\": {}\n        }\n    },\n    \"key_moments\": {\n        \"points\": [\n            {\n                \"timestamp\": \"\",\n                \"duration\": \"\",  // 持续时长\n                \"type\": \"\",      // 产品展示/功效说明/互动引导等\n                \"description\": \"\",\n                \"tags\": [],\n                \"importance\": 0-1,\n                \"action_points\": [] // 转化/互动关键点\n            }\n        ],\n        \"highlights\": {         // 视频亮点时刻\n            \"product_show\": [], // 产品展示时间点\n            \"value_props\": [],  // 价值主张时间点\n            \"call_to_action\": [] // 行动召唤时间点\n        }\n    }\n}\n\n标签生成原则：\n    1. 准确性：标签应准确反映视频内容\n    2. 完整性：覆盖所有重要维度\n    3. 分级性：区分主次标签重要程度\n    4. 可用性：便于后续推荐系统使用\n\n注意事项：\n    1. 关注各元素间的关联性\n    2. 标记关键时间节点\n    3. 识别品质与专业程度\n    4. 考虑跨文化因素\n    5. 注意内容安全性\n",
        )

        # 更新使用计数
        rate_limiter = get_rate_limiter()
        rate_limiter.increment_usage_count(api_key)

        return model
    except Exception as e:
        # 如果API调用失败，标记key为不可用
        rate_limiter = get_rate_limiter()
        rate_limiter.update_api_key_status(api_key, 'inactive')
        raise e


def send_chat_message(chat_session, message):
    try:
        api_key = configure_genai()
        response = chat_session.send_message(message)

        # 更新使用计数
        rate_limiter = get_rate_limiter()
        rate_limiter.increment_usage_count(api_key)

        return response
    except Exception as e:
        # 如果API调用失败，标记key为不可用
        rate_limiter = get_rate_limiter()
        rate_limiter.update_api_key_status(api_key, 'inactive')
        raise e


def get_video_tag(save_path):
    try:
        # 判断文件是否可用
        if not os.path.exists(save_path):
            raise Exception(f"文件 {save_path} 不存在")

        if not os.path.isfile(save_path):
            raise Exception(f"文件 {save_path} 不是一个文件")

        files = [
            upload_to_gemini(save_path, mime_type="video/mp4"),
        ]

        # 某些文件有处理延迟，等待它们准备就绪
        wait_for_files_active(files)

        model = create_model()

        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        files[0],
                    ],
                }
            ]
        )
        write_log("info", "开始分析视频内容")
        response = send_chat_message(chat_session, "分析视频内容")
        return response.text
    except Exception as e:
        raise e
