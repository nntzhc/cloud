#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断存储文件问题
"""

import os
import json
from datetime import datetime
from latest_dynamic_storage import storage as dynamic_storage

def diagnose_storage_issue():
    """诊断存储文件问题"""
    print("🔍 诊断存储文件问题")
    print("=" * 60)
    
    # 1. 检查当前工作目录
    print(f"\n📁 当前工作目录: {os.getcwd()}")
    
    # 2. 检查存储文件路径
    storage_file = dynamic_storage.storage_file
    print(f"📄 存储文件路径: {storage_file}")
    print(f"📄 绝对路径: {os.path.abspath(storage_file)}")
    
    # 3. 检查文件是否存在
    exists = os.path.exists(storage_file)
    print(f"\n✅ 文件存在: {exists}")
    
    if exists:
        # 4. 检查文件权限
        print(f"\n🔒 文件权限检查:")
        print(f"   可读: {os.access(storage_file, os.R_OK)}")
        print(f"   可写: {os.access(storage_file, os.W_OK)}")
        print(f"   文件大小: {os.path.getsize(storage_file)} 字节")
        
        # 5. 检查文件内容
        print(f"\n📋 文件内容:")
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"   内容长度: {len(content)} 字符")
                
                if content.strip():
                    data = json.loads(content)
                    print(f"   JSON数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                else:
                    print("   ⚠️ 文件为空！")
        except Exception as e:
            print(f"   ❌ 读取文件失败: {e}")
    else:
        print("\n❌ 文件不存在")
    
    # 6. 检查内存中的数据
    print(f"\n💾 内存中的数据:")
    memory_data = dynamic_storage.data
    print(f"   数据长度: {len(memory_data)}")
    if memory_data:
        print(f"   数据内容: {json.dumps(memory_data, ensure_ascii=False, indent=2)}")
    else:
        print("   ⚠️ 内存数据为空！")
    
    # 7. 测试写入操作
    print(f"\n📝 测试写入操作:")
    try:
        # 添加测试数据
        test_up = "测试UP主_诊断"
        test_id = f"test_{int(datetime.now().timestamp())}"
        
        print(f"   添加测试数据: {test_up} -> {test_id}")
        dynamic_storage.update_latest_dynamic_id(test_up, test_id)
        
        # 检查是否写入成功
        if os.path.exists(storage_file):
            with open(storage_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
                if test_up in new_content and test_id in new_content:
                    print("   ✅ 写入成功！")
                else:
                    print("   ❌ 写入失败：文件中没有测试数据")
        else:
            print("   ❌ 写入失败：文件仍然不存在")
            
        # 清理测试数据
        dynamic_storage.clear_up_storage(test_up)
        print("   🧹 清理测试数据")
        
    except Exception as e:
        print(f"   ❌ 写入测试失败: {e}")
    
    # 8. 检查目录权限
    print(f"\n📂 目录权限检查:")
    current_dir = os.getcwd()
    print(f"   目录: {current_dir}")
    print(f"   目录可写: {os.access(current_dir, os.W_OK)}")
    print(f"   目录可读: {os.access(current_dir, os.R_OK)}")
    
    print("\n✅ 诊断完成")

if __name__ == "__main__":
    diagnose_storage_issue()