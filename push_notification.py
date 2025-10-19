import requests
from datetime import datetime
import os

# PushPlus配置 - 从config文件导入
try:
    from config import PUSHPLUS_TOKEN, ENABLE_PUSH
except ImportError:
    PUSHPLUS_TOKEN = os.environ.get('PUSHPLUS_TOKEN', '')
    ENABLE_PUSH = True  # 默认启用推送

def should_send_notification(dynamic_created_time, up_uid=None, dynamic_id=None, dynamic_storage=None):
    """判断是否应该发送通知（基于动态ID对比）
    
    Args:
        dynamic_created_time: 动态创建时间（保留参数，用于兼容性）
        up_uid: UP主UID（可选）
        dynamic_id: 动态ID（可选，优先使用ID对比）
        dynamic_storage: 动态ID存储实例
    
    Returns:
        tuple: (是否应该发送, 原因描述)
    """
    try:
        # 使用ID对比逻辑判断是否为新的动态
        if up_uid and dynamic_id and dynamic_storage:
            is_new, reason = dynamic_storage.is_new_dynamic(up_uid, dynamic_id)
            if is_new:
                return True, f"发现新动态: {reason}"
            else:
                return False, f"不推送: {reason}"
        
        # 如果没有提供必要参数，返回错误信息
        return False, "缺少必要参数（UP主UID或动态ID）"
            
    except Exception as e:
        print(f"[ERROR] 动态判断出错: {e}")
        return False, "动态判断出错"

