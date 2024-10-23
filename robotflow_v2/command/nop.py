from view import Writer
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
    task_status = True

    if task_status == True:
        # 写入资源视图的position需要用<>包起来
        results = {'Result': 'true'}
        writer = Writer("127.0.0.1", 4001)
        writer.update_task_param(params,results,writer)
        writer.set_task_completed(params, writer)
    else:
        writer = Writer("127.0.0.1", 4001)
        writer.set_task_error(params, writer)
