import json
import time
import random
import requests
import gzip
from api_bypass import APIRestrictionBypass
from latest_dynamic_storage import storage as dynamic_storage
from datetime import datetime
from config import TEST_MODE
from push_notification import send_wechat_notification

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
                    
                    # 🔍 增强调试：打印响应数据的前500字符
                    if data:
                        bypass.log_message('DEBUG', "API响应数据预览: {}".format(json.dumps(data, ensure_ascii=False)[:500]))
                    
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

def get_up_latest_video(uid=None, up_name=None):
    """获取UP主最新视频投稿"""
    if not uid:
        uid = "22376577"
    if not up_name:
        up_name = "牛奶糖好吃"
    
    bypass = APIRestrictionBypass()
    bypass.setup_logger(log_level='DEBUG', enable_console=True)
    
    bypass.log_message('INFO', "=== 获取UP主 {} 最新视频 ===".format(up_name))
    bypass.log_message('INFO', "用户UID: {}".format(uid))
    
    # 使用视频搜索API获取最新视频
    search_url = f"https://api.bilibili.com/x/space/arc/search?mid={uid}&ps=30&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp"
    
    # 添加随机延迟，避免请求过于频繁
    time.sleep(random.uniform(1.0, 3.0))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': f'https://space.bilibili.com/{uid}/video',
        'Origin': 'https://space.bilibili.com',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    # 添加随机cookie来降低风控
    random_cookie = bypass.generate_random_cookie()
    cookie_str = '; '.join([f'{k}={v}' for k, v in random_cookie.items() if v])
    if cookie_str:
        headers['Cookie'] = cookie_str
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        bypass.log_message('INFO', f"视频搜索API状态码: {response.status_code}")
        
        data = response.json()
        bypass.log_message('INFO', f"视频搜索API返回code: {data.get('code', 'unknown')}")
        
        # 处理API频率限制
        if data.get('code') == -799:
            bypass.log_message('WARNING', f"视频搜索API频率限制: {data.get('message', '请求过于频繁')}")
            return f"视频搜索API频率限制: code=-799"
        elif data.get('code') == -352:
            bypass.log_message('WARNING', f"视频搜索API风控校验失败: {data.get('message', '风控校验失败')}")
            return f"视频搜索API风控校验失败: code=-352"
        elif data.get('code') == 0:
            vlist = data.get('data', {}).get('list', {}).get('vlist', [])
            bypass.log_message('INFO', f"获取到 {len(vlist)} 个视频")
            
            if vlist:
                # 获取最新视频
                latest_video = vlist[0]
                
                title = latest_video.get('title', '')
                aid = latest_video.get('aid', '')
                bvid = latest_video.get('bvid', '')
                created = latest_video.get('created', 0)
                length = latest_video.get('length', '')
                pic = latest_video.get('pic', '')
                description = latest_video.get('description', '')
                
                bypass.log_message('INFO', f"最新视频标题: {title}")
                bypass.log_message('INFO', f"AV号: {aid}")
                bypass.log_message('INFO', f"BV号: {bvid}")
                bypass.log_message('INFO', f"时长: {length}")
                bypass.log_message('INFO', f"封面: {pic}")
                
                # 转换时间
                create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created))
                bypass.log_message('INFO', f"发布时间: {create_time}")
                
                # 检查时间是否在阈值内（30分钟）
                current_time = int(time.time())
                time_diff_minutes = (current_time - created) // 60
                bypass.log_message('INFO', f"距现在: {time_diff_minutes} 分钟")
                
                # 使用动态ID对比判断是否为新视频
                is_new_video = dynamic_storage.is_new_dynamic(uid, bvid)
                if is_new_video:
                    
                    # 构建视频URL
                    video_url = f"https://www.bilibili.com/video/{bvid}"
                    
                    # 构建推送内容
                    content = f"【{title}】\n视频AV号: {aid}\n发布时间: {create_time}\n时长: {length}\n视频链接: {video_url}"
                    
                    if TEST_MODE:
                        bypass.log_message('INFO', f"[测试模式] 准备推送视频: {content}")
                        return f"测试模式：找到{time_diff_minutes}分钟前的视频({title})，消息发送已屏蔽"
                    else:
                        # 构建视频信息
                        video_info = {
                            'dynamic_id': bvid,  # 使用BV号作为ID
                            'content': title,
                            'content_type': '视频投稿',
                            'timestamp': created,
                            'url': video_url,
                            'pics': [pic] if pic else [],
                            'like': 0,
                            'reply': 0,
                            'forward': 0,
                            'description': description,
                            'length': length,
                            'aid': aid,
                            'bvid': bvid
                        }
                        
                        success = send_wechat_notification(up_name, video_info)
                        if success:
                            return f"成功推送{time_diff_minutes}分钟前的视频: {title}"
                        else:
                            return f"推送失败：{time_diff_minutes}分钟前的视频: {title}"
                else:
                    bypass.log_message('INFO', f"视频已推送过，不重复推送")
                    return f"视频已推送过，不重复推送"
            else:
                bypass.log_message('INFO', "未获取到视频列表")
                return None
        else:
            bypass.log_message('WARNING', f"视频搜索API返回错误: {data.get('message', '未知错误')}")
            return f"视频搜索API返回错误: code={data.get('code')}"
            
    except Exception as e:
        bypass.log_message('ERROR', f"视频搜索API请求失败: {e}")
        return f"视频搜索API请求失败: {e}"

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
    
    # 首先尝试获取最新视频
    bypass.log_message('INFO', "首先尝试获取最新视频投稿...")
    video_result = get_up_latest_video(uid, up_name)
    
    # 如果视频获取成功且在时间范围内，直接返回
    if "成功推送" in video_result:
        return video_result
    
    # 如果视频API被频率限制，记录但继续获取动态
    video_api_limited = False
    if "频率限制" in video_result or "风控" in video_result:
        bypass.log_message('WARNING', f"视频API受限: {video_result}，尝试从动态数据获取视频信息...")
        video_api_limited = True
    else:
        bypass.log_message('INFO', "视频检查完成，继续获取动态...")
    
    bypass.log_message('INFO', f"视频结果: {video_result}")
    
    # 使用新的get_user_dynamics函数获取数据
    data = get_user_dynamics(uid, real_cookies, use_bypass=True)
    
    if not data:
        bypass.log_message('ERROR', "获取动态失败")
        return None
    
    # 解析polymer API返回的数据
    try:
        bypass.log_message('INFO', "正在解析polymer API数据...")
        
        # 🔍 增强调试：打印完整的API响应结构
        bypass.log_message('DEBUG', "polymer API完整响应: {}".format(json.dumps(data, ensure_ascii=False, indent=2)[:500]))
        
        # 检查多种可能的数据结构
        items = []
        if 'data' in data and isinstance(data['data'], dict):
            # 尝试不同的items路径
            items = data['data'].get('items', [])
            if not items:
                # 尝试其他可能的路径
                items = data['data'].get('list', [])
            if not items:
                # 尝试cards路径（兼容旧格式）
                items = data['data'].get('cards', [])
        elif 'data' in data and isinstance(data['data'], list):
            # 如果data本身就是列表
            items = data['data']
        
        # 确保items是列表类型
        if items is None:
            items = []
        
        bypass.log_message('INFO', "polymer API获取到 {} 条动态".format(len(items) if items else 0))
        
        # 如果items为空，尝试其他数据结构
        if not items and 'data' in data:
            bypass.log_message('WARNING', "polymer API items为空，尝试其他数据结构...")
            # 打印data结构以便调试
            data_content = data.get('data')
            bypass.log_message('DEBUG', "data结构: {}".format(type(data_content)))
            if isinstance(data_content, dict):
                bypass.log_message('DEBUG', "data键值: {}".format(list(data_content.keys()) if data_content else []))
        
        # 检查响应码
        code = data.get('code', -1)
        bypass.log_message('INFO', "polymer API返回code: {}".format(code))
        
        if code == -352:
            bypass.log_message('WARNING', "polymer API返回风控错误code=-352")
            # 尝试获取风控信息
            if 'data' in data and isinstance(data['data'], dict):
                if 'v_voucher' in data['data']:
                    bypass.log_message('WARNING', "风控信息v_voucher: {}".format(data['data']['v_voucher']))
            return None
        elif code == 0:
            bypass.log_message('INFO', "polymer API返回成功")
            
            # 如果仍然没有items，尝试更深层的解析
            if not items:
                bypass.log_message('WARNING', "polymer API返回成功但items为空，尝试备用解析...")
                # 尝试直接从data中获取可能的动态数据
                data_content = data.get('data', {})
                if isinstance(data_content, dict) and data_content:
                    # 检查是否有其他包含动态数据的字段
                    for key, value in data_content.items():
                        if isinstance(value, list) and value and len(value) > 0:
                            bypass.log_message('INFO', "发现潜在动态数据在字段 '{}': {} 项".format(key, len(value)))
                            # 检查第一项是否像动态数据
                            if isinstance(value[0], dict):
                                bypass.log_message('DEBUG', "第一项结构: {}".format(list(value[0].keys()) if value[0] else []))
                            items = value
                            break
            
            if items:
                bypass.log_message('INFO', "=== 详细分析最新动态 ===")
                
                # 🔧 修复：获取前两条动态，比较时间戳，选择真正最新的动态
                target_dynamic = None
                
                if len(items) >= 2:
                    # 获取前两条动态进行比较
                    first_item = items[0]  # 可能是置顶动态
                    second_item = items[1]  # 可能是真正的最新动态
                    
                    # 获取两条动态的时间戳
                    first_ts = first_item.get('modules', {}).get('module_author', {}).get('pub_ts', 0)
                    second_ts = second_item.get('modules', {}).get('module_author', {}).get('pub_ts', 0)
                    
                    bypass.log_message('INFO', "比较两条动态的时间戳:")
                    bypass.log_message('INFO', "  第一条动态时间戳: {} ({}))".format(first_ts, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(first_ts)) if first_ts else '未知'))
                    bypass.log_message('INFO', "  第二条动态时间戳: {} ({}))".format(second_ts, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(second_ts)) if second_ts else '未知'))
                    
                    # 选择时间更新的动态（时间戳更大的表示更新的动态）
                    if second_ts > first_ts:
                        latest_item = second_item
                        bypass.log_message('INFO', "✅ 选择第二条动态作为最新动态（时间更新）")
                    else:
                        latest_item = first_item
                        bypass.log_message('INFO', "✅ 选择第一条动态作为最新动态")
                else:
                    # 只有一条动态，直接使用
                    latest_item = items[0]
                    bypass.log_message('INFO', "📝 只有一条动态，直接使用")
                
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
                    if major_info and isinstance(major_info, dict):
                        # 2.1 视频内容（archive）- 优先处理视频动态
                        if 'archive' in major_info:
                            archive = major_info['archive']
                            if archive and isinstance(archive, dict):
                                title = archive.get('title', '')
                                if title and title.strip():
                                    text_content = title.strip()
                                    bypass.log_message('INFO', "  从archive提取视频标题: '{}'".format(text_content))
                        
                        # 2.2 图文内容（draw）- 关键修复区域
                        if not text_content.strip() and 'draw' in major_info:
                            draw = major_info['draw']
                            if isinstance(draw, dict):
                                # 检查draw中的文本内容
                                draw_text = draw.get('text', '')
                                if draw_text and draw_text.strip():
                                    text_content = draw_text.strip()
                                    bypass.log_message('INFO', "  从draw提取文本: '{}'".format(text_content))
                                else:
                                    # 检查图片数量信息
                                    items = draw.get('items', [])
                                    if items and isinstance(items, list):
                                        img_count = len(items)
                                        if img_count > 0:
                                            text_content = f"分享了{img_count}张图片"
                                            bypass.log_message('INFO', "  从draw提取图片数量: '{}'".format(text_content))
                        
                        # 2.3 专栏内容（opus）
                        if not text_content.strip() and 'opus' in major_info:
                            opus = major_info['opus']
                            if opus and isinstance(opus, dict):
                                title = opus.get('title', '')
                                summary = opus.get('summary', '')
                                if title and title.strip():
                                    text_content = title.strip()
                                    bypass.log_message('INFO', "  从opus提取标题: '{}'".format(text_content))
                                elif summary and summary.strip():
                                    text_content = summary.strip()
                                    bypass.log_message('INFO', "  从opus提取摘要: '{}'".format(text_content))
                        
                        # 2.4 其他major类型的通用处理
                        if not text_content.strip():
                            for major_type, major_data in major_info.items():
                                if major_data and isinstance(major_data, dict):
                                    if 'title' in major_data:
                                        title = major_data['title']
                                        if title and title.strip():
                                            text_content = title.strip()
                                            bypass.log_message('INFO', "  从{}提取标题: '{}'".format(major_type, text_content))
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
                
                bypass.log_message('INFO', "最新动态: ID={}, 时间={}".format(dynamic_id, pub_time))
                bypass.log_message('INFO', "  文本内容: '{}'".format(text_content))
                bypass.log_message('INFO', "  module_dynamic 数据: {}".format(json.dumps(module_dynamic, ensure_ascii=False) if module_dynamic else "None"))
                
                # 动态类型映射（仅用于内部处理，不显示在推送中）
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
                    bypass.log_message('INFO', "  文本内容: '{}'".format(target_dynamic['text_content']))
                    
                    # 使用动态ID对比判断是否为新动态（替代时间判断）
                    is_new_dynamic = dynamic_storage.is_new_dynamic(uid, target_dynamic['id'])
                    bypass.log_message('INFO', "  动态ID对比结果: {}".format("新动态" if is_new_dynamic else "已存在动态"))
                    
                    if is_new_dynamic:
                        bypass.log_message('INFO', "*** 发现新动态，准备推送 ***")
                        
                        # 特殊处理：如果视频API受限且动态是视频类型，优先推送视频信息
                        if video_api_limited and target_dynamic['major_type'] == 'MAJOR_TYPE_ARCHIVE':
                            bypass.log_message('INFO', "视频API受限，但从动态数据中发现视频投稿，准备推送视频信息...")
                            
                            # 从archive数据中提取视频信息
                            archive_info = target_dynamic['raw_item'].get('modules', {}).get('module_dynamic', {}).get('major', {}).get('archive', {})
                            if archive_info:
                                video_title = archive_info.get('title', target_dynamic['text_content'])
                                video_cover = archive_info.get('cover', '')
                                video_bvid = archive_info.get('bvid', '')
                                video_url = f"https://www.bilibili.com/video/{video_bvid}" if video_bvid else f"https://t.bilibili.com/{target_dynamic['id']}"
                                
                                # 构建视频推送内容
                                content = f"【{video_title}】\n视频BV号: {video_bvid}\n发布时间: {target_dynamic['pub_time']}\n视频链接: {video_url}"
                                
                                # 更新存储的动态ID
                                dynamic_storage.update_latest_dynamic_id(uid, target_dynamic['id'], datetime.fromtimestamp(target_dynamic['pub_ts']))
                                
                                if TEST_MODE:
                                    bypass.log_message('INFO', f"[测试模式] 准备推送视频(从动态数据): {content}")
                                    return f"测试模式：找到新视频({video_title})，消息发送已屏蔽"
                                else:
                                    # 构建视频信息（模拟视频API格式）
                                    video_info = {
                                        'dynamic_id': video_bvid or target_dynamic['id'],
                                        'content': video_title,
                                        'content_type': '视频投稿',
                                        'timestamp': target_dynamic['pub_ts'],
                                        'url': video_url,
                                        'pics': [video_cover] if video_cover else [],
                                        'like': 0,
                                        'reply': 0,
                                        'forward': 0,
                                        'description': '',
                                        'length': '',
                                        'aid': '',
                                        'bvid': video_bvid
                                    }
                                    
                                    success = send_wechat_notification(up_name, video_info)
                                    if success:
                                        return f"成功推送新视频(从动态数据): {video_title}"
                                    else:
                                        return f"推送失败：新视频(从动态数据): {video_title}"
                        
                        # 普通动态推送逻辑
                        # 构建推送内容 - 仅显示文本内容，不显示动态类型
                        content = "【{}】\n动态ID: {}\n发布时间: {}".format(
                            target_dynamic['text_content'] or '新动态',
                            target_dynamic['id'],
                            target_dynamic['pub_time']
                        )
                        
                        # 屏蔽消息发送功能（测试模式）
                        # 更新存储的动态ID
                        dynamic_storage.update_latest_dynamic_id(uid, target_dynamic['id'], datetime.fromtimestamp(target_dynamic['pub_ts']))
                        
                        if TEST_MODE:
                            bypass.log_message('INFO', "[测试模式] 准备推送内容: {}".format(content))
                            bypass.log_message('INFO', "[测试模式] 消息发送功能已屏蔽")
                            return "测试模式：找到新动态(ID: {})，消息发送已屏蔽".format(target_dynamic['id'])
                        else:
                            bypass.log_message('INFO', "准备推送内容: {}".format(content))
                            # 实际发送通知
                            # 使用实际提取的文本内容
                            actual_content = target_dynamic['text_content'].strip() if target_dynamic['text_content'] else '新动态'
                            dynamic_info = {
                                'dynamic_id': target_dynamic['id'],
                                'content': actual_content,
                                'timestamp': target_dynamic['pub_ts'],
                                'url': "https://t.bilibili.com/{}".format(target_dynamic['id']),
                                'pics': [],  # 可以后续添加图片处理
                                'like': 0,
                                'reply': 0,
                                'forward': 0
                            }
                            success = send_wechat_notification(up_name, dynamic_info)
                            if success:
                                return "成功推送新动态(ID: {})".format(target_dynamic['id'])
                            else:
                                return "推送失败：新动态(ID: {})".format(target_dynamic['id'])
                    else:
                        bypass.log_message('INFO', "动态ID已存在，不重复推送")
                        return None
                else:
                    bypass.log_message('INFO', "未找到最新动态")
                return None
            else:
                bypass.log_message('INFO', "polymer API未获取到动态")
                return None
        else:
            bypass.log_message('WARNING', "polymer API返回错误: code={}".format(code))
            return None
            
    except Exception as e:
        bypass.log_message('ERROR', "polymer API请求失败: {}".format(e))
        return None
    
    # 如果polymer API失败，尝试vc API作为备选
    bypass.log_message('INFO', "尝试vc API作为备选...")
    return None