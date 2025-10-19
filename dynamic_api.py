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

def get_up_latest_video_info(uid, up_name):
    """获取最新视频信息（不直接推送，只返回信息）"""
    bypass = APIRestrictionBypass()
    bypass.setup_logger(log_level='INFO', enable_console=True)
    
    try:
        # 构建搜索视频的URL
        search_url = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={uid}&ps=1&tid=0&pn=1&order=pubdate&order_avoided=true"
        
        # 获取真实cookie值
        real_cookies = "buvid3=7AC36028-D057-284A-14E8-5BB817F3DCEA40753infoc; b_nut=1760541240; __at_once=3401840458030349206"
        
        bypass.log_message('INFO', "获取视频信息，URL: {}".format(search_url))
        
        # 使用API风控绕过模式
        result = bypass.make_request_with_bypass(search_url, method='GET', headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f'https://space.bilibili.com/{uid}/video',
            'Cookie': real_cookies
        })
        
        if not result or result.get('code') != 0:
            bypass.log_message('ERROR', "视频API请求失败")
            return None
            
        data = result
        
        # 处理API频率限制
        if data.get('code') == -799:
            bypass.log_message('WARNING', f"视频搜索API频率限制: {data.get('message', '请求过于频繁')}")
            return None
        elif data.get('code') == -352:
            bypass.log_message('WARNING', f"视频搜索API风控校验失败: {data.get('message', '风控校验失败')}")
            return None
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
                bypass.log_message('INFO', f"发布时间戳: {created}")
                
                # 检查是否为新视频
                is_new_video = dynamic_storage.is_new_dynamic(up_name, bvid)
                if not is_new_video:
                    bypass.log_message('INFO', f"视频已推送过，不重复处理")
                    return None
                
                # 构建视频信息对象
                video_info = {
                    'type': 'video',
                    'id': bvid,
                    'title': title,
                    'aid': aid,
                    'bvid': bvid,
                    'timestamp': created,
                    'pub_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created)),
                    'length': length,
                    'pic': pic,
                    'description': description,
                    'url': f"https://www.bilibili.com/video/{bvid}"
                }
                
                bypass.log_message('INFO', "获取到最新视频信息")
                return video_info
            else:
                bypass.log_message('INFO', "未获取到视频列表")
                return None
        else:
            bypass.log_message('WARNING', f"视频搜索API返回错误: {data.get('message', '未知错误')}")
            return None
            
    except Exception as e:
         bypass.log_message('ERROR', f"获取视频信息失败: {e}")
         return None
 
