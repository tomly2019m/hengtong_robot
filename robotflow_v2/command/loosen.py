from view import Writer
from cmd import grab,loosen
import sys
import json
import time

def para_input():
  print(sys.argv[1])
  params = json.loads(sys.argv[1])
  return params

if __name__ == '__main__':
    # 解析输入参数 获取到robot id 和 robot target position
    params = para_input()
    arm_id = ''
    workpiece_current_position = ''
    workpiece_target_position = ''
    task_status = True
    position = ''
    for input_param in params['Inputs']:
        if input_param['Name'] == 'ArmID':
            arm_id = input_param['Value']
        elif input_param['Name'] == 'WorkpieceTargetPosition':
            workpiece_target_position = input_param['Value']

    #临时性配置
    if workpiece_current_position == 'ship3':
        workpiece_current_position = 'ship1'
    elif workpiece_current_position == 'ship4':
        workpiece_current_position = 'ship2'

    # 临时性配置
    if arm_id == '105':
        # 如果是移动机械臂
        workpiece_target_position = 'arm1-' + workpiece_target_position
    elif arm_id == '106':
        # 如果是固定机械臂
        workpiece_target_position = 'arm2-' + workpiece_target_position

    # 抓取货物
    (task_status,position) = loosen(arm_id,workpiece_target_position)

    # 测试用
#     time.sleep(1)
# #     print(arm_id)
# #     print(workpiece_target_position)

    # 临时性配置，屏蔽固定机械臂
#     if arm_id == '105':
#         time.sleep(1)
#     else:
#         (task_status,position) = loosen(arm_id,workpiece_target_position)

    if task_status == True:
        # 写入资源视图的position需要用<>包起来
        results = {'WorkpieceAfterMovePosition': f'<{position}>', 'Result': 'true'}
        writer = Writer("127.0.0.1", 4001)
        writer.update_task_param(params,results,writer)
        writer.set_task_completed(params, writer)
    else:
        writer = Writer("127.0.0.1", 4001)
        writer.set_task_error(params, writer)
