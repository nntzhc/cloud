#!/usr/bin/env python3
"""
Git保存和推送脚本
自动添加所有更改、提交并推送到远程仓库
提交信息使用当前日期格式：YYYYMMDD
"""

import subprocess
import sys
from datetime import datetime

def run_git_command(command, description):
    """运行git命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=".")
        if result.returncode != 0:
            print(f"❌ {description}失败:")
            print(f"错误信息: {result.stderr}")
            return False
        else:
            if result.stdout.strip():
                print(f"✅ {description}成功")
                print(f"输出: {result.stdout.strip()}")
            else:
                print(f"✅ {description}成功")
            return True
    except Exception as e:
        print(f"❌ {description}时发生异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Git保存和推送工具")
    print("=" * 40)
    
    # 获取当前日期作为提交信息
    current_date = datetime.now().strftime("%Y%m%d")
    commit_message = current_date
    
    print(f"📅 提交信息: {commit_message}")
    print()
    
    # 步骤1: git add .
    if not run_git_command("git add .", "添加所有更改到暂存区"):
        return 1
    print()
    
    # 步骤2: git commit
    commit_cmd = f'git commit -m "{commit_message}"'
    if not run_git_command(commit_cmd, f"提交更改 (消息: {commit_message})"):
        # 检查是否因为没有更改而失败
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        if not result.stdout.strip():
            print("ℹ️  没有需要提交的更改")
            print("🔄 继续执行推送...")
        else:
            return 1
    print()
    
    # 步骤3: git push
    if not run_git_command("git push", "推送到远程仓库"):
        # 检查是否因为远程仓库有更新而失败
        result = subprocess.run("git push", shell=True, capture_output=True, text=True)
        if "Updates were rejected" in result.stderr:
            print("⚠️  检测到远程仓库有更新，尝试强制推送...")
            print("💡 建议使用: git pull 先拉取更新，或使用 git push --force 强制推送")
            response = input("是否执行强制推送? (y/N): ").strip().lower()
            if response == 'y':
                if not run_git_command("git push --force", "强制推送到远程仓库"):
                    return 1
            else:
                print("❌ 推送取消")
                return 1
        else:
            return 1
    
    print()
    print("🎉 所有操作完成！")
    print("=" * 40)
    return 0

if __name__ == "__main__":
    sys.exit(main())