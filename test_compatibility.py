#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新旧存储格式的向后兼容性
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from latest_dynamic_storage import DynamicStorage

def test_backward_compatibility():
    """测试向后兼容性"""
    print("=== 测试新旧存储格式兼容性 ===")
    
    # 创建测试文件，模拟旧的存储格式
    test_file = "test_old_format.json"
    old_data = {
        "测试UP主1": {
            "dynamic_id": "old_dyn_123",
            "update_time": "2025-10-19T14:00:00",
            "publish_time": "2025-10-19T13:00:00"
        },
        "测试UP主2": {
            "dynamic_id": "old_dyn_456", 
            "update_time": "2025-10-19T15:00:00",
            "publish_time": "2025-10-19T14:00:00"
        }
    }
    
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(old_data, f, ensure_ascii=False, indent=2)
    
    # 使用DynamicStorage加载旧格式数据
    storage = DynamicStorage()
    storage.storage_file = test_file
    storage.load_storage()
    
    print("1. 加载旧格式数据:")
    print(f"   存储的UP主数量: {len(storage.data)}")
    
    for up_name in ["测试UP主1", "测试UP主2"]:
        latest_id = storage.get_latest_dynamic_id(up_name)
        recent_ids = storage.get_recent_dynamic_ids(up_name)
        print(f"   {up_name}:")
        print(f"     最新动态ID: {latest_id}")
        print(f"     最近动态列表: {recent_ids}")
    
    print("\n2. 测试is_new_dynamic函数:")
    # 测试旧格式的UP主
    is_new = storage.is_new_dynamic("测试UP主1", "old_dyn_123")
    print(f"   旧动态old_dyn_123是否为新: {is_new} (应该为False)")
    
    is_new = storage.is_new_dynamic("测试UP主1", "new_dyn_999")
    print(f"   新动态new_dyn_999是否为新: {is_new} (应该为True)")
    
    print("\n3. 测试更新到新格式:")
    storage.update_latest_dynamic_id("测试UP主1", "new_dyn_999")
    
    latest_id = storage.get_latest_dynamic_id("测试UP主1")
    recent_ids = storage.get_recent_dynamic_ids("测试UP主1")
    print(f"   更新后最新动态ID: {latest_id}")
    print(f"   更新后最近动态列表: {recent_ids}")
    
    print("\n4. 测试保存的新格式:")
    # 重新加载文件查看保存的格式
    with open(test_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    
    print("   保存的数据结构:")
    for up_name, data in saved_data.items():
        print(f"     {up_name}: {list(data.keys())}")
    
    print("\n5. 清理测试文件")
    os.remove(test_file)
    
    print("\n=== 兼容性测试完成 ===")

if __name__ == "__main__":
    test_backward_compatibility()