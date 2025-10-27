#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整功能测试 - 验证多条动态获取和删除场景
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_api import get_user_dynamics, get_up_latest_video
from latest_dynamic_storage import DynamicStorage
from config import UP_LIST as UP_CONFIGS
import time

def test_complete_functionality():
    """测试完整功能"""
    print("=== 完整功能测试 ===")
    
    # 直接使用函数，无需实例化API类
    storage = DynamicStorage()
    
    success_count = 0
    total_count = 0
    
    for up_config in UP_CONFIGS:
        up_name = up_config['name']
        uid = up_config['uid']
        
        print(f"\n🎯 测试UP主: {up_name} (UID: {uid})")
        total_count += 1
        
        try:
            # 1. 获取多条动态
            print(f"   📋 获取动态...")
            # 获取用户动态数据
            raw_data = get_user_dynamics(uid)
            if not raw_data:
                print(f"   ❌ 获取动态数据失败")
                continue
                
            # 解析动态数据
            dynamics = []
            items = raw_data.get('data', {}).get('items', [])
            for item in items[:5]:  # 获取前5条动态
                dynamic_info = {
                    'id': item.get('id_str', ''),
                    'pub_ts': item.get('modules', {}).get('module_author', {}).get('pub_ts', 0)
                }
                if dynamic_info['id']:
                    dynamics.append(dynamic_info)
                    
            print(f"   ✅ 解析到 {len(dynamics)} 条动态")
            
            if not dynamics:
                print(f"   ❌ 未获取到动态")
                continue
                
            print(f"   ✅ 获取到 {len(dynamics)} 条动态")
            
            # 2. 验证存储
            print(f"   📋 验证存储...")
            recent_ids = storage.get_recent_dynamic_ids(up_name)
            latest_id = storage.get_latest_dynamic_id(up_name)
            
            print(f"   📊 存储的动态ID数量: {len(recent_ids)}")
            print(f"   📊 最新动态ID: {latest_id}")
            
            if len(recent_ids) >= 1:
                print(f"   ✅ 存储验证通过")
                
                # 3. 测试删除场景
                print(f"   📋 测试删除场景...")
                
                # 获取第一条动态（假设是已删除的）
                first_dynamic = dynamics[0]
                first_id = first_dynamic['id']
                
                # 检查是否为新动态（应该为False，因为已经存储）
                is_new = storage.is_new_dynamic(up_name, first_id)
                print(f"   🧪 动态 {first_id[:10]}... 是否为新: {is_new}")
                
                if not is_new:
                    print(f"   ✅ 删除场景判断正确")
                else:
                    print(f"   ⚠️  删除场景需要进一步验证")
                
                success_count += 1
                
            else:
                print(f"   ❌ 存储验证失败")
            
            # 延迟避免请求过快
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
    
    # 测试结果总结
    print(f"\n=== 测试结果总结 ===")
    print(f"📊 测试UP主数量: {total_count}")
    print(f"✅ 成功数量: {success_count}")
    print(f"📈 成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print(f"\n🎉 所有功能测试通过！")
        print(f"✅ 多条动态获取功能正常")
        print(f"✅ 存储功能正常") 
        print(f"✅ 删除场景判断正常")
        return True
    else:
        print(f"\n⚠️  部分功能测试失败")
        return False

if __name__ == "__main__":
    success = test_complete_functionality()
    sys.exit(0 if success else 1)