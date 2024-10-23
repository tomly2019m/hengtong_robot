# //检测巡检摄像头，关闭播放能力，关闭摄像能力。
# identify 118 0
# preview 117 112 121 131 0
# preview 117 113 121 132 0
# preview 117 114 121 133 0
# camera 112 0
# camera 113 0
# camera 114 0

# //返回关闭结果
# Result根据返回结果以决定是否进行下一步流程，如果关闭摄像头成功为Success，则继续下一个任务。
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from robotflow_v2.command.view import Writer
from robotflow_v2.command.cmd import camera, preview, identify
import json


def para_input():
    print(sys.argv[1])
    params = json.loads(sys.argv[1])
    return params


if __name__ == '__main__':
    # 解析输入参数 获取到robot id 和 robot target position
    params = para_input()

    task_status = identify("118", 0)

    if task_status:
        task_status = preview("117", "112", "121", "131", 0)

    if task_status:
        task_status = preview("117", "113", "121", "132", 0)

    if task_status:
        task_status = preview("117", "114", "121", "133", 0)

    if task_status:
        task_status = camera("112", 0)

    if task_status:
        task_status = camera("113", 0)

    if task_status:
        task_status = camera("114", 0)

    if task_status:
        # 写入资源视图的position需要用<>包起来
        results = {'Result': 'true'}
        writer = Writer("127.0.0.1", 4001)
        writer.update_task_param(params, results, writer)
        writer.set_task_completed(params, writer)
    else:
        writer = Writer("127.0.0.1", 4001)
        writer.set_task_error(params, writer)
