# PushPlus配置
PUSHPLUS_TOKEN = "dadf10121525470ea7f9fe27c86722ca"
# 测试标志位 - 设置为True时强制推送测试
TEST_MODE = False    # 开启测试模式，验证推送功能

# 实际推送控制标志位
ENABLE_PUSH = True  # 设置为False时只打印推送信息，不进行实际推送（节省推送额度）True

# 动态推送判断配置
# 现在主要使用动态ID对比来判断是否推送新动态
# 时间阈值已废弃，仅作为备用判断逻辑

# 监控的UP主列表
UP_LIST = [
    {"name": "史诗级韭菜", "uid": "322005137"},
    {"name": "茉菲特_Official", "uid": "3546839915694905"}
]