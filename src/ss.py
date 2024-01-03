import threading
import time
import logging
import json
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
from sservodo import main_daemon_work

class WorkerThread(threading.Thread):
    def __init__(self, daemon_config, stop_event):
        super().__init__()
        self.daemon_config = daemon_config
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            if self.daemon_config['daemon']['daemon_run'] == "true":
                logging.info(f"守护进程线程 {self.daemon_config['daemon']['daemon_name']} 正在执行...")
                # TODO: 执行守护进程的工作
                main_daemon_work(self.daemon_config, self.stop_event)

                # # 打印正在运行的日志
                # self.log_running_status()

                # time.sleep(self.daemon_config['retry']['success_wait_time'])
            else:
                logging.info(f"守护进程线程 {self.daemon_config['daemon']['daemon_name']} 未启动，跳过执行.")
                time.sleep(5)  # 如果线程未启动，等待一段时间再检查

    def log_running_status(self):
        # 打印正在运行的日志
        logging.info(f"线程 {self.daemon_config['daemon']['daemon_name']} 正在运行，等待 {self.daemon_config['retry']['success_wait_time']} 秒后继续执行.")

def create_worker_threads(config, stop_event):
    threads = []
    for daemon_config in config['daemon_list']:
        thread = WorkerThread(daemon_config, stop_event)
        threads.append(thread)
    return threads

# class ConfigFileHandler(FileSystemEventHandler):
#     def __init__(self, threads):
#         self.threads = threads

#     def on_modified(self, event):
#         logging.info("配置文件被修改，重新加载配置...")
#         time.sleep(1)
#         # 在配置文件被修改时，重新加载配置
#         with open('./config.json', 'r') as file:
#             new_config = json.load(file)

#         # 更新工作线程的配置
#         for thread, daemon_config in zip(self.threads, new_config['daemon_list']):
#             thread.daemon_config = daemon_config

# 全局变量，用于在多线程间传递配置
config = None

def main():
    global config

    # 读取配置文件
    with open('./config.json', 'r') as file:
        config = json.load(file)

    # 将 success_wait_time 转换为整数
    for daemon_config in config['daemon_list']:
        daemon_config['retry']['success_wait_time'] = int(daemon_config['retry']['success_wait_time'])

    # 配置日志
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=[
                            logging.StreamHandler(),  # 输出到控制台
                            logging.FileHandler('sservo.log', encoding='utf-8')  # 输出到日志文件，指定编码为utf-8
                        ])

    # 创建停止事件，用于通知线程停止
    stop_event = threading.Event()

    # 创建工作线程时传递停止事件
    threads = create_worker_threads(config, stop_event)

    # 创建配置文件监控
    # event_handler = ConfigFileHandler(threads)
    # observer = Observer()
    # observer.schedule(event_handler, path='.', recursive=False)
    # observer.start()

    try:
        # 启动工作线程
        for thread in threads:
            thread.start()

        # 主线程等待键盘中断
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("用户请求关闭程序，系统将在最后一次访问后关闭，请稍后...")

    finally:
        # 设置停止事件，通知所有工作线程停止
        stop_event.set()

        # 停止配置文件监控
        # observer.stop()
        # observer.join()

        # 等待工作线程完成
        for thread in threads:
            thread.join()
            logging.info(thread.name)

        # 关闭日志记录
        logging.shutdown()

        logging.info("程序关闭完成")

if __name__ == "__main__":
    main()
