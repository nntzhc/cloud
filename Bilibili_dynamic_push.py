#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站动态监控推送系统 - 主入口文件
负责总体架构和入口逻辑，功能模块已拆分到各个子模块
"""

import json
import time
import io
import sys
import os
from datetime import datetime

# 设置标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 导入配置和模块
from config import PUSHPLUS_TOKEN, TEST_MODE, UP_LIST
from api_bypass import APIRestrictionBypass
from push_notification import should_send_notification, send_wechat_notification, is_aliyun_environment
from dynamic_api import get_up_latest_dynamic, get_user_dynamics, get_up_latest_video
from latest_dynamic_storage import storage as dynamic_storage

def monitor_bilibili_dynamics():
    """监控B站UP主动态 - 主监控逻辑"""
    current_time = datetime.now()
    bypass = APIRestrictionBypass()
    bypass.setup_logger()
    
    bypass.log_message('INFO', "🚀 开始监控B站动态 - {}".format(current_time.strftime('%Y-%m-%d %H:%M:%S')))
    bypass.log_message('INFO', "🔍 使用动态ID判断最新动态")
    bypass.log_message('INFO', "=" * 60)
    
    new_count = 0
    notified_count = 0
    
    for up in UP_LIST:
        bypass.log_message('INFO', "\n📱 检查 {} 的动态...".format(up['name']))
        
        try:
            # 显示当前本地存储状态
            recent_ids = dynamic_storage.get_recent_dynamic_ids(up['name'])
            bypass.log_message('INFO', "📋 本地存储: 共 {} 条历史动态".format(len(recent_ids)))
            if recent_ids:
                bypass.log_message('INFO', "📋 本地最新: {} (第1条)".format(recent_ids[0]))
                if len(recent_ids) > 1:
                    bypass.log_message('INFO', "📋 历史第2条: {}".format(recent_ids[1]))
                    if len(recent_ids) > 2:
                        bypass.log_message('INFO', "📋 历史第3条: {}".format(recent_ids[2]))
            
            # 获取UP主最新动态，传入uid和name
            dynamic = get_up_latest_dynamic(uid=up['uid'], up_name=up['name'])
            
            # 解析动态信息
            bypass.log_message('INFO', "✅ {}".format(dynamic))
            
            # 检查是否找到并成功推送动态
            if "成功推送" in dynamic or ("找到" in dynamic and "分钟前" in dynamic):
                notified_count += 1
                new_count += 1
            elif "测试模式" in dynamic and "找到" in dynamic:
                # 测试模式下找到但未推送的情况
                new_count += 1
            
            # 延迟避免频繁请求
            time.sleep(2)
            
        except Exception as e:
            bypass.log_message('ERROR', "❌ 检查失败: {}".format(e))
            continue
    
    bypass.log_message('INFO', "\n✅ 监控完成，共检查 {} 条动态，发送 {} 条通知".format(new_count, notified_count))
    return {
        "checked_count": new_count,
        "notified_count": notified_count
    }

def handler(event, context):
    """阿里云函数计算入口函数"""
    bypass = APIRestrictionBypass()
    bypass.setup_logger()
    
    bypass.log_message('INFO', "⏰ 当前时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    bypass.log_message('INFO', "🔍 使用动态ID判断最新动态")
    
    try:
        # 执行动态监控
        result = monitor_bilibili_dynamics()
        
        return_result = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "动态监控完成，检查 {} 条动态，发送 {} 条通知".format(result['checked_count'], result['notified_count']),
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "monitored_up_count": len(UP_LIST),
                    "checked_dynamics": result['checked_count'],
                    "sent_notifications": result['notified_count'],
                    "test_mode": TEST_MODE,
                    "dynamic_id_check": True,
                    "environment": "aliyun" if is_aliyun_environment() else "local"
                }
            }, ensure_ascii=False)
        }
        
        bypass.log_message('INFO', "✅ 函数执行成功")
        return return_result
        
    except Exception as e:
        error_msg = "动态监控执行失败: {}".format(str(e))
        bypass.log_message('ERROR', "❌ {}".format(error_msg))
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)
        }

# 本地测试
if __name__ == "__main__":
    bypass = APIRestrictionBypass()
    bypass.setup_logger()
    
    bypass.log_message('INFO', "🧪 本地测试模式")
    bypass.log_message('INFO', "=" * 60)
    bypass.log_message('INFO', "⏰ 当前时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    bypass.log_message('INFO', "🔍 使用动态ID判断最新动态")
    
    event = {}
    context = type('Context', (), {'request_id': 'local-test-123'})()
    
    # 调用处理函数
    result = handler(event, context)
    
    bypass.log_message('INFO', "\n📊 测试结果:")
    bypass.log_message('INFO', json.dumps(result, ensure_ascii=False, indent=2))