from view import Writer,Reader,View
from cmd import go_to_place,go_to_place_and_wait,end_wait,go_to_place_and_dock_wait
import sys
import json
import time

viewC = View()

def para_input():
  print(sys.argv[1])
  params = json.loads(sys.argv[1])
  return params

if __name__ == '__main__':
    # 解析输入参数 获取到robot id 和 robot target position
    params = para_input()
    robot_id = ''
    robot_target_position = ''
    robot_resource_position = ''
    robot_resource_position_ref = 0
    task_status = True
    for input_param in params['Inputs']:
        if input_param['Name'] == 'RobotID':
            robot_id = input_param['Value']
        elif input_param['Name'] == 'RobotTargetPosition':
            robot_target_position = input_param['Value']
        elif input_param['Name'] == 'RobotResourcePosition':
            robot_resource_position = input_param['Value']
        elif input_param['Name'] == 'RobotResourcePositionRef':
            robot_resource_position_ref = input_param['Value']

    # 测试用
    time.sleep(1)
    print(robot_resource_position)
    print(robot_resource_position_ref)
    if robot_resource_position != '' and robot_resource_position_ref != 0:
        viewC.releaseMutex(robot_resource_position,robot_resource_position_ref)

    # 临时性配置，207点使用dock函数
    #if robot_target_position == '207' or robot_target_position == 'R207':
    #    end_wait(robot_id)
    #    go_to_place_and_dock_wait(robot_id, robot_target_position,200)
    #else:
    #    end_wait(robot_id)
    #    (task_status,position) =  go_to_place_and_wait(robot_id, robot_target_position)

    if task_status:
        # 写入资源视图的position需要用<>包起来
        results = {'Result': 'true'}
        writer = Writer("127.0.0.1", 4001)
        writer.update_task_param(params,results,writer)
        writer.set_task_completed(params, writer)
    else:
        writer = Writer("127.0.0.1", 4001)
        writer.set_task_error(params, writer)

