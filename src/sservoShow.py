import curses
import colorama

def display_log(window, log_content, current_line):
    window.clear()
    height, width = window.getmaxyx()
    
    # 计算总行数
    total_lines = len(log_content)
    
    # 计算起始行和结束行
    start_line = min(max(0, current_line - height + 1), total_lines - height)
    end_line = min(start_line + height, total_lines)

    # 显示内容
    for i in range(start_line, end_line):
        try:
            if i == current_line:
                window.addstr(i - start_line, 0, log_content[i], curses.A_REVERSE)
            else:
                window.addstr(i - start_line, 0, log_content[i])
        except curses.error:
            pass

    window.refresh()

def main(stdscr):
    global current_line
    current_line = 0
    
    # 读取日志文件内容
    with open('sservo.log', 'r', encoding='utf-8', errors='replace') as file:
        log_content = file.readlines()

    # 使用curses进行初始化
    curses.curs_set(0)
    stdscr.timeout(100)

    while True:
        key = stdscr.getch()

        # 处理上下方向键
        if key == curses.KEY_UP:
            current_line = max(0, current_line - 1)
        elif key == curses.KEY_DOWN:
            current_line = min(len(log_content) - 1, current_line + 1)
        elif key == ord('q'):
            break

        # 显示日志内容
        display_log(stdscr, log_content, current_line)

if __name__ == "__main__":
    # 初始化 colorama（在 Windows 上）
    colorama.init()
    
    curses.wrapper(main)

    # 在程序结束前，恢复 colorama 状态
    colorama.deinit()
