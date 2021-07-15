import platform

base = {
    'log_path': '/var/log/saaya.log' if platform.system() not in  ['Windows', 'Darwin'] else 'saaya.log'
}

feature = {
    'RepeatEnable': True  # 如果需发送内容与上一条相同
}

store = {
    'LastMessage': None
}