def get_up_latest_dynamic_info(uid, up_name):
    """获取最新动态信息（不直接推送，只返回信息）"""
    bypass = APIRestrictionBypass()
    bypass.setup_logger(log_level='INFO', enable_console=True)
    
    try:
        # 获取真实cookie值
        real_cookies = "buvid3=7AC36028-D057-284A-14E8-5BB817F3DCEA40753infoc; b_nut=1760541240; __at_once=3401840458030349206"
        
        # 使用get_user_dynamics函数获取数据
        data = get_user_dynamics(uid, real_cookies, use_bypass=True)
        
        if not data:
            bypass.log_message('ERROR', "获取动态失败")
            return None
        
        # 解析polymer API返回的数据
        bypass.log_message('INFO', "正在解析polymer API数据...")
        
        # 检查多种可能的数据结构
        items = []
        if 'data' in data and isinstance(data['data'], dict):
            items = data['data'].get('items', [])
            if not items:
                items = data['data'].get('list', [])
            if not items:
                items = data['data'].get('cards', [])
        elif 'data' in data and isinstance(data['data'], list):
            items = data['data']
        
        # 确保items是列表类型
        if items is None:
            items = []
        
        bypass.log_message('INFO', "polymer API获取到 {} 条动态".format(len(items) if items else 0))
        
        # 检查响应码
        code = data.get('code', -1)
        bypass.log_message('INFO', "polymer API返回code: {}".format(code))
        
        if code == -352:
            bypass.log_message('WARNING', "polymer API返回风控错误code=-352")
            return None
        elif code == 0:
            bypass.log_message('INFO', "polymer API返回成功")
            
            # 如果仍然没有items，尝试更深层的解析
            if not items:
                bypass.log_message('WARNING', "polymer API返回成功但items为空")
                data_content = data.get('data', {})
                if isinstance(data_content, dict) and data_content:
                    for key, value in data_content.items():
                        if isinstance(value, list) and value and len(value) > 0:
                            items = value
                            break
            
            if items:
                bypass.log_message('INFO', "=== 详细分析最新动态 ===")
                
                # 获取前两条动态，比较时间戳，选择真正最新的动态
                target_dynamic = None
                
                if len(items) >= 2:
                    first_item = items[0]
                    second_item = items[1]
                    
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
                    
                    # 提取文本内容
                    text_content = ""
                    
                    # 处理desc字段
                    desc_info = module_dynamic.get('desc')
                    if desc_info is not None and isinstance(desc_info, dict):
                        desc_text = desc_info.get('text', '')
                        if desc_text and desc_text.strip():
                            text_content = desc_text.strip()
                    
                    # 处理major字段
                    if not text_content.strip() and major_info:
                        # 视频内容
                        if 'archive' in major_info:
                            archive = major_info['archive']
                            if archive and isinstance(archive, dict):
                                title = archive.get('title', '')
                                if title and title.strip():
                                    text_content = title.strip()
                        
                        # 图文内容
                        if not text_content.strip() and 'draw' in major_info:
                            draw = major_info['draw']
                            if draw and isinstance(draw, dict):
                                draw_text = draw.get('text', '')
                                if draw_text and draw_text.strip():
                                    text_content = draw_text.strip()
                                else:
                                    text_content = "分享了图片"
                        
                        # 专栏内容
                        if not text_content.strip() and 'opus' in major_info:
                            opus = major_info['opus']
                            if opus and isinstance(opus, dict):
                                title = opus.get('title', '')
                                summary = opus.get('summary', '')
                                if title and title.strip():
                                    text_content = title.strip()
                                elif summary and summary.strip():
                                    text_content = summary.strip()
                        
                        # 其他类型
                        if not text_content.strip():
                            for major_type_key, major_data in major_info.items():
                                if major_data and isinstance(major_data, dict):
                                    if 'title' in major_data:
                                        title = major_data['title']
                                        if title and title.strip():
                                            text_content = title.strip()
                                            break
                    
                    # 备用方案
                    if not text_content.strip():
                        if 'content' in module_dynamic:
                            content = module_dynamic['content']
                            if content and isinstance(content, dict):
                                content_text = content.get('text', '')
                                if content_text and content_text.strip():
                                    text_content = content_text.strip()
                        
                        if not text_content.strip() and 'item' in module_dynamic:
                            item = module_dynamic['item']
                            if item and isinstance(item, dict):
                                item_text = item.get('text', '') or item.get('title', '') or item.get('description', '')
                                if item_text and item_text.strip():
                                    text_content = item_text.strip()
                    
                    # 最后尝试card字段
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
                
                # 检查是否为新动态
                is_new_dynamic = dynamic_storage.is_new_dynamic(up_name, dynamic_id)
                bypass.log_message('INFO', "  动态ID对比结果: {}".format("新动态" if is_new_dynamic else "已存在动态"))
                
                if not is_new_dynamic:
                    bypass.log_message('INFO', "动态已推送过，不重复处理")
                    return None
                
                # 构建动态信息对象
                dynamic_info = {
                    'type': 'dynamic',
                    'id': dynamic_id,
                    'pub_time': pub_time,
                    'pub_ts': pub_ts,
                    'major_type': major_type,
                    'text_content': text_content,
                    'raw_item': latest_item
                }
                
                bypass.log_message('INFO', "获取到最新动态信息")
                return dynamic_info
            else:
                bypass.log_message('INFO', "未找到动态数据")
                return None
        else:
            bypass.log_message('WARNING', "polymer API返回错误: code={}".format(code))
            return None
            
    except Exception as e:
        bypass.log_message('ERROR', "获取动态信息失败: {}".format(e))
        return None

def compare_and_get_latest(video_info, dynamic_info, bypass):
    """比较视频和动态的时间戳，返回最新的项目"""
    bypass.log_message('INFO', "=== 比较视频和动态的时间戳 ===")
    
    # 记录获取到的信息
    if video_info:
        bypass.log_message('INFO', "视频信息: 时间={}, 标题='{}'".format(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video_info['timestamp'])),
            video_info['title']
        ))
    else:
        bypass.log_message('INFO', "未获取到视频信息")
    
    if dynamic_info:
        bypass.log_message('INFO', "动态信息: 时间={}, 内容='{}'".format(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dynamic_info['pub_ts'])),
            dynamic_info['text_content'][:50] + '...' if len(dynamic_info['text_content']) > 50 else dynamic_info['text_content']
        ))
    else:
        bypass.log_message('INFO', "未获取到动态信息")
    
    # 比较时间戳，选择最新的
    if video_info and dynamic_info:
        # 都有信息，比较时间戳
        if video_info['timestamp'] >= dynamic_info['pub_ts']:
            bypass.log_message('INFO', "✅ 选择视频（时间更新或相同）")
            return video_info
        else:
            bypass.log_message('INFO', "✅ 选择动态（时间更新）")
            return dynamic_info
    elif video_info:
        # 只有视频信息
        bypass.log_message('INFO', "✅ 只有视频信息，选择视频")
        return video_info
    elif dynamic_info:
        # 只有动态信息
        bypass.log_message('INFO', "✅ 只有动态信息，选择动态")
        return dynamic_info
    else:
        # 都没有信息
        bypass.log_message('INFO', "❌ 未获取到任何新内容")
        return None

