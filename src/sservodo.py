# sservo.py

import os
import time
import logging
import subprocess
import platform
from datetime import datetime
from page import page_get_and_validate  # 指定页面检查
# from server_linux import check_system_resources  # linux 服务器资源检查
from wx_notification import send_notification  # 发送通知 调用 wxpusher

# 发生通知
def send_notification(self, summary, content):
    send_notification(summary, content, self['notification']['notification_url'], self['notification']['appToken'], self['notification']['topicIds'])

# 主运行程序
def main_daemon_work(self):
    failure_count = 0
    first_failure_time = 0
    sucess_count = 0
    while True:
        try:
            server_name = self['daemon']['daemon_name']
            page_url = self['daemon']['page_url']
            validate_text = self['daemon']['validate_text']
            success_wait_time = self['retry']['success_wait_time']
            failure_wait_time = self['retry']['failure_wait_time']
            notify_after_failures = self['retry']['notify_after_failures']
            notify_after_success = self['retry']['notify_after_success']
            command_after_failures = self['retry']['command_after_failures']
            command_file = self['retry']['command_file']
            notification_url = self['notification']['notification_url']
            appToken = self['notification']['appToken']
            topicIds = self['notification']['topicIds']

            # 调用 "page.py" 中的方法
            result = page_get_and_validate(page_url, validate_text)

            # 根据返回值进行逻辑判断
            if result == 1:
                # 处理访问成功的逻辑
                sucess_count += 1  # 仅在访问成功时递增
                first_failure_time = 0 # 重置首次失败时间

                if failure_count == 0:
                    logging.info(f"{server_name}访问成功！")
                else:
                    sucess_message = f"{server_name}访问成功！之前失败次数: {failure_count}"
                    logging.info(sucess_message)
                    self.send_notification(sucess_message, sucess_message)

                failure_count = 0  # 重置失败次数
                
                # 在成功次数达到N次，及倍数时发送通知 
                if sucess_count >= notify_after_success and sucess_count % notify_after_success == 0:
                    sucess_message = f"{server_name}访问成功！连续成功次数: {sucess_count}"
                    logging.info(sucess_message)
                    self.send_notification(sucess_message, sucess_message)

                # 等待10分钟再次访问
                time.sleep(success_wait_time)
            else:
                # 处理访问失败的逻辑
                failure_count += 1  # 仅在访问失败时递增
                if failure_count == 1:
                    first_failure_time = time.time() # 首次失败时记录时间
                sucess_count = 0  # 重置成功次数

                failure_message = f"{server_name}访问失败，失败次数: {failure_count}"
                logging.info(failure_message)

                # 在失败次数达到5次及以上时发送通知
                if failure_count >= notify_after_failures:
                    # 发送通知
                    self.send_notification(failure_message, failure_message)

                    # if self.failure_count >= self.command_after_failures and self.failure_count % self.command_after_failures == 0:  # 达到失败限制时，则重启服务
                    if  int((time.time() - first_failure_time)/60) >= command_after_failures:  # 调整为根据首次失败时间 对比当前时间 如果大于参数 则重启服务

                        # 判断是否在 Linux 环境下执行 Linux 命令
                        if platform.system() == "Linux":
                            # 检查文件是否存在并可执行
                            if os.path.exists(command_file) and os.access(command_file, os.X_OK):
                                # 执行 Linux 命令
                                subprocess.run([self.command_file])

                                # 发送服务已重启通知
                                reboot_message_info = f"{server_name}-本轮首次失败时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(first_failure_time))}" 
                                reboot_message_info = f"{reboot_message_info}, 失败持续时间: {int((time.time() - first_failure_time) / 60)} 分钟"
                                reboot_message_info = f"{reboot_message_info}, 本次文件执行时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                                reboot_message = f"{server_name}-达到失败设定({command_after_failures}分钟)，程序已执行."
                                logging.info(reboot_message)
                                logging.info(reboot_message_info)
                                self.send_notification(reboot_message, reboot_message_info)
                            else:
                                reboot_failure_message=f"{server_name}-文件执行失败, 文件不存在或不可执行."
                                logging.info(reboot_failure_message)
                                self.send_notification(reboot_failure_message, reboot_failure_message)
                        else:
                            reboot_failure_message=f"{server_name}-文件执行失败, 非linux服务器无法执行."
                            logging.info(reboot_failure_message)
                            self.send_notification(reboot_failure_message, reboot_failure_message)

                # 等待1分钟再次访问
                time.sleep(failure_wait_time)

        except Exception as e:
            # 在发生异常时记录错误
            logging.error(f"发生了异常: {e}")

            # 等待1分钟再次访问
            time.sleep(failure_wait_time)
