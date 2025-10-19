#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from latest_dynamic_storage import storage

# 模拟修复后的存储逻辑验证
print('=== 验证修复后的存储逻辑 ===')

up_name = "史诗级韭菜"
dynamic_id = "1125347191838212099"  # 当前存储的最新动态ID

# 测试is_new_dynamic函数 - 应该返回False（不是新动态）
print(f'测试UP主: {up_name}')
print(f'测试动态ID: {dynamic_id}')
print(f'存储中的最新动态ID: {storage.get_latest_dynamic_id(up_name)}')

is_new = storage.is_new_dynamic(up_name, dynamic_id)
print(f'is_new_dynamic结果: {is_new} (应该为False)')

# 测试使用不同的动态ID - 应该返回True（是新动态）
test_new_id = "9999999999999999999"
is_new_test = storage.is_new_dynamic(up_name, test_new_id)
print(f'测试新动态ID结果: {is_new_test} (应该为True)')

# 验证存储更新逻辑
print('\n=== 验证存储更新逻辑 ===')
print('修复前：检查使用uid，更新使用up_name，导致键不匹配')
print('修复后：统一使用up_name作为键，确保一致性')

# 显示当前存储状态
import json
with open('latest_dynamic_ids.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print('当前存储内容:')
    print(json.dumps(data, ensure_ascii=False, indent=2))