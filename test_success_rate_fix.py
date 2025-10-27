#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试端点成功率显示修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_bypass import BilibiliAPIBypass

def test_success_rate_display():
    """测试成功率显示逻辑"""
    print("=== 测试端点成功率显示修复 ===")
    
    # 创建API实例
    api = BilibiliAPIBypass()
    
    print("\n1. 初始状态测试（无请求）:")
    api.log_system_stats()
    
    print("\n2. 模拟一些失败请求:")
    # 模拟一些失败请求
    api.update_endpoint_health('polymer', success=False, response_time=1.5)
    api.update_endpoint_health('polymer', success=False, response_time=2.0)
    api.update_endpoint_health('vc', success=False, response_time=1.8)
    
    api.log_system_stats()
    
    print("\n3. 模拟一些成功请求:")
    # 模拟一些成功请求
    api.update_endpoint_health('polymer', success=True, response_time=0.5)
    api.update_endpoint_health('polymer', success=True, response_time=0.8)
    api.update_endpoint_health('vc', success=True, response_time=0.6)
    api.update_endpoint_health('wbi', success=True, response_time=1.2)
    
    api.log_system_stats()
    
    print("\n4. 重置统计后测试:")
    api.reset_all_stats()
    api.log_system_stats()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_success_rate_display()