def push_latest_item(latest_item, up_name, bypass):
    """推送最新的项目"""
    bypass.log_message('INFO', "=== 准备推送最新内容 ===")
    
    if latest_item['type'] == 'video':
        # 推送视频
        bypass.log_message('INFO', "准备推送视频: {}".format(latest_item['title']))
        
        # 构建推送内容
        content = f"【{latest_item['title']}】\n视频AV号: {latest_item['aid']}\n发布时间: {latest_item['pub_time']}\n时长: {latest_item['length']}\n视频链接: {latest_item['url']}"
        
        # 更新存储的动态ID
        dynamic_storage.update_latest_dynamic_id(up_name, latest_item['id'], datetime.fromtimestamp(latest_item['timestamp']))
        
        if TEST_MODE:
            bypass.log_message('INFO', f"[测试模式] 准备推送视频: {content}")
            return f"测试模式：找到新视频({latest_item['title']})，消息发送已屏蔽"
        else:
            # 构建视频信息
            video_info = {
                'dynamic_id': latest_item['bvid'],
                'content': latest_item['title'],
                'content_type': '视频投稿',
                'timestamp': latest_item['timestamp'],
                'url': latest_item['url'],
                'pics': [latest_item['pic']] if latest_item['pic'] else [],
                'like': 0,
                'reply': 0,
                'forward': 0,
                'description': latest_item['description'],
                'length': latest_item['length'],
                'aid': latest_item['aid'],
                'bvid': latest_item['bvid']
            }
            
            success = send_wechat_notification(up_name, video_info)
            if success:
                return f"成功推送新视频: {latest_item['title']}"
            else:
                return f"推送失败：新视频: {latest_item['title']}"
    
    else:  # dynamic
        # 推送动态
        bypass.log_message('INFO', "准备推送动态: {}".format(latest_item['text_content'][:50]))
        
        # 构建推送内容
        content = "【{}】\n动态ID: {}\n发布时间: {}".format(
            latest_item['text_content'] or '新动态',
            latest_item['id'],
            latest_item['pub_time']
        )
        
        # 更新存储的动态ID
        dynamic_storage.update_latest_dynamic_id(up_name, latest_item['id'], datetime.fromtimestamp(latest_item['pub_ts']))
        
        if TEST_MODE:
            bypass.log_message('INFO', "[测试模式] 准备推送内容: {}".format(content))
            return "测试模式：找到新动态(ID: {})，消息发送已屏蔽".format(latest_item['id'])
        else:
            # 构建动态信息
            actual_content = latest_item['text_content'].strip() if latest_item['text_content'] else '新动态'
            dynamic_info = {
                'dynamic_id': latest_item['id'],
                'content': actual_content,
                'timestamp': latest_item['pub_ts'],
                'url': "https://t.bilibili.com/{}".format(latest_item['id']),
                'pics': [],  # 可以后续添加图片处理
                'like': 0,
                'reply': 0,
                'forward': 0
            }
            
            success = send_wechat_notification(up_name, dynamic_info)
            if success:
                return "成功推送新动态(ID: {})".format(latest_item['id'])
            else:
                return "推送失败：新动态(ID: {})".format(latest_item['id'])

def get_up_latest_dynamic(uid=None, up_name=None):
    """获取UP主最新动态（包括视频、图文、专栏等）"""
    if not uid:
        uid = "22376577"
    if not up_name:
        up_name = "牛奶糖好吃"
    
    bypass = APIRestrictionBypass()
    bypass.setup_logger(log_level='INFO', enable_console=True)
    
    bypass.log_message('INFO', "=== 获取UP主 {} 最新动态 ===".format(up_name))
    bypass.log_message('INFO', "用户UID: {}".format(uid))
    
    # 获取最新视频信息（不直接推送，只返回信息）
    bypass.log_message('INFO', "获取最新视频信息...")
    video_info = get_up_latest_video_info(uid, up_name)
    
    # 获取最新动态信息（不直接推送，只返回信息）
    bypass.log_message('INFO', "获取最新动态信息...")
    dynamic_info = get_up_latest_dynamic_info(uid, up_name)
    
    # 比较并获取最新的内容
    latest_item = compare_and_get_latest(video_info, dynamic_info, bypass)
    
    if latest_item:
        # 推送最新的内容
        return push_latest_item(latest_item, up_name, bypass)
    else:
        bypass.log_message('INFO', "没有新的内容需要推送")
        return None