import requests
import logging

def page_get_and_validate(page_url, validate_text=None):
    try:
        # 发送 GET 请求
        response = requests.get(page_url)

        # 检查请求是否成功（状态码为 200 表示成功）
        response.raise_for_status()

        # 判断文本中是否包含指定的验证文本
        if validate_text is not None and validate_text not in response.text:
            return 0
        else:
            return 1
    
    except requests.exceptions.RequestException as err:
        logging.error(f"发生了请求异常: {err}")
        return 0

