#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站UP主动态监控 - Python 3.5兼容版本
基于动态发布时间判断是否发送消息
"""

import json
import requests
import time
import random
import string
from datetime import datetime, timezone, timedelta
import gzip
import os
import io
import sys
import hashlib
import urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# PushPlus配置
PUSHPLUS_TOKEN = "dadf10121525470ea7f9fe27c86722ca"

# 测试标志位 - 设置为True时强制推送测试
TEST_MODE = False    # 开启测试模式，验证推送功能

# 时间判断配置
# 时间阈值：动态发布时间在多少分钟内才发送通知（单位：分钟）
TIME_THRESHOLD_MINUTES = 2  # 正常监控时间阈值

# 监控的UP主列表
UP_LIST = [
    {"name": "史诗级韭菜", "uid": "322005137"},
    {"name": "茉菲特_Official", "uid": "3546839915694905"}
]

# 🔧 API风控绕过配置
class APIRestrictionBypass:
    """B站API风控绕过器"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0'
        ]
        
        self.accept_languages = [
            'zh-CN,zh;q=0.9,en;q=0.8',
            'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7'
        ]
        
        self.api_endpoints = [
            {
                'name': 'polymer',
                'url': 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={uid}&timezone_offset=-480',
                'headers': {
                    'Referer': 'https://space.bilibili.com/{uid}/dynamic',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            },
            {
                'name': 'vc',
                'url': 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&need_top=1&platform=web',
                'headers': {
                    'Referer': 'https://space.bilibili.com/{uid}',
                    'Origin': 'https://space.bilibili.com'
                }
            },
            {
                'name': 'wbi',
                'url': 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={uid}',
                'headers': {
                    'Referer': 'https://t.bilibili.com/',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }
        ]
        
        self.retry_config = {
            'max_retries': 5,
            'base_delay': 1.0,
            'max_delay': 30.0,
            'backoff_factor': 2.0,
            'jitter_range': (0.1, 0.5)
        }
        
        # 代理IP池配置
        self.proxy_pools = [
            # 免费代理示例（实际使用时需要验证可用性）
            # 注意：免费代理通常不稳定，建议购买付费代理服务
            {
                'http': 'http://proxy1.example.com:8080',
                'https': 'https://proxy1.example.com:8080'
            },
            {
                'http': 'http://proxy2.example.com:8080',
                'https': 'https://proxy2.example.com:8080'
            },
            {
                'http': 'http://proxy3.example.com:8080',
                'https': 'https://proxy3.example.com:8080'
            }
        ]
        
        # 代理使用统计
        self.proxy_stats = {
            'total_proxy_requests': 0,
            'successful_proxy_requests': 0,
            'failed_proxy_requests': 0,
            'proxy_rotation_enabled': False
        }
        
        # 代理轮换状态属性
        self.proxy_rotation_enabled = False
        
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'last_successful_endpoint': None
        }
        
        # 请求频率控制和限流机制
        self.rate_limiter = {
            'request_times': [],  # 存储最近请求时间
            'max_requests_per_minute': 30,  # 每分钟最大请求数
            'max_requests_per_hour': 500,  # 每小时最大请求数
            'min_request_interval': 2.0,  # 最小请求间隔（秒）
            'burst_threshold': 5,  # 突发请求阈值
            'current_window_requests': 0,  # 当前时间窗口请求数
            'window_start_time': time.time(),  # 时间窗口开始时间
            'window_duration': 60,  # 时间窗口长度（秒）
            'adaptive_delay_enabled': True,  # 自适应延迟启用
            'base_delay_multiplier': 1.0,  # 基础延迟倍数
            'last_rate_limit_time': None  # 上次触发限流的时间
        }
        
        # 日志配置
        self.logger = None
        self.log_level = 'INFO'
        self.log_file = None
        self.enable_console_log = True
        self.log_buffer = []  # 日志缓冲区
        self.max_log_buffer_size = 1000  # 最大日志缓冲区大小
    
    def generate_buvid(self):
        """生成有效的buvid"""
        # buvid3格式: 16位十六进制-16位十六进制infoc
        part1 = ''.join(random.choices('0123456789ABCDEF', k=16))
        part2 = ''.join(random.choices('0123456789ABCDEF', k=16))
        return f"{part1}-{part2}infoc"
    
    def generate_buvid4(self):
        """生成有效的buvid4"""
        # buvid4格式: 16位十六进制-16位十六进制
        part1 = ''.join(random.choices('0123456789ABCDEF', k=16))
        part2 = ''.join(random.choices('0123456789ABCDEF', k=16))
        return f"{part1}-{part2}"
    
    def generate_random_cookie(self):
        """生成随机但有效的cookie组合"""
        cookies = {
            'buvid3': self.generate_buvid(),
            'buvid4': self.generate_buvid4(),
            'b_nut': str(int(time.time()) - random.randint(0, 86400)),  # 24小时内随机时间
            '_uuid': self.generate_uuid(),
            'buvid_fp': self.generate_buvid_fp(),
            'SESSDATA': '',  # 留空，非登录状态
            'bili_jct': '',  # 留空，非登录状态
        }
        
        # 随机添加一些可选cookie
        optional_cookies = {
            'CURRENT_FNVAL': '4048',
            'blackside_state': '1',
            'b_lsid': self.generate_b_lsid(),
            'sid': self.generate_sid(),
        }
        
        # 随机选择添加一些可选cookie
        for key, value in optional_cookies.items():
            if random.random() < 0.3:  # 30%概率添加
                cookies[key] = value
        
        return cookies
    
    def generate_uuid(self):
        """生成UUID格式字符串"""
        parts = [
            ''.join(random.choices('0123456789ABCDEF', k=8)),
            ''.join(random.choices('0123456789ABCDEF', k=4)),
            ''.join(random.choices('0123456789ABCDEF', k=4)),
            ''.join(random.choices('0123456789ABCDEF', k=4)),
            ''.join(random.choices('0123456789ABCDEF', k=12))
        ]
        return '-'.join(parts)
    
    def generate_buvid_fp(self):
        """生成buvid_fp"""
        # 简单的MD5哈希
        random_str = str(time.time()) + str(random.randint(100000, 999999))
        return hashlib.md5(random_str.encode()).hexdigest()
    
    def generate_b_lsid(self):
        """生成b_lsid"""
        part1 = str(int(time.time() * 1000))[-8:]
        part2 = ''.join(random.choices('0123456789ABCDEF', k=6))
        return f"{part1}_{part2}"
    
    def generate_sid(self):
        """生成sid"""
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    
    def get_random_headers(self, uid=None, endpoint_name=None):
        """获取随机化的请求头"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        
        # 根据端点设置特定的头部
        if endpoint_name == 'polymer' and uid:
            headers.update({
                'Referer': f'https://space.bilibili.com/{uid}/dynamic',
                'X-Requested-With': 'XMLHttpRequest'
            })
        elif endpoint_name == 'vc' and uid:
            headers.update({
                'Referer': f'https://space.bilibili.com/{uid}',
                'Origin': 'https://space.bilibili.com'
            })
        elif endpoint_name == 'wbi':
            headers.update({
                'Referer': 'https://t.bilibili.com/',
                'X-Requested-With': 'XMLHttpRequest'
            })
        
        return headers
    
    def calculate_retry_delay(self, attempt):
        """计算重试延迟时间（指数退避+随机抖动）"""
        base_delay = self.retry_config['base_delay'] * (self.retry_config['backoff_factor'] ** attempt)
        jitter = random.uniform(*self.retry_config['jitter_range'])
        delay = min(base_delay + jitter, self.retry_config['max_delay'])
        return delay
    
    def is_rate_limited(self, response_data):
        """检查是否被风控限制"""
        if not isinstance(response_data, dict):
            return False
        
        code = response_data.get('code', 0)
        message = response_data.get('message', '').lower()
        
        # 常见的风控错误码
        rate_limit_codes = [-352, -401, -403, 12002, 12003]
        rate_limit_messages = ['风控', '验证', '频繁', '限制', 'risk', 'verify', 'captcha']
        
        if code in rate_limit_codes:
            return True
        
        for keyword in rate_limit_messages:
            if keyword in message:
                return True
        
        return False
    
    def make_request_with_bypass(self, url, headers, cookies=None, max_retries=None, use_rate_limiter=True):
        """带风控绕过的请求方法"""
        if max_retries is None:
            max_retries = self.retry_config['max_retries']
        
        session = requests.Session()
        request_start_time = time.time()
        
        # 设置cookie
        if cookies:
            for key, value in cookies.items():
                if value:  # 只设置非空值
                    session.cookies.set(key, value, domain='.bilibili.com')
        
        # 记录请求开始
        self.log_request_start(url, headers, cookies)
        
        for attempt in range(max_retries):
            try:
                # 请求频率控制检查
                if use_rate_limiter:
                    # 检查限流
                    is_limited, reason = self.check_rate_limit()
                    if is_limited:
                        self.log_message('WARNING', f"触发限流: {reason}")
                        self.record_rate_limit()
                        
                        if attempt < max_retries - 1:
                            # 计算等待时间
                            adaptive_delay = self.calculate_adaptive_delay()
                            self.log_message('INFO', f"限流等待 {adaptive_delay:.1f} 秒...")
                            time.sleep(adaptive_delay)
                            continue
                        else:
                            self.log_message('ERROR', "达到最大重试次数，限流失败")
                            return None
                    
                    # 计算自适应延迟
                    adaptive_delay = self.calculate_adaptive_delay()
                    if adaptive_delay > 0:
                        self.log_message('DEBUG', f"自适应延迟 {adaptive_delay:.1f} 秒...")
                        time.sleep(adaptive_delay)
                
                # 记录请求时间
                self.record_request()
                self.request_stats['total_requests'] += 1
                
                # 添加随机延迟（重试时）
                if attempt > 0:
                    retry_delay = self.calculate_retry_delay(attempt - 1)
                    self.log_message('INFO', f"第{attempt + 1}次尝试，等待{retry_delay:.1f}秒...")
                    time.sleep(retry_delay)
                
                # 随机化请求头
                current_headers = headers.copy()
                if 'User-Agent' in current_headers:
                    current_headers['User-Agent'] = random.choice(self.user_agents)
                if 'Accept-Language' in current_headers:
                    current_headers['Accept-Language'] = random.choice(self.accept_languages)
                
                self.log_message('DEBUG', f"发送请求: URL={url}, User-Agent={current_headers.get('User-Agent', 'Unknown')}")
                
                response = session.get(url, headers=current_headers, timeout=15)
                response.raise_for_status()
                
                # 尝试解析响应
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试解压后解析
                    content = response.content
                    try:
                        content = gzip.decompress(content)
                    except:
                        pass
                    data = json.loads(content.decode('utf-8'))
                
                # 检查是否被风控
                if self.is_rate_limited(data):
                    self.request_stats['rate_limited_requests'] += 1
                    self.request_stats['failed_requests'] += 1
                    
                    self.log_rate_limit_detected(data, attempt)
                    
                    if attempt < max_retries - 1:
                        # 更换策略
                        self.log_message('INFO', "更换请求策略...")
                        continue
                    else:
                        self.log_message('ERROR', "达到最大重试次数，请求失败")
                        return None
                
                # 请求成功，重置限流倍数
                if attempt == 0:  # 第一次尝试就成功
                    self.reset_rate_limit_multiplier()
                
                # 请求成功
                self.request_stats['successful_requests'] += 1
                request_duration = time.time() - request_start_time
                self.log_request_end(url, True, data, duration=request_duration)
                
                return data
                
            except requests.exceptions.RequestException as e:
                self.request_stats['failed_requests'] += 1
                self.log_message('ERROR', f"第{attempt + 1}次请求异常: {e}")
                
                if attempt < max_retries - 1:
                    continue
                else:
                    request_duration = time.time() - request_start_time
                    self.log_request_end(url, False, error=e, duration=request_duration)
                    return None
            except Exception as e:
                self.request_stats['failed_requests'] += 1
                self.log_message('ERROR', f"第{attempt + 1}次处理异常: {e}")
                request_duration = time.time() - request_start_time
                self.log_request_end(url, False, error=e, duration=request_duration)
                return None
        
        return None
    
    def get_random_proxy(self):
        """获取随机代理"""
        if not self.proxy_pools:
            return None
        return random.choice(self.proxy_pools)
    
    def make_request_with_proxy(self, url, headers, cookies=None, use_proxy=True, timeout=20):
        """使用代理IP进行请求"""
        if not use_proxy or not self.proxy_pools:
            return None
        
        proxy = self.get_random_proxy()
        if not proxy:
            self.log_message('WARNING', "没有可用的代理服务器")
            return None
        
        self.proxy_stats['total_proxy_requests'] += 1
        request_start_time = time.time()
        
        try:
            session = requests.Session()
            
            # 设置cookie
            if cookies:
                for key, value in cookies.items():
                    if value:
                        session.cookies.set(key, value, domain='.bilibili.com')
            
            # 设置代理
            session.proxies.update(proxy)
            
            self.log_message('INFO', f"使用代理请求: {proxy}")
            
            # 设置超时时间
            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # 解析响应
            try:
                data = response.json()
            except json.JSONDecodeError:
                content = response.content
                try:
                    content = gzip.decompress(content)
                except:
                    pass
                data = json.loads(content.decode('utf-8'))
            
            # 检查是否被风控
            if self.is_rate_limited(data):
                self.proxy_stats['failed_proxy_requests'] += 1
                self.log_rate_limit_detected(data, proxy_info=proxy)
                return None
            
            # 代理请求成功
            self.proxy_stats['successful_proxy_requests'] += 1
            request_duration = time.time() - request_start_time
            self.log_proxy_usage(proxy, success=True, duration=request_duration)
            self.log_message('INFO', f"代理请求成功: {proxy}")
            
            return data
            
        except Exception as e:
            self.proxy_stats['failed_proxy_requests'] += 1
            request_duration = time.time() - request_start_time
            self.log_proxy_usage(proxy, success=False, error=e, duration=request_duration)
            self.log_message('ERROR', f"代理请求失败 {proxy}: {e}")
            return None
    
    def enable_proxy_rotation(self, enabled=True):
        """启用/禁用代理轮换"""
        self.proxy_stats['proxy_rotation_enabled'] = enabled
        self.proxy_rotation_enabled = enabled
        if enabled:
            self.log_message('INFO', f"代理轮换已启用，代理池大小: {len(self.proxy_pools)}")
        else:
            self.log_message('INFO', "代理轮换已禁用")
    
    def get_proxy_stats(self):
        """获取代理使用统计"""
        success_rate = 0
        if self.proxy_stats['total_proxy_requests'] > 0:
            success_rate = (self.proxy_stats['successful_proxy_requests'] / self.proxy_stats['total_proxy_requests']) * 100
        
        return {
            'total_proxy_requests': self.proxy_stats['total_proxy_requests'],
            'successful_proxy_requests': self.proxy_stats['successful_proxy_requests'],
            'failed_proxy_requests': self.proxy_stats['failed_proxy_requests'],
            'proxy_success_rate': f"{success_rate:.1f}%",
            'proxy_rotation_enabled': self.proxy_stats['proxy_rotation_enabled'],
            'proxy_pool_size': len(self.proxy_pools)
        }
    
    def check_rate_limit(self):
        """检查是否需要限流"""
        current_time = time.time()
        
        # 清理过期的请求时间记录（保留最近1小时）
        self.rate_limiter['request_times'] = [
            t for t in self.rate_limiter['request_times'] 
            if current_time - t < 3600
        ]
        
        # 检查时间窗口
        if current_time - self.rate_limiter['window_start_time'] >= self.rate_limiter['window_duration']:
            # 重置时间窗口
            self.rate_limiter['window_start_time'] = current_time
            self.rate_limiter['current_window_requests'] = 0
        
        # 检查各种限流条件
        
        # 1. 每分钟请求数限制
        recent_requests = len([
            t for t in self.rate_limiter['request_times'] 
            if current_time - t < 60
        ])
        if recent_requests >= self.rate_limiter['max_requests_per_minute']:
            return True, f"每分钟请求数超限: {recent_requests}/{self.rate_limiter['max_requests_per_minute']}"
        
        # 2. 每小时请求数限制
        if len(self.rate_limiter['request_times']) >= self.rate_limiter['max_requests_per_hour']:
            return True, f"每小时请求数超限: {len(self.rate_limiter['request_times'])}/{self.rate_limiter['max_requests_per_hour']}"
        
        # 3. 最小请求间隔
        if self.rate_limiter['request_times']:
            last_request_time = self.rate_limiter['request_times'][-1]
            if current_time - last_request_time < self.rate_limiter['min_request_interval']:
                return True, f"请求间隔过短: {current_time - last_request_time:.1f}s < {self.rate_limiter['min_request_interval']}s"
        
        # 4. 突发请求检测
        recent_burst = len([
            t for t in self.rate_limiter['request_times'] 
            if current_time - t < 10  # 最近10秒
        ])
        if recent_burst >= self.rate_limiter['burst_threshold']:
            return True, f"突发请求过多: {recent_burst}/{self.rate_limiter['burst_threshold']} (10秒内)"
        
        # 5. 当前时间窗口请求数
        if self.rate_limiter['current_window_requests'] >= self.rate_limiter['max_requests_per_minute']:
            return True, f"时间窗口请求数超限: {self.rate_limiter['current_window_requests']}/{self.rate_limiter['max_requests_per_minute']}"
        
        return False, "通过限流检查"
    
    def calculate_adaptive_delay(self):
        """计算自适应延迟时间"""
        if not self.rate_limiter['adaptive_delay_enabled']:
            return 0
        
        current_time = time.time()
        
        # 基础延迟
        base_delay = self.rate_limiter['min_request_interval']
        
        # 根据请求频率调整延迟
        recent_requests = len([
            t for t in self.rate_limiter['request_times'] 
            if current_time - t < 60
        ])
        
        # 请求频率越高，延迟越长
        frequency_factor = max(1.0, recent_requests / self.rate_limiter['max_requests_per_minute'])
        
        # 根据上次触发限流的时间调整
        rate_limit_factor = 1.0
        if self.rate_limiter['last_rate_limit_time']:
            time_since_rate_limit = current_time - self.rate_limiter['last_rate_limit_time']
            if time_since_rate_limit < 300:  # 5分钟内触发过限流
                rate_limit_factor = max(2.0, 5.0 - time_since_rate_limit / 60)  # 逐渐增加
        
        # 计算最终延迟
        adaptive_delay = base_delay * frequency_factor * rate_limit_factor * self.rate_limiter['base_delay_multiplier']
        
        # 添加随机抖动
        jitter = random.uniform(0.1, 0.5)
        final_delay = adaptive_delay + jitter
        
        return min(final_delay, 10.0)  # 最大延迟不超过10秒
    
    def record_request(self):
        """记录请求时间"""
        current_time = time.time()
        self.rate_limiter['request_times'].append(current_time)
        self.rate_limiter['current_window_requests'] += 1
    
    def record_rate_limit(self):
        """记录触发限流"""
        self.rate_limiter['last_rate_limit_time'] = time.time()
        self.rate_limiter['base_delay_multiplier'] = min(self.rate_limiter['base_delay_multiplier'] * 1.5, 3.0)
    
    def reset_rate_limit_multiplier(self):
        """重置限流倍数"""
        self.rate_limiter['base_delay_multiplier'] = 1.0
    
    def get_rate_limit_stats(self):
        """获取限流统计信息"""
        current_time = time.time()
        
        recent_requests = len([
            t for t in self.rate_limiter['request_times'] 
            if current_time - t < 60
        ])
        
        return {
            'recent_requests_per_minute': recent_requests,
            'total_requests_hour': len(self.rate_limiter['request_times']),
            'current_window_requests': self.rate_limiter['current_window_requests'],
            'window_duration': self.rate_limiter['window_duration'],
            'min_request_interval': self.rate_limiter['min_request_interval'],
            'adaptive_delay_enabled': self.rate_limiter['adaptive_delay_enabled'],
            'base_delay_multiplier': self.rate_limiter['base_delay_multiplier'],
            'last_rate_limit_time': self.rate_limiter['last_rate_limit_time']
        }
    
    def get_stats(self):
        """获取请求统计信息"""
        success_rate = 0
        if self.request_stats['total_requests'] > 0:
            success_rate = (self.request_stats['successful_requests'] / self.request_stats['total_requests']) * 100
        
        proxy_stats = self.get_proxy_stats()
        rate_limit_stats = self.get_rate_limit_stats()
        
        return {
            'total_requests': self.request_stats['total_requests'],
            'successful_requests': self.request_stats['successful_requests'],
            'failed_requests': self.request_stats['failed_requests'],
            'rate_limited_requests': self.request_stats['rate_limited_requests'],
            'success_rate': f"{success_rate:.1f}%",
            'last_successful_endpoint': self.request_stats['last_successful_endpoint'],
            'proxy_stats': proxy_stats,
            'rate_limit_stats': rate_limit_stats
        }
    
    def setup_logger(self, log_level='INFO', log_file=None, enable_console=True):
        """设置日志记录器"""
        import logging
        
        self.log_level = log_level
        self.log_file = log_file
        self.enable_console_log = enable_console
        
        # 创建logger
        self.logger = logging.getLogger(f'APIRestrictionBypass_{id(self)}')
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 清除之前的处理器
        self.logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.log_message('ERROR', f'无法创建日志文件 {log_file}: {e}')
        
        self.log_message('INFO', '日志记录器初始化完成')
    
    def log_message(self, level, message, **kwargs):
        """记录日志消息"""
        # 如果logger未初始化，使用print
        if self.logger is None:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] {level}: {message}"
            if self.enable_console_log:
                print(log_entry)
            
            # 添加到缓冲区
            self.log_buffer.append(log_entry)
            if len(self.log_buffer) > self.max_log_buffer_size:
                self.log_buffer.pop(0)
            return
        
        # 使用logger记录
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message, **kwargs)
    
    def log_request_start(self, url, headers, cookies=None, use_proxy=False):
        """记录请求开始"""
        log_data = {
            'url': url,
            'user_agent': headers.get('User-Agent', 'Unknown'),
            'referer': headers.get('Referer', 'None'),
            'use_proxy': use_proxy,
            'has_cookies': bool(cookies),
            'timestamp': time.time()
        }
        
        self.log_message('DEBUG', f"请求开始: {log_data}")
        return log_data
    
    def log_request_end(self, url, success, response_data=None, error=None, duration=0):
        """记录请求结束"""
        log_data = {
            'url': url,
            'success': success,
            'duration': duration,
            'timestamp': time.time()
        }
        
        if success:
            code = response_data.get('code', 'unknown') if response_data else 'unknown'
            self.log_message('DEBUG', f"请求成功: URL={url}, Code={code}, Duration={duration:.2f}s")
        else:
            error_msg = str(error) if error else 'Unknown error'
            self.log_message('WARNING', f"请求失败: URL={url}, Error={error_msg}, Duration={duration:.2f}s")
    
    def log_rate_limit_detected(self, response_data, retry_attempt=0):
        """记录风控检测"""
        code = response_data.get('code', -1)
        message = response_data.get('message', '')
        
        self.log_message('WARNING', f"风控检测: Code={code}, Message='{message}', Retry={retry_attempt}")
        
        # 详细的风控信息
        if code == -352:
            self.log_message('WARNING', '检测到频繁访问限制 (-352)')
        elif code == -401:
            self.log_message('WARNING', '检测到身份验证失败 (-401)')
        elif code == -403:
            self.log_message('WARNING', '检测到访问被拒绝 (-403)')
    
    def log_proxy_usage(self, proxy_info, success, error=None, duration=None):
        """记录代理使用情况"""
        proxy_str = str(proxy_info) if proxy_info else 'None'
        
        if success:
            duration_str = f" ({duration:.2f}s)" if duration else ""
            self.log_message('DEBUG', f"代理请求成功: {proxy_str}{duration_str}")
        else:
            error_msg = str(error) if error else 'Unknown error'
            duration_str = f" ({duration:.2f}s)" if duration else ""
            self.log_message('WARNING', f"代理请求失败: {proxy_str}{duration_str}, Error: {error_msg}")
    
    def log_rate_limit_stats(self):
        """记录限流统计信息"""
        stats = self.get_rate_limit_stats()
        
        self.log_message('INFO', f"限流统计: 最近1分钟请求={stats['recent_requests_per_minute']}, "
                                  f"当前倍数={stats['base_delay_multiplier']:.2f}, "
                                  f"自适应延迟={stats['adaptive_delay_enabled']}")
    
    def log_system_stats(self):
        """记录系统统计信息"""
        stats = self.get_stats()
        
        self.log_message('INFO', f"系统统计: 总请求={stats['total_requests']}, "
                                  f"成功={stats['successful_requests']}, "
                                  f"失败={stats['failed_requests']}, "
                                  f"风控={stats['rate_limited_requests']}")
        
        if stats.get('proxy_stats'):
            self.log_message('INFO', f"代理统计: 总代理请求={stats['proxy_stats']['total_proxy_requests']}, "
                                      f"成功={stats['proxy_stats']['successful_proxy_requests']}, "
                                      f"失败={stats['proxy_stats']['failed_proxy_requests']}")
    
    def get_log_buffer(self):
        """获取日志缓冲区内容"""
        return self.log_buffer.copy()
    
    def clear_log_buffer(self):
        """清空日志缓冲区"""
        self.log_buffer.clear()
    
    def export_logs(self, filename=None):
        """导出日志到文件"""
        if not filename:
            filename = f'api_bypass_logs_{time.strftime("%Y%m%d_%H%M%S")}.log'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # 写入缓冲区日志
                for log_entry in self.log_buffer:
                    f.write(log_entry + '\n')
                
                # 写入当前统计信息
                f.write('\n=== 系统统计信息 ===\n')
                stats = self.get_stats()
                f.write(json.dumps(stats, indent=2, ensure_ascii=False) + '\n')
                
                # 写入限流统计
                f.write('\n=== 限流统计信息 ===\n')
                rate_stats = self.get_rate_limit_stats()
                f.write(json.dumps(rate_stats, indent=2, ensure_ascii=False) + '\n')
            
            self.log_message('INFO', f"日志导出成功: {filename}")
            return self.log_buffer.copy()  # 返回日志缓冲区内容
        except Exception as e:
            self.log_message('ERROR', f"日志导出失败: {e}")
            return []

def handler(environ, start_response):
    try:
        # 初始化日志记录
        bypass = APIRestrictionBypass()
        bypass.setup_logger(log_level='INFO', enable_console=True)
        
        bypass.log_message('INFO', '开始处理请求')
        result = get_up_latest_dynamic()
        
        bypass.log_message('INFO', '请求处理完成')
        bypass.log_system_stats()
        
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        return [result.encode('utf-8')]
    except Exception as e:
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        error_msg = "Error: " + str(e)
        return [error_msg.encode('utf-8')]

def get_user_dynamics(uid, cookie_string=None, use_bypass=True):
    """
    获取用户动态（集成API风控绕过功能）
    
    Args:
        uid: 用户ID
        cookie_string: 可选的cookie字符串
        use_bypass: 是否使用风控绕过（默认启用）
    
    Returns:
        dict: 用户动态数据，失败返回None
    """
    
    if use_bypass:
        bypass = APIRestrictionBypass()
        bypass.setup_logger(log_level='INFO', enable_console=True)
        bypass.log_message('INFO', f"使用API风控绕过模式获取用户 {uid} 的动态...")
        
        # 尝试多个API端点
        for endpoint in bypass.api_endpoints:
            try:
                bypass.log_message('INFO', f"尝试端点: {endpoint['name']}")
                
                # 构建URL
                url = endpoint['url'].format(uid=uid)
                
                # 获取随机化请求头
                headers = bypass.get_random_headers(uid, endpoint['name'])
                
                # 添加端点特定的头部
                if endpoint['name'] == 'polymer':
                    headers.update(endpoint['headers'])
                elif endpoint['name'] == 'vc':
                    headers.update(endpoint['headers'])
                elif endpoint['name'] == 'wbi':
                    headers.update(endpoint['headers'])
                
                # 生成随机cookie
                random_cookies = bypass.generate_random_cookie()
                
                # 如果有提供cookie字符串，合并使用
                if cookie_string:
                    cookie_pairs = cookie_string.split('; ')
                    for pair in cookie_pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            if value.strip():  # 只合并非空值
                                random_cookies[key.strip()] = value.strip()
                
                # 使用风控绕过请求
                data = bypass.make_request_with_bypass(url, headers, random_cookies)
                
                if data and data.get('code') == 0:
                    bypass.log_message('INFO', f"端点 {endpoint['name']} 请求成功")
                    bypass.request_stats['last_successful_endpoint'] = endpoint['name']
                    return data
                elif data and bypass.is_rate_limited(data):
                    bypass.log_message('WARNING', f"端点 {endpoint['name']} 触发风控，尝试下一个端点...")
                    continue
                else:
                    bypass.log_message('WARNING', f"端点 {endpoint['name']} 返回异常，尝试下一个端点...")
                    continue
                    
            except Exception as e:
                bypass.log_message('ERROR', f"端点 {endpoint['name']} 异常: {e}")
                continue
        
        # 所有端点都失败，打印统计信息
        stats = bypass.get_stats()
        bypass.log_message('ERROR', f"所有端点都失败，API绕过统计: {stats}")
        bypass.log_system_stats()
        return None
    
    else:
        # 传统模式（不使用风控绕过）
        bypass = APIRestrictionBypass()
        bypass.setup_logger(log_level='INFO', enable_console=True)
        bypass.log_message('INFO', f"使用传统模式获取用户 {uid} 的动态...")
        
        url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={uid}&timezone_offset=-480"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': f'https://space.bilibili.com/{uid}/dynamic',
            'Origin': 'https://space.bilibili.com',
            'X-Requested-With': 'XMLHttpRequest',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        
        # 设置cookie
        session = requests.Session()
        if cookie_string:
            # 解析现有的cookie字符串
            cookie_pairs = cookie_string.split('; ')
            for pair in cookie_pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    session.cookies.set(key.strip(), value.strip(), domain='.bilibili.com')
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 检查响应是否被gzip压缩
            content = response.content
            try:
                content = gzip.decompress(content)
            except:
                pass
            
            data = json.loads(content.decode('utf-8'))
            
            # 检查返回状态
            if data.get('code') == -352:
                bypass.log_message('WARNING', f"用户 {uid} 遇到风控限制 (-352)")
                return None
            elif data.get('code') != 0:
                bypass.log_message('WARNING', f"获取用户 {uid} 动态失败: {data.get('message', '未知错误')}")
                return None
            
            bypass.log_message('INFO', f"传统模式获取用户 {uid} 动态成功")
            return data
            
        except requests.exceptions.RequestException as e:
            bypass.log_message('ERROR', f"获取用户 {uid} 动态网络错误: {e}")
            return None
        except json.JSONDecodeError as e:
            bypass.log_message('ERROR', f"解析用户 {uid} 动态数据失败: {e}")
            return None
        except Exception as e:
            bypass.log_message('ERROR', f"获取用户 {uid} 动态异常: {e}")
            return None

def get_up_latest_dynamic(uid=None, up_name=None):
    # 如果没有提供UID，使用默认UID
    if not uid:
        uid = "22376577"
    if not up_name:
        up_name = "牛奶糖好吃"
    
    # 获取真实cookie值
    real_cookies = "buvid3=7AC36028-D057-284A-14E8-5BB817F3DCEA40753infoc; b_nut=1760541240; __at_once=3401840458030349206"
    
    bypass = APIRestrictionBypass()
    bypass.setup_logger(log_level='INFO', enable_console=True)
    
    bypass.log_message('INFO', "=== 获取UP主 {} 最新动态 ===".format(up_name))
    bypass.log_message('INFO', "用户UID: {}".format(uid))
    
    # 使用新的get_user_dynamics函数获取数据
    data = get_user_dynamics(uid, real_cookies, use_bypass=True)
    
    if not data:
        bypass.log_message('ERROR', "获取动态失败")
        return "获取动态失败"
    
    # 解析polymer API返回的数据
    try:
        bypass.log_message('INFO', "正在解析polymer API数据...")
        items = data.get('data', {}).get('items', [])
        bypass.log_message('INFO', "polymer API获取到 {} 条动态".format(len(items)))
        
        # 检查响应码
        code = data.get('code', -1)
        bypass.log_message('INFO', "polymer API返回code: {}".format(code))
        
        if code == -352:
            bypass.log_message('WARNING', "polymer API返回风控错误code=-352")
            # 尝试获取风控信息
            if 'data' in data and isinstance(data['data'], dict):
                if 'v_voucher' in data['data']:
                    bypass.log_message('WARNING', "风控信息v_voucher: {}".format(data['data']['v_voucher']))
            return "polymer API风控校验失败: code=-352"
        elif code == 0:
            bypass.log_message('INFO', "polymer API返回成功")
            items = data.get('data', {}).get('items', [])
            bypass.log_message('INFO', "polymer API获取到 {} 条动态".format(len(items)))
            
            if items:
                bypass.log_message('INFO', "=== 详细分析最新动态 ===")
                
                # 获取最新动态（第一条动态）
                target_dynamic = None
                if items:
                    # 直接获取第一条（最新）动态
                    latest_item = items[0]
                    
                    # 获取动态信息
                    dynamic_id = latest_item.get('id_str', '')
                    pub_time = latest_item.get('modules', {}).get('module_author', {}).get('pub_time', '')
                    pub_ts = latest_item.get('modules', {}).get('module_author', {}).get('pub_ts', 0)
                    dynamic_type = latest_item.get('type', '')
                    
                    # 获取主要类型和内容
                    module_dynamic = latest_item.get('modules', {}).get('module_dynamic', {})
                    major_type = ""
                    text_content = ""
                    
                    if module_dynamic:
                        major_info = module_dynamic.get('major', {})
                        if major_info:
                            major_type = major_info.get('type', '')
                        
                        # 提取文本内容 - 修复版（解决图文动态文字提取问题）
                        text_content = ""
                        
                        # 🔧 修复1：正确处理desc字段 - 不要使用{}作为默认值
                        desc_info = module_dynamic.get('desc')
                        if desc_info is not None and isinstance(desc_info, dict):
                            desc_text = desc_info.get('text', '')
                            if desc_text and desc_text.strip():
                                text_content = desc_text.strip()
                        
                        # 第二步：从major字段提取（增强版）
                        if not text_content.strip() and major_info and isinstance(major_info, dict):
                            # 2.1 视频内容（archive）
                            if 'archive' in major_info:
                                archive = major_info['archive']
                                if archive and isinstance(archive, dict):
                                    title = archive.get('title', '')
                                    if title and title.strip():
                                        text_content = title.strip()
                            
                            # 2.2 图文内容（draw）- 关键修复区域
                            if not text_content.strip() and 'draw' in major_info:
                                draw = major_info['draw']
                                if isinstance(draw, dict):
                                    # 检查draw中的文本内容
                                    draw_text = draw.get('text', '')
                                    if draw_text and draw_text.strip():
                                        text_content = draw_text.strip()
                                    else:
                                        # 检查图片数量信息
                                        items = draw.get('items', [])
                                        if items and isinstance(items, list):
                                            img_count = len(items)
                                            if img_count > 0:
                                                text_content = f"分享了{img_count}张图片"
                            
                            # 2.3 专栏内容（opus）
                            if not text_content.strip() and 'opus' in major_info:
                                opus = major_info['opus']
                                if opus and isinstance(opus, dict):
                                    title = opus.get('title', '')
                                    summary = opus.get('summary', '')
                                    if title and title.strip():
                                        text_content = title.strip()
                                    elif summary and summary.strip():
                                        text_content = summary.strip()
                            
                            # 2.4 其他major类型的通用处理
                            if not text_content.strip():
                                for major_type, major_data in major_info.items():
                                    if major_data and isinstance(major_data, dict):
                                        if 'title' in major_data:
                                            title = major_data['title']
                                            if title and title.strip():
                                                text_content = title.strip()
                                                break
                        
                        # 第三步：备用方案 - 检查其他可能的字段
                        if not text_content.strip():
                            # 检查content字段
                            if 'content' in module_dynamic:
                                content = module_dynamic['content']
                                if content and isinstance(content, dict):
                                    content_text = content.get('text', '')
                                    if content_text and content_text.strip():
                                        text_content = content_text.strip()
                            
                            # 检查item字段
                            if not text_content.strip() and 'item' in module_dynamic:
                                item = module_dynamic['item']
                                if item and isinstance(item, dict):
                                    item_text = item.get('text', '') or item.get('title', '') or item.get('description', '')
                                    if item_text and item_text.strip():
                                        text_content = item_text.strip()
                        
                        # 第四步：如果仍为空，尝试直接解析card字段（兼容vc API格式）
                        if not text_content.strip() and 'card' in latest_item:
                            try:
                                card_data = json.loads(latest_item['card'])
                                if 'item' in card_data:
                                    item_data = card_data['item']
                                    card_text = item_data.get('content', '') or item_data.get('description', '') or item_data.get('title', '')
                                    if card_text and card_text.strip():
                                        text_content = card_text.strip()
                            except:
                                pass
                    
                    bypass.log_message('INFO', "最新动态: ID={}, 时间={}, 类型={}, 主要类型={}".format(dynamic_id, pub_time, dynamic_type, major_type))
                    bypass.log_message('INFO', "  文本内容: '{}'".format(text_content))
                    bypass.log_message('INFO', "  module_dynamic 数据: {}".format(json.dumps(module_dynamic, ensure_ascii=False) if module_dynamic else "None"))
                    
                    # 获取所有动态类型映射
                    content_type_map = {
                        "MAJOR_TYPE_DRAW": "图片分享",
                        "MAJOR_TYPE_OPUS": "图文动态", 
                        "MAJOR_TYPE_ARCHIVE": "视频投稿",
                        "MAJOR_TYPE_LIVE_RCMD": "直播推荐",
                        "MAJOR_TYPE_UGC_SEASON": "合集更新",
                        "MAJOR_TYPE_COURSES_SEASON": "课程更新",
                        "MAJOR_TYPE_NONE": "纯文本动态",
                        "": "未知类型"
                    }
                    
                    content_type = content_type_map.get(major_type, "其他类型({})".format(major_type))
                    
                    bypass.log_message('INFO', "*** 找到最新动态！***")
                    target_dynamic = {
                        'id': dynamic_id,
                        'pub_time': pub_time,
                        'pub_ts': pub_ts,
                        'type': dynamic_type,
                        'major_type': major_type,
                        'content_type': content_type,
                        'text_content': text_content,
                        'raw_item': latest_item
                    }
                
                if target_dynamic:
                    bypass.log_message('INFO', "目标动态详情:")
                    bypass.log_message('INFO', "  动态ID: {}".format(target_dynamic['id']))
                    bypass.log_message('INFO', "  发布时间: {}".format(target_dynamic['pub_time']))
                    bypass.log_message('INFO', "  时间戳: {}".format(target_dynamic['pub_ts']))
                    bypass.log_message('INFO', "  动态类型: {}".format(target_dynamic['type']))
                    bypass.log_message('INFO', "  主要类型: {}".format(target_dynamic['major_type']))
                    bypass.log_message('INFO', "  文本内容: '{}'".format(target_dynamic['text_content']))
                    
                    # 检查时间是否在30分钟内
                    current_time = int(time.time())
                    time_diff_minutes = (current_time - target_dynamic['pub_ts']) // 60
                    bypass.log_message('INFO', "  距现在: {} 分钟".format(time_diff_minutes))
                    
                    if time_diff_minutes <= TIME_THRESHOLD_MINUTES:
                        bypass.log_message('INFO', "*** 动态在{}分钟内，准备推送 ***".format(TIME_THRESHOLD_MINUTES))
                        
                        # 构建推送内容
                        content = "UP主发布了新{}\n动态ID: {}\n发布时间: {}\n类型: {}\n文本内容: {}".format(
                            target_dynamic['content_type'],
                            target_dynamic['id'],
                            target_dynamic['pub_time'],
                            target_dynamic['content_type'],
                            target_dynamic['text_content'] or '（无文本）'
                        )
                        
                        # 屏蔽消息发送功能（测试模式）
                        if TEST_MODE:
                            bypass.log_message('INFO', "[测试模式] 准备推送内容: {}".format(content))
                            bypass.log_message('INFO', "[测试模式] 消息发送功能已屏蔽")
                            return "测试模式：找到{}分钟前的动态(ID: {})，消息发送已屏蔽".format(time_diff_minutes, target_dynamic['id'])
                        else:
                            bypass.log_message('INFO', "准备推送内容: {}".format(content))
                            # 实际发送通知
                            # 使用实际提取的文本内容，如果为空则显示内容类型
                            actual_content = target_dynamic['text_content'].strip() if target_dynamic['text_content'] else target_dynamic['content_type']
                            dynamic_info = {
                                'dynamic_id': target_dynamic['id'],
                                'content': actual_content,
                                'content_type': target_dynamic['content_type'],
                                'timestamp': target_dynamic['pub_ts'],
                                'url': "https://t.bilibili.com/{}".format(target_dynamic['id']),
                                'pics': [],  # 可以后续添加图片处理
                                'like': 0,
                                'reply': 0,
                                'forward': 0
                            }
                            success = send_wechat_notification(up_name, dynamic_info)
                            if success:
                                return "成功推送{}分钟前的动态(ID: {})".format(time_diff_minutes, target_dynamic['id'])
                            else:
                                return "推送失败：{}分钟前的动态(ID: {})".format(time_diff_minutes, target_dynamic['id'])
                    else:
                        bypass.log_message('INFO', "动态超过{}分钟，不推送".format(TIME_THRESHOLD_MINUTES))
                        return "动态超过{}分钟，不推送".format(TIME_THRESHOLD_MINUTES)
                else:
                    bypass.log_message('INFO', "未找到最新动态")
                    return "未找到最新动态"
            else:
                bypass.log_message('INFO', "polymer API未获取到动态")
                return "polymer API未获取到动态"
        else:
            bypass.log_message('WARNING', "polymer API返回错误: code={}".format(code))
            return "polymer API返回错误: code={}".format(code)
            
    except Exception as e:
        bypass.log_message('ERROR', "polymer API请求失败: {}".format(e))
        return "polymer API请求失败: {}".format(e)
    
    # 如果polymer API失败，尝试vc API作为备选
    bypass.log_message('INFO', "尝试vc API作为备选...")
    vc_url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={}&need_top=1&platform=web".format(uid)
    
    try:
        bypass.log_message('INFO', "正在请求vc API: {}".format(vc_url))
        response = requests.get(vc_url, headers=headers, timeout=10)
        bypass.log_message('INFO', "vc API状态码: {}".format(response.status_code))
        
        # 尝试直接解析JSON
        try:
            data = response.json()
            bypass.log_message('INFO', "vc API直接JSON解析成功")
        except json.JSONDecodeError as json_error:
            bypass.log_message('WARNING', "vc API直接JSON解析失败: {}".format(json_error))
            # 如果直接解析失败，尝试手动解压缩
            content = response.content
            bypass.log_message('INFO', "响应内容长度: {} 字节".format(len(content)))
            
            # 尝试gzip解压（简化处理，移除brotli依赖）
            try:
                content = gzip.decompress(content)
                bypass.log_message('INFO', "vc API gzip解压成功")
            except:
                bypass.log_message('WARNING', "vc API gzip解压失败，使用原始内容")
            
            # 尝试解析解压后的内容
            try:
                data = json.loads(content.decode('utf-8'))
                bypass.log_message('INFO', "vc API 手动解压后JSON解析成功")
            except Exception as e:
                bypass.log_message('ERROR', "vc API 手动解压后JSON解析也失败: {}".format(e))
                return "vc API JSON解析失败: {}".format(e)
        
        # 检查响应码
        code = data.get('code', -1)
        bypass.log_message('INFO', "vc API返回code: {}".format(code))
        
        if code == 0:
            bypass.log_message('INFO', "vc API返回成功")
            cards = data.get('data', {}).get('cards', [])
            bypass.log_message('INFO', "vc API获取到 {} 条动态".format(len(cards)))
            
            if cards:
                # 处理最新动态
                latest_card = cards[0]
                card_id = latest_card.get('desc', {}).get('dynamic_id_str', '')
                timestamp = latest_card.get('desc', {}).get('timestamp', 0)
                card_type = latest_card.get('desc', {}).get('type', '')
                
                # 解析卡片内容 - 尝试多个字段
                card_content = ""
                try:
                    card_json = json.loads(latest_card.get('card', '{}'))
                    
                    # 尝试从item字段获取
                    if 'item' in card_json:
                        item_data = card_json['item']
                        card_content = item_data.get('content', '')
                        if not card_content:
                            card_content = item_data.get('description', '')
                            if not card_content:
                                card_content = item_data.get('title', '')
                                if not card_content and 'summary' in item_data:
                                    card_content = item_data.get('summary', '')
                    
                    # 尝试从dynamic字段获取
                    if not card_content and 'dynamic' in card_json:
                        dynamic_data = card_json['dynamic']
                        card_content = dynamic_data.get('content', '')
                        if not card_content:
                            card_content = dynamic_data.get('description', '')
                    
                    # 尝试从其他常见字段获取
                    if not card_content:
                        # 尝试直接获取content字段
                        card_content = card_json.get('content', '')
                        if not card_content:
                            card_content = card_json.get('description', '')
                        if not card_content:
                            card_content = card_json.get('title', '')
                        if not card_content:
                            card_content = card_json.get('summary', '')
                    
                except:
                    card_content = "解析失败"
                
                # 动态类型映射
                content_type_map = {
                    'DYNAMIC_TYPE_DRAW': '图片分享',
                    'DYNAMIC_TYPE_WORD': '纯文字动态',
                    'DYNAMIC_TYPE_AV': '视频投稿',
                    'DYNAMIC_TYPE_FORWARD': '转发动态',
                    'DYNAMIC_TYPE_LIVE': '直播动态',
                    'DYNAMIC_TYPE_ARTICLE': '专栏文章',
                    'MAJOR_TYPE_DRAW': '图片分享',
                    'MAJOR_TYPE_OPUS': '图文动态',
                    'MAJOR_TYPE_ARCHIVE': '视频投稿',
                    'MAJOR_TYPE_LIVE_RCMD': '直播推荐',
                    'MAJOR_TYPE_UGC_SEASON': '合集更新',
                    'MAJOR_TYPE_COURSES_SEASON': '课程更新',
                    'MAJOR_TYPE_NONE': '纯文本动态',
                }
                
                content_type = content_type_map.get(card_type, '动态({})'.format(card_type))
                 
                bypass.log_message('INFO', "vc API最新动态: ID={}, 时间戳={}, 类型={}({})".format(card_id, timestamp, card_type, content_type))
                bypass.log_message('INFO', "vc API动态内容: {}...".format(card_content[:100]))
                
                # 检查时间
                current_time = int(time.time())
                time_diff_minutes = (current_time - timestamp) // 60
                
                if time_diff_minutes <= TIME_THRESHOLD_MINUTES:
                    bypass.log_message('INFO', "vc API动态在{}分钟内，准备推送".format(TIME_THRESHOLD_MINUTES))
                    
                    content = "UP主发布了新{}\n动态ID: {}\n发布时间: {}分钟前\n类型: {}\n内容: {}...".format(
                        content_type, card_id, time_diff_minutes, content_type, card_content[:100]
                    )
                    
                    # 屏蔽消息发送功能（测试模式）
                    if TEST_MODE:
                        bypass.log_message('INFO', "[测试模式] 准备推送内容: {}".format(content))
                        bypass.log_message('INFO', "[测试模式] 消息发送功能已屏蔽")
                        return "vc API测试模式：找到{}分钟前的动态(ID: {})，消息发送已屏蔽".format(time_diff_minutes, card_id)
                    else:
                        bypass.log_message('INFO', "准备推送内容: {}".format(content))
                        # 实际发送通知
                        # 使用实际提取的卡片内容，如果为空则显示内容类型
                        actual_content = card_content.strip() if card_content else content_type
                        dynamic_info = {
                            'dynamic_id': card_id,
                            'content': actual_content,
                            'content_type': content_type,
                            'timestamp': timestamp,
                            'url': "https://t.bilibili.com/{}".format(card_id),
                            'pics': [],
                            'like': 0,
                            'reply': 0,
                            'forward': 0
                        }
                        success = send_wechat_notification(up_name, dynamic_info)
                        if success:
                            return "vc API成功推送{}分钟前的动态(ID: {})".format(time_diff_minutes, card_id)
                        else:
                            return "vc API推送失败：{}分钟前的动态(ID: {})".format(time_diff_minutes, card_id)
                else:
                    bypass.log_message('INFO', "vc API动态超过{}分钟，不推送".format(TIME_THRESHOLD_MINUTES))
                    return "vc API动态超过{}分钟，不推送".format(TIME_THRESHOLD_MINUTES)
            else:
                bypass.log_message('INFO', "vc API未获取到动态")
                return "vc API未获取到动态"
        else:
            bypass.log_message('WARNING', "vc API返回错误: code={}".format(code))
            return "vc API返回错误: code={}".format(code)
    
    except Exception as e:
        bypass.log_message('ERROR', "vc API请求失败: {}".format(e))
        return "vc API请求失败: {}".format(e)
    
    # 如果所有API都失败
    return "所有API尝试均失败，获取动态失败"

def should_send_notification(dynamic_created_time):
    """判断是否应该发送通知（基于发布时间）"""
    try:
        # 将Unix时间戳转换为datetime对象
        dynamic_time = datetime.fromtimestamp(dynamic_created_time)
        current_time = datetime.now()
        
        # 计算时间差（分钟）
        time_diff_minutes = (current_time - dynamic_time).total_seconds() / 60
        
        # 检查是否在时间阈值内（30分钟内）
        if time_diff_minutes <= TIME_THRESHOLD_MINUTES:
            return True, "动态发布时间符合条件（{:.1f}分钟内）".format(time_diff_minutes)
        else:
            return False, "动态发布时间过久（{:.1f}分钟前，超过{}分钟阈值）".format(time_diff_minutes, TIME_THRESHOLD_MINUTES)
            
    except Exception as e:
        bypass.log_message('ERROR', "时间判断出错: {}".format(e))
        return False, "时间判断出错"

def send_wechat_notification(up_name, dynamic_info):
    """发送微信通知"""
    try:
        title = "🔔 {} 发布了新{}".format(up_name, dynamic_info['content_type'])
        
        # 格式化时间
        pub_time = datetime.fromtimestamp(dynamic_info["timestamp"]).strftime('%Y-%m-%d %H:%M:%S') if dynamic_info["timestamp"] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dynamic_url = dynamic_info['url']
        
        # 构建内容预览（截取前200字符）
        content_preview = dynamic_info['content']
        if len(content_preview) > 200:
            content_preview = content_preview[:200] + "..."
        
        # 构建图片信息
        pic_info = ""
        if dynamic_info['pics']:
            pic_count = len(dynamic_info['pics'])
            pic_info = "📸 包含 {} 张图片".format(pic_count)
        
        # 构建HTML内容
        html_content = """
<div style="max-width: 600px; margin: 0 auto; font-family: 'Microsoft YaHei', Arial, sans-serif;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px 12px 0 0; text-align: center; color: white;">
        <h2 style="margin: 0; font-size: 24px; font-weight: bold;">📝 {} 新{}发布</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">B站动态监控通知</p>
    </div>
    
    <div style="background: white; padding: 25px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #00a1d6;">
            <h3 style="color: #2c3e50; margin: 0 0 10px 0; font-size: 18px;">{}</h3>
            <p style="color: #666; margin: 0; line-height: 1.6;">{}</p>
            {}
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="display: flex; align-items: center;">
                <span style="background-color: #e3f2fd; color: #1976d2; padding: 6px 12px; border-radius: 20px; font-size: 14px; margin-right: 10px;">⏰ {}</span>
                <span style="background-color: #f3e5f5; color: #7b1fa2; padding: 6px 12px; border-radius: 20px; font-size: 14px;">🆔 {}</span>
            </div>
            <a href="{}" style="background: linear-gradient(135deg, #00a1d6, #0088cc); color: white; text-decoration: none; padding: 10px 20px; border-radius: 25px; font-weight: bold; transition: all 0.3s ease;">👉 查看动态</a>
        </div>
        
        <div style="display: flex; justify-content: space-around; background-color: #fafafa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <div style="text-align: center;">
                <div style="font-size: 20px; font-weight: bold; color: #e91e63;">👍 {:,}</div>
                <div style="font-size: 12px; color: #666;">点赞</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px; font-weight: bold; color: #2196f3;">💬 {:,}</div>
                <div style="font-size: 12px; color: #666;">评论</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px; font-weight: bold; color: #4caf50;">🔄 {:,}</div>
                <div style="font-size: 12px; color: #666;">转发</div>
            </div>
        </div>
        
        <div style="border-top: 1px solid #eee; padding-top: 15px; text-align: center;">
            <p style="color: #999; font-size: 12px; margin: 0;">⏰ 推送时间：{}</p>
            <p style="color: #999; font-size: 12px; margin: 5px 0 0 0;">💡 来自B站动态监控系统</p>
        </div>
    </div>
</div>
""".format(
            up_name, dynamic_info['content_type'],
            dynamic_info['content_type'], content_preview,
            '<p style="color: #2196f3; margin: 10px 0 0 0; font-weight: bold;">{}</p>'.format(pic_info) if pic_info else '',
            pub_time, dynamic_info['dynamic_id'], dynamic_url,
            dynamic_info['like'], dynamic_info['reply'], dynamic_info['forward'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # 发送通知
        data = {
            "token": PUSHPLUS_TOKEN,
            "title": title,
            "content": html_content,
            "template": "html"
        }
        
        response = requests.post(
            "http://www.pushplus.plus/send/",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, dict) and result.get("code") == 200:
                    bypass.log_message('INFO', "✅ 通知发送成功: {}".format(up_name))
                    return True
                else:
                    error_msg = result.get("msg", "发送失败") if isinstance(result, dict) else str(result)
                    bypass.log_message('ERROR', "❌ 通知发送失败: {}".format(error_msg))
                    return False
            except:
                bypass.log_message('ERROR', "❌ 响应解析失败: {}".format(response.text))
                return False
        else:
            bypass.log_message('ERROR', "❌ HTTP错误: {}".format(response.status_code))
            return False
            
    except Exception as e:
        bypass.log_message('ERROR', "❌ 发送通知异常: {}".format(e))
        return False

def is_aliyun_environment():
    """判断是否在阿里云函数计算环境中"""
    return os.environ.get('FC_FUNCTION_NAME') is not None

def monitor_bilibili_dynamics():
    """监控B站UP主动态"""
    current_time = datetime.now()
    bypass = APIRestrictionBypass()
    bypass.setup_logger()
    
    bypass.log_message('INFO', "🚀 开始监控B站动态 - {}".format(current_time.strftime('%Y-%m-%d %H:%M:%S')))
    bypass.log_message('INFO', "⏰ 时间阈值: {}分钟内发布的动态才推送".format(TIME_THRESHOLD_MINUTES))
    bypass.log_message('INFO', "=" * 60)
    
    new_count = 0
    notified_count = 0
    
    for up in UP_LIST:
        bypass.log_message('INFO', "\n📱 检查 {} 的动态...".format(up['name']))
        
        try:
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
    bypass = APIRestrictionBypass()
    bypass.setup_logger()
    
    bypass.log_message('INFO', "⏰ 当前时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    bypass.log_message('INFO', "⏰ 当前时间: {}分钟内发布的动态才推送".format(TIME_THRESHOLD_MINUTES))
    
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
                    "time_threshold_minutes": TIME_THRESHOLD_MINUTES,
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
    bypass.log_message('INFO', "⏰ 时间阈值: {}分钟内发布的动态才推送".format(TIME_THRESHOLD_MINUTES))
    
    event = {}
    context = type('Context', (), {'request_id': 'local-test-123'})()
    
    # 调用处理函数
    result = handler(event, context)
    
    bypass.log_message('INFO', "\n📊 测试结果:")
    bypass.log_message('INFO', json.dumps(result, ensure_ascii=False, indent=2))