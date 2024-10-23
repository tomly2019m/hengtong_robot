from cmd import go_to_place_and_wait,end_wait,go_to_place,go_to_place_and_dock_wait
import time

if __name__ == '__main__':
    # 解析输入参数 获取到robot id 和 workpiece id
    robot_id = '101'
    robot_target_position = "207"
    
    # task_status = end_wait(robot_id)
    # print(task_status)
    
    (task_status,position) = go_to_place_and_dock_wait(robot_id, robot_target_position)
    #(task_status,position) = go_to_place_and_wait(robot_id, robot_target_position)
    print(task_status)
    print(position)
    time.sleep(10)
    task_status = end_wait(robot_id)
    print(task_status)
    

