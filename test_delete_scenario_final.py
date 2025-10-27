#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除场景功能验证 - 基于现有存储数据测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from latest_dynamic_storage import DynamicStorage
from config import UP_LIST
import json

def test_delete_scenario_with_existing_data():
    """使用现有存储数据测试删除场景功能"""
    print("=== 删除场景功能验证 ===")
    
    storage = DynamicStorage()
    
    print("\n1. 检查当前存储状态")
    try:
        with open('latest_dynamic_ids.json', 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        print(f"   ✅ 存储文件读取成功")
        print(f"   📋 存储的UP主: {list(all_data.keys())}")
    except Exception as e:
        print(f"   ❌ 读取存储文件失败: {e}")
        return False
    
    success_count = 0
    total_count = 0
    
    print("\n2. 验证删除场景功能")
    
    for up_config in UP_LIST:
        up_name = up_config['name']
        total_count += 1
        
        print(f"\n🎯 测试UP主: {up_name}")
        
        try:
            # 获取存储的动态ID列表
            recent_ids = storage.get_recent_dynamic_ids(up_name)
            latest_id = storage.get_latest_dynamic_id(up_name)
            
            print(f"   📊 recent_dynamic_ids数量: {len(recent_ids)}")
            print(f"   📊 latest_dynamic_id: {latest_id}")
            
            if not recent_ids:
                print(f"   ⚠️  未找到存储的动态ID")
                continue
            
            # 测试删除场景判断
            print(f"\n   🧪 测试删除场景判断:")
            
            # 1. 测试存储中存在的动态（模拟已删除的动态）
            existing_id = recent_ids[0]
            is_existing_new = storage.is_new_dynamic(up_name, existing_id)
            print(f"   🧪 存储中的动态 {existing_id[:10]}... 是否为新: {is_existing_new}")
            
            # 2. 测试全新的动态ID
            new_id = "test_new_dynamic_id_12345"
            is_new_dynamic = storage.is_new_dynamic(up_name, new_id)
            print(f"   🧪 全新的动态 {new_id[:10]}... 是否为新: {is_new_dynamic}")
            
            # 3. 验证逻辑正确性
            print(f"\n   ✅ 验证结果:")
            if not is_existing_new and is_new_dynamic:
                print(f"   ✅ 删除场景判断正确")
                print(f"   ✅ 新动态识别正确")
                success_count += 1
            else:
                print(f"   ❌ 删除场景判断异常")
                if is_existing_new:
                    print(f"   ❌ 存储的动态被误判为新动态")
                if not is_new_dynamic:
                    print(f"   ❌ 新动态被误判为旧动态")
            
            # 显示存储详情
            if up_name in all_data:
                up_data = all_data[up_name]
                print(f"\n   📋 存储详情:")
                print(f"   📋 update_time: {up_data.get('update_time', 'N/A')}")
                print(f"   📋 publish_time: {up_data.get('publish_time', 'N/A')}")
                print(f"   📋 recent_dynamic_ids: {len(up_data.get('recent_dynamic_ids', []))} 条")
                print(f"   📋 latest_dynamic_id: {up_data.get('latest_dynamic_id', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
    
    # 测试结果总结
    print(f"\n=== 验证结果总结 ===")
    print(f"📊 测试UP主数量: {total_count}")
    print(f"✅ 成功数量: {success_count}")
    print(f"📈 成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print(f"\n🎉 删除场景功能验证通过！")
        print(f"✅ 多条动态存储功能正常")
        print(f"✅ 删除场景判断逻辑正确")
        print(f"✅ 新动态识别功能正常")
        return True
    else:
        print(f"\n⚠️  部分功能验证失败")
        return False

if __name__ == "__main__":
    success = test_delete_scenario_with_existing_data()
    sys.exit(0 if success else 1)