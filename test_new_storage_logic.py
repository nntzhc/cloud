#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的动态存储逻辑 - 存储最近5条动态ID避免博主删除动态导致的误判
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from latest_dynamic_storage import DynamicStorage
from datetime import datetime

def test_new_storage_logic():
    """测试新的存储逻辑"""
    print("=== 测试新的动态存储逻辑 ===")
    
    # 创建新的存储实例（避免影响现有数据）
    storage = DynamicStorage()
    test_uid = "test_up_001"
    
    print(f"\n1. 初始状态测试 - UP主: {test_uid}")
    print(f"   是否为新动态 (ID: 'dyn_001'): {storage.is_new_dynamic(test_uid, 'dyn_001')}")
    print(f"   最近动态ID列表: {storage.get_recent_dynamic_ids(test_uid)}")
    
    print(f"\n2. 添加第一条动态")
    storage.update_latest_dynamic_id(test_uid, 'dyn_001', datetime.now())
    print(f"   是否为新动态 (ID: 'dyn_001'): {storage.is_new_dynamic(test_uid, 'dyn_001')}")
    print(f"   是否为新动态 (ID: 'dyn_002'): {storage.is_new_dynamic(test_uid, 'dyn_002')}")
    print(f"   最近动态ID列表: {storage.get_recent_dynamic_ids(test_uid)}")
    
    print(f"\n3. 添加第二条动态")
    storage.update_latest_dynamic_id(test_uid, 'dyn_002', datetime.now())
    print(f"   是否为新动态 (ID: 'dyn_001'): {storage.is_new_dynamic(test_uid, 'dyn_001')}")
    print(f"   是否为新动态 (ID: 'dyn_002'): {storage.is_new_dynamic(test_uid, 'dyn_002')}")
    print(f"   是否为新动态 (ID: 'dyn_003'): {storage.is_new_dynamic(test_uid, 'dyn_003')}")
    print(f"   最近动态ID列表: {storage.get_recent_dynamic_ids(test_uid)}")
    
    print(f"\n4. 模拟博主删除最新动态的场景")
    # 假设博主删除了dyn_002，现在dyn_001又变成了"最新"动态
    print(f"   是否为新动态 (ID: 'dyn_001'): {storage.is_new_dynamic(test_uid, 'dyn_001')}")
    print(f"   结果: {'❌ 会误判为新动态' if storage.is_new_dynamic(test_uid, 'dyn_001') else '✅ 正确识别为旧动态'}")
    
    print(f"\n5. 添加更多动态，测试5条限制")
    for i in range(3, 8):
        storage.update_latest_dynamic_id(test_uid, f'dyn_{i:03d}', datetime.now())
    print(f"   最近动态ID列表: {storage.get_recent_dynamic_ids(test_uid)}")
    print(f"   列表长度: {len(storage.get_recent_dynamic_ids(test_uid))}")
    
    print(f"\n6. 测试重复添加同一条动态")
    storage.update_latest_dynamic_id(test_uid, 'dyn_007', datetime.now())
    print(f"   重复添加dyn_007后的列表: {storage.get_recent_dynamic_ids(test_uid)}")
    print(f"   列表长度: {len(storage.get_recent_dynamic_ids(test_uid))}")
    
    print(f"\n7. 清理测试数据")
    storage.clear_up_storage(test_uid)
    print(f"   清理后是否为新动态 (ID: 'dyn_001'): {storage.is_new_dynamic(test_uid, 'dyn_001')}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_new_storage_logic()