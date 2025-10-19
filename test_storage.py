#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from latest_dynamic_storage import storage

# 检查史诗级韭菜的存储键值
print('=== 检查存储键值问题 ===')
up_name = '史诗级韭菜'
dynamic_id = '1125115632993435656'

# 查看存储中的所有键
all_keys = list(storage.data.keys())
print(f'存储中的所有键: {all_keys}')

# 检查史诗级韭菜的数据
if up_name in storage.data:
    stored_data = storage.data[up_name]
    print(f'史诗级韭菜的存储数据: {stored_data}')
    print(f'存储的动态ID类型: {type(stored_data.get("dynamic_id"))}')
    print(f'传入的动态ID类型: {type(dynamic_id)}')
else:
    print('史诗级韭菜不在存储中')

# 测试不同方式的键访问
test_keys = ['史诗级韭菜', str('史诗级韭菜')]
for key in test_keys:
    result = storage.get_latest_dynamic_id(key)
    print(f'使用键 "{key}" 获取的动态ID: {result}')

# 测试is_new_dynamic函数
print('\n=== 测试is_new_dynamic函数 ===')
is_new = storage.is_new_dynamic(up_name, dynamic_id)
print(f'是否为新动态: {is_new}')

# 手动对比
latest_id = storage.get_latest_dynamic_id(up_name)
print(f'最新动态ID: {latest_id}')
print(f'当前动态ID: {dynamic_id}')
print(f'手动对比结果: {latest_id != str(dynamic_id)}')