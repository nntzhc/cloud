#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析API响应中cards: null问题的脚本
"""

import json
import sys
from api_bypass import APIRestrictionBypass

def test_api_response_structure():
    """测试API响应数据结构解析"""
    
    print("🔍 测试API响应数据结构分析")
    print("=" * 50)
    
    # 模拟Terminal#44-46中显示的API响应情况
    test_cases = [
        {
            'name': 'cards为null的情况',
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
            'name': 'cards为空列表的情况',
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
            'name': '正常有数据的情况',
            'data': {
                'code': 0,
                'message': '0',
                'data': {
                    'items': [
                        {
                            'id_str': '123456',
                            'modules': {
                                'module_author': {
                                    'pub_ts': 1700000000
                                }
                            }
                        }
                    ],
                    'cards': [],
                    'list': [],
                    'has_more': 1
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: {test_case['name']}")
        print("-" * 30)
        
        data = test_case['data']
        print("原始响应数据:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 使用当前的解析逻辑
        items = []
        if 'data' in data and isinstance(data['data'], dict):
            items = data['data'].get('items', [])
            if not items:
                items = data['data'].get('list', [])
            if not items:
                items = data['data'].get('cards', [])
        
        # 确保items是列表类型
        if items is None:
            items = []
        
        print(f"\n解析结果:")
        print(f"  items类型: {type(items)}")
        print(f"  items长度: {len(items) if items else 0}")
        print(f"  是否为空: {items is None or len(items) == 0}")
        
        # 检查响应码
        code = data.get('code', -1)
        print(f"  响应码: {code}")
        
        if code == 0 and (not items or len(items) == 0):
            print("  ⚠️  问题识别: API返回成功但没有动态数据")
        elif code == 0 and items:
            print("  ✅ 正常: API返回成功且有动态数据")
        else:
            print(f"  ❌ 异常: API返回错误码 {code}")

def analyze_real_api_response():
    """分析真实的API响应"""
    
    print("\n\n🌐 真实API响应分析")
    print("=" * 50)
    
    # 模拟从Terminal#44-46的日志中看到的响应
    print("根据Terminal#44-46日志显示:")
    print("- vc端点请求成功")
    print("- API响应数据中cards为null")
    print("- has_more为0")
    print("- 当前正在解析polymer API数据")
    
    print("\n可能的原因分析:")
    reasons = [
        "1. UP主确实没有新动态发布",
        "2. API端点返回了空数据，但请求本身成功",
        "3. 数据结构变化，items字段为null",
        "4. UP主设置了隐私或权限限制",
        "5. 风控影响，部分数据被过滤"
    ]
    
    for reason in reasons:
        print(f"  {reason}")
    
    print("\n解决方案建议:")
    solutions = [
        "1. 增加更详细的数据结构检查",
        "2. 添加空数据情况的处理逻辑", 
        "3. 实现多端点数据合并机制",
        "4. 增加数据验证和容错处理",
        "5. 添加手动刷新机制"
    ]
    
    for solution in solutions:
        print(f"  {solution}")

def generate_improved_parsing_logic():
    """生成改进的解析逻辑"""
    
    print("\n\n🔧 改进的解析逻辑")
    print("=" * 50)
    
    improved_code = '''
def improved_get_user_dynamics(uid, cookie_string=None, use_bypass=True):
    """改进的用户动态获取函数"""
    
    if use_bypass:
        bypass = APIRestrictionBypass()
        bypass.log_message('INFO', f"使用API风控绕过模式获取用户 {uid} 的动态...")
        
        # 尝试多个API端点
        for endpoint in bypass.api_endpoints:
            try:
                bypass.log_message('INFO', f"尝试端点: {endpoint['name']}")
                
                url = endpoint['url'].format(uid=uid)
                headers = bypass.get_random_headers(uid, endpoint['name'])
                
                # 添加端点特定的头部
                if endpoint['name'] == 'polymer':
                    headers.update(endpoint['headers'])
                elif endpoint['name'] == 'vc':
                    headers.update(endpoint['headers'])
                elif endpoint['name'] == 'wbi':
                    headers.update(endpoint['headers'])
                
                random_cookies = bypass.generate_random_cookie()
                
                # 合并cookie
                if cookie_string:
                    cookie_pairs = cookie_string.split('; ')
                    for pair in cookie_pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            if value.strip():
                                random_cookies[key.strip()] = value.strip()
                
                data = bypass.make_request_with_bypass(url, headers, random_cookies)
                
                if data and data.get('code') == 0:
                    bypass.log_message('INFO', f"端点 {endpoint['name']} 请求成功")
                    
                    # 🔍 改进的数据解析逻辑
                    items = parse_api_response(data, bypass)
                    
                    if items and len(items) > 0:
                        bypass.log_message('INFO', f"端点 {endpoint['name']} 成功获取到 {len(items)} 条动态")
                        bypass.request_stats['last_successful_endpoint'] = endpoint['name']
                        return data
                    else:
                        bypass.log_message('WARNING', f"端点 {endpoint['name']} 返回成功但无动态数据")
                        # 继续尝试下一个端点
                        continue
                        
                elif data and bypass.is_rate_limited(data):
                    bypass.log_message('WARNING', f"端点 {endpoint['name']} 触发风控，尝试下一个端点...")
                    continue
                else:
                    bypass.log_message('WARNING', f"端点 {endpoint['name']} 返回异常，尝试下一个端点...")
                    continue
                    
            except Exception as e:
                bypass.log_message('ERROR', f"端点 {endpoint['name']} 异常: {e}")
                continue
        
        # 所有端点都失败
        stats = bypass.get_stats()
        bypass.log_message('ERROR', f"所有端点都失败，API绕过统计: {stats}")
        return None
    
    return None

def parse_api_response(data, bypass):
    """改进的API响应解析函数"""
    
    try:
        # 检查响应状态
        code = data.get('code', -1)
        if code != 0:
            bypass.log_message('WARNING', f"API返回错误码: {code}")
            return []
        
        # 🔍 多层次数据结构检查
        items = []
        data_content = data.get('data', {})
        
        if not data_content:
            bypass.log_message('WARNING', "API响应中data字段为空")
            return []
        
        # 记录原始数据结构用于调试
        bypass.log_message('DEBUG', f"数据结构类型: {type(data_content)}")
        if isinstance(data_content, dict):
            bypass.log_message('DEBUG', f"data字段包含的键: {list(data_content.keys())}")
        
        # 方法1: 直接检查items字段
        if 'items' in data_content:
            items = data_content['items']
            bypass.log_message('DEBUG', f"找到items字段，类型: {type(items)}")
        
        # 方法2: 检查cards字段
        if not items and 'cards' in data_content:
            items = data_content['cards']
            bypass.log_message('DEBUG', f"找到cards字段，类型: {type(items)}")
        
        # 方法3: 检查list字段
        if not items and 'list' in data_content:
            items = data_content['list']
            bypass.log_message('DEBUG', f"找到list字段，类型: {type(items)}")
        
        # 方法4: 检查更深层的数据结构
        if not items and isinstance(data_content, dict):
            for key, value in data_content.items():
                if isinstance(value, list) and len(value) > 0:
                    items = value
                    bypass.log_message('DEBUG', f"在深层结构中找到数据: {key}")
                    break
        
        # 确保items是列表类型
        if items is None:
            items = []
        
        # 数据验证
        if not isinstance(items, list):
            bypass.log_message('WARNING', f"items不是列表类型，而是: {type(items)}")
            items = []
        
        # 记录最终结果
        bypass.log_message('INFO', f"解析完成，获取到 {len(items)} 条动态")
        
        # 如果数据为空，记录详细信息用于调试
        if len(items) == 0:
            bypass.log_message('WARNING', "API返回成功但动态数据为空，可能原因:")
            bypass.log_message('WARNING', "  1. UP主确实没有新动态")
            bypass.log_message('WARNING', "  2. 数据结构发生变化")
            bypass.log_message('WARNING', "  3. 权限或隐私设置限制")
            bypass.log_message('WARNING', "  4. 风控过滤了数据")
        
        return items
        
    except Exception as e:
        bypass.log_message('ERROR', f"解析API响应失败: {e}")
        return []
'''
    
    print(improved_code)

if __name__ == "__main__":
    test_api_response_structure()
    analyze_real_api_response()
    generate_improved_parsing_logic()
    
    print("\n\n📝 总结")
    print("=" * 50)
    print("Terminal#44-46显示API请求成功但cards为null的主要原因是:")
    print("1. UP主当前没有新动态发布")
    print("2. API数据结构中items/cards字段为空")
    print("3. has_more为0表示没有更多数据")
    print("\n建议的解决方案:")
    print("1. 实施多端点数据合并机制")
    print("2. 增加空数据的详细日志记录")
    print("3. 改进数据解析逻辑，支持多种数据结构")
    print("4. 添加手动刷新和数据验证功能")