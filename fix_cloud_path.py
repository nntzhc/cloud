#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复云主机路径问题
"""

import os
import json
import shutil
from latest_dynamic_storage import DynamicStorage

def fix_cloud_storage():
    """修复云主机存储路径问题"""
    print("🔧 修复云主机存储路径问题")
    print("=" * 60)
    
    # 1. 创建绝对路径版本的存储类
    class CloudDynamicStorage(DynamicStorage):
        def __init__(self, storage_path="/home/cloud/latest_dynamic_ids.json"):
            # 使用绝对路径
            self.storage_file = storage_path
            self.data = {}
            self.load_storage()
    
    # 2. 测试不同路径
    test_paths = [
        "/home/cloud/latest_dynamic_ids.json",  # 云主机路径
        "./latest_dynamic_ids.json",            # 相对路径
        os.path.abspath("latest_dynamic_ids.json")  # 绝对路径
    ]
    
    print("📍 测试不同存储路径:")
    
    for path in test_paths:
        print(f"\n测试路径: {path}")
        try:
            # 创建存储实例
            storage = CloudDynamicStorage(path)
            
            # 检查文件是否存在
            exists = os.path.exists(path)
            print(f"   文件存在: {'✅' if exists else '❌'}")
            
            if exists:
                # 显示内容
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        data = json.loads(content)
                        print(f"   UP主数量: {len(data)}")
                        for up_name, up_data in data.items():
                            recent_ids = up_data.get('recent_dynamic_ids', [])
                            print(f"   {up_name}: {len(recent_ids)} 条动态")
                            if recent_ids:
                                print(f"      最新: {recent_ids[0]}")
                    else:
                        print("   ⚠️ 文件为空")
            
            # 测试动态ID检查
            test_up = "史诗级韭菜"
            test_id = "1128763498993549318"
            is_new = storage.is_new_dynamic(test_up, test_id)
            print(f"   动态ID {test_id}: {'✅ 新动态' if is_new else '❌ 已存在'}")
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    # 3. 创建云主机配置文件
    print(f"\n📝 创建云主机配置文件:")
    
    config_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云主机配置文件
解决路径问题
"""

import os
import sys

# 设置工作目录为脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 确保存储文件路径正确
STORAGE_FILE = os.path.join(script_dir, "latest_dynamic_ids.json")

print(f"工作目录: {os.getcwd()}")
print(f"存储文件: {STORAGE_FILE}")
'''
    
    with open('cloud_config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ 已创建 cloud_config.py")
    
    # 4. 创建修改后的主脚本
    print(f"\n🔄 创建云主机版本主脚本:")
    
    # 读取原脚本
    try:
        with open('Bilibili_dynamic_push.py', 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 在文件开头添加配置
        modified_content = config_content + "\n\n" + original_content
        
        with open('Bilibili_dynamic_push_cloud.py', 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print("✅ 已创建 Bilibili_dynamic_push_cloud.py")
        
    except FileNotFoundError:
        print("⚠️ 找不到 Bilibili_dynamic_push.py，跳过创建云主机版本")
    
    print("\n🎯 解决方案总结:")
    print("1. 使用绝对路径: /home/cloud/latest_dynamic_ids.json")
    print("2. 在脚本开头设置工作目录")
    print("3. 确保存储文件在云主机上正确创建")
    print("4. 使用 cloud_config.py 中的配置")

if __name__ == "__main__":
    fix_cloud_storage()