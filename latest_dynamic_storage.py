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
        # 支持多环境的存储文件路径配置
        self.storage_file = self._get_storage_file_path()
        self.data = {}
        self.load_storage()
    
    def _get_storage_file_path(self):
        """获取存储文件路径，支持本目录和指定目录的兼容性"""
        # 1. 首先尝试当前目录
        current_dir_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latest_dynamic_ids.json")
        if os.path.exists(current_dir_file):
            return current_dir_file
        
        # 2. 尝试用户主目录下的标准路径
        home_path = os.path.expanduser("~/home/cloud/latest_dynamic_ids.json")
        if os.path.exists(home_path):
            return home_path
        
        # 3. 尝试云主机标准路径
        cloud_path = "/home/cloud/latest_dynamic_ids.json"
        if os.path.exists(cloud_path):
            return cloud_path
        
        # 4. 如果都不存在，根据环境选择默认路径
        # Windows环境下优先使用当前目录
        if os.name == 'nt':  # Windows
            return current_dir_file
        else:
            # Linux/云主机环境使用标准路径
            return home_path
    
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
        uid_str = str(uid)
        if uid_str not in self.data:
            return None
        
        # 从recent_dynamic_ids获取最新的ID
        recent_ids = self.data[uid_str].get('recent_dynamic_ids', [])
        if recent_ids:
            return recent_ids[0]  # 列表第一个是最新的
        
        return None
    
    def update_latest_dynamic_id(self, uid, dynamic_id, publish_time=None):
        """更新指定UP主的最新动态ID（存储最近5条）"""
        uid_str = str(uid)
        if uid_str not in self.data:
            self.data[uid_str] = {
                'recent_dynamic_ids': []  # 只存储最近5条动态ID
            }
        
        # 将新动态ID添加到列表开头
        dynamic_id_str = str(dynamic_id)
        if 'recent_dynamic_ids' not in self.data[uid_str]:
            self.data[uid_str]['recent_dynamic_ids'] = []
        
        # 如果ID已存在，先移除它（避免重复）
        if dynamic_id_str in self.data[uid_str]['recent_dynamic_ids']:
            self.data[uid_str]['recent_dynamic_ids'].remove(dynamic_id_str)
        
        # 将新ID添加到列表开头
        self.data[uid_str]['recent_dynamic_ids'].insert(0, dynamic_id_str)
        
        # 只保留最近5条
        self.data[uid_str]['recent_dynamic_ids'] = self.data[uid_str]['recent_dynamic_ids'][:5]
        
        self.save_storage()
    
    def is_new_dynamic(self, uid, dynamic_id):
        """判断是否为新的动态（检查最近5条动态ID）"""
        uid_str = str(uid)
        dynamic_id_str = str(dynamic_id)
        
        # 如果该UP主没有记录，认为是新动态
        if uid_str not in self.data:
            return True
        
        # 获取最近5条动态ID列表
        recent_ids = self.data[uid_str].get('recent_dynamic_ids', [])
        
        # 如果列表为空，认为是新动态
        if not recent_ids:
            return True
        
        # 检查新动态ID是否在最近5条中
        if dynamic_id_str in recent_ids:
            return False  # 已存在，不是新动态
        
        return True  # 不在最近5条中，是新动态
    
    def get_storage_info(self):
        """获取存储信息"""
        return {
            'total_up_count': len(self.data),
            'up_list': list(self.data.keys()),
            'storage_file': self.storage_file
        }
    
    def get_recent_dynamic_ids(self, uid):
        """获取指定UP主的最近5条动态ID"""
        uid_str = str(uid)
        if uid_str not in self.data:
            return []
        return self.data[uid_str].get('recent_dynamic_ids', [])
    
    def clear_up_storage(self, uid):
        """清空指定UP主的存储信息"""
        uid_str = str(uid)
        if uid_str in self.data:
            del self.data[uid_str]
            self.save_storage()
            return True
        return False

# 创建全局存储实例
storage = DynamicStorage()