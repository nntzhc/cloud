#!/usr/bin/env python3
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
    # 使用与DynamicStorage相同的路径选择逻辑
    from latest_dynamic_storage import DynamicStorage
    temp_storage = DynamicStorage()
    storage_file = temp_storage.storage_file
    
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
