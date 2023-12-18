# sservo.py

import os
import time
import logging
import threading
import subprocess
import platform
import json
from datetime import datetime
from page import page_get_and_validate  # 指定页面检查
# from server_linux import check_system_resources  # linux 服务器资源检查
from wx_notification import send_notification  # 发送通知 调用 wxpusher

class DaemonThread(threading.Thread):
    def __init__(self, config_path='config.json'):
        super().__init__()
        self.config_path = config_path
        self.config = self.load_config()
        self.last_modified_time = os.path.getmtime(self.config_path)
        self.failure_count = 0
        self.first_failure_time = 0
        self.sucess_count = 0

    # 读取配置文件
    def load_config(self):
        try:
            with open(self.config_path) as config_file:
                self.config = json.load(config_file)
                try:
                    self.page_url = self.config['DaemonSettings']['page_url']
                    self.validate_text = self.config['DaemonSettings']['validate_text']
                    self.success_wait_time = self.config['RetrySettings']['success_wait_time']
                    self.failure_wait_time = self.config['RetrySettings']['failure_wait_time']
                    self.notify_after_failures = self.config['RetrySettings']['notify_after_failures']
                    self.notify_after_success = self.config['RetrySettings']['notify_after_success']
                    self.command_after_failures = self.config['RetrySettings']['command_after_failures']
                    self.command_file = self.config['RetrySettings']['command_file']
                    self.notification_url = self.config['NotificationSettings']['notification_url']
                    self.appToken = self.config['NotificationSettings']['appToken']
                    self.topicIds = self.config['NotificationSettings']['topicIds']
                except KeyError as e:
                    logging.error(f"配置文件参数缺失: {e}")
                    raise SystemExit(f"配置文件参数缺失: {e}")

                return self.config
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logging.error(f"无法读取配置文件: {e}")
            raise SystemExit(f"无法读取配置文件: {e}")
    
    # 检查配置文件是否被修改
    def is_config_modified(self):
        current_modified_time = os.path.getmtime(self.config_path)
        if current_modified_time > self.last_modified_time:
            self.last_modified_time = current_modified_time
            return True
        return False
    
    # 发生通知
    def send_notification(self, summary, content):
        send_notification(summary, content, self.notification_url, self.appToken, self.topicIds)

    # 主运行程序
    def run(self):
        while True:
            try:
                # 检查配置文件是否被修改
                if self.is_config_modified():
                    logging.info("配置文件发生变化，重新加载配置...")
                    self.config = self.load_config()

                # 调用 "page.py" 中的方法
                result = page_get_and_validate(self.page_url, self.validate_text)

                # 根据返回值进行逻辑判断
                if result == 1:
                    # 处理访问成功的逻辑
                    self.sucess_count += 1  # 仅在访问成功时递增
                    self.first_failure_time = 0 # 重置首次失败时间

                    if self.failure_count == 0:
                        logging.info("访问成功！")
                    else:
                        sucess_message = f"访问成功！之前失败次数: {self.failure_count}"
                        logging.info(sucess_message)
                        self.send_notification(sucess_message, sucess_message)

                    self.failure_count = 0  # 重置失败次数
                    
                    # 在成功次数达到N次，及倍数时发送通知 
                    if self.sucess_count >= self.notify_after_success and self.sucess_count % self.notify_after_success == 0:
                        sucess_message = f"访问成功！连续成功次数: {self.sucess_count}"
                        logging.info(sucess_message)
                        self.send_notification(sucess_message, sucess_message)

                    # 等待10分钟再次访问
                    time.sleep(self.success_wait_time)
                else:
                    # 处理访问失败的逻辑
                    self.failure_count += 1  # 仅在访问失败时递增
                    if self.failure_count == 1:
                        self.first_failure_time = time.time() # 首次失败时记录时间
                    self.sucess_count = 0  # 重置成功次数

                    failure_message = f"访问失败，失败次数: {self.failure_count}"
                    logging.info(failure_message)

                    # 在失败次数达到5次及以上时发送通知
                    if self.failure_count >= self.notify_after_failures:
                        # 发送通知
                        self.send_notification(failure_message, failure_message)

                        # if self.failure_count >= self.command_after_failures and self.failure_count % self.command_after_failures == 0:  # 达到失败限制时，则重启服务
                        if  int((time.time() - self.first_failure_time)/60) >= self.command_after_failures:  # 调整为根据首次失败时间 对比当前时间 如果大于参数 则重启服务

                            # 判断是否在 Linux 环境下执行 Linux 命令
                            if platform.system() == "Linux":
                                # 检查文件是否存在并可执行
                                if os.path.exists(self.command_file) and os.access(self.command_file, os.X_OK):
                                    # 执行 Linux 命令
                                    subprocess.run([self.command_file])

                                    # 发送服务已重启通知
                                    reboot_message_info = f"本轮首次失败时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.first_failure_time))}" 
                                    reboot_message_info = f"{reboot_message_info}, 失败持续时间: {int((time.time() - self.first_failure_time) / 60)} 分钟"
                                    reboot_message_info = f"{reboot_message_info}, 本次文件执行时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                                    reboot_message = f"达到访问失败设定时间({self.command_after_failures}分钟)，重启程序已执行."
                                    logging.info(reboot_message)
                                    logging.info(reboot_message_info)
                                    self.send_notification(reboot_message, reboot_message_info)
                                else:
                                    reboot_failure_message="文件执行失败, 文件不存在或不可执行."
                                    logging.info(reboot_failure_message)
                                    self.send_notification(reboot_failure_message, reboot_failure_message)
                            else:
                                reboot_failure_message="文件执行失败, 非linux服务器无法执行."
                                logging.info(reboot_failure_message)
                                self.send_notification(reboot_failure_message, reboot_failure_message)

                    # 等待1分钟再次访问
                    time.sleep(self.failure_wait_time)

            except Exception as e:
                # 在发生异常时记录错误
                logging.error(f"发生了异常: {e}")

                # 等待1分钟再次访问
                time.sleep(self.failure_wait_time)

def main():
    # 配置日志
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=[
                            logging.StreamHandler(),  # 输出到控制台
                            logging.FileHandler('sservo.log', encoding='utf-8')  # 输出到日志文件
                        ])
    
    # 创建并启动守护进程线程
    daemon_thread = DaemonThread()
    daemon_thread.daemon = True
    daemon_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("守护进程被终止.")

if __name__ == "__main__":
    main()