def send_wechat_notification(up_name, dynamic_info, bypass=None):
    """发送微信通知"""
    try:
        # 检查是否启用推送
        if not ENABLE_PUSH:
            print(f"[INFO] 📝 推送功能已关闭，仅模拟推送: {up_name}")
            if bypass:
                bypass.log_message('INFO', f"📝 推送功能已关闭，仅模拟推送: {up_name}")
            # 打印推送内容预览
            content_text = dynamic_info.get('content', '').replace('\n', ' ').replace('\r', ' ').strip() if dynamic_info.get('content') else "新动态"
            if len(content_text) > 50:
                content_text = content_text[:50] + "..."
            print(f"[INFO] 📋 推送预览 - 标题: {up_name} - {content_text}")
            return True
        # 构建标题，移除换行符和特殊字符，确保单行
        content_text = dynamic_info.get('content', '').replace('\n', ' ').replace('\r', ' ').strip() if dynamic_info.get('content') else "新动态"
        if len(content_text) > 30:
            content_text = content_text[:30] + "..."
        title = "🔔 {}: {}".format(up_name, content_text)
        
        # 格式化时间 - 处理None情况
        timestamp = dynamic_info.get("timestamp")
        pub_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dynamic_url = dynamic_info.get('url', '')
        
        # 构建内容预览（截取前200字符）
        content_preview = dynamic_info.get('content', '')
        if len(content_preview) > 200:
            content_preview = content_preview[:200] + "..."
        
        # 构建图片信息 - 安全处理None情况
        pic_info = ""
        pics = dynamic_info.get('pics')
        if pics and isinstance(pics, list):
            pic_count = len(pics)
            pic_info = "📸 包含 {} 张图片".format(pic_count)
        
        # 获取统计数据 - 安全处理None情况
        like_count = dynamic_info.get('like', 0) or 0
        reply_count = dynamic_info.get('reply', 0) or 0
        forward_count = dynamic_info.get('forward', 0) or 0
        dynamic_id = dynamic_info.get('dynamic_id', '未知')
        
        # 构建简化HTML内容 - 基于测试成功的格式（简化版）
        html_content = f"""
<div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
    <div style="background: #667eea; padding: 15px; border-radius: 8px; color: white; text-align: center;">
        <h2 style="margin: 0; font-size: 20px;">📝 {up_name} 新动态</h2>
    </div>
    
    <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 10px;">
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 3px solid #00a1d6;">
            <p style="color: #666; margin: 0;">{content_preview}</p>
            {f'<p style="color: #2196f3; margin: 5px 0 0 0;">{pic_info}</p>' if pic_info else ''}
        </div>
        
        <div style="margin-top: 15px; text-align: center;">
            <span style="background: #e3f2fd; color: #1976d2; padding: 5px 10px; border-radius: 15px; font-size: 12px;">⏰ {pub_time}</span>
            <a href="{dynamic_url}" style="background: #00a1d6; color: white; padding: 8px 15px; border-radius: 20px; text-decoration: none; margin-left: 10px;">查看动态</a>
        </div>
        
        <div style="display: flex; justify-content: space-around; margin-top: 15px; background: #fafafa; padding: 10px; border-radius: 5px;">
            <div style="text-align: center;">
                <div style="font-size: 16px; color: #e91e63;">👍 {like_count:,}</div>
                <div style="font-size: 12px; color: #666;">点赞</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 16px; color: #2196f3;">💬 {reply_count:,}</div>
                <div style="font-size: 12px; color: #666;">评论</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 16px; color: #4caf50;">🔄 {forward_count:,}</div>
                <div style="font-size: 12px; color: #666;">转发</div>
            </div>
        </div>
        
        <div style="border-top: 1px solid #eee; padding-top: 10px; text-align: center; margin-top: 15px;">
            <p style="color: #999; font-size: 11px; margin: 0;">⏰ 推送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</div>
"""
        
        # 发送通知 - 添加频率控制
        data = {
            "token": PUSHPLUS_TOKEN,
            "title": title,
            "content": html_content,
            "template": "html"
        }
        
        # 添加重试机制
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "http://www.pushplus.plus/send/",
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict) and result.get("code") == 200:
                        if bypass:
                            bypass.log_message('INFO', "✅ 通知发送成功: {}".format(up_name))
                        else:
                            print(f"[INFO] ✅ 通知发送成功: {up_name}")
                        return True
                    else:
                        error_msg = result.get("msg", "发送失败") if isinstance(result, dict) else str(result)
                        error_code = result.get("code", "unknown") if isinstance(result, dict) else "unknown"
                        
                        # 如果是频率限制错误，等待后重试
                        if error_code == 999 and attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # 指数退避
                            if bypass:
                                bypass.log_message('WARNING', "⚠️ 推送频率限制，等待{}秒后重试...".format(wait_time))
                            else:
                                print(f"[WARNING] ⚠️ 推送频率限制，等待{wait_time}秒后重试...")
                            import time
                            time.sleep(wait_time)
                            continue
                        
                        if bypass:
                            bypass.log_message('ERROR', "❌ 通知发送失败: {} (code: {})".format(error_msg, error_code))
                            bypass.log_message('ERROR', "❌ 推送数据详情 - 标题: {} (长度: {})".format(repr(title), len(title)))
                            bypass.log_message('ERROR', "❌ 推送数据详情 - 内容长度: {}".format(len(html_content)))
                        else:
                            print(f"[ERROR] ❌ 通知发送失败: {error_msg} (code: {error_code})")
                            print(f"[ERROR] ❌ 推送数据详情 - 标题: {repr(title)} (长度: {len(title)})")
                            print(f"[ERROR] ❌ 推送数据详情 - 内容长度: {len(html_content)}")
                        return False
                else:
                    if bypass:
                        bypass.log_message('ERROR', "❌ HTTP错误: {}".format(response.status_code))
                    else:
                        print(f"[ERROR] ❌ HTTP错误: {response.status_code}")
                    return False
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    if bypass:
                        bypass.log_message('WARNING', "⚠️ 推送异常，等待2秒后重试: {}".format(e))
                    else:
                        print(f"[WARNING] ⚠️ 推送异常，等待2秒后重试: {e}")
                    import time
                    time.sleep(2)
                    continue
                else:
                    if bypass:
                        bypass.log_message('ERROR', "❌ 发送通知异常: {}".format(e))
                    else:
                        print(f"[ERROR] ❌ 发送通知异常: {e}")
                    return False
            
            break  # 如果成功或不需要重试，跳出循环
            
    except Exception as e:
        if bypass:
            bypass.log_message('ERROR', "❌ 构建推送数据异常: {}".format(e))
        else:
            print(f"[ERROR] ❌ 构建推送数据异常: {e}")
        return False

def is_aliyun_environment():
    """判断是否在阿里云函数计算环境中"""
    return os.environ.get('FC_FUNCTION_NAME') is not None