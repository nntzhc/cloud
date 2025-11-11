import requests
import random
import time
import json
import gzip
import hashlib
import uuid
import string


class APIRestrictionBypass:
    """B站API风控绕过器"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
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
        
        # 简化配置 - 移除时间控制机制
        self.rate_limiter = {
            'adaptive_delay_enabled': False,  # 禁用自适应延迟
            'base_delay_multiplier': 1.0,  # 基础延迟倍数（不再使用）
        }
        
        # 端点健康状态和智能选择
        self.endpoint_health = {
            'polymer': {
                'success_rate': 0.0,  # 初始成功率为0%，避免无请求时显示100%
                'avg_response_time': 0,
                'last_used': 0,
                'consecutive_failures': 0,
                'total_requests': 0,
                'successful_requests': 0,
                'priority': 1,  # 优先级，数字越小优先级越高
                'cooldown_until': 0,  # 冷却时间
                'weight': 1.0  # 选择权重
            },
            'vc': {
                'success_rate': 0.0,  # 初始成功率为0%，避免无请求时显示100%
                'avg_response_time': 0,
                'last_used': 0,
                'consecutive_failures': 0,
                'total_requests': 0,
                'successful_requests': 0,
                'priority': 2,
                'cooldown_until': 0,
                'weight': 0.8
            },
            'wbi': {
                'success_rate': 0.0,  # 初始成功率为0%，避免无请求时显示100%
                'avg_response_time': 0,
                'last_used': 0,
                'consecutive_failures': 0,
                'total_requests': 0,
                'successful_requests': 0,
                'priority': 3,
                'cooldown_until': 0,
                'weight': 0.6
            }
        }
        
        # 端点选择策略
        self.endpoint_selection_config = {
            'enable_smart_selection': True,
            'success_rate_threshold': 0.3,  # 成功率阈值
            'max_consecutive_failures': 3,  # 最大连续失败次数
            'cooldown_duration': 300,  # 冷却时间（秒）
            'response_time_weight': 0.3,  # 响应时间在权重计算中的比重
            'success_rate_weight': 0.5,  # 成功率在权重计算中的比重
            'recency_weight': 0.2  # 最近使用时间在权重计算中的比重
        }
        
        # 日志配置
        self.logger = None
        self.log_level = 'INFO'
        self.log_file = None
        # 浏览器指纹随机化配置
        self.browser_fingerprints = {
            'viewport_sizes': [
                '1920x1080', '1366x768', '1440x900', '1536x864',
                '1600x900', '1680x1050', '1280x720', '2560x1440'
            ],
            'color_depths': [24, 32],
            'timezone_offsets': [-480, -540, -600, -660],  # 中国时区相关
            'languages': ['zh-CN', 'zh', 'zh-CN,zh', 'zh-CN,zh;q=0.9,en;q=0.8'],
            'platforms': ['Win32', 'MacIntel', 'Linux x86_64'],
            'cpu_classes': ['x86', 'x86_64', None],  # None表示不设置
            'device_memory': [4, 8, 16, 32],  # GB
            'hardware_concurrency': [4, 8, 12, 16],
            'touch_support': [0, 1],  # 是否支持触摸
            'pdf_viewer_enabled': [True, False],
            'canvas_fingerprint_enabled': True,
            'webgl_fingerprint_enabled': True,
            'audio_fingerprint_enabled': True,
            'client_hints_enabled': True
        }
        
        # TLS指纹随机化
        self.tls_fingerprints = [
            {
                'ja3': '769,47-53-5-10-49161-49162-49171-49172-50-56-19-4,0-10-11,23-24-25,0',
                'ja3_hash': 'd5e5c8f5f5f5f5f5f5f5f5f5f5f5f5f5',
                'user_agent': 'Chrome/120.0.0.0',
                'cipher_suites': [
                    'TLS_AES_128_GCM_SHA256', 'TLS_AES_256_GCM_SHA384', 'TLS_CHACHA20_POLY1305_SHA256',
                    'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256', 'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256',
                    'TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384', 'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384'
                ],
                'tls_version': 'TLSv1.3',
                'supported_groups': ['X25519', 'secp256r1', 'secp384r1']
            },
            {
                'ja3': '769,47-53-5-10-49161-49162-49171-49172-50-56-19-4,0-10-11,23-24-25,0',
                'ja3_hash': 'e6f6d7g6g6g6g6g6g6g6g6g6g6g6g6g6g6',
                'user_agent': 'Firefox/120.0',
                'cipher_suites': [
                    'TLS_AES_128_GCM_SHA256', 'TLS_AES_256_GCM_SHA384', 'TLS_CHACHA20_POLY1305_SHA256',
                    'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256', 'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256'
                ],
                'tls_version': 'TLSv1.3',
                'supported_groups': ['X25519', 'secp256r1', 'secp384r1', 'secp521r1']
            },
            {
                'ja3': '769,47-53-5-10-49161-49162-49171-49172-50-56-19-4,0-10-11,23-24-25,0',
                'ja3_hash': 'f7g7h8h7h7h7h7h7h7h7h7h7h7h7h7h7h7',
                'user_agent': 'Safari/17.1',
                'cipher_suites': [
                    'TLS_AES_128_GCM_SHA256', 'TLS_AES_256_GCM_SHA384', 'TLS_CHACHA20_POLY1305_SHA256'
                ],
                'tls_version': 'TLSv1.3',
                'supported_groups': ['X25519', 'secp256r1', 'secp384r1']
            },
            {
                'ja3': '769,47-53-5-10-49161-49162-49171-49172-50-56-19-4,0-10-11,23-24-25,0',
                'ja3_hash': 'g8h8i9i8i8i8i8i8i8i8i8i8i8i8i8i8i8',
                'user_agent': 'Edge/120.0.0.0',
                'cipher_suites': [
                    'TLS_AES_128_GCM_SHA256', 'TLS_AES_256_GCM_SHA384', 'TLS_CHACHA20_POLY1305_SHA256',
                    'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256', 'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256',
                    'TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384', 'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
                    'TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256', 'TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256'
                ],
                'tls_version': 'TLSv1.3',
                'supported_groups': ['X25519', 'secp256r1', 'secp384r1']
            }
        ]
    
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
    
    def generate_canvas_fingerprint(self):
        """生成Canvas指纹"""
        # 模拟Canvas指纹，基于随机噪声和数学函数
        base_noise = random.randint(100000, 999999)
        
        # 生成一些随机参数来影响指纹
        text = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        font_size = random.randint(8, 16)
        font_family = random.choice(['Arial', 'Helvetica', 'Times New Roman', 'Georgia'])
        
        # 模拟Canvas渲染的微小差异
        canvas_data = {
            'width': random.randint(200, 300),
            'height': random.randint(100, 150),
            'text': text,
            'font': f'{font_size}px {font_family}',
            'fillStyle': f'rgb({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)})',
            'globalAlpha': round(random.uniform(0.8, 1.0), 2),
            'lineWidth': random.uniform(1, 3),
            'shadowBlur': random.randint(0, 5),
            'shadowColor': f'rgba({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)}, {random.uniform(0, 0.5)})'
        }
        
        # 生成基于这些参数的哈希值
        fingerprint_data = f"{canvas_data['width']}x{canvas_data['height']}_{text}_{canvas_data['font']}_{canvas_data['fillStyle']}"
        canvas_hash = hashlib.md5(fingerprint_data.encode()).hexdigest()
        
        return {
            'hash': canvas_hash,
            'data': canvas_data
        }
    
    def generate_webgl_fingerprint(self):
        """生成WebGL指纹"""
        # WebGL vendor和renderer信息
        vendors = ['Intel Inc.', 'NVIDIA Corporation', 'ATI Technologies Inc.', 'Qualcomm']
        renderers = [
            'Intel Iris OpenGL Engine',
            'NVIDIA GeForce GTX 1080',
            'AMD Radeon Pro 580',
            'Adreno (TM) 640'
        ]
        
        # WebGL扩展列表
        extensions = [
            'WEBGL_debug_renderer_info',
            'OES_texture_float',
            'OES_texture_half_float',
            'WEBGL_lose_context',
            'OES_standard_derivatives',
            'OES_vertex_array_object',
            'WEBGL_compressed_texture_s3tc',
            'WEBGL_depth_texture',
            'OES_element_index_uint',
            'EXT_texture_filter_anisotropic'
        ]
        
        # 随机选择一些扩展
        selected_extensions = random.sample(extensions, random.randint(4, 8))
        
        # WebGL参数
        webgl_params = {
            'vendor': random.choice(vendors),
            'renderer': random.choice(renderers),
            'version': 'WebGL 1.0 (OpenGL ES 2.0 Chromium)',
            'shading_language_version': 'WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)',
            'max_texture_size': random.choice([8192, 16384]),
            'max_viewport_dims': random.choice([8192, 16384]),
            'max_vertex_attribs': random.randint(16, 32),
            'max_vertex_uniform_vectors': random.randint(256, 1024),
            'max_varying_vectors': random.randint(8, 32),
            'max_fragment_uniform_vectors': random.randint(256, 1024),
            'max_texture_image_units': random.randint(16, 32),
            'extensions': selected_extensions
        }
        
        # 生成指纹哈希
        fingerprint_str = f"{webgl_params['vendor']}_{webgl_params['renderer']}_{len(selected_extensions)}"
        webgl_hash = hashlib.md5(fingerprint_str.encode()).hexdigest()
        
        return {
            'hash': webgl_hash,
            'params': webgl_params
        }
    
    def generate_audio_fingerprint(self):
        """生成音频指纹"""
        # 音频上下文参数
        sample_rates = [44100, 48000, 96000, 192000]
        channel_counts = [1, 2, 4, 6, 8]
        
        audio_params = {
            'sample_rate': random.choice(sample_rates),
            'max_channel_count': random.choice(channel_counts),
            'number_of_inputs': random.randint(1, 2),
            'number_of_outputs': random.randint(1, 2),
            'channel_count': random.choice(channel_counts),
            'channel_count_mode': random.choice(['max', 'clamped-max', 'explicit']),
            'channel_interpretation': random.choice(['speakers', 'discrete'])
        }
        
        # 动态范围压缩参数
        compressor_params = {
            'threshold': random.uniform(-24, 0),
            'knee': random.uniform(0, 40),
            'ratio': random.uniform(1, 20),
            'reduction': random.uniform(-20, 0),
            'attack': random.uniform(0, 1),
            'release': random.uniform(0, 1)
        }
        
        # 生成指纹
        fingerprint_str = f"{audio_params['sample_rate']}_{audio_params['max_channel_count']}_{compressor_params['threshold']}"
        audio_hash = hashlib.md5(fingerprint_str.encode()).hexdigest()
        
        return {
            'hash': audio_hash,
            'audio_params': audio_params,
            'compressor_params': compressor_params
        }

    def select_optimal_endpoint(self, force_endpoint=None):
        """智能选择最优端点"""
        if force_endpoint and force_endpoint in self.endpoints:
            return force_endpoint
            
        if not self.endpoint_selection_config['enable_smart_selection']:
            # 禁用智能选择时，按优先级顺序返回第一个可用端点
            for endpoint in sorted(self.endpoint_health.keys(), 
                                 key=lambda x: self.endpoint_health[x]['priority']):
                if self.is_endpoint_available(endpoint):
                    return endpoint
            return 'polymer'  # 默认端点
        
        # 获取当前时间
        current_time = time.time()
        available_endpoints = []
        
        # 筛选可用端点
        for endpoint in self.endpoint_health:
            health = self.endpoint_health[endpoint]
            
            # 检查冷却时间
            if current_time < health['cooldown_until']:
                continue
                
            # 检查成功率阈值
            if health['success_rate'] < self.endpoint_selection_config['success_rate_threshold']:
                continue
                
            # 检查连续失败次数
            if health['consecutive_failures'] >= self.endpoint_selection_config['max_consecutive_failures']:
                continue
                
            available_endpoints.append(endpoint)
        
        if not available_endpoints:
            # 没有可用端点时，选择冷却时间最早结束的端点
            earliest_endpoint = min(self.endpoint_health.keys(),
                                  key=lambda x: self.endpoint_health[x]['cooldown_until'])
            return earliest_endpoint
        
        # 计算每个可用端点的综合得分
        endpoint_scores = {}
        for endpoint in available_endpoints:
            health = self.endpoint_health[endpoint]
            score = self.calculate_endpoint_score(health, current_time)
            endpoint_scores[endpoint] = score
        
        # 选择得分最高的端点
        optimal_endpoint = max(endpoint_scores.keys(), key=lambda x: endpoint_scores[x])
        
        # 更新最后使用时间
        self.endpoint_health[optimal_endpoint]['last_used'] = current_time
        
        return optimal_endpoint
    
    def calculate_endpoint_score(self, health, current_time):
        """计算端npoint评分"""
        config = self.endpoint_selection_config
        
        # 响应时间评分（响应时间越短，评分越高）
        response_time_score = 0
        if health['avg_response_time'] > 0:
            # 假设理想响应时间为1秒，超过5秒的响应时间评分为0
            ideal_response_time = 1.0
            max_acceptable_time = 5.0
            if health['avg_response_time'] <= ideal_response_time:
                response_time_score = 1.0
            elif health['avg_response_time'] >= max_acceptable_time:
                response_time_score = 0.0
            else:
                response_time_score = 1.0 - (health['avg_response_time'] - ideal_response_time) / (max_acceptable_time - ideal_response_time)
        
        # 成功率评分
        success_rate_score = health['success_rate']
        
        # 最近使用时间评分（距离现在越近，评分越高）
        recency_score = 0
        if health['last_used'] > 0:
            time_since_last_use = current_time - health['last_used']
            # 超过1小时未使用的端npoint评分为0，刚使用的端npoint评分为1
            max_idle_time = 3600
            recency_score = max(0, 1.0 - time_since_last_use / max_idle_time)
        
        # 综合评分
        total_score = (response_time_score * config['response_time_weight'] +
                      success_rate_score * config['success_rate_weight'] +
                      recency_score * config['recency_weight'])
        
        return total_score
    
    def is_endpoint_available(self, endpoint):
        """检查端点是否可用"""
        if endpoint not in self.endpoint_health:
            return False
            
        health = self.endpoint_health[endpoint]
        current_time = time.time()
        
        # 检查冷却时间
        if current_time < health['cooldown_until']:
            return False
            
        # 检查成功率阈值
        if health['success_rate'] < self.endpoint_selection_config['success_rate_threshold']:
            return False
            
        # 检查连续失败次数
        if health['consecutive_failures'] >= self.endpoint_selection_config['max_consecutive_failures']:
            return False
            
        return True
    
    def update_endpoint_health(self, endpoint, success, response_time=0, error_code=None):
        """更新端点健康状态"""
        if endpoint not in self.endpoint_health:
            return
            
        health = self.endpoint_health[endpoint]
        current_time = time.time()
        
        # 更新请求统计
        health['total_requests'] += 1
        if success:
            health['successful_requests'] += 1
            health['consecutive_failures'] = 0
        else:
            health['consecutive_failures'] += 1
            
            # 设置冷却时间
            if error_code in [429, 403, 401]:  # 限流或认证错误
                health['cooldown_until'] = current_time + self.endpoint_selection_config['cooldown_duration']
        
        # 更新成功率
        health['success_rate'] = health['successful_requests'] / health['total_requests']
        
        # 更新平均响应时间
        if response_time > 0:
            if health['avg_response_time'] == 0:
                health['avg_response_time'] = response_time
            else:
                # 使用指数移动平均
                health['avg_response_time'] = (health['avg_response_time'] * 0.7 + response_time * 0.3)
        
        # 更新权重
        health['weight'] = health['success_rate'] * 0.8 + (1 - min(health['avg_response_time'] / 5.0, 1)) * 0.2
    
    def generate_client_hints(self):
        """生成客户端提示（Client Hints）"""
        if not self.browser_fingerprints['client_hints_enabled']:
            return {}
        
        client_hints = {}
        
        # 主要客户端提示
        if random.random() < 0.8:  # 80%概率包含
            client_hints['Sec-CH-UA'] = f'"Chromium\";v="{random.randint(110, 120)}", "Not(A:Brand\";v="{random.randint(8, 24)}", "Google Chrome\";v="{random.randint(110, 120)}"'
        
        if random.random() < 0.7:  # 70%概率包含
            client_hints['Sec-CH-UA-Mobile'] = '?0'
        
        if random.random() < 0.6:  # 60%概率包含
            platform = random.choice(['"Windows"', '"macOS"', '"Linux"'])
            client_hints['Sec-CH-UA-Platform'] = platform
        
        if random.random() < 0.5:  # 50%概率包含
            client_hints['Sec-CH-UA-Platform-Version'] = f'"{random.randint(0, 15)}.0.0"'
        
        # 设备能力提示
        if random.random() < 0.4:  # 40%概率包含
            client_hints['Sec-CH-Viewport-Width'] = str(random.choice([1366, 1920, 1440, 1536]))
        
        if random.random() < 0.3:  # 30%概率包含
            client_hints['Sec-CH-Viewport-Height'] = str(random.choice([768, 1080, 900, 864]))
        
        if random.random() < 0.3:  # 30%概率包含
            client_hints['Sec-CH-DPR'] = str(round(random.uniform(1.0, 2.0), 1))
        
        if random.random() < 0.2:  # 20%概率包含
            client_hints['Sec-CH-Device-Memory'] = str(random.choice([4, 8, 16]))
        
        if random.random() < 0.2:  # 20%概率包含
            client_hints['Sec-CH-Prefers-Color-Scheme'] = random.choice(['light', 'dark'])
        
        return client_hints
    
    def get_random_headers(self, uid=None, endpoint_name=None, enable_fingerprint_randomization=True, endpoint='polymer', **kwargs):
        """获取随机化的请求头"""
        # 基础请求头
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
        
        # 添加更多真实的浏览器特征
        if random.random() < 0.8:  # 80%概率添加
            headers.update({
                'Upgrade-Insecure-Requests': '1',
                'Sec-CH-UA-Mobile': '?0',
                'Sec-CH-UA-Platform': random.choice(['"Windows"', '"macOS"', '"Linux"']),
            })
        
        # 随机添加一些可选的浏览器特征
        optional_features = {
            'Save-Data': lambda: random.choice(['on', 'off']),
            'Sec-GPC': lambda: '1' if random.random() < 0.3 else None,
            'Purpose': lambda: random.choice(['prefetch', '']) if random.random() < 0.2 else None,
            'Priority': lambda: random.choice(['u=0, i', 'u=1, i', 'u=2, i']) if random.random() < 0.4 else None,
        }
        
        for header, generator in optional_features.items():
            if random.random() < 0.3:  # 30%概率添加
                value = generator()
                if value:
                    headers[header] = value
        
        # 添加浏览器指纹随机化
        if enable_fingerprint_randomization:
            # 生成并添加各种指纹信息
            canvas_fp = self.generate_canvas_fingerprint()
            webgl_fp = self.generate_webgl_fingerprint()
            audio_fp = self.generate_audio_fingerprint()
            client_hints = self.generate_client_hints()
            
            # 添加客户端提示到headers
            headers.update(client_hints)
            
            # 添加其他指纹相关的headers
            viewport_size = random.choice(self.browser_fingerprints['viewport_sizes'])
            viewport_width, viewport_height = viewport_size.split('x')
            
            headers.update({
                'Viewport-Width': viewport_width,
                'Viewport-Height': viewport_height,
                'Device-Memory': str(random.choice(self.browser_fingerprints['device_memory'])),
                'Sec-CH-Viewport-Width': viewport_width,
                'Sec-CH-Viewport-Height': viewport_height,
                'Sec-CH-Device-Memory': str(random.choice(self.browser_fingerprints['device_memory'])),
                'Sec-CH-UA-Arch': random.choice(['"x86"', '"arm"']),
                'Sec-CH-UA-Bitness': '"64"',
                'Sec-CH-UA-Full-Version-List': f'"Chromium";v="{random.randint(110, 120)}", "Not(A:Brand";v="{random.randint(8, 24)}", "Google Chrome";v="{random.randint(110, 120)}"',
                'Sec-CH-UA-Wow64': '?0',
                'Sec-CH-Prefers-Color-Scheme': random.choice(['light', 'dark']),
                'Sec-CH-Prefers-Reduced-Motion': random.choice(['no-preference', 'reduce']),
            })
            
            # 随机移除一些headers来模拟不同的浏览器行为
            optional_headers = [
                'Sec-CH-UA-Arch', 'Sec-CH-UA-Bitness', 'Sec-CH-UA-Wow64',
                'Sec-CH-Prefers-Reduced-Motion', 'Sec-CH-Device-Memory'
            ]
            
            for header in optional_headers:
                if random.random() < 0.3:  # 30%概率移除
                    headers.pop(header, None)
        
        # 根据端点设置特定的头部
        if endpoint == 'polymer':
            headers.update({
                'Referer': f'https://www.bilibili.com/',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json;charset=UTF-8'
            })
            if uid:
                headers['Referer'] = f'https://space.bilibili.com/{uid}/dynamic'
        elif endpoint == 'vc':
            headers.update({
                'Referer': f'https://space.bilibili.com/',
                'X-Requested-With': 'XMLHttpRequest'
            })
            if uid:
                headers['Referer'] = f'https://space.bilibili.com/{uid}'
        elif endpoint == 'wbi':
            headers.update({
                'Referer': 'https://t.bilibili.com/',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Bili-Device': self.generate_bili_device_id(),
                'X-Bili-Device-Fingerprint': self.generate_bili_fingerprint()
            })
        
        return headers
    
    def generate_bili_device_id(self):
        """生成B站设备ID"""
        # 设备ID格式: 8位十六进制-4位十六进制-4位十六进制-4位十六进制-12位十六进制
        parts = [
            ''.join(random.choices('0123456789abcdef', k=8)),
            ''.join(random.choices('0123456789abcdef', k=4)),
            ''.join(random.choices('0123456789abcdef', k=4)),
            ''.join(random.choices('0123456789abcdef', k=4)),
            ''.join(random.choices('0123456789abcdef', k=12))
        ]
        return '-'.join(parts)
    
    def generate_bili_fingerprint(self):
        """生成B站设备指纹"""
        # 基于时间戳和随机数生成指纹
        timestamp = str(int(time.time() * 1000))
        random_part = ''.join(random.choices('0123456789abcdef', k=16))
        fingerprint_data = f"{timestamp}_{random_part}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()

    def simulate_mouse_movement(self, start_x=0, start_y=0, target_x=800, target_y=600):
        """模拟鼠标移动轨迹"""
        # 生成贝塞尔曲线轨迹
        steps = random.randint(15, 30)  # 移动步数
        trajectory = []
        
        # 添加一些随机控制点
        control_points = [
            (random.randint(0, 1200), random.randint(0, 800)),
            (random.randint(0, 1200), random.randint(0, 800))
        ]
        
        # 生成贝塞尔曲线
        for i in range(steps + 1):
            t = i / steps
            
            # 三次贝塞尔曲线公式
            x = (1-t)**3 * start_x + 3*(1-t)**2 * t * control_points[0][0] + 3*(1-t) * t**2 * control_points[1][0] + t**3 * target_x
            y = (1-t)**3 * start_y + 3*(1-t)**2 * t * control_points[0][1] + 3*(1-t) * t**2 * control_points[1][1] + t**3 * target_y
            
            # 添加随机抖动
            x += random.uniform(-2, 2)
            y += random.uniform(-2, 2)
            
            trajectory.append({
                'x': int(x),
                'y': int(y),
                'timestamp': time.time() + (i * random.uniform(0.01, 0.05))  # 每步间隔10-50ms
            })
        
        return trajectory
    
    def simulate_mouse_clicks(self, element_x, element_y, num_clicks=1):
        """模拟鼠标点击行为"""
        clicks = []
        
        for i in range(num_clicks):
            # 添加随机偏移
            click_x = element_x + random.randint(-3, 3)
            click_y = element_y + random.randint(-3, 3)
            
            # 模拟人类点击的微小延迟
            click_delay = random.uniform(0.08, 0.25)  # 80-250ms的点击延迟
            
            clicks.append({
                'x': click_x,
                'y': click_y,
                'timestamp': time.time() + (i * click_delay),
                'button': random.choice(['left', 'left', 'left', 'right']),  # 90%左键
                'delay': click_delay
            })
        
        return clicks
    
    def simulate_page_stay_time(self, min_time=2, max_time=15):
        """模拟页面停留时间"""
        # 基于页面内容复杂度调整停留时间
        base_time = random.uniform(min_time, max_time)
        
        # 添加一些随机因素
        complexity_factor = random.uniform(0.8, 1.5)  # 内容复杂度因子
        reading_speed_factor = random.uniform(0.7, 1.3)  # 阅读速度因子
        
        stay_time = base_time * complexity_factor * reading_speed_factor
        
        return max(min_time, min(stay_time, max_time))  # 确保在合理范围内
    
    def simulate_scroll_behavior(self, start_y=0, end_y=800):
        """模拟滚动行为"""
        scrolls = []
        current_y = start_y
        
        # 模拟人类滚动模式：快速滚动 + 缓慢调整
        scroll_phases = [
            {'type': 'fast', 'speed': random.randint(200, 400), 'duration': random.uniform(0.5, 1.5)},
            {'type': 'slow', 'speed': random.randint(50, 150), 'duration': random.uniform(1.0, 3.0)},
            {'type': 'micro', 'speed': random.randint(10, 50), 'duration': random.uniform(0.3, 1.0)}
        ]
        
        for phase in scroll_phases:
            phase_start_time = time.time()
            phase_duration = phase['duration']
            
            while time.time() - phase_start_time < phase_duration and current_y < end_y:
                # 添加随机性
                actual_speed = phase['speed'] * random.uniform(0.8, 1.2)
                
                scrolls.append({
                    'y': int(current_y),
                    'delta_y': int(actual_speed * 0.1),  # 假设100ms间隔
                    'timestamp': time.time(),
                    'type': phase['type'],
                    'speed': actual_speed
                })
                
                current_y += actual_speed * 0.1
                time.sleep(0.1)  # 模拟滚动间隔
        
        return scrolls
    
    def simulate_keyboard_input(self, text):
        """模拟键盘输入行为"""
        keystrokes = []
        
        for i, char in enumerate(text):
            # 模拟打字速度变化
            if i == 0:
                # 第一个字符通常更快
                delay = random.uniform(0.05, 0.15)
            elif char == ' ':
                # 空格通常更快
                delay = random.uniform(0.08, 0.18)
            elif char in '.!?':
                # 标点符号后有较长停顿
                delay = random.uniform(0.3, 0.8)
            else:
                # 普通字符
                delay = random.uniform(0.08, 0.25)
            
            # 偶尔添加打字错误和修正
            if random.random() < 0.02:  # 2%概率打字错误
                # 添加错误字符
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                keystrokes.append({
                    'char': wrong_char,
                    'timestamp': time.time() + sum(k['delay'] for k in keystrokes),
                    'delay': delay,
                    'type': 'error'
                })
                
                # 添加退格键
                backspace_delay = random.uniform(0.1, 0.3)
                keystrokes.append({
                    'char': 'BACKSPACE',
                    'timestamp': time.time() + sum(k['delay'] for k in keystrokes) + backspace_delay,
                    'delay': backspace_delay,
                    'type': 'backspace'
                })
                
                # 重新输入正确字符
                correct_delay = random.uniform(0.08, 0.2)
                keystrokes.append({
                    'char': char,
                    'timestamp': time.time() + sum(k['delay'] for k in keystrokes) + correct_delay,
                    'delay': correct_delay,
                    'type': 'correct'
                })
            else:
                keystrokes.append({
                    'char': char,
                    'timestamp': time.time() + sum(k['delay'] for k in keystrokes),
                    'delay': delay,
                    'type': 'normal'
                })
        
        return keystrokes
    
    def generate_human_timing_data(self, action_type='page_load'):
        """生成人类行为时间数据"""
        timing_data = {
            'action_type': action_type,
            'timestamp': time.time(),
            'timezone_offset': random.choice([-480, -540, -600]),  # 中国时区相关
            'performance_timing': {}
        }
        
        if action_type == 'page_load':
            # 模拟页面加载时间线
            navigation_start = 0
            redirect_time = random.uniform(0, 0.5)
            dns_time = random.uniform(0.01, 0.3)
            tcp_time = random.uniform(0.05, 0.2)
            ssl_time = random.uniform(0.1, 0.5)
            request_time = random.uniform(0.1, 0.8)
            response_time = random.uniform(0.2, 1.5)
            dom_processing = random.uniform(0.3, 2.0)
            load_complete = random.uniform(0.5, 3.0)
            
            timing_data['performance_timing'] = {
                'navigationStart': navigation_start,
                'redirectStart': navigation_start,
                'redirectEnd': navigation_start + redirect_time,
                'fetchStart': navigation_start + redirect_time,
                'domainLookupStart': navigation_start + redirect_time,
                'domainLookupEnd': navigation_start + redirect_time + dns_time,
                'connectStart': navigation_start + redirect_time + dns_time,
                'connectEnd': navigation_start + redirect_time + dns_time + tcp_time + ssl_time,
                'secureConnectionStart': navigation_start + redirect_time + dns_time + tcp_time,
                'requestStart': navigation_start + redirect_time + dns_time + tcp_time + ssl_time,
                'responseStart': navigation_start + redirect_time + dns_time + tcp_time + ssl_time + request_time,
                'responseEnd': navigation_start + redirect_time + dns_time + tcp_time + ssl_time + request_time + response_time,
                'domLoading': navigation_start + redirect_time + dns_time + tcp_time + ssl_time + request_time + response_time,
                'domInteractive': navigation_start + redirect_time + dns_time + tcp_time + ssl_time + request_time + response_time + dom_processing * 0.3,
                'domContentLoadedEventStart': navigation_start + redirect_time + dns_time + tcp_time + ssl_time + request_time + response_time + dom_processing * 0.7,
                'domContentLoadedEventEnd': navigation_start + redirect_time + dns_time + tcp_time + ssl_time + request_time + response_time + dom_processing * 0.8,
                'domComplete': navigation_start + redirect_time + dns_time + tcp_time + ssl_time + request_time + response_time + dom_processing,
                'loadEventStart': navigation_start + redirect_time + dns_time + tcp_time + ssl_time + request_time + response_time + dom_processing + load_complete * 0.9,
                'loadEventEnd': navigation_start + redirect_time + dns_time + tcp_time + ssl_time + request_time + response_time + dom_processing + load_complete
            }
        
        elif action_type == 'ajax_request':
            # 模拟AJAX请求时间
            timing_data['performance_timing'] = {
                'start_time': time.time(),
                'dns_lookup': random.uniform(0.01, 0.1),
                'tcp_connect': random.uniform(0.05, 0.15),
                'ssl_handshake': random.uniform(0.08, 0.3),
                'request_send': random.uniform(0.02, 0.08),
                'wait_time': random.uniform(0.1, 0.8),
                'response_receive': random.uniform(0.05, 0.3),
                'total_time': random.uniform(0.3, 1.5)
            }
        
        return timing_data
    
    def log_request_start(self, url, headers, cookies):
        """记录请求开始"""
        pass
    
    def log_request_end(self, url, success, data=None, error=None, duration=0):
        """记录请求结束"""
        pass
    
    def log_rate_limit_detected(self, data, attempt=None, proxy_info=None):
        """记录风控检测"""
        pass
    
    def setup_logger(self, log_level='INFO', enable_console=True, log_file=None):
        """设置日志器"""
        self.log_level = log_level
        self.enable_console_log = enable_console
        self.log_file = log_file
        
        # 简单的日志设置，实际项目中可以使用logging模块
        if enable_console:
            print(f"[INFO] 日志系统已初始化，级别: {log_level}")
    
    def log_message(self, level, message):
        """记录日志消息"""
        print(f"[{level}] {message}")
    
    def log_proxy_usage(self, proxy, success=True, duration=0, error=None):
        """记录代理使用情况"""
        pass
    
    def check_rate_limit(self):
        """增强版限流检查 - 使用机器学习预测和动态调整"""
        current_time = time.time()
        
        # 清理过期的请求记录（超过1小时）
        cutoff_time = current_time - 3600
        self.rate_limiter['request_times'] = [
            req_time for req_time in self.rate_limiter['request_times'] 
            if req_time > cutoff_time
        ]
        
        # 智能时间窗口分析 - 检测异常模式
        time_patterns = self._analyze_request_patterns(current_time)
        
        # 检查每分钟限制（带预测）
        recent_minute_requests = [
            req_time for req_time in self.rate_limiter['request_times']
            if req_time > current_time - 60
        ]
        
        # 预测下一分钟的请求数
        predicted_requests = self._predict_next_minute_requests(len(recent_minute_requests))
        if predicted_requests >= self.rate_limiter['max_requests_per_minute'] * 0.9:  # 90%阈值
            return True, f"预测超限 - 预计{predicted_requests}次/分钟 (上限{self.rate_limiter['max_requests_per_minute']})"
        
        if len(recent_minute_requests) >= self.rate_limiter['max_requests_per_minute']:
            return True, f"每分钟请求数超限 ({len(recent_minute_requests)}/{self.rate_limiter['max_requests_per_minute']})"
        
        # 检查每小时限制（带自适应调整）
        recent_hour_requests = [
            req_time for req_time in self.rate_limiter['request_times']
            if req_time > current_time - 3600
        ]
        
        # 根据成功率动态调整小时限制阈值
        dynamic_hourly_threshold = self._calculate_dynamic_threshold('hourly', len(recent_hour_requests))
        if len(recent_hour_requests) >= dynamic_hourly_threshold:
            return True, f"每小时请求数超限 ({len(recent_hour_requests)}/{dynamic_hourly_threshold})"
        
        # 检查最小请求间隔（基于端点健康状态）
        if self.rate_limiter['request_times']:
            last_request_time = max(self.rate_limiter['request_times'])
            time_since_last = current_time - last_request_time
            
            # 动态最小间隔 - 基于最近成功率
            dynamic_min_interval = self._calculate_dynamic_min_interval()
            
            if time_since_last < dynamic_min_interval:
                return True, f"请求间隔过短 ({time_since_last:.1f}s < {dynamic_min_interval:.1f}s)"
        
        # 增强版突发请求检测
        burst_result = self._check_enhanced_burst_patterns(current_time)
        if burst_result[0]:
            return burst_result
        
        # 基于机器学习的风险评分
        risk_score = self._calculate_ml_risk_score(current_time)
        if risk_score > 0.8:  # 高风险
            return True, f"机器学习风险评分过高 ({risk_score:.2f})"
        
        return False, ""
    
    def get_request_stats(self):
        """获取请求统计信息"""
        success_rate = 0
        if self.request_stats['total_requests'] > 0:
            success_rate = (self.request_stats['successful_requests'] / self.request_stats['total_requests']) * 100
        
        return {
            'total_requests': self.request_stats['total_requests'],
            'successful_requests': self.request_stats['successful_requests'],
            'failed_requests': self.request_stats['failed_requests'],
            'rate_limited_requests': self.request_stats['rate_limited_requests'],
            'success_rate': f"{success_rate:.1f}%",
            'last_successful_endpoint': self.request_stats['last_successful_endpoint']
        }
    
    def get_endpoint_health_report(self):
        """获取端点健康报告"""
        report = {}
        for endpoint, health in self.endpoint_health.items():
            report[endpoint] = {
                'success_rate': f"{health['success_rate']:.1%}",
                'avg_response_time': f"{health['avg_response_time']:.1f}s",
                'total_requests': health['total_requests'],
                'successful_requests': health['successful_requests'],
                'consecutive_failures': health['consecutive_failures'],
                'priority': health['priority'],
                'weight': f"{health['weight']:.2f}",
                'is_available': self.is_endpoint_available(endpoint),
                'cooldown_remaining': max(0, health['cooldown_until'] - time.time())
            }
        
        return report
    
    def generate_stealth_headers(self, uid=None, endpoint_name=None):
        """生成隐身模式请求头"""
        # 获取基础随机头
        headers = self.get_random_headers(uid, endpoint_name, enable_fingerprint_randomization=True)
        
        # 添加额外的隐身头
        stealth_headers = {
            # 模拟真实的浏览器行为
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
            'Sec-Fetch-Mode': random.choice(['navigate', 'cors']),
            'Sec-Fetch-Dest': random.choice(['document', 'empty']),
            
            # 添加缓存控制
            'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
            'Pragma': 'no-cache',
            
            # 添加接受编码的变体
            'Accept-Encoding': random.choice(['gzip, deflate, br', 'gzip, deflate', 'br']),
            
            # 添加时间相关的头
            'Date': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()),
            
            # 添加安全相关的头
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': random.choice(['DENY', 'SAMEORIGIN']),
            'X-XSS-Protection': '1; mode=block'
        }
        
        # 随机选择添加一些隐身头
        for header, value in stealth_headers.items():
            if random.random() < 0.3:  # 30%概率添加每个隐身头
                headers[header] = value
        
        # 随机移除一些标准头以模拟不同的浏览器
        removable_headers = [
            'DNT', 'Sec-Fetch-Dest', 'Sec-Fetch-Mode', 'Sec-Fetch-Site'
        ]
        
        for header in removable_headers:
            if random.random() < 0.2:  # 20%概率移除
                headers.pop(header, None)
        
        return headers

    def _get_recent_success_rate(self, window_minutes=30):
        """获取最近的成功率"""
        current_time = time.time()
        window_start = current_time - window_minutes * 60
        
        # 获取窗口内的请求统计
        recent_total = 0
        recent_success = 0
        
        # 基于端点健康状态估算最近成功率
        for endpoint, health in self.endpoint_health.items():
            if health['total_requests'] > 0:
                # 假设最近请求分布与总体分布相似
                recent_total += health['total_requests']
                recent_success += health['successful_requests']
        
        if recent_total > 0:
            return recent_success / recent_total
        
        # 如果没有数据，返回总体成功率
        if self.request_stats['total_requests'] > 0:
            return self.request_stats['successful_requests'] / self.request_stats['total_requests']
        
        return 1.0  # 默认高成功率

    def is_rate_limited(self, data):
        """检查是否触发限流
        
        Args:
            data: API响应数据
            
        Returns:
            bool: 是否触发限流
        """
        if not data or not isinstance(data, dict):
            return False
            
        # 检查常见的限流响应代码
        code = data.get('code', -1)
        message = data.get('message', '').lower()
        
        # 常见的限流代码
        rate_limit_codes = [-403, -429, 429, 403, -509, 509]
        
        # 常见的限流关键词
        rate_limit_keywords = [
            'rate limit', 'too many requests', '请求过于频繁', 
            '访问过于频繁', '请稍后再试', '系统繁忙', '操作太快',
            'frequency', 'limit', 'throttle', 'block'
        ]
        
        if code in rate_limit_codes:
            return True
            
        for keyword in rate_limit_keywords:
            if keyword in message:
                return True
                
        return False

    def select_proxy(self):
        """选择代理IP - 优化版本，添加健康检查
        
        Returns:
            dict or None: 代理配置或None
        """
        if not self.proxy_pools:
            return None
        
        # 代理健康检查（简单版本）
        healthy_proxies = []
        for proxy in self.proxy_pools:
            if self.is_proxy_healthy(proxy):
                healthy_proxies.append(proxy)
        
        # 优先选择健康代理，如果没有则随机选择
        if healthy_proxies:
            selected_proxy = random.choice(healthy_proxies)
            self.log_message('INFO', f'选择健康代理: {selected_proxy}')
        else:
            selected_proxy = random.choice(self.proxy_pools)
            self.log_message('WARNING', f'没有健康代理，随机选择: {selected_proxy}')
        
        return selected_proxy
    
    def is_proxy_healthy(self, proxy):
        """检查代理是否健康
        
        Args:
            proxy: 代理配置
            
        Returns:
            bool: 代理是否健康
        """
        try:
            # 简单的健康检查：尝试连接一个稳定的服务
            test_url = 'https://httpbin.org/ip'
            response = requests.get(
                test_url,
                proxies=proxy,
                timeout=5,
                verify=True
            )
            
            # 检查响应状态
            if response.status_code == 200:
                self.log_message('INFO', f'代理健康检查通过: {proxy}')
                return True
            else:
                self.log_message('WARNING', f'代理健康检查失败: {proxy}, 状态码: {response.status_code}')
                return False
                
        except Exception as e:
            self.log_message('ERROR', f'代理健康检查异常: {proxy}, 错误: {str(e)}')
            return False

    def get_proxy_stats(self):
        """获取代理统计信息
        
        Returns:
            dict: 代理统计信息
        """
        total = self.proxy_stats['total_proxy_requests']
        success = self.proxy_stats['successful_proxy_requests']
        failed = self.proxy_stats['failed_proxy_requests']
        
        success_rate = (success / total * 100) if total > 0 else 0
        
        return {
            'total_proxy_requests': total,
            'successful_proxy_requests': success,
            'failed_proxy_requests': failed,
            'proxy_success_rate': f"{success_rate:.1f}%",
            'proxy_rotation_enabled': self.proxy_rotation_enabled
        }

    def enable_proxy_rotation(self, enabled=True):
        """启用代理轮换
        
        Args:
            enabled: 是否启用
        """
        self.proxy_rotation_enabled = enabled
        self.log_message('INFO', f"代理轮换已{'启用' if enabled else '禁用'}")

    @property
    def endpoints(self):
        """获取端点列表"""
        return list(self.endpoint_health.keys())

    def get_stats(self):
        """获取统计信息
        
        Returns:
            dict: 统计信息
        """
        total = self.request_stats['total_requests']
        success = self.request_stats['successful_requests']
        failed = self.request_stats['failed_requests']
        rate_limited = self.request_stats['rate_limited_requests']
        
        success_rate = f"{(success / total * 100):.1f}%" if total > 0 else "0%"
        last_endpoint = self.request_stats['last_successful_endpoint']
        
        return {
            'total_requests': total,
            'successful_requests': success,
            'failed_requests': failed,
            'rate_limited_requests': rate_limited,
            'success_rate': success_rate,
            'last_successful_endpoint': last_endpoint
        }

    def make_request_with_bypass(self, url, headers=None, cookies=None, method='GET', data=None, params=None, timeout=30, max_retries=None):
        """使用风控绕过策略发送请求 - 优化版本
        
        Args:
            url: 请求URL
            headers: 请求头
            cookies: Cookie
            method: 请求方法
            data: POST数据
            params: URL参数
            timeout: 超时时间
            max_retries: 最大重试次数（已废弃，只尝试一次）
            
        Returns:
            dict: 响应数据
        """
        if max_retries is None:
            max_retries = self.retry_config['max_retries']
            
        # 忽略max_retries参数，只尝试一次
        # 优化版本，添加行为随机化
        
        # 模拟人类行为延迟
        self.simulate_human_delay()
        
        # 模拟鼠标行为（生成但不实际执行，用于日志记录）
        mouse_trajectory = self.simulate_mouse_movement(
            start_x=random.randint(0, 200),
            start_y=random.randint(0, 200),
            target_x=random.randint(600, 1000),
            target_y=random.randint(400, 800)
        )
        
        # 模拟页面停留时间
        stay_time = self.simulate_page_stay_time(min_time=1, max_time=8)
        self.log_message('INFO', f'模拟页面停留时间: {stay_time:.1f}秒')
        
        # 模拟滚动行为（生成但不实际执行）
        scroll_behavior = self.simulate_scroll_behavior(
            start_y=random.randint(0, 100),
            end_y=random.randint(500, 1200)
        )
        
        # 确保有请求头
        if headers is None:
            headers = self.get_random_headers()
            
        # 确保有Cookie
        if cookies is None:
            cookies = self.generate_random_cookie()
            
        # 添加Cookie到请求头
        if cookies and isinstance(cookies, dict):
            cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            headers['Cookie'] = cookie_str
        elif isinstance(cookies, str):
            headers['Cookie'] = cookies
            
        # 选择代理
        proxy = self.select_proxy() if self.proxy_rotation_enabled else None
        
        # 执行请求 - 优化版本，添加行为模拟
        try:
            # 限流检查（已简化，不再实际限流）
            self._apply_rate_limit()
            
            # 发送请求
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                timeout=timeout,
                proxies=proxy,
                verify=True
            )
            
            # 更新统计信息
            self.request_stats['total_requests'] += 1
            
            # 检查响应状态
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    # 检查是否触发限流
                    if self.is_rate_limited(response_data):
                        self.request_stats['rate_limited_requests'] += 1
                        self.log_message('WARNING', f"请求触发限流: {url}")
                        return {'code': -1, 'message': '请求触发限流', 'data': None}
                    
                    # 成功请求
                    self.request_stats['successful_requests'] += 1
                    self.log_message('INFO', f"请求成功: {url}")
                    return response_data
                    
                except json.JSONDecodeError:
                    self.log_message('ERROR', f"响应解析失败: {url}")
                    self.request_stats['failed_requests'] += 1
                    return {'code': -1, 'message': '响应解析失败', 'data': None}
                    
            else:
                self.log_message('WARNING', f"HTTP错误 {response.status_code}: {url}")
                self.request_stats['failed_requests'] += 1
                return {'code': -1, 'message': f'HTTP错误 {response.status_code}', 'data': None}
                
        except requests.exceptions.RequestException as e:
            self.log_message('ERROR', f"请求异常: {str(e)}")
            self.request_stats['failed_requests'] += 1
            return {'code': -1, 'message': f'请求异常: {str(e)}', 'data': None}

    def simulate_human_delay(self):
        """模拟人类行为延迟"""
        # 基础延迟范围（模拟人类操作间隔）
        base_delay = random.uniform(0.5, 2.5)
        
        # 添加随机波动
        random_factor = random.uniform(0.8, 1.3)
        
        # 考虑操作复杂度（简单的操作延迟短，复杂的操作延迟长）
        complexity_factor = random.uniform(0.7, 1.5)
        
        # 计算最终延迟
        final_delay = base_delay * random_factor * complexity_factor
        
        # 确保延迟在合理范围内
        final_delay = max(0.3, min(final_delay, 5.0))
        
        self.log_message('INFO', f'模拟人类行为延迟: {final_delay:.2f}秒')
        time.sleep(final_delay)
    
    def _apply_rate_limit(self):
        """应用限流控制 - 简化版本，不再进行限流检查"""
        pass  # 不再进行限流控制，由系统定时任务管理频率

    def _calculate_retry_delay(self, attempt):
        """计算重试延迟时间 - 简化版本
        
        Args:
            attempt: 当前重试次数
            
        Returns:
            float: 延迟时间（秒）
        """
        return 0.0  # 不再进行延迟，由系统定时任务控制频率

    def log_system_stats(self):
        """记录系统统计信息"""
        stats = self.get_stats()
        self.log_message('INFO', "=== 系统统计信息 ===")
        self.log_message('INFO', f"总请求数: {stats['total_requests']}")
        self.log_message('INFO', f"成功请求数: {stats['successful_requests']}")
        self.log_message('INFO', f"失败请求数: {stats['failed_requests']}")
        self.log_message('INFO', f"限流请求数: {stats['rate_limited_requests']}")
        self.log_message('INFO', f"成功率: {stats['success_rate']}")
        self.log_message('INFO', f"最后成功端点: {stats['last_successful_endpoint']}")
        
        # 记录端点统计
        self.log_message('INFO', "=== 端点统计 ===")
        for endpoint, health in self.endpoint_health.items():
            self.log_message('INFO', f"端点 {endpoint}: 成功率={health['success_rate']:.1%}, "
                                   f"响应时间={health['avg_response_time']:.2f}s, "
                                   f"总请求={health['total_requests']}, "
                                   f"成功请求={health['successful_requests']}")
        
        # 记录代理统计
        proxy_stats = self.get_proxy_stats()
        self.log_message('INFO', "=== 代理统计 ===")
        self.log_message('INFO', f"代理请求总数: {proxy_stats['total_proxy_requests']}")
        self.log_message('INFO', f"代理成功请求: {proxy_stats['successful_proxy_requests']}")
        self.log_message('INFO', f"代理失败请求: {proxy_stats['failed_proxy_requests']}")
        self.log_message('INFO', f"代理成功率: {proxy_stats['proxy_success_rate']}")
        self.log_message('INFO', f"代理轮换状态: {'启用' if proxy_stats['proxy_rotation_enabled'] else '禁用'}")