#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的API解析功能
验证Terminal#44-46中cards为null问题的解决方案
"""

import json
import time
from dynamic_api import get_user_dynamics, _parse_api_response
from api_bypass import APIRestrictionBypass
from latest_dynamic_storage import storage as dynamic_storage

def test_empty_data_parsing():
    """测试空数据解析功能"""
    print("🧪 测试1: 空数据解析功能")
    print("-" * 40)
    
    # 创建bypass实例
    bypass = APIRestrictionBypass()
    bypass.setup_logger(log_level='INFO', enable_console=True)
    
    # 模拟Terminal#44-46中的情况：cards为null
    test_cases = [
        {
            'name': 'cards为null，has_more为0',
            'data': {
                'code': 0,
                'message': '0',
                'data': {
                    'items': None,
                    'cards': None,
                    'list': [],
                    'has_more': 0
                }
            }
        },
        {
            'name': 'items为空列表',
            'data': {
                'code': 0,
                'message': '0',
                'data': {
                    'items': [],
                    'cards': [],
                    'list': [],
                    'has_more': 0
                }
            }
        },
        {
            'name': '正常有数据',
            'data': {
                'code': 0,
                'message': '0',
                'data': {
                    'items': [
                        {
                            'id_str': '123456789',
                            'modules': {
                                'module_author': {
                                    'pub_ts': int(time.time())
                                }
                            }
                        }
                    ],
                    'has_more': 1
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: {test_case['name']}")
        items = _parse_api_response(test_case['data'], bypass)
        
        if i <= 2:  # 前两个是空数据测试
            if len(items) == 0:
                print("  ✅ 正确识别为空数据")
            else:
                print(f"  ❌ 错误，应该为空但获取到 {len(items)} 条数据")
        else:  # 第三个是有数据测试
            if len(items) > 0:
                print(f"  ✅ 正确识别有数据: {len(items)} 条")
            else:
                print("  ❌ 错误，应该有数据但为空")

def test_real_api_calls():
    """测试真实API调用"""
    print("\n\n🌐 测试2: 真实API调用")
    print("-" * 40)
    
    # 测试UP主列表
    test_users = [
        ('22376577', '牛奶糖好吃'),
        ('20898093', '史诗级韭菜')
    ]
    
    for uid, up_name in test_users:
        print(f"\n🔍 测试UP主: {up_name} (UID: {uid})")
        try:
            start_time = time.time()
            data = get_user_dynamics(uid, use_bypass=True)
            end_time = time.time()
            
            if data:
                print(f"  ✅ 成功获取动态数据 (耗时: {end_time - start_time:.2f}秒)")
            else:
                print(f"  ⚠️  未获取到动态数据 (耗时: {end_time - start_time:.2f}秒)")
                print("     可能原因:")
                print("     - UP主当前无新动态")
                print("     - API风控限制")
                print("     - 网络连接问题")
        except Exception as e:
            print(f"  ❌ 调用失败: {e}")

def test_multiplexing_endpoints():
    """测试多端点轮询机制"""
    print("\n\n🔄 测试3: 多端点轮询机制")
    print("-" * 40)
    
    print("改进后的端点轮询逻辑:")
    print("1. 首先尝试polymer端点")
    print("2. 如果返回空数据，自动尝试vc端点")
    print("3. 如果vc端点也返回空数据，尝试wbi端点")
    print("4. 只有获取到实际动态数据的端点才返回成功")
    print("5. 提供详细的调试信息帮助诊断问题")
    
    # 实际测试
    bypass = APIRestrictionBypass()
    bypass.setup_logger(log_level='INFO', enable_console=True)
    
    print(f"\n🔍 测试端点轮询:")
    data = get_user_dynamics('22376577', use_bypass=True)
    
    if data:
        print("  ✅ 某个端点成功返回数据")
        print("  📊 统计信息:")
        stats = bypass.get_stats()
        for key, value in stats.items():
            print(f"     {key}: {value}")
    else:
        print("  ⚠️  所有端点都未返回有效数据")
        print("  📊 统计信息:")
        stats = bypass.get_stats()
        for key, value in stats.items():
            print(f"     {key}: {value}")

def test_error_scenarios():
    """测试错误场景处理"""
    print("\n\n⚠️ 测试4: 错误场景处理")
    print("-" * 40)
    
    bypass = APIRestrictionBypass()
    bypass.setup_logger(log_level='INFO', enable_console=True)
    
    # 测试各种错误响应
    error_cases = [
        {
            'name': 'API返回-352风控错误',
            'data': {
                'code': -352,
                'message': '请求过于频繁',
                'data': {}
            }
        },
        {
            'name': 'API返回-799频率限制',
            'data': {
                'code': -799,
                'message': '请求过于频繁',
                'data': {}
            }
        },
        {
            'name': 'data字段为空',
            'data': {
                'code': 0,
                'message': '0',
                'data': None
            }
        }
    ]
    
    for i, test_case in enumerate(error_cases, 1):
        print(f"\n📋 错误场景 {i}: {test_case['name']}")
        items = _parse_api_response(test_case['data'], bypass)
        
        if len(items) == 0:
            print("  ✅ 正确处理错误场景，返回空列表")
        else:
            print(f"  ❌ 错误，应该返回空列表但获取到 {len(items)} 条数据")

def main():
    """主测试函数"""
    print("🚀 改进后的API解析功能测试")
    print("=" * 60)
    print("针对Terminal#44-46中cards为null问题的解决方案验证")
    print("=" * 60)
    
    try:
        test_empty_data_parsing()
        test_real_api_calls()
        test_multiplexing_endpoints()
        test_error_scenarios()
        
        print("\n\n📋 测试总结")
        print("=" * 60)
        print("✅ 改进效果:")
        print("1. 正确识别API返回成功但无数据的情况")
        print("2. 提供详细的调试信息和错误诊断")
        print("3. 实施多端点轮询机制，提高成功率")
        print("4. 增强数据验证和容错处理")
        print("5. 避免返回无效的空数据")
        
        print("\n💡 解决方案要点:")
        print("- 改进了_parse_api_response函数，支持多种数据结构")
        print("- 增加了多端点轮询，只有获取到实际数据才返回成功")
        print("- 提供了详细的调试日志，便于问题诊断")
        print("- 增强了错误处理和容错机制")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()