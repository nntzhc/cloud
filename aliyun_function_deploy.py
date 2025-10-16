#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站UP主动态监控 - 本地使用专用版本
基于动态发布时间判断是否发送消息
"""

import json
import requests
import time
from datetime import datetime, timezone, timedelta
import gzip
import os

# PushPlus配置
PUSHPLUS_TOKEN = "dadf10121525470ea7f9fe27c86722ca"

# 测试标志位 - 设置为True时强制推送测试
TEST_MODE = False    # 开启测试模式，验证推送功能

# 时间判断配置
# 时间阈值：动态发布时间在多少分钟内才发送通知（单位：分钟）
TIME_THRESHOLD_MINUTES = 5  # 正常监控时间阈值

# 监控的UP主列表
UP_LIST = [
    {"name": "史诗级韭菜", "uid": "322005137"},
    {"name": "茉菲特_Official", "uid": "3546839915694905"}
]

def handler(environ, start_response):
    try:
        result = get_up_latest_dynamic()
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        return [result.encode('utf-8')]
    except Exception as e:
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        return [f"Error: {str(e)}".encode('utf-8')]

def get_up_latest_dynamic(uid=None, up_name=None):
    # 如果没有提供UID，使用默认UID
    if not uid:
        uid = "22376577"
    if not up_name:
        up_name = "牛奶糖好吃"
    
    # 测试模式 - 设置为False以启用实际推送
    
    # 使用全局时间阈值，不再重新设置
    # TIME_THRESHOLD_MINUTES = 30  # 移除这行，使用全局变量
    
    # 获取真实cookie值
    real_cookies = "buvid3=7AC36028-D057-284A-14E8-5BB817F3DCEA40753infoc; b_nut=1760541240; __at_once=3401840458030349206"
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'https://space.bilibili.com/{uid}/dynamic',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': real_cookies
    }
    
    # 尝试polymer API
    polymer_url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={uid}&timezone_offset=-480"
    
    try:
        print(f"正在请求polymer API: {polymer_url}")
        response = requests.get(polymer_url, headers=headers, timeout=10)
        print(f"polymer API状态码: {response.status_code}")
        
        # 首先尝试直接解析JSON
        try:
            data = response.json()
            print(f"polymer API直接JSON解析成功")
        except json.JSONDecodeError as json_error:
            print(f"polymer API直接JSON解析失败: {json_error}")
            # 如果直接解析失败，尝试手动解压缩
            content = response.content
            print(f"响应内容长度: {len(content)} 字节")
            print(f"响应头: {dict(response.headers)}")
            
            # 尝试gzip解压（简化处理，移除brotli依赖）
            try:
                content = gzip.decompress(content)
                print("gzip解压成功")
            except:
                print("gzip解压失败，使用原始内容")
            
            # 尝试解析解压后的内容
            try:
                data = json.loads(content.decode('utf-8'))
                print("手动解压后JSON解析成功")
            except Exception as e:
                print(f"手动解压后JSON解析也失败: {e}")
                return f"polymer API JSON解析失败: {e}"
        
        # 检查响应码
        code = data.get('code', -1)
        print(f"polymer API返回code: {code}")
        
        if code == -352:
            print("polymer API返回风控错误code=-352")
            # 尝试获取风控信息
            if 'data' in data and isinstance(data['data'], dict):
                if 'v_voucher' in data['data']:
                    print(f"风控信息v_voucher: {data['data']['v_voucher']}")
            return f"polymer API风控校验失败: code=-352"
        elif code == 0:
            print("polymer API返回成功")
            items = data.get('data', {}).get('items', [])
            print(f"polymer API获取到 {len(items)} 条动态")
            
            if items:
                print("=== 详细分析最新动态 ===")
                
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
                        
                        # 获取文本内容
                        desc = module_dynamic.get('desc', {})
                        if desc and isinstance(desc, dict):
                            text_content = desc.get('text', '')
                    
                    print(f"最新动态: ID={dynamic_id}, 时间={pub_time}, 类型={dynamic_type}, 主要类型={major_type}")
                    print(f"  文本内容: '{text_content}'")
                    
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
                    
                    content_type = content_type_map.get(major_type, f"其他类型({major_type})")
                    
                    print(f"*** 找到最新动态！***")
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
                    print(f"目标动态详情:")
                    print(f"  动态ID: {target_dynamic['id']}")
                    print(f"  发布时间: {target_dynamic['pub_time']}")
                    print(f"  时间戳: {target_dynamic['pub_ts']}")
                    print(f"  动态类型: {target_dynamic['type']}")
                    print(f"  主要类型: {target_dynamic['major_type']}")
                    print(f"  文本内容: '{target_dynamic['text_content']}'")
                    
                    # 检查时间是否在30分钟内
                    current_time = int(time.time())
                    time_diff_minutes = (current_time - target_dynamic['pub_ts']) // 60
                    print(f"  距现在: {time_diff_minutes} 分钟")
                    
                    if time_diff_minutes <= TIME_THRESHOLD_MINUTES:
                        print(f"*** 动态在{TIME_THRESHOLD_MINUTES}分钟内，准备推送 ***")
                        
                        # 构建推送内容
                        content = f"UP主发布了新{target_dynamic['content_type']}\n动态ID: {target_dynamic['id']}\n发布时间: {target_dynamic['pub_time']}\n类型: {target_dynamic['content_type']}\n文本内容: {target_dynamic['text_content'] or '（无文本）'}"
                        
                        # 屏蔽消息发送功能（测试模式）
                        if TEST_MODE:
                            print(f"[测试模式] 准备推送内容: {content}")
                            print("[测试模式] 消息发送功能已屏蔽")
                            return f"测试模式：找到{time_diff_minutes}分钟前的动态(ID: {target_dynamic['id']})，消息发送已屏蔽"
                        else:
                            print(f"准备推送内容: {content}")
                            # 实际发送通知
                            dynamic_info = {
                                'dynamic_id': target_dynamic['id'],
                                'content': target_dynamic['text_content'] or f'UP主发布了新{target_dynamic["content_type"]}',
                                'content_type': target_dynamic['content_type'],
                                'timestamp': target_dynamic['pub_ts'],
                                'url': f"https://t.bilibili.com/{target_dynamic['id']}",
                                'pics': [],  # 可以后续添加图片处理
                                'like': 0,
                                'reply': 0,
                                'forward': 0
                            }
                            success = send_wechat_notification(up_name, dynamic_info)
                            if success:
                                return f"成功推送{time_diff_minutes}分钟前的动态(ID: {target_dynamic['id']})"
                            else:
                                return f"推送失败：{time_diff_minutes}分钟前的动态(ID: {target_dynamic['id']})"
                    else:
                        print(f"动态超过{TIME_THRESHOLD_MINUTES}分钟，不推送")
                        return f"动态超过{TIME_THRESHOLD_MINUTES}分钟，不推送"
                else:
                    print("未找到最新动态")
                    return "未找到最新动态"
            else:
                print("polymer API未获取到动态")
                return "polymer API未获取到动态"
        else:
            print(f"polymer API返回错误: code={code}")
            return f"polymer API返回错误: code={code}"
            
    except Exception as e:
        print(f"polymer API请求失败: {e}")
        return f"polymer API请求失败: {e}"
    
    # 如果polymer API失败，尝试vc API作为备选
    print("尝试vc API作为备选...")
    vc_url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&need_top=1&platform=web"
    
    try:
        print(f"正在请求vc API: {vc_url}")
        response = requests.get(vc_url, headers=headers, timeout=10)
        print(f"vc API状态码: {response.status_code}")
        
        # 尝试直接解析JSON
        try:
            data = response.json()
            print(f"vc API直接JSON解析成功")
        except json.JSONDecodeError as json_error:
            print(f"vc API直接JSON解析失败: {json_error}")
            # 如果直接解析失败，尝试手动解压缩
            content = response.content
            print(f"响应内容长度: {len(content)} 字节")
            
            # 尝试gzip解压（简化处理，移除brotli依赖）
            try:
                content = gzip.decompress(content)
                print("vc API gzip解压成功")
            except:
                print("vc API gzip解压失败，使用原始内容")
            
            # 尝试解析解压后的内容
            try:
                data = json.loads(content.decode('utf-8'))
                print("vc API 手动解压后JSON解析成功")
            except Exception as e:
                print(f"vc API 手动解压后JSON解析也失败: {e}")
                return f"vc API JSON解析失败: {e}"
        
        # 检查响应码
        code = data.get('code', -1)
        print(f"vc API返回code: {code}")
        
        if code == 0:
            print("vc API返回成功")
            cards = data.get('data', {}).get('cards', [])
            print(f"vc API获取到 {len(cards)} 条动态")
            
            if cards:
                # 处理最新动态
                latest_card = cards[0]
                card_id = latest_card.get('desc', {}).get('dynamic_id_str', '')
                timestamp = latest_card.get('desc', {}).get('timestamp', 0)
                card_type = latest_card.get('desc', {}).get('type', '')
                
                # 解析卡片内容
                card_content = ""
                try:
                    card_json = json.loads(latest_card.get('card', '{}'))
                    if 'item' in card_json:
                        card_content = card_json['item'].get('content', '')
                        if not card_content:
                            card_content = card_json['item'].get('description', '')
                            if not card_content and 'title' in card_json['item']:
                                card_content = card_json['item'].get('title', '')
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
                
                content_type = content_type_map.get(card_type, f'动态({card_type})')
                 
                print(f"vc API最新动态: ID={card_id}, 时间戳={timestamp}, 类型={card_type}({content_type})")
                print(f"vc API动态内容: {card_content[:100]}...")
                
                # 检查时间
                current_time = int(time.time())
                time_diff_minutes = (current_time - timestamp) // 60
                
                if time_diff_minutes <= TIME_THRESHOLD_MINUTES:
                    print(f"vc API动态在{TIME_THRESHOLD_MINUTES}分钟内，准备推送")
                    
                    content = f"UP主发布了新{content_type}\n动态ID: {card_id}\n发布时间: {time_diff_minutes}分钟前\n类型: {content_type}\n内容: {card_content[:100]}..."
                    
                    # 屏蔽消息发送功能（测试模式）
                    if TEST_MODE:
                        print(f"[测试模式] 准备推送内容: {content}")
                        print("[测试模式] 消息发送功能已屏蔽")
                        return f"vc API测试模式：找到{time_diff_minutes}分钟前的动态(ID: {card_id})，消息发送已屏蔽"
                    else:
                        print(f"准备推送内容: {content}")
                        # 实际发送通知
                        dynamic_info = {
                            'dynamic_id': card_id,
                            'content': card_content or f'UP主发布了新{content_type}',
                            'content_type': content_type,
                            'timestamp': timestamp,
                            'url': f"https://t.bilibili.com/{card_id}",
                            'pics': [],
                            'like': 0,
                            'reply': 0,
                            'forward': 0
                        }
                        success = send_wechat_notification(up_name, dynamic_info)
                        if success:
                            return f"vc API成功推送{time_diff_minutes}分钟前的动态(ID: {card_id})"
                        else:
                            return f"vc API推送失败：{time_diff_minutes}分钟前的动态(ID: {card_id})"
                else:
                    print(f"vc API动态超过{TIME_THRESHOLD_MINUTES}分钟，不推送")
                    return f"vc API动态超过{TIME_THRESHOLD_MINUTES}分钟，不推送"
            else:
                print("vc API未获取到动态")
                return "vc API未获取到动态"
        else:
            print(f"vc API返回错误: code={code}")
            return f"vc API返回错误: code={code}"
    
    except Exception as e:
        print(f"vc API请求失败: {e}")
        return f"vc API请求失败: {e}"
    
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
            return True, f"动态发布时间符合条件（{time_diff_minutes:.1f}分钟内）"
        else:
            return False, f"动态发布时间过久（{time_diff_minutes:.1f}分钟前，超过{TIME_THRESHOLD_MINUTES}分钟阈值）"
            
    except Exception as e:
        print(f"时间判断出错: {e}")
        return False, "时间判断出错"

def send_wechat_notification(up_name, dynamic_info):
    """发送微信通知"""
    try:
        title = f"🔔 {up_name} 发布了新{dynamic_info['content_type']}"
        
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
            pic_info = f"📸 包含 {pic_count} 张图片"
        
        # 构建HTML内容
        html_content = f"""
<div style="max-width: 600px; margin: 0 auto; font-family: 'Microsoft YaHei', Arial, sans-serif;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px 12px 0 0; text-align: center; color: white;">
        <h2 style="margin: 0; font-size: 24px; font-weight: bold;">📝 {up_name} 新{dynamic_info['content_type']}发布</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">B站动态监控通知</p>
    </div>
    
    <div style="background: white; padding: 25px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #00a1d6;">
            <h3 style="color: #2c3e50; margin: 0 0 10px 0; font-size: 18px;">{dynamic_info['content_type']}</h3>
            <p style="color: #666; margin: 0; line-height: 1.6;">{content_preview}</p>
            {f'<p style="color: #2196f3; margin: 10px 0 0 0; font-weight: bold;">{pic_info}</p>' if pic_info else ''}
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="display: flex; align-items: center;">
                <span style="background-color: #e3f2fd; color: #1976d2; padding: 6px 12px; border-radius: 20px; font-size: 14px; margin-right: 10px;">⏰ {pub_time}</span>
                <span style="background-color: #f3e5f5; color: #7b1fa2; padding: 6px 12px; border-radius: 20px; font-size: 14px;">🆔 {dynamic_info['dynamic_id']}</span>
            </div>
            <a href="{dynamic_url}" style="background: linear-gradient(135deg, #00a1d6, #0088cc); color: white; text-decoration: none; padding: 10px 20px; border-radius: 25px; font-weight: bold; transition: all 0.3s ease;">👉 查看动态</a>
        </div>
        
        <div style="display: flex; justify-content: space-around; background-color: #fafafa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <div style="text-align: center;">
                <div style="font-size: 20px; font-weight: bold; color: #e91e63;">👍 {dynamic_info['like']:,}</div>
                <div style="font-size: 12px; color: #666;">点赞</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px; font-weight: bold; color: #2196f3;">💬 {dynamic_info['reply']:,}</div>
                <div style="font-size: 12px; color: #666;">评论</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px; font-weight: bold; color: #4caf50;">🔄 {dynamic_info['forward']:,}</div>
                <div style="font-size: 12px; color: #666;">转发</div>
            </div>
        </div>
        
        <div style="border-top: 1px solid #eee; padding-top: 15px; text-align: center;">
            <p style="color: #999; font-size: 12px; margin: 0;">⏰ 推送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="color: #999; font-size: 12px; margin: 5px 0 0 0;">💡 来自B站动态监控系统</p>
        </div>
    </div>
</div>
"""
        
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
                    print(f"✅ 通知发送成功: {up_name}")
                    return True
                else:
                    error_msg = result.get("msg", "发送失败") if isinstance(result, dict) else str(result)
                    print(f"❌ 通知发送失败: {error_msg}")
                    return False
            except:
                print(f"❌ 响应解析失败: {response.text}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 发送通知异常: {e}")
        return False

def is_aliyun_environment():
    """判断是否在阿里云函数计算环境中"""
    return os.environ.get('FC_FUNCTION_NAME') is not None

def monitor_bilibili_dynamics():
    """监控B站UP主动态"""
    current_time = datetime.now()
    print(f"🚀 开始监控B站动态 - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 时间阈值: {TIME_THRESHOLD_MINUTES}分钟内发布的动态才推送")
    print("=" * 60)
    
    new_count = 0
    notified_count = 0
    
    for up in UP_LIST:
        print(f"\n📱 检查 {up['name']} 的动态...")
        
        try:
            # 获取UP主最新动态，传入uid和name
            dynamic = get_up_latest_dynamic(uid=up['uid'], up_name=up['name'])
            
            # 解析动态信息
            print(f"✅ {dynamic}")
            
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
            print(f"❌ 检查失败: {e}")
            continue
    
    print(f"\n✅ 监控完成，共检查 {new_count} 条动态，发送 {notified_count} 条通知")
    return {
        "checked_count": new_count,
        "notified_count": notified_count
    }

def handler(event, context):

    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 当前时间: {TIME_THRESHOLD_MINUTES}分钟内发布的动态才推送")
    
    try:
        # 执行动态监控
        result = monitor_bilibili_dynamics()
        
        return_result = {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"动态监控完成，检查 {result['checked_count']} 条动态，发送 {result['notified_count']} 条通知",
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
        
        print(f"✅ 函数执行成功")
        return return_result
        
    except Exception as e:
        error_msg = f"动态监控执行失败: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)
        }

# 本地测试
if __name__ == "__main__":
    print("🧪 本地测试模式")
    print("=" * 60)
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 时间阈值: {TIME_THRESHOLD_MINUTES}分钟内发布的动态才推送")
    
    event = {}
    context = type('Context', (), {'request_id': 'local-test-123'})()
    
    # 调用处理函数
    result = handler(event, context)
    
    print("\n📊 测试结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))