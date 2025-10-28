#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断云主机存储问题
"""

import os
import json
from latest_dynamic_storage import storage as dynamic_storage

def diagnose_cloud_issue():
    """诊断云主机存储问题"""
    print("☁️ 诊断云主机存储问题")
    print("=" * 60)
    
    # 1. 详细的路径信息
    print(f"\n📍 路径信息:")
    print(f"   当前工作目录: {os.getcwd()}")
    print(f"   脚本绝对路径: {os.path.abspath(__file__)}")
    print(f"   存储文件相对路径: {dynamic_storage.storage_file}")
    print(f"   存储文件绝对路径: {os.path.abspath(dynamic_storage.storage_file)}")
    
    # 2. 检查多个可能的路径
    possible_paths = [
        dynamic_storage.storage_file,
        "/home/cloud/latest_dynamic_ids.json",
        "./latest_dynamic_ids.json",
        "../latest_dynamic_ids.json",
        os.path.join(os.path.dirname(__file__), "latest_dynamic_ids.json")
    ]
    
    print(f"\n🔍 检查多个可能的路径:")
    for path in possible_paths:
        exists = os.path.exists(path)
        abs_path = os.path.abspath(path)
        print(f"   {path} -> {abs_path}: {'✅ 存在' if exists else '❌ 不存在'}")
        if exists:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"      内容长度: {len(content)} 字符")
                    if content.strip():
                        data = json.loads(content)
                        print(f"      UP主数量: {len(data)}")
                    else:
                        print(f"      ⚠️ 文件为空")
            except Exception as e:
                print(f"      ❌ 读取失败: {e}")
    
    # 3. 检查内存状态
    print(f"\n💾 内存状态:")
    print(f"   内存中的UP主数量: {len(dynamic_storage.data)}")
    for up_name in dynamic_storage.data:
        recent_ids = dynamic_storage.get_recent_dynamic_ids(up_name)
        print(f"   {up_name}: {len(recent_ids)} 条动态")
        if recent_ids:
            print(f"      最新: {recent_ids[0]}")
    
    # 4. 模拟云主机环境测试
    print(f"\n🧪 模拟云主机环境测试:")
    
    # 测试UP主
    test_up = "史诗级韭菜"
    test_id = "1128763498993549318"  # 你日志中提到的ID
    
    print(f"测试UP主: {test_up}")
    print(f"测试动态ID: {test_id}")
    
    # 检查是否为新的动态
    is_new = dynamic_storage.is_new_dynamic(test_up, test_id)
    print(f"is_new_dynamic() 结果: {is_new}")
    
    if not is_new:
        print("   说明：系统认为这个动态已存在")
        recent_ids = dynamic_storage.get_recent_dynamic_ids(test_up)
        print(f"   存储中的动态ID: {recent_ids}")
        if test_id in recent_ids:
            print(f"   ✅ 确认：{test_id} 确实在存储中")
        else:
            print(f"   ❌ 矛盾：{test_id} 不在存储中，但系统认为已存在")
    
    # 5. 检查文件创建时间
    print(f"\n⏰ 文件时间信息:")
    for path in possible_paths:
        if os.path.exists(path):
            stat = os.stat(path)
            print(f"   {path}:")
            print(f"      创建时间: {stat.st_ctime}")
            print(f"      修改时间: {stat.st_mtime}")
            print(f"      访问时间: {stat.st_atime}")
    
    print("\n✅ 诊断完成")

if __name__ == "__main__":
    diagnose_cloud_issue()