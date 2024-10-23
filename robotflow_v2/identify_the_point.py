import time

from command.view import Writer
import sys
import json


def para_input():
    print(sys.argv[1])
    params = json.loads(sys.argv[1])
    return params


if __name__ == '__main__':
    # 解析输入参数 获取到robot id 和 robot target position
    params = para_input()
    robot_id = ''
    camera_id = ''
    task_status = True
    for input_param in params['Inputs']:
        if input_param['Name'] == 'RobotID':
            robot_id = input_param['Value'][1:-1]
        elif input_param['Name'] == 'CameraID':
            camera_id = input_param['Value'][1:-1]

    time.sleep(5)

    if task_status:
        results = {'ArmTCPPosition': '<4,5,6>', 'Result': 'true'}
        writer = Writer("127.0.0.1", 4001)
        writer.update_task_param(params, results, writer)
        writer.set_task_completed(params, writer)
    else:
        writer = Writer("127.0.0.1", 4001)
        writer.set_task_error(params, writer)
