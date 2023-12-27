import requests
import logging

def page_get_and_validate(page_url, validate_text=None):
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'zhdj.xfc.gov.cn',
            'Origin': 'https://zhdj.xfc.gov.cn',
            'Content-Type': 'application/octet-stream',
            'Referer': 'https://zhdj.xfc.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'}


        # 发送 GET 请求
        response = requests.get(page_url, headers=headers)

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

