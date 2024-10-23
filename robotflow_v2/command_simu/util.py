import json
import time
import requests
# sys.path.append("..")

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from robotflow_v2.command.view import Writer

from robotflow_v2.constants import Constants

rmf_addr = Constants.RMF_ADDR

# 从Constants中的表项中查找函数
def search(table:dict,key:str):
    if key in table:
        return table[key]
    else:
        print(f"Not Found {key} in Table {table}")
        return None

# 获取指定机器人的位置(非坐标形式)
def get_position(robot_id):
    fleet = "tinyRobot"
    url = f"http://"+ rmf_addr + ":8000/fleets/{fleet}/state"
    response = requests.get(url).json()
    robots = response["robots"]
    coordinate = []
    for robot in robots:
        if robot["name"] == id:
            coordinate.append(robot["location"]["x"])
            coordinate.append(robot["location"]["y"])
    return coordinate_to_position(coordinate[0], coordinate[1])


# 将坐标位置转化为工作流格式的位置 需要查询资源视图来确定
def coordinate_to_position(x, y):
    pass
    return 0


# 利用robot id获取当前正在执行的task_id
def get_task_id(robot_id) -> str:
    pass


def param_input():
    return json.loads(sys.argv[1])


# 轮询某个机器人是否已经到正确的位置
def polling_in_position(robot_id, position):
    while True:
        if get_position(robot_id) == position:
            break
        time.sleep(0.05)


# 更新任务参数
def update_task_param(writer: Writer, params: dict, results: dict):
    for output in params['Outputs']:
        if output['Name'] in results:
            output['Value'] = results[output['Name']]
            sql = 'update TaskParam set data' + '=\'' + str(output['Value']) + '\',dataType=\'' + output[
                'Type'] + '\' where taskId=\'' + params['TaskID'] + '\' and name=\'' + output[
                      'Name'] + '\' and serviceID=\'' + params['ServiceID'] + '\''
            # print(sql)
            print(writer.exec(sql))


def insert_task_param(writer: Writer, params: dict, results: dict):
    for output in params['Outputs']:
        if output['Name'] in results:
            output['Value'] = results[output['Name']]
            sql = (f"'insert into TaskParam(taskId, name, serviceID, data, dataType) values("
                   f"{params['TaskID']}, {output['Name']}, {params['ServiceID']}, {output['Value']}, {output['Type']}"
                   f")'")

            # print(sql)
            print(writer.exec(sql))
