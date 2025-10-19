#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from api_bypass import APIBypass

def test_success_rate_calculation():
    """测试成功率计算逻辑"""
    print("=== 测试成功率计算逻辑 ===")
    
    # 创建APIBypass实例
    bypass = APIBypass()
    
    # 测试用例1：成功请求数为0，总请求数大于0
    print("\n--- 测试用例1：成功请求数为0，总请求数=5 ---")
    bypass.request_stats['total_requests'] = 5
    bypass.request_stats['successful_requests'] = 0
    bypass.request_stats['failed_requests'] = 5
    
    stats = bypass.get_stats()
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功请求数: {stats['successful_requests']}")
    print(f"失败请求数: {stats['failed_requests']}")
    print(f"成功率: {stats['success_rate']}")
    print(f"成功率类型: {type(stats['success_rate'])}")
    
    # 测试用例2：成功请求数为0，总请求数为0
    print("\n--- 测试用例2：成功请求数为0，总请求数=0 ---")
    bypass.request_stats['total_requests'] = 0
    bypass.request_stats['successful_requests'] = 0
    bypass.request_stats['failed_requests'] = 0
    
    stats = bypass.get_stats()
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功请求数: {stats['successful_requests']}")
    print(f"失败请求数: {stats['failed_requests']}")
    print(f"成功率: {stats['success_rate']}")
    print(f"成功率类型: {type(stats['success_rate'])}")
    
    # 测试用例3：正常情况，有成功请求
    print("\n--- 测试用例3：正常情况，成功请求数=3，总请求数=5 ---")
    bypass.request_stats['total_requests'] = 5
    bypass.request_stats['successful_requests'] = 3
    bypass.request_stats['failed_requests'] = 2
    
    stats = bypass.get_stats()
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功请求数: {stats['successful_requests']}")
    print(f"失败请求数: {stats['failed_requests']}")
    print(f"成功率: {stats['success_rate']}")
    print(f"成功率类型: {type(stats['success_rate'])}")

if __name__ == "__main__":
    test_success_rate_calculation()