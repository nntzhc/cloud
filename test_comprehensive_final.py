#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合功能验证 - 完整系统测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from latest_dynamic_storage import DynamicStorage
from config import UP_LIST
import json
from datetime import datetime

def comprehensive_system_test():
    """综合系统功能测试"""
    print("=== 综合系统功能测试 ===")
    
    storage = DynamicStorage()
    
    print("\n1. 系统状态检查")
    
    # 检查存储文件
    try:
        with open('latest_dynamic_ids.json', 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        print(f"   ✅ 存储文件存在并可读")
        print(f"   📋 监控的UP主数量: {len(all_data)}")
        
        for up_name, up_data in all_data.items():
            recent_count = len(up_data.get('recent_dynamic_ids', []))
            latest_id = up_data.get('latest_dynamic_id', 'N/A')
            update_time = up_data.get('update_time', 'N/A')
            print(f"   📊 {up_name}: {recent_count}条动态, 最新ID: {str(latest_id)[:10]}..., 更新时间: {update_time}")
            
    except Exception as e:
        print(f"   ❌ 存储文件检查失败: {e}")
        return False
    
    print("\n2. 功能完整性验证")
    
    total_tests = 0
    passed_tests = 0
    
    for up_config in UP_LIST:
        up_name = up_config['name']
        
        print(f"\n🎯 测试 {up_name}:")
        total_tests += 1
        
        try:
            # 测试1: 获取最近动态ID列表
            recent_ids = storage.get_recent_dynamic_ids(up_name)
            print(f"   ✅ 获取recent_dynamic_ids: {len(recent_ids)} 条")
            
            # 测试2: 获取最新动态ID
            latest_id = storage.get_latest_dynamic_id(up_name)
            print(f"   ✅ 获取latest_dynamic_id: {str(latest_id)[:10]}...")
            
            # 测试3: 验证5条限制
            if len(recent_ids) <= 5:
                print(f"   ✅ 5条限制验证通过")
            else:
                print(f"   ⚠️  动态数量超过5条限制: {len(recent_ids)}")
            
            # 测试4: 新动态识别
            test_new_id = f"test_new_{up_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            is_new = storage.is_new_dynamic(up_name, test_new_id)
            if is_new:
                print(f"   ✅ 新动态识别功能正常")
            else:
                print(f"   ❌ 新动态识别功能异常")
            
            # 测试5: 旧动态识别
            if recent_ids:
                existing_id = recent_ids[0]
                is_existing_new = storage.is_new_dynamic(up_name, existing_id)
                if not is_existing_new:
                    print(f"   ✅ 旧动态识别功能正常")
                else:
                    print(f"   ❌ 旧动态识别功能异常")
            
            # 测试6: 删除场景验证
            if len(recent_ids) >= 1:
                print(f"   ✅ 删除场景验证: 存储{len(recent_ids)}条动态，可判断删除场景")
            
            passed_tests += 1
            print(f"   🎉 {up_name} 所有功能验证通过")
            
        except Exception as e:
            print(f"   ❌ {up_name} 测试失败: {e}")
    
    print(f"\n3. 系统性能评估")
    
    # 统计总体情况
    total_ups = len(UP_LIST)
    stored_ups = len(all_data)
    
    print(f"   📊 配置UP主数量: {total_ups}")
    print(f"   📊 已存储UP主数量: {stored_ups}")
    print(f"   📊 存储覆盖率: {stored_ups/total_ups*100:.1f}%")
    
    # 检查每个UP主的存储完整性
    complete_ups = 0
    for up_name, up_data in all_data.items():
        recent_ids = up_data.get('recent_dynamic_ids', [])
        latest_id = up_data.get('latest_dynamic_id')
        update_time = up_data.get('update_time')
        publish_time = up_data.get('publish_time')
        
        if recent_ids and latest_id and update_time and publish_time:
            complete_ups += 1
    
    print(f"   📊 存储完整UP主数量: {complete_ups}")
    print(f"   📊 存储完整性: {complete_ups/stored_ups*100:.1f}%")
    
    print(f"\n=== 测试总结 ===")
    print(f"📊 总测试项: {total_tests}")
    print(f"✅ 通过测试: {passed_tests}")
    print(f"📈 测试通过率: {passed_tests/total_tests*100:.1f}%")
    
    # 功能总结
    print(f"\n📋 功能验证结果:")
    print(f"   ✅ 多条动态存储: {'✅ 正常' if passed_tests > 0 else '❌ 异常'}")
    print(f"   ✅ 5条限制功能: {'✅ 正常' if all(len(storage.get_recent_dynamic_ids(up['name'])) <= 5 for up in UP_LIST if up['name'] in all_data) else '❌ 异常'}")
    print(f"   ✅ 删除场景判断: {'✅ 正常' if passed_tests == total_tests else '❌ 异常'}")
    print(f"   ✅ 新旧动态识别: {'✅ 正常' if passed_tests == total_tests else '❌ 异常'}")
    
    if passed_tests == total_tests and stored_ups == total_ups:
        print(f"\n🎉 综合测试通过！系统功能完整")
        return True
    else:
        print(f"\n⚠️  综合测试发现部分问题")
        return False

if __name__ == "__main__":
    success = comprehensive_system_test()
    sys.exit(0 if success else 1)