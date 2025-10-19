#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from dynamic_api import get_up_latest_dynamic
from latest_dynamic_storage import storage

# 测试真实场景：使用配置文件中的UP主信息
print('=== 测试真实场景 ===')

# 史诗级韭菜的真实信息
up_name = "史诗级韭菜"
uid = "322005137"
dynamic_id = "1125115632993435656"

print(f'UP主: {up_name}')
print(f'UID: {uid}')
print(f'动态ID: {dynamic_id}')

# 检查存储状态
print('\n=== 存储状态检查 ===')
is_new = storage.is_new_dynamic(up_name, dynamic_id)
print(f'是否为新动态: {is_new}')
latest_id = storage.get_latest_dynamic_id(up_name)
print(f'存储的最新动态ID: {latest_id}')

# 模拟调用主函数（但由于API限制，会返回None）
print('\n=== 模拟调用主函数 ===')
try:
    result = get_up_latest_dynamic(uid=uid, up_name=up_name)
    print(f'主函数返回: {result}')
except Exception as e:
    print(f'主函数异常: {e}')

# 检查问题所在：对比使用UID和UP主名的情况
print('\n=== 检查存储逻辑问题 ===')
print('存储函数使用UID作为键，但推送函数使用UP主名作为键')
print('这可能导致存储和读取使用不同的键')

# 测试UID作为键的情况
uid_key = str(uid)
is_new_uid = storage.is_new_dynamic(uid_key, dynamic_id)
print(f'使用UID作为键是否为新动态: {is_new_uid}')
latest_id_uid = storage.get_latest_dynamic_id(uid_key)
print(f'使用UID作为键存储的最新动态ID: {latest_id_uid}')

# 测试UP主名作为键的情况
is_new_name = storage.is_new_dynamic(up_name, dynamic_id)
print(f'使用UP主名作为键是否为新动态: {is_new_name}')
latest_id_name = storage.get_latest_dynamic_id(up_name)
print(f'使用UP主名作为键存储的最新动态ID: {latest_id_name}')