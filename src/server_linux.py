# server.py

import datetime
import psutil
import logging

def check_system_resources(daemon_instance):
    """
    检查系统资源使用情况，如果任意一项超过80%，发出通知。
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent

        if cpu_percent > 80 or memory_percent > 80 or disk_percent > 80:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            resource_message = (
                f"系统资源使用过高："
                f"CPU 使用率: {cpu_percent}%，"
                f"内存使用率: {memory_percent}%，"
                f"硬盘使用率: {disk_percent}%"
            )
            print(f"{current_time} {resource_message}")

            # 发送通知
            daemon_instance.send_notification(resource_message, resource_message)

    except Exception as e:
        logging.error(f"检查系统资源时发生异常: {e}")
