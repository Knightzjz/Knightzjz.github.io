#!/usr/bin/env python3
"""
预提交脚本：自动更新 Current Version 为即将生成的 commit SHA
用法: python3 commit_with_version.py "你的提交信息"
"""

import subprocess
import sys
import re

def get_staged_changes():
    """获取暂存区的文件列表"""
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                          capture_output=True, text=True)
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def update_version_in_file():
    """更新 about.md 中的 Current Version 为占位符"""
    filepath = '_pages/about.md'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换 Current Version 的值
    # 使用占位符，因为真实的 SHA 要在提交后才能知道
    pattern = r'(Current Version:</span>\s*<span class="number"[^>]*>)[^<]+(</span>)'
    
    # 暂时标记为 WILL_BE_UPDATED
    new_content = re.sub(pattern, r'\1WILL_BE_UPDATED\2', content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        subprocess.run(['git', 'add', filepath])
        print("✅ 标记 Current Version 为待更新")
        return True
    return False

def commit_and_update(message):
    """提交并获取 SHA，然后更新文件"""
    # 先提交（包含 WILL_BE_UPDATED）
    subprocess.run(['git', 'commit', '-m', message], check=True)
    
    # 获取刚生成的 commit SHA
    result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                          capture_output=True, text=True, check=True)
    commit_sha = result.stdout.strip()
    print(f"✅ 已提交，SHA: {commit_sha}")
    
    # 更新文件中的版本号
    filepath = '_pages/about.md'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace('WILL_BE_UPDATED', commit_sha)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # 修正提交（amend）
    subprocess.run(['git', 'add', filepath])
    subprocess.run(['git', 'commit', '--amend', '--no-edit'], check=True)
    
    print(f"✅ Current Version 已更新为: {commit_sha}")
    
    # 强制推送（因为 amend 会改变历史）
    subprocess.run(['git', 'push', '--force-with-lease'], check=True)
    print("✅ 已推送")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 commit_with_version.py '提交信息'")
        sys.exit(1)
    
    message = sys.argv[1]
    
    # 检查 about.md 是否在暂存区
    staged = get_staged_changes()
    if '_pages/about.md' not in staged:
        print("⚠️ about.md 不在暂存区，先添加...")
        subprocess.run(['git', 'add', '_pages/about.md'])
    
    commit_and_update(message)
