import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

reader = Reader("127.0.0.1", 4001)
writer = Writer("127.0.0.1", 4001)

def go_to_place(robot_id, position):
    # 调用机器人的相关操作接口
    # 在资源视图中存储任务的状态
    new_position = (0, 0, 0)
    return True, new_position

def open_camera():
    return True

def check_highest_point():
    return True

def locate_QR_code():
    # 获取到二维码的位置 并返回
    return True, QR_position


 def scan_QR_code(QR_position):
    pass
    return True

def grab(position):
    # 依据定位到的二维码位置，使用机械臂抓取指定位置
    # 涉及到位置和自由度的转换
    return True

def loosen():
    # 控制机械臂松手，放置货物
    return True