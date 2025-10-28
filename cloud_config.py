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

# 确保存储文件路径正确
STORAGE_FILE = os.path.join(script_dir, "latest_dynamic_ids.json")

print(f"工作目录: {os.getcwd()}")
print(f"存储文件: {STORAGE_FILE}")
