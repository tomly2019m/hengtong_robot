from view import Writer
from cmd import process
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
    pipeline_id = ''
    speed = ''
    action = ''
    task_status = True

    for input_param in params['Inputs']:
        if input_param['Name'] == 'PipelineID':
            pipeline_id = input_param['Value']
        elif input_param['Name'] == 'SpeedValue':
            speed = input_param['Value']
        elif input_param['Name'] == 'Action':
            action = input_param['Value']
    # 测试用
#     time.sleep(1)
#     print(pipeline_id)
#     print(speed)
#     print(action)

    # 加工货物
    task_status = process(pipeline_id,speed,int(action))

    if task_status == True:
        # 写入资源视图的position需要用<>包起来
        results = {'Result': 'true'}
        writer = Writer("127.0.0.1", 4001)
        writer.update_task_param(params,results,writer)
        writer.set_task_completed(params, writer)
    else:
        writer = Writer("127.0.0.1", 4001)
        writer.set_task_error(params, writer)
