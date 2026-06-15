import random
import sys
import time

# ANSI 颜色转义字符定义
COLOR_RESET = "\033[0m"
COLOR_TITLE = "\033[1;35m"    # 洋红粗体
COLOR_SUCCESS = "\033[1;32m"  # 绿色粗体
COLOR_ERROR = "\033[1;31m"    # 红色粗体
COLOR_WARN = "\033[1;33m"     # 黄色粗体
COLOR_INFO = "\033[1;36m"     # 青色粗体
COLOR_GRAY = "\033[90m"       # 灰色

def print_colored(text, color_code):
    """打印彩色文本"""
    print(f"{color_code}{text}{COLOR_RESET}")

def print_banner():
    """打印游戏横幅"""
    banner = """
    =========================================
    🎉       欢迎来到【猜数字小游戏】        🎉
    =========================================
    """
    print_colored(banner, COLOR_TITLE)

def select_difficulty():
    """选择游戏难度，返回 (数字上限, 最大猜测次数, 难度名称)"""
    while True:
        print_colored("\n请选择游戏难度：", COLOR_INFO)
        print("1. 简单 (数字范围 1-50， 8 次机会)")
        print("2. 中等 (数字范围 1-100，6 次机会)")
        print("3. 困难 (数字范围 1-200，4 次机会)")
        choice = input(f"{COLOR_WARN}请输入难度编号 (1/2/3): {COLOR_RESET}").strip()
        
        if choice == '1':
            return 50, 8, "简单"
        elif choice == '2':
            return 100, 6, "中等"
        elif choice == '3':
            return 200, 4, "困难"
        else:
            print_colored("❌ 输入无效，请输入 1、2 或 3！", COLOR_ERROR)

def play_game(best_scores):
    """单局游戏主循环"""
    max_num, max_attempts, difficulty_name = select_difficulty()
    target_num = random.randint(1, max_num)
    
    print_colored(f"\n🎮 游戏开始！我已经想好了一个 1 到 {max_num} 之间的数字。", COLOR_INFO)
    print_colored(f"当前难度：【{difficulty_name}】，你有 {max_attempts} 次猜测机会。\n", COLOR_INFO)
    
    start_time = time.time()
    attempts = 0
    
    while attempts < max_attempts:
        # 显示剩余生命值
        remaining = max_attempts - attempts
        hearts = "❤️ " * remaining + "🖤 " * (max_attempts - remaining)
        print(f"生命值: {hearts} ({remaining}/{max_attempts})")
        
        # 获取用户输入
        try:
            guess_str = input(f"{COLOR_WARN}请输入你猜的数字: {COLOR_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print_colored("\n👋 游戏已退出，期待下次再玩！", COLOR_INFO)
            sys.exit(0)
            
        # 输入校验
        if not guess_str.isdigit():
            print_colored("⚠️ 警告：请输入有效的正整数！本次猜测不计入次数。\n", COLOR_WARN)
            continue
            
        guess = int(guess_str)
        if guess < 1 or guess > max_num:
            print_colored(f"⚠️ 警告：数字必须在 1 到 {max_num} 之间！本次猜测不计入次数。\n", COLOR_WARN)
            continue
            
        # 计入有效猜测次数
        attempts += 1
        
        # 结果比对
        if guess == target_num:
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            print_colored(f"\n🎉 恭喜你答对了！答案就是 {target_num}！ 🎉", COLOR_SUCCESS)
            print_colored(f"⏱️ 本次耗时：{elapsed_time} 秒，共猜了 {attempts} 次。", COLOR_SUCCESS)
            
            # 更新并显示历史最佳成绩
            prev_best = best_scores.get(difficulty_name)
            if prev_best is None or attempts < prev_best:
                best_scores[difficulty_name] = attempts
                print_colored(f"🏆 创纪录！这是你在【{difficulty_name}】难度下的历史最佳成绩！", COLOR_SUCCESS)
            else:
                print_colored(f"ℹ️ 该难度下的历史最佳成绩为：{prev_best} 次猜测。", COLOR_GRAY)
            return
        elif guess > target_num:
            print_colored("📈 太高了！再试一次。\n", COLOR_ERROR)
        else:
            print_colored("📉 太低了！再试一次。\n", COLOR_INFO)
            
    # 生命值耗尽，游戏失败
    print_colored(f"\n💀 游戏结束！你的机会用光了。正确答案其实是 {target_num}。别气馁，下回再战！", COLOR_ERROR)

def main():
    print_banner()
    best_scores = {} # 用于保存本次运行中各个难度的历史最佳成绩
    
    while True:
        play_game(best_scores)
        
        # 询问是否重玩
        while True:
            retry = input(f"\n{COLOR_WARN}是否再玩一局？(y/n): {COLOR_RESET}").strip().lower()
            if retry in ('y', 'yes'):
                print_colored("\n🔄 重新载入游戏...", COLOR_TITLE)
                break
            elif retry in ('n', 'no'):
                print_colored("\n👋 谢谢游玩，再见！", COLOR_TITLE)
                return
            else:
                print_colored("❌ 输入无效，请输入 y 或 n！", COLOR_ERROR)

if __name__ == "__main__":
    main()
