from cmd import go_up_and_down
if __name__ == '__main__':
    # 解析输入参数 获取到robot id 和 workpiece id
    robot_id = '107'
    height = "low"
    (task_status,position) = go_up_and_down(robot_id,height)
    print(task_status)
    print(position)
