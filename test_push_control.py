#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from push_notification import send_wechat_notification

# 测试推送控制功能
print('=== 测试推送控制功能 ===')

# 模拟动态数据
test_dynamic_info = {
    'content': '这是一个测试动态内容，用于验证推送控制功能是否正常工作',
    'timestamp': 1736167892,
    'url': 'https://t.bilibili.com/1125112197021696037',
    'pics': ['https://i0.hdslb.com/bfs/album/123.jpg'],
    'like': 123,
    'reply': 45,
    'forward': 67,
    'dynamic_id': '1125112197021696037'
}

# 测试推送功能
print('测试UP主: 茉菲特_Official')
print('当前推送状态: 已关闭 (ENABLE_PUSH = False)')
print('预期结果: 只打印信息，不进行实际推送')

result = send_wechat_notification('茉菲特_Official', test_dynamic_info)
print(f'推送结果: {result}')

print('\n=== 测试完成 ===')
print('当ENABLE_PUSH设置为True时，将进行实际推送')
print('当ENABLE_PUSH设置为False时，只打印推送预览信息')