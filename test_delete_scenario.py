#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟博主删除动态的真实场景测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from latest_dynamic_storage import DynamicStorage
from datetime import datetime

def test_delete_scenario():
    """测试博主删除动态的场景"""
    print("=== 模拟博主删除动态场景测试 ===")
    
    storage = DynamicStorage()
    up_name = "测试博主"
    
    print(f"\n1. 博主连续发布5条动态")
    dynamic_ids = ['dyn_001', 'dyn_002', 'dyn_003', 'dyn_004', 'dyn_005']
    for i, dyn_id in enumerate(dynamic_ids):
        storage.update_latest_dynamic_id(up_name, dyn_id, datetime.now())
        print(f"   发布动态 {dyn_id}: 存储列表 = {storage.get_recent_dynamic_ids(up_name)}")
    
    print(f"\n2. 当前存储状态:")
    print(f"   最近5条动态: {storage.get_recent_dynamic_ids(up_name)}")
    print(f"   最新动态ID: {storage.get_latest_dynamic_id(up_name)}")
    
    print(f"\n3. 博主删除了最新动态(dyn_005)，系统获取到dyn_004作为'最新动态'")
    # 模拟系统获取到dyn_004作为最新动态（因为dyn_005被删除了）
    latest_fetched = 'dyn_004'
    is_new = storage.is_new_dynamic(up_name, latest_fetched)
    print(f"   获取到的动态ID: {latest_fetched}")
    print(f"   是否判断为新动态: {is_new}")
    print(f"   结果: {'❌ 会误判为新动态' if is_new else '✅ 正确识别为旧动态'}")
    
    print(f"\n4. 博主又发布了新动态(dyn_006)")
    # 先判断是否为新的，再更新存储（模拟真实流程）
    is_new = storage.is_new_dynamic(up_name, 'dyn_006')
    print(f"   是否判断为新动态: {is_new}")
    print(f"   结果: {'✅ 正确识别为新动态' if is_new else '❌ 错误识别为旧动态'}")
    
    # 如果是新动态，再更新存储
    if is_new:
        storage.update_latest_dynamic_id(up_name, 'dyn_006', datetime.now())
        print(f"   更新后的存储列表: {storage.get_recent_dynamic_ids(up_name)}")
    
    print(f"\n5. 测试边界情况 - 获取到列表中不存在的动态")
    test_ids = ['dyn_000', 'dyn_007', 'dyn_003']  # 一个旧的，一个新的，一个存在的
    for test_id in test_ids:
        is_new = storage.is_new_dynamic(up_name, test_id)
        status = "新动态" if is_new else "旧动态"
        print(f"   动态 {test_id}: {status}")
    
    print(f"\n6. 清理测试数据")
    storage.clear_up_storage(up_name)
    print(f"   清理后存储: {storage.get_recent_dynamic_ids(up_name)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_delete_scenario()