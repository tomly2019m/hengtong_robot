import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from time import sleep
from robotflow_v2.command.view import Writer
from robotflow_v2.command.cmd import camera, preview, identify
from robotflow_v2.constants import Status
import json


def para_input():
    print(sys.argv[1])
    params = json.loads(sys.argv[1])
    return params


if __name__ == '__main__':
    # 解析输入参数 获取到robot id
    # "Inputs": [
    #       {
    #         "Name": "WorkpieceID",
    #         "Type": "String",
    #         "Describe": "工件ID"
    #       }
    #     ]
    params = para_input()
    workpiece_id = ''
    workpiece_ids = []
    for input_param in params['Inputs']:
        if input_param['Name'] == 'WorkpieceID':
            workpiece_id = input_param['Value'][1:-1]
            workpiece_ids = workpiece_id.split(',')

    # camera 传入摄像头编号和行为(1 代表开启，0 代表关闭),True代表执行正常
    task_status = camera("112", 1)

    if task_status:
        camera("113", 1)

    if task_status:
        camera("114", 1)

    if task_status:
        preview("117", "112", "121", "131", 1)

    if task_status:
        preview("117", "113", "121", "132", 1)

    if task_status:
        preview("117", "114", "121", "133", 1)

    if task_status:
        task_status, status = identify("118",1)
    sleep(3)

    # 默认一系列识别任务执行成功，在任一识别任务失败后修改result为false，并终止for循环
    if task_status:
        results = {'Result': 'true'}
        for workpiece_id in workpiece_ids:
            task_status, workpiece_status = identify("118", workpiece_id)

            # 写入资源视图的position需要用<>包起来
            if workpiece_status == Status.INDENTIFY_EXIST:
                continue
            else:
                results = {'Result': 'false'}
                break

        if task_status:
            writer = Writer("127.0.0.1", 4001)
            writer.update_task_param(params, results, writer)
            writer.set_task_completed(params, writer)

        else:
            writer = Writer("127.0.0.1", 4001)
            writer.set_task_error(params, writer)

    else:
        writer = Writer("127.0.0.1", 4001)
        writer.set_task_error(params, writer)
