#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云主机配置文件
解决路径问题
"""

import os
import sys

# 设置工作目录为脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 使用与DynamicStorage相同的路径选择逻辑确保兼容性
from latest_dynamic_storage import DynamicStorage
temp_storage = DynamicStorage()
STORAGE_FILE = temp_storage.storage_file

print(f"工作目录: {os.getcwd()}")
print(f"存储文件: {STORAGE_FILE}")
