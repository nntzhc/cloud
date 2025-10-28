#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复空存储文件问题
"""

import os
import json
from latest_dynamic_storage import DynamicStorage

def fix_empty_storage():
    """修复空的存储文件"""
    print("🔧 修复空存储文件问题")
    print("=" * 60)
    
    # 1. 检查当前存储文件
    storage_file = "latest_dynamic_ids.json"
    
    print(f"📄 检查存储文件: {storage_file}")
    
    if os.path.exists(storage_file):
        file_size = os.path.getsize(storage_file)
        print(f"   文件大小: {file_size} 字节")
        
        if file_size == 0:
            print("   ⚠️ 文件为空，需要初始化")
            
            # 创建默认数据结构
            default_data = {
                "茉菲特_Official": {
                    "recent_dynamic_ids": []
                },
                "史诗级韭菜": {
                    "recent_dynamic_ids": []
                }
            }
            
            # 写入默认数据
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            
            print("   ✅ 已写入默认数据结构")
            
        else:
            # 检查文件内容是否有效
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"   ✅ 文件内容有效，包含 {len(data)} 个UP主")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON格式错误: {e}")
                print("   正在备份并重新创建...")
                
                # 备份损坏的文件
                backup_file = f"{storage_file}.backup"
                shutil.copy2(storage_file, backup_file)
                print(f"   ✅ 已备份到: {backup_file}")
                
                # 创建新的默认文件
                default_data = {
                    "茉菲特_Official": {
                        "recent_dynamic_ids": []
                    },
                    "史诗级韭菜": {
                        "recent_dynamic_ids": []
                    }
                }
                
                with open(storage_file, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=2)
                
                print("   ✅ 已重新创建存储文件")
    
    # 2. 验证修复结果
    print(f"\n🔍 验证修复结果:")
    try:
        storage = DynamicStorage()
        print(f"   ✅ 存储类初始化成功")
        print(f"   内存中的UP主数量: {len(storage.data)}")
        
        for up_name in storage.data:
            recent_ids = storage.get_recent_dynamic_ids(up_name)
            print(f"   {up_name}: {len(recent_ids)} 条动态")
        
        # 测试动态ID检查功能
        test_up = "史诗级韭菜"
        test_id = "1128763498993549318"
        is_new = storage.is_new_dynamic(test_up, test_id)
        print(f"\n   测试动态ID检查:")
        print(f"   UP主: {test_up}")
        print(f"   动态ID: {test_id}")
        print(f"   是否新动态: {'✅ 是' if is_new else '❌ 否'}")
        
        if is_new:
            print(f"   ✅ 系统现在能正确识别新动态了！")
        else:
            print(f"   ⚠️ 动态已存在于存储中")
            
    except Exception as e:
        print(f"   ❌ 验证失败: {e}")
    
    print("\n✅ 修复完成")

def create_cloud_startup_script():
    """创建云主机启动脚本"""
    print(f"\n📝 创建云主机启动脚本...")
    
    startup_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云主机启动脚本
确保存储文件存在且有效
"""

import os
import json
import sys

def ensure_storage_file():
    """确保存储文件存在且有效"""
    storage_file = "/home/cloud/latest_dynamic_ids.json"
    
    print(f"确保存储文件: {storage_file}")
    
    # 检查文件是否存在且有效
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    json.loads(content)
                    print("✅ 存储文件有效")
                    return True
                else:
                    print("⚠️ 文件为空")
        except json.JSONDecodeError:
            print("❌ JSON格式错误")
    else:
        print("⚠️ 文件不存在")
    
    # 创建默认文件
    print("创建默认存储文件...")
    default_data = {
        "茉菲特_Official": {"recent_dynamic_ids": []},
        "史诗级韭菜": {"recent_dynamic_ids": []}
    }
    
    try:
        with open(storage_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        print("✅ 默认文件创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建文件失败: {e}")
        return False

if __name__ == "__main__":
    success = ensure_storage_file()
    sys.exit(0 if success else 1)
'''
    
    with open('ensure_storage.py', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    print("✅ 已创建 ensure_storage.py")
    print("\n在云主机上使用:")
    print("1. python3.11 ensure_storage.py")
    print("2. python3.11 Bilibili_dynamic_push.py")

if __name__ == "__main__":
    fix_empty_storage()
    create_cloud_startup_script()