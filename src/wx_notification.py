# {
#   "appToken":"AT_v3kqAspvdcV9ypsZzEz8a3fwA74YrVzO",
#   "content":"文件获取失败，检测失败次数：{{variables.$$err}}",
#   "summary":"文件获取失败，检测失败次数：{{variables.$$err}}",
#   "contentType":1,
#   "topicIds":[23376],
#   "uids":[],
#   "url":"",
#   "verifyPay":false
# }
# wx_notification.py

import requests
import logging

def send_notification(summary, content, notification_url, appToken, topicIds):
    try:
        # 发送 POST 请求通知
        data = {
                "appToken":appToken,
                "content":content,
                "summary":summary,
                "contentType":1,
                "topicIds":topicIds
            }
        response = requests.post(notification_url, json=data)

        # 检查请求是否成功（状态码为 200 表示成功）
        response.raise_for_status()

        logging.info("通知发送成功！")
    except requests.exceptions.RequestException as err:
        logging.info(f"发送通知时发生请求异常: {err}")
