#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最新动态ID存储模块
用于存储和管理各UP主的最新动态ID，避免重复推送
"""

import json
import os
from datetime import datetime

class DynamicStorage:
    """动态ID存储管理器"""
    
    def __init__(self):
        self.storage_file = "latest_dynamic_ids.json"
        self.data = {}
        self.load_storage()
    
    def load_storage(self):
        """从文件加载存储的数据"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"加载存储文件失败: {e}")
                self.data = {}
        else:
            self.data = {}
    
    def save_storage(self):
        """保存数据到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存存储文件失败: {e}")
    
    def get_latest_dynamic_id(self, uid):
        """获取指定UP主的最新动态ID"""
        return self.data.get(str(uid), {}).get('dynamic_id')
    
    def update_latest_dynamic_id(self, uid, dynamic_id, publish_time=None):
        """更新指定UP主的最新动态ID"""
        uid_str = str(uid)
        if uid_str not in self.data:
            self.data[uid_str] = {}
        
        self.data[uid_str]['dynamic_id'] = str(dynamic_id)
        self.data[uid_str]['update_time'] = datetime.now().isoformat()
        if publish_time:
            self.data[uid_str]['publish_time'] = publish_time.isoformat()
        
        self.save_storage()
    
    def is_new_dynamic(self, uid, dynamic_id):
        """判断是否为新的动态"""
        latest_id = self.get_latest_dynamic_id(uid)
        return latest_id != str(dynamic_id)
    
    def get_storage_info(self):
        """获取存储信息"""
        return {
            'total_up_count': len(self.data),
            'up_list': list(self.data.keys()),
            'storage_file': self.storage_file
        }

# 创建全局存储实例
storage = DynamicStorage()