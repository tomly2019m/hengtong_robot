from cmd import end_wait
if __name__ == '__main__':
    # 解析输入参数 获取到robot id 和 workpiece id
    robot_id = '101'
    task_status = end_wait(robot_id)
