# RMF 指令
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import time
import requests
import json

from robotflow_v2.command.util import search
from robotflow_v2.constants import Status, Constants, LogType
from robotflow_v2.command.camera_modified import camera as camera_modify
from robotflow_v2.command.view import Reader,Writer,View

import math

# rmf服务器地址
rmf_addr = Constants.RMF_ADDR

# log服务器地址
log_addr = Constants.LOG_ADDR

reader = Reader("127.0.0.1", 4001)
writer = Writer("127.0.0.1", 4001)
viewC = View()

# 远端log
# type: log类型，有
def log(type,str):
    timestap = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime())
    output = f"[{type}][{timestap}] {str}"

    url = f"http://{log_addr}:7000/api/taskFlowInfo"
    request_json = {"info": output}

    requests.post(url=url, json=request_json)

# 移动机器人
def go_to_place(robot_id, position):
    # 查找机器人表，把robot_id转换成robot_name
    robot_name = search(Constants.ROBOT, robot_id)
    if robot_name == None:
        print(f"Failed To Get RobotName, Robot id {robot_id}")
        str = f"机器人{robot_id}移动到位置{position}失败"
        log(LogType.ERROR, str)
        return False,position

    if position.startswith('R'):
        # Position需要从id转换为rmf接受的格式
        robot_position = position
        print(robot_position)
    else:
        # Position需要从id转换为rmf接受的格式
        robot_position = 'R' + position
        print(robot_position)

    # 查Orientation表，获取机器人转向角
    robot_orientation = search(Constants.ORIENTATION, robot_position)
    print(robot_orientation)
    if robot_orientation == None:
        print(f"Failed To Get RobotOrientation, Robot id {robot_id}")
        str = f"机器人{robot_id}移动到位置{position}失败"
        log(LogType.ERROR, str)
        return False,position

    print(robot_orientation)

    # 临时性配置，207点使用dock函数
    if robot_position == 'R203_t':
        robot_position = 'R203'

    # 构造json串，发起HTTP请求
    url = f"http://{rmf_addr}:8000/tasks/robot_task"
    request_json = {
        "type": "robot_task_request",
        "fleet": "tinyRobot",
        "robot": f"{robot_name}",
        "request": {
            "category": "compose",
            "description": {
                "category": "go_to_place",
                "phases": [{
                    "activity": {
                        "category": "sequence",
                        "description": {
                            "activities": [{
                                "category": "go_to_place",
                                "description": {
                                    "waypoint": f"{robot_position}",
                                    "orientation": robot_orientation
                                }
                            }, {
                                "category": "wait_for",
                                "description": {
                                    "duration": 100
                                }
                            }]
                        }
                    }
                }]
            },
            "unix_millis_earliest_start_time": 0,
            "priority": {
                "type": "binary",
                "value": 0
            }
        }
    }
    response = requests.post(url=url, json=request_json)
    # 解析response，获得taskid
    data_json = response.json()
    task_id = ""
    try:
        task_id = data_json["state"]["booking"]["id"]
        print("task id:\t" + task_id)
    except:
        print("json格式错误")
    # while true，轮询task，直到status变为completed
    url = f"http://{rmf_addr}:8000/tasks/{task_id}/state"
    print(url)
    task_status = ""
    is_release = False
    while not task_status == "completed":
        response = requests.get(url).json()
        print(response)
        task_status = response["status"]

        # 检查是否可以释放resource
        if resource != '' and ref != 0 and is_release == False:
            if release_resource_position(robot_id,resource,ref) == True:
                viewC.releaseMutex(resource,ref)
                is_release = True

        if task_status == 'canceled':
            str = f"机器人{robot_id}移动到位置{position}取消"
            log(LogType.INFO, str)
            return False, position
        elif task_status == 'failed':
            str = f"机器人{robot_id}移动到位置{position}失败"
            log(LogType.ERROR, str)
            return False, position
        # 减少性能占用
        time.sleep(1)
        
        # TODO: 检查go_to_place出现错误的情况
    # 保底机制
    if resource != '' and ref != 0 and is_release == False:
        viewC.releaseMutex(resource,ref)
        is_release = True

    str = f"机器人{robot_id}移动到位置{position}正常"
    log(LogType.INFO, str)
    print(str)
    return True, position

# 让机器人到指定位置，同时等待100秒，返回任务的id
def go_to_place_and_wait(robot_id, position, resource='', ref=0):
    # 查找机器人表，把robot_id转换成robot_name
    robot_name = search(Constants.ROBOT, robot_id)
    print(robot_name)
    if robot_name == None:
        print(f"Failed To Get RobotName, Robot id {robot_id}")
        str = f"机器人{robot_id}移动到位置{position}失败"
        log(LogType.ERROR, str)
        return False,position
    
    if position.startswith('R'):
        # Position需要从id转换为rmf接受的格式
        robot_position = position
        print(robot_position)
    else:
        # Position需要从id转换为rmf接受的格式
        robot_position = 'R' + position
        print(robot_position)

    # 查Orientation表，获取机器人转向角
    robot_orientation = search(Constants.ORIENTATION, robot_position)
    if robot_orientation == None:
        print(f"Failed To Get RobotOrientation, Robot id {robot_id}")
        str = f"机器人{robot_id}移动到位置{position}失败"
        log(LogType.ERROR, str)
        return False,position

    print(robot_orientation)
    # 临时性配置，207点使用dock函数
    if robot_position == 'R203_t':
        robot_position = 'R203'

    # 构造json串，发起HTTP请求
    url = f"http://{rmf_addr}:8000/tasks/robot_task"
    request_json = {
        "type": "robot_task_request",
        "fleet": "tinyRobot",
        "robot": robot_name,
        "request": {
            "category": "compose",
            "description": {
                "category": "go_to_place_and_wait",
                "phases": [{
                    "activity": {
                        "category": "sequence",
                        "description": {
                            "activities": [{
                                "category": "go_to_place",
                                "description": {
                                    "waypoint": robot_position,
                                    "orientation": robot_orientation
                                }
                            }, {
                                "category": "wait_for",
                                "description": {
                                    "duration": 100
                                }
                            }]
                        }
                    }
                },
                {
                    "activity": {
                        "category": "sequence",
                        "description": {
                            "activities": [{
                                "category": "wait_for",
                                "description": {
                                    "duration": 2000000
                                }
                            }]
                        }
                    }
                }
                ]
            },
            "unix_millis_earliest_start_time": 0,
            "priority": {
                "type": "binary",
                "value": 0
            }
        }
    }
    print(request_json)
    response = requests.post(url=url, json=request_json)
    # 解析response，获得taskid
    data_json = response.json()
    task_id = ""
    try:
        task_id = data_json["state"]["booking"]["id"]
        print("taskid:\t" + task_id)
    except:
        str = f"机器人{robot_id}移动到位置{position}失败"
        log(LogType.ERROR, str)
        print("json格式错误")
    # while true，轮询task，直到status变为completed
    url = f"http://{rmf_addr}:8000/tasks/{task_id}/state"
    print(url)
    task_status = ""
    is_release = False
    while not task_status == "completed":
        response = requests.get(url).json()
        print(response)
        task_status = response["status"]
        if task_status != 'queued':
            go_to_place_status = response["completed"]
            print(go_to_place_status)
            if 1 in go_to_place_status:
               break

        # 检查是否可以释放resource
        if resource != '' and ref != 0 and is_release == False:
            if release_resource_position(robot_id,position,resource,ref) == True:
                viewC.releaseMutex(resource,ref)
                is_release = True

        if task_status == 'canceled':
            str = f"机器人{robot_id}移动到位置{position}取消"
            log(LogType.INFO, str)
            return False, position
        elif task_status == 'failed':
            str = f"机器人{robot_id}移动到位置{position}失败"
            log(LogType.ERROR, str)
            return False, position
        # 减少性能占用
        time.sleep(1)

        # TODO: 检查go_to_place出现错误的情况
    # 保底机制
    if resource != '' and ref != 0 and is_release == False:
        viewC.releaseMutex(resource,ref)
        is_release = True

    str = f"机器人{robot_id}移动到位置{position}正常"
    log(LogType.INFO, str)
    print(str)
    return True, position

def cancel_wait(task_id, phase_id):
    url = f"http://{rmf_addr}:8000/tasks/skip_phase"
    payload = {
        "type": "skip_phase_request",
        "task_id": f"{task_id}",
        "phase_id": phase_id,
        "labels": [
            "string"
        ]
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(response)
    return response.json()

# 让机器人到指定位置，同时等待100秒，返回任务的id
def go_to_place_and_dock_wait(robot_id, position,wait_time=400, resource='', ref=0):
    # 查找机器人表，把robot_id转换成robot_name
    robot_name = search(Constants.ROBOT, robot_id)
    print(robot_name)
    if robot_name == None:
        print(f"Failed To Get RobotName, Robot id {robot_id}")
        str = f"机器人{robot_id}移动到位置{position}失败"
        log(LogType.ERROR, str)
        return False,position
    
    if position.startswith('R'):
        # Position需要从id转换为rmf接受的格式
        robot_position = position
        print(robot_position)
    else:
        # Position需要从id转换为rmf接受的格式
        robot_position = 'R' + position
        print(robot_position)

    # 查Orientation表，获取机器人转向角
    robot_orientation = search(Constants.ORIENTATION, robot_position)
    if robot_orientation == None:
        print(f"Failed To Get RobotOrientation, Robot id {robot_id}")
        str = f"机器人{robot_id}移动到位置{position}失败"
        log(LogType.ERROR, str)
        return False,position

    print(robot_orientation)

    # 临时性配置，207点使用dock函数
    if robot_position == 'R203_t':
        robot_position = 'R203'

    PARAM_JSON= {
        "action": "dock",
        "param": {
            "target_dock": robot_position,
        }
    }

    # 构造json串，发起HTTP请求
    url = f"http://{rmf_addr}:8000/tasks/robot_task"
    request_json = {
        "type": "robot_task_request",
        "fleet": "tinyRobot",
        "robot": robot_name,
        "request": {
            "category": "compose",
            "description": {
                "category": "go_to_place_and_dock_wait",
                "phases": [{
                    "activity": {
                        "category": "sequence",
                        "description": {
                            "activities": [{
                                "category": "go_to_place",
                                "description": {
                                    "waypoint": robot_position,
                                    "orientation": robot_orientation
                                }
                            }, 
                            {
                                "category": "device_action",
                                "description": {
                                "device_id":robot_name,
                                "param_json_str":json.dumps(PARAM_JSON)
                                }
                            },
                            {
                                "category": "wait_for",
                                "description": {
                                    "duration": wait_time
                                }
                            }]
                        }
                    }
                },
                {
                    "activity": {
                        "category": "sequence",
                        "description": {
                            "activities": [{
                                "category": "wait_for",
                                "description": {
                                    "duration": wait_time * 10000
                                }
                            }]
                        }
                    }
                }
                ]
            },
            "unix_millis_earliest_start_time": 0,
            "priority": {
                "type": "binary",
                "value": 0
            }
        }
    }
    #"duration": 2000000
    print(json.dumps(request_json))
    response = requests.post(url=url, json=request_json)
    # 解析response，获得taskid
    data_json = response.json()
    print(data_json)
    task_id = ""
    try:
        task_id = data_json["state"]["booking"]["id"]
        print("taskid:\t" + task_id)
    except:
        str = f"机器人{robot_id}移动到位置{position}失败"
        log(LogType.ERROR, str)
        print("json格式错误")
    # while true，轮询task，直到status变为completed
    url = f"http://{rmf_addr}:8000/tasks/{task_id}/state"
    print(url)
    task_status = ""
    is_release = False
    while not task_status == "completed":
        response = requests.get(url).json()
        print(response)
        task_status = response["status"]
        if task_status != 'queued':
            #dock_status = response["phases"]["1"]["events"]["2"]["status"]
            #if dock_status == "completed":
            #   break
            go_to_place_status = response["completed"]
            print(go_to_place_status)
            if 1 in go_to_place_status:
               break

        # 检查是否可以释放resource
        if resource != '' and ref != 0 and is_release == False:
            if release_resource_position(robot_id,position,resource,ref) == True:
                viewC.releaseMutex(resource,ref)
                is_release = True

        if task_status == 'canceled':
            str = f"机器人{robot_id}移动到位置{position}取消"
            log(LogType.INFO, str)
            return False, position
        elif task_status == 'failed':
            str = f"机器人{robot_id}移动到位置{position}失败"
            log(LogType.ERROR, str)
            return False, position
        # 减少性能占用
        time.sleep(1)

        # TODO: 检查go_to_place出现错误的情况

    # 保底机制
    if resource != '' and ref != 0 and is_release == False:
        viewC.releaseMutex(resource,ref)
        is_release = True

    str = f"机器人{robot_id}移动到位置{position}正常"
    log(LogType.INFO, str)
    print(str)
    return True, position

def release_resource_position(robot_id,target,resource,ref):
    if target.startswith('R'):
        # Position需要从id转换为rmf接受的格式
        target = target
    else:
        # Position需要从id转换为rmf接受的格式
        target = 'R' + target

    if target == resource:
        return False

    # 检查resource的位置
    position_str = reader.get_resource_items_by_id(resource,reader)
    position = json.loads(position_str)
    x = float(position["x"])
    y = float(position["y"])
    z = float(position["z"])

    # 检查机器人位置
    px = 0.0
    py = 0.0
    pz = 0.0

    # 查找机器人表，把robot_id转换成robot_name
    robot_name = search(Constants.ROBOT, robot_id)
    if robot_name == None:
        print(f"Failed To Get RobotName, Robot id {robot_id}")
        return False

    # 向rmf发送查询请求
    fleet = "tinyRobot"
    url = f"http://{rmf_addr}:8000/fleets/{fleet}/state"
    print(url)

    response = requests.get(url).json()
    robots = response["robots"]
    # 遍历整个车队 寻找指定的机器人
    for (robot,value) in robots.items():
        print(robot)
        if robot == robot_name:
            location = value["location"]
            px = abs(float(location["x"]))/0.03
            py = abs(float(location["y"]))/0.03

    # 检查机器人是否移动超过某个区域
    dx = abs(x - px)
    dy = abs(y - py)

    # 计算距离
    distance = dx * dx + dy * dy #TODO: 加入转向角
    if math.sqrt(distance) >= 30: #真实距离阈值 90cm时
        print("机器人当前位置" + str(px) + ' ' + str(py))
        print("位置" + resource + ' ' + str(x) + ' ' + str(y))
        print("判断位置可以被释放")
        return True

    return False

def cancel_wait(task_id, phase_id):
    url = f"http://{rmf_addr}:8000/tasks/skip_phase"
    payload = {
        "type": "skip_phase_request",
        "task_id": f"{task_id}",
        "phase_id": phase_id,
        "labels": [
            "string"
        ]
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(response)
    return response.json()

def end_wait(robot_id):
    # 查找机器人表，把robot_id转换成robot_name
    robot_name = search(Constants.ROBOT, robot_id)
    if robot_name == None:
        print(f"Failed To Get RobotName, Robot id {robot_id}")
        return False

    task_id = ""
    fleet = "tinyRobot"
    url = f"http://{rmf_addr}:8000/fleets/{fleet}/state"
    print(url)
    response = requests.get(url).json()
    print(response)
    robots = response["robots"]
    print(robots)
    # 遍历整个车队 寻找指定的机器人
    for (robot,value) in robots.items():
        print(robot)
        if robot == robot_name:
            task_id = value["task_id"]
            print(task_id)

    if task_id != "":
        # TODO: 查询任务，检查该任务是否处于等待状态
        response = cancel_wait(task_id,2)
        # TODO: if reponse == <200>,检查取消任务是否成功
        return True
    else:
        return False

def cancel_task(task_id):
    url = f"http://{rmf_addr}:8000/tasks/cancel_task"
    payload = {
        "type": "cancel_task_request",
        "task_id": f"{task_id}",
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(response)
    return response.json()

# 控制云台升降
def go_up_and_down(robot_id, height):
    robot_name = search(Constants.ROBOT, robot_id)
    print(robot_name)
    if robot_name == None:
        print(f"Failed To Get RobotName, Robot id {robot_id}")
        return False

    # height: low;middle;high TODO: 做输入检查
    # 构造json串，发起HTTP请求
    url = f"http://{rmf_addr}:8000/tasks/robot_task"
    param_json = {
        "action":"go_up_and_down",
        "param":{
            "height": height
        }
    }

    # 构造json串，发起HTTP请求
    request_json = {
        "type": "robot_task_request",
        "fleet": "tinyRobot",
        "robot": robot_name,
        "request": {
            "category": "compose",
            "description": {
                "category": "go_up_and_down",
                "phases": [{
                    "activity": {
                        "category": "sequence",
                        "description": {
                            "activities": [{
                                "category": "device_action",
                                "description": {
                                    "device_id": robot_id,
                                    "param_json_str":json.dumps(param_json)
                                }
                            }]
                        }
                    }
                }]
            },
            "unix_millis_earliest_start_time": 0,
            "priority": {
                "type": "binary",
                "value": 0
            }
        }
    }
    print(request_json)
    response = requests.post(url=url, json=request_json)
    # 解析response，获得taskid
    data_json = response.json()
    task_id = ""
    try:
        task_id = data_json["state"]["booking"]["id"]
        print("taskid:\t" + task_id)
    except:
        print("json格式错误")
    # while true，轮询task，直到status变为completed
    url = f"http://{rmf_addr}:8000/tasks/{task_id}/state"
    print(url)
    task_status = ""
    while not task_status == "completed":
        response = requests.get(url).json()
        print(response)
        task_status = response["status"]
        # 减少性能占用
        time.sleep(1)

        # TODO：检查任务是否执行失败
    str = f"升降机{robot_id}升降到{height}正常"
    log(LogType.INFO, str)
    print(str)
    return task_status, height

# 控制移动机械臂夹取
def grab2(robot_id,position):
    robot_name = search(Constants.ROBOT, robot_id)
    print(robot_name)
    if robot_name == None:
        print(f"Failed To Get RobotName, Robot id {robot_id}")
        return False

    # 查表，将Position转换为x,y,z,rx,ry,rz,speed
    param = search(Constants.GRAB, position)
    if param == None:
        print(f"Failed To Get Param, Robot id {robot_id}")
        str = f"机械臂{robot_id}夹取位置{position}失败"
        log(LogType.ERROR, str)
        return False,position

    x = param[0]
    y = param[1]
    z = param[2]
    rx = param[3]
    ry = param[4]
    rz = param[5]
    speed = param[6]

    # 构造json串，发起HTTP请求
    # url = f"http://{rmf_addr}:8000/tasks/dispatch_task"
    url = f"http://{rmf_addr}:8000/tasks/robot_task"
    param_json = {
        "action":"grab",
        "param":{
            "position": position,
            "x": x,
            "y": y,
            "z": z,
            "rx": rx,
            "ry": ry,
            "rz": rz,
            "speed": speed
        }
    }

    request_json = {
        "type": "robot_task_request",
        "fleet": "tinyRobot",
        "robot": robot_name,
        "request": {
            "category": "compose",
            "description": {
                "category": "grab",
                "phases": [{
                    "activity": {
                        "category": "sequence",
                        "description": {
                            "activities": [{
                                "category": "device_action",
                                "description": {
                                    "device_id": robot_id,
                                    "param_json_str":json.dumps(param_json)
                                }
                            }]
                        }
                    }
                }]
            },
            "unix_millis_earliest_start_time": 0,
            "priority": {
                "type": "binary",
                "value": 0
            }
        }
    }
    response = requests.post(url=url, json=request_json)
    # 解析response，获得taskid
    data_json = response.json()
    task_id = ""
    try:
        task_id = data_json["state"]["booking"]["id"]
        print("taskid:\t" + task_id)
    except:
        str = f"机械臂{robot_id}夹取位置{position}失败"
        log(LogType.ERROR, str)
        print("json格式错误")
    # while true，轮询task，直到status变为completed
    url = f"http://{rmf_addr}:8000/tasks/{task_id}/state"
    print(url)
    task_status = ""
    while not task_status == "completed":
        response = requests.get(url).json()
        task_status = response["status"]
        print(response)
        
        if task_status == 'failed':
            str = f"机械臂{robot_id}夹取位置{position}失败"
            log(LogType.ERROR, str)
            return False, position

        if task_status == 'canceled':
            str = f"机械臂{robot_id}夹取位置{position}失败"
            log(LogType.ERROR, str)
            return False, position

        # 减少性能占用
        time.sleep(1)
        # TODO：检查任务是否执行失败
    str = f"机械臂{robot_id}夹取位置{position}正常"
    log(LogType.INFO, str)
    print(str)

    return True,position

def grab(robot_id,position):
    return grab2(robot_id,position)

    #if robot_id == '105':
    #    return grab2(robot_id,position)
    #else:
    #    return grab1(robot_id,position)


# 控制固定机械臂夹取
def grab1(robot_id,position):
    # 重试次数
    count = 0

    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, robot_id)
    if ip == None:
        return False,position

    addr = ip

    # cameraPost接口是异步的
    url = f"http://{addr}:7070/grab"
    print(url)

    # 查表，将Position转换为x,y,z,rx,ry,rz,speed
    param = search(Constants.GRAB, position)
    if param == None:
        print(f"Failed To Get Param, Robot id {robot_id}")
        str = f"机械臂{robot_id}夹取位置{position}失败"
        log(LogType.ERROR, str)
        return False,position

    x = param[0]
    y = param[1]
    z = param[2]
    rx = param[3]
    ry = param[4]
    rz = param[5]
    speed = param[6]

    request_json = {
        "action":{
            "class":"grab",
            "object":"grabn"
        },
        "param":{
            "position": position,
            "x": x,
            "y": y,
            "z": z,
            "rx": rx,
            "ry": ry,
            "rz": rz,
            "speed": speed
        }
    }

    print(request_json)
    response = requests.post(url=url, json=request_json)
    # 解析response，获得taskid
    data_json = response.json()
    print(data_json)
    str = f"机械臂{robot_id}夹取位置{position}正常"
    log(LogType.INFO, str)
    print(str)
    return True,position

def loosen(robot_id,position):
    return loosen2(robot_id,position)
    #if robot_id == '105':
    #    return loosen2(robot_id,position)
    #else:
    #    return loosen1(robot_id,position)

# 控制固定机械臂夹取
def loosen1(robot_id,position):
    # 重试次数
    count = 0

    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, robot_id)
    if ip == None:
        return False,position

    addr = ip

    # cameraPost接口是异步的
    url = f"http://{addr}:7070/loosen"
    print(url)

    # 查表，将Position转换为x,y,z,rx,ry,rz,speed
    param = search(Constants.LOOSEN, position)
    if param == None:
        print(f"Failed To Get Param, Robot id {robot_id}")
        str = f"机械臂{robot_id}放置位置{position}失败"
        log(LogType.ERROR, str)
        return False,position

    x = param[0]
    y = param[1]
    z = param[2]
    rx = param[3]
    ry = param[4]
    rz = param[5]
    speed = param[6]

    request_json = {
            "action":{
                "class":"loosen",
                "object":"loosenn"
            },
            "param":{
                "position": position,
                "x": x,
                "y": y,
                "z": z,
                "rx": rx,
                "ry": ry,
                "rz": rz,
                "speed": speed
            }
    }

    # print(json.dumps(request_json))
    response = requests.post(url=url, json=request_json)
    # 解析response，获得taskid
    data_json = response.json()
    str = f"机械臂{robot_id}放置位置{position}正常"
    log(LogType.INFO, str)
    print(str)
    return True,position


# 控制移动机械臂松开
def loosen2(robot_id,position):
    robot_name = search(Constants.ROBOT, robot_id)
    print(robot_name)
    if robot_name == None:
        print(f"Failed To Get RobotName, Robot id {robot_id}")
        return False

    # 查表，将Position转换为x,y,z,rx,ry,rz,speed
    param = search(Constants.LOOSEN, position)
    if param == None:
        print(f"Failed To Get Param, Robot id {robot_id}")
        str = f"机械臂{robot_id}放置位置{position}失败"
        log(LogType.ERROR, str)
        return False,position

    x = param[0]
    y = param[1]
    z = param[2]
    rx = param[3]
    ry = param[4]
    rz = param[5]
    speed = param[6]

    # 构造json串，发起HTTP请求
    # url = f"http://{rmf_addr}:8000/tasks/dispatch_task"
    url = f"http://{rmf_addr}:8000/tasks/robot_task"
    param_json = {
        "action":"loosen",
        "param":{
            "position": position,
            "x": x,
            "y": y,
            "z": z,
            "rx": rx,
            "ry": ry,
            "rz": rz,
            "speed": speed
        }
    }

    request_json = {
        "type": "robot_task_request",
        "fleet": "tinyRobot",
        "robot": robot_name,
        "request": {
            "category": "compose",
            "description": {
                "category": "loosen",
                "phases": [{
                    "activity": {
                        "category": "sequence",
                        "description": {
                            "activities": [{
                                "category": "device_action",
                                "description": {
                                    "device_id": robot_id,
                                    "param_json_str":json.dumps(param_json)
                                }
                            }]
                        }
                    }
                }]
            },
            "unix_millis_earliest_start_time": 0,
            "priority": {
                "type": "binary",
                "value": 0
            }
        }
    }
    print(request_json)
    response = requests.post(url=url, json=request_json)
    # 解析response，获得taskid
    data_json = response.json()
    task_id = ""
    try:
        task_id = data_json["state"]["booking"]["id"]
        print("taskid:\t" + task_id)
    except:
        str = f"机械臂{robot_id}放置位置{position}失败"
        log(LogType.ERROR, str)
        print("json格式错误")
    # while true，轮询task，直到status变为completed
    url = f"http://{rmf_addr}:8000/tasks/{task_id}/state"
    print(url)
    task_status = ""
    while not task_status == "completed":
        response = requests.get(url).json()
        print(response)
        task_status = response["status"]
        
        if task_status == 'failed':
            str = f"机械臂{robot_id}放置位置{position}失败"
            log(LogType.ERROR, str)
            return False, position

        if task_status == 'canceled':
            str = f"机械臂{robot_id}放置位置{position}失败"
            log(LogType.ERROR, str)
            return False, position
        # 减少性能占用
        time.sleep(1)

        # TODO：检查任务是否执行失败

    str = f"机械臂{robot_id}放置位置{position}正常"
    log(LogType.INFO, str)
    print(str)
    return True,position

def cameraPost(id,action):
    # 重试次数
    count = 0

    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        if action == 0:
            str = f"摄像头{id}摄像能力关闭失败"
        else:
            str = f"摄像头{id}摄像能力开启失败"
        log(LogType.ERROR, str)
        return False, Status.CAMERA_UNKNOWN

    addr = ip

    # cameraPost接口是异步的
    url = f"http://{addr}:8001/api/cameraPost"
    print(url)

    request_json = {
        "id": int(id),
        "action": action
    }

    print(request_json)
    response = requests.post(url=url, json=request_json)
    # 解析response
    data_json = response.json()
    while data_json["status"] != Status.STATUS_OK:
        print("retry cameraPost")
        time.sleep(5)
        response = requests.post(url=url, json=request_json)
        print(response)
        data_json = response.json()
        count = count + 1
        if count == 3:
            if action == 0:
                str = f"摄像头{id}摄像能力关闭失败"
            else:
                str = f"摄像头{id}摄像能力开启失败"
            log(LogType.ERROR, str)
            return False, Status.CAMERA_UNKNOWN
    
    return True,data_json["cameraStatus"]

def cameraGet(id):
    count = 0
    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        return False, Status.CAMERA_UNKNOWN

    addr = ip

    params = {
        "id": int(id)
    }

    # cameraGet接口是同步的
    url = f"http://{addr}:8001/api/cameraGet"

    print(url)
    response = requests.get(url=url,params=params)

    data_json = response.json()
    while data_json["status"] != Status.STATUS_OK:
        print("retry cameraGet")
        time.sleep(1)
        response = requests.get(url=url, params=params)
        data_json = response.json()
        count = count + 1
        if count == 3:
            return (False, Status.CAMERA_UNKNOWN)
    return (True,data_json["cameraStatus"])

def cameraAbility(id):
    # 重试次数
    count = 0

    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        if action == 0:
            str = f"摄像头{id}摄像能力关闭失败"
        else:
            str = f"摄像头{id}摄像能力开启失败"
        log(LogType.ERROR, str)
        return False, Status.CAMERA_UNKNOWN

    addr = ip

    # cameraPost接口是异步的
    url = f"http://{addr}:8080/api/AbilitySupport"
    print(url)
    params = {}
    params=params

    response = requests.get(url=url, params=params)
    # 解析response
    data_json = response.json()
    for data in data_json:
#         print(data)
        data_str = json.dumps(data)
        if ('raspberrypi-' + id) in data_str:
            print("find " + id)
            print(data["id"])
            return data["id"]

    return 0
#     print(data_json)

#     print(data_json[0])

def cameraStart(id):
    # 重试次数
    count = 0

    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        if action == 0:
            str = f"摄像头{id}摄像能力关闭失败"
        else:
            str = f"摄像头{id}摄像能力开启失败"
        log(LogType.ERROR, str)
        return False, Status.CAMERA_UNKNOWN
    abilityId = cameraAbility(id)
    addr = ip

    # cameraPost接口是异步的
    url = f"http://{addr}:8080/api/AbilityRequest"
    print('-----------')
    print(url)

    request_json = {
        "abilityName": "camera",
        "cmd": "start",
        "IPCPort": 0,
        "connectIP":"127.0.0.1",
        "connectPort": 0,
        "abilityId": abilityId,
        "abilityInstanceId": int(id)
    }

    print(request_json)
    response = requests.post(url=url, json=request_json)
    print(response)
    return True
    # 解析response
    #data_json = response.json()
    #print(data_json)
    #return True,data_json["cameraStatus"]

def cameraConnect(id):
    # 重试次数
    count = 0

    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        if action == 0:
            str = f"摄像头{id}摄像能力关闭失败"
        else:
            str = f"摄像头{id}摄像能力开启失败"
        log(LogType.ERROR, str)
        return False, Status.CAMERA_UNKNOWN
    abilityId = cameraAbility(id)
    addr = ip

    # cameraPost接口是异步的
    url = f"http://{addr}:8080/api/AbilityRequest"
    print('-----------')
    print(url)

    request_json = {
        "abilityName": "camera",
        "cmd": "connect",
        "IPCPort": 0,
        "connectIP":"127.0.0.1",
        "connectPort": 0,
        "abilityId": abilityId,
        "abilityInstanceId": int(id)
    }

    print(request_json)
    response = requests.post(url=url, json=request_json)
    print(response)
    return True
    # 解析response

def cameraDesire(id):
    # 重试次数
    count = 0

    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        if action == 0:
            str = f"摄像头{id}摄像能力关闭失败"
        else:
            str = f"摄像头{id}摄像能力开启失败"
        log(LogType.ERROR, str)
        return False, Status.CAMERA_UNKNOWN

    abilityId = cameraAbility(id)
    addr = ip

    # cameraPost接口是异步的
    url = f"http://{addr}:8080/api/AbilityDesireUpdate"
    print('-----------')
    print(url)

    request_json = {
                    "abilityInstanceId" : int(id),
                    "desire":
                    {
                        "switch":True
                    }
                    }
    print(request_json)
    response = requests.post(url=url, json=request_json)
    print(response)
    return True
    # 解析response

def cameraDisconnect(id):
    # 重试次数
    count = 0

    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        if action == 0:
            str = f"摄像头{id}摄像能力关闭失败"
        else:
            str = f"摄像头{id}摄像能力开启失败"
        log(LogType.ERROR, str)
        return False, Status.CAMERA_UNKNOWN
    abilityId = cameraAbility(id)
    addr = ip

    # cameraPost接口是异步的
    url = f"http://{addr}:8080/api/AbilityRequest"
    print('-----------')
    print(url)

    request_json = {
        "abilityName": "camera",
        "cmd": "disconnect",
        "IPCPort": 0,
        "connectIP":"127.0.0.1",
        "connectPort": 0,
        "abilityId": abilityId,
        "abilityInstanceId": int(id)
    }

    print(request_json)
    response = requests.post(url=url, json=request_json)
    print(response)
    return True

def camera1(id,action):
    count = 0
    # 发送Post请求
    (success,status) = cameraPost(id,action)
    if not success:
        return False

    (success,status) = cameraGet(id)
    while action == 0 and (not status in [Status.CAMERA_OFFLINE, Status.CAMERA_READY]):
        count = count + 1
        (success,status) = cameraGet(id)
        time.sleep(1)
        if count >= 3:
            str = f"摄像头{id}摄像能力关闭失败"
            log(LogType.ERROR, str)
            return False
    
    while action == 1 and (not status in [Status.CAMERA_WORKING]):
        count = count + 1
        (success,status) = cameraGet(id)
        time.sleep(1)
        if count >= 3:
            str = f"摄像头{id}摄像能力开启失败"
            print(str)
            log(LogType.ERROR, str)
            return False

    if action == 0:
        str = f"摄像头{id}摄像能力关闭正常"
    else:
        str = f"摄像头{id}摄像能力开启正常"
    log(LogType.INFO, str)
    return True

def camera2(id,action):
    if action == 1:
        success = cameraStart(id)
        if not success:
            str = f"摄像头{id}摄像能力开启失败"
            log(LogType.ERROR, str)
            return False

        success = cameraConnect(id)
        if not success:
            str = f"摄像头{id}摄像能力开启失败"
            log(LogType.ERROR, str)
            return False

        success = cameraDesire(id)
        if not success:
            str = f"摄像头{id}摄像能力开启失败"
            log(LogType.ERROR, str)
            return False

        str = f"摄像头{id}摄像能力开启正常"
        log(LogType.INFO, str)
    else:
        success = cameraDisconnect(id)
        if not success:
            str = f"摄像头{id}摄像能力关闭失败"
            log(LogType.ERROR, str)
            return False

        str = f"摄像头{id}摄像能力关闭正常"
        log(LogType.INFO, str)
    return True

def camera(id,action):
    return camera_modify(int(id),action)

def previewGet(id,cam_id):
    count = 0
    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        return False, Status.PREVIEW_UNKNOWN

    addr = ip

    params = {
        "id": int(cam_id)
    }

    # previewGet接口是同步的
    url = f"http://{addr}:8001/api/previewGet"

    print(url)
    response = requests.get(url=url,params=params)

    data_json = response.json()
    while data_json["status"] != Status.STATUS_OK:
        print("retry preview Get")
        time.sleep(1)
        response = requests.get(url=url, params= params)
        data_json = response.json()
        count = count + 1
        if count == 5:
            return False, Status.PREVIEW_UNKNOWN
    
    return True,data_json["previewStatus"]

def previewPost(id,cam_id,screen_id,screen_position_id,action):
    # 重试次数
    count = 0
    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        if action == 0:
            str = f"播放主机{id}关闭摄像头{cam_id}视频流失败"
        else:
            str = f"播放主机{id}开启摄像头{cam_id}视频流失败"
        log(LogType.ERROR, str)
        return False, Status.PREVIEW_UNKNOWN

    addr = ip

    # previewPost接口是异步的
    url = f"http://{addr}:8001/api/previewPost"
    print(url)

    request_json = {
        "id": int(id),
        "cam_id": int(cam_id),
        "screen_id": int(screen_id),
        "screen_position_id": int(screen_position_id),
        "action": action
    }

    print(request_json)
    response = requests.post(url=url, json=request_json)
    # 解析response
    data_json = response.json()
    while data_json["status"] != Status.STATUS_OK:
        print("retry preview Post")
        time.sleep(1)
        response = requests.post(url=url, json=request_json)
        print(response)
        data_json = response.json()
        count = count + 1
        if count == 3:
            if action == 0:
                str = f"播放主机{id}关闭摄像头{cam_id}视频流失败"
            else:
                str = f"播放主机{id}开启摄像头{cam_id}视频流失败"
            log(LogType.ERROR, str)
            print(str)
            return False, Status.PREVIEW_UNKNOWN
    
    return True,data_json["previewStatus"]

def preview(id,cam_id,screen_id,screen_position_id,action):
    count = 0
    # 发送Post请求
    (success,status) = previewPost(id,cam_id,screen_id,screen_position_id,action)
    if not success:
        return False

    (success,status) = previewGet(id,cam_id)
    while action == 0 and (not status in [Status.PREVIEW_OFFLINE, Status.PREVIEW_READY]):
        count = count + 1
        (success,status) = previewGet(id,cam_id)
        print(status)
        time.sleep(1)
        if count >= 3:
            str = f"播放主机{id}关闭摄像头{cam_id}视频流失败"
            print(str)
            log(LogType.ERROR, str)
            return False
    
    while action == 1 and (not status in [Status.PREVIEW_WORKING]):
        count = count + 1
        (success,status) = previewGet(id,cam_id)
        print(status)
        time.sleep(1)
        if count >= 3:
            str = f"播放主机{id}开启摄像头{cam_id}视频流失败"
            print(str)
            log(LogType.ERROR, str)
            return False

    if action == 0:
        str = f"播放主机{id}关闭摄像头{cam_id}视频流正常"
    else:
        str = f"播放主机{id}开启摄像头{cam_id}视频流正常"
    log(LogType.INFO, str)
    print(str)
    return True


def identifyGet(id,target):
    count = 0
    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, "118")
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        return False, Status.INDENTIFY_UNKNOWN

    params = {
        "id": int(id),
        "target": target
    }

    addr = ip

    # identifyGet接口是同步的
    url = f"http://{addr}:8001/api/identifyGet"

    print(url)
    response = requests.get(url=url,params= params)

    data_json = response.json()
    print(data_json)
    while (data_json["status"] != Status.STATUS_OK) or (data_json["identifyServerStatus"] != Status.INDENTIFY_SERVER_WORKING):
        print("retry indentify Get")
        time.sleep(1)
        response = requests.get(url=url, params=params)
        data_json = response.json()
        count = count + 1
        if count == 5:
            return False, Status.INDENTIFY_UNKNOWN
    
    if data_json["identifyStatus"] != Status.INDENTIFY_EXIST:
        str = f"识别主机{id}识别{target}失败"
        log(LogType.ERROR, str)
    return True,data_json["identifyStatus"]

def identifyPost(id,action):
    # 重试次数
    count = 0
    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, "118")
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        if action == 0:
            str = f"识别主机{id}关闭识别能力失败"
        else:
            str = f"识别主机{id}开启识别能力失败"
        log(LogType.ERROR, str)
        return False, Status.INDENTIFY_SERVER_UNKNOWN

    addr = ip
    # identifyPost接口是异步的
    url = f"http://{addr}:8001/api/identifyPost"
    print(url)

    request_json = {
        "id": int(id),
        "action": action
    }

    print(request_json)
    response = requests.post(url=url, json=request_json)
    # 解析response
    data_json = response.json()
    while data_json["status"] != Status.STATUS_OK:
        print("retry identify Post")
        time.sleep(1)
        response = requests.post(url=url, json=request_json)
        print(response)
        data_json = response.json()
        count = count + 1
        if count == 3:
            print(f"Failed To Get IP, id {id}")
            if action == 0:
                str = f"识别主机{id}关闭识别能力失败"
            else:
                str = f"识别主机{id}开启识别能力失败"
            log(LogType.ERROR, str)
            #print(str)
            return False, Status.INDENTIFY_SERVER_UNKNOWN
    
    if action == 0:
        str = f"识别主机{id}关闭识别能力正常"
    else:
        str = f"识别主机{id}开启识别能力正常"
    log(LogType.INFO, str)
    print(data_json)
    return True,data_json["identifyServerStatus"]

def indentify(id,target):
    (success,status) = identifyPost(id,1)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN
    
    time.sleep(1)

    (success,status) = identifyGet(id,target)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN
    else:
        # identifyPost(id,0)
        time.sleep(1)
        return True,status

def identify_get(id,target):
    (success,status) = identifyGet("112",target)
    if success:
        return True,status

    (success,status) = identifyGet("113",target)
    if success:
        return True,status

    (success,status) = identifyGet("114",target)
    if success:
        return True,status

    (success,status) = identifyGet("115",target)
    if success:
        return True,status

    return False, Status.INDENTIFY_UNKNOWN

def identify_open(id,target):
    (success,status) = identifyPost("112",1)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN

    (success,status) = identifyPost("113",1)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN

    (success,status) = identifyPost("114",1)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN

    (success,status) = identifyPost("115",1)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN

    return True,status

def identify_close(id,target):
    (success,status) = identifyPost("112",0)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN

    (success,status) = identifyPost("113",0)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN

    (success,status) = identifyPost("114",0)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN

    (success,status) = identifyPost("115",0)
    if not success:
        return False, Status.INDENTIFY_UNKNOWN

    return True,status

def identify(id,target):
    if target == 1:
        return identify_open(id,target)
    elif target == 0:
        return identify_close(id,target)
    else:
        return identify_get(id,target)

def processPost(id,speed,action):
    print(id)
    print(speed)
    # 重试次数
    count = 0
    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        if action == 0:
            str = f"流水线{id}加工关闭失败"
        else:
            str = f"流水线{id}加工开启失败"
        log(LogType.ERROR, str)
        return False, Status.PROCESS_UNKNOWN

    addr = ip

    # previewPost接口是异步的
    url = f"http://{addr}:8001/api/processPost"
    print(url)

    request_json = {
        "id": int(id),
        "speed": speed,
        "action": action
    }

    print(request_json)
    response = requests.post(url=url, json=request_json)
    # 解析response
    data_json = response.json()
    while data_json["status"] != Status.STATUS_OK:
        print("retry process Post")
        time.sleep(1)
        response = requests.post(url=url, json=request_json)
        print(response)
        data_json = response.json()
        count = count + 1
        if count == 3:
            if action == 0:
                str = f"流水线{id}加工关闭失败"
            else:
                str = f"流水线{id}加工开启失败"
            log(LogType.ERROR, str)
            print(str)
            return False, Status.PROCESS_UNKNOWN
    
    return True,data_json["processStatus"]

def processGet(id):
    count = 0
    # 查表，确定设备ip
    ip = search(Constants.IP_LIST, id)
    if ip == None:
        print(f"Failed To Get IP, id {id}")
        return False, Status.PROCESS_UNKNOWN

    addr = ip

    params = {
        "id": int(id)
    }

    # previewGet接口是同步的
    url = f"http://{addr}:8001/api/processGet"

    print(url)
    response = requests.get(url=url,params=params)

    data_json = response.json()
    while data_json["status"] != Status.STATUS_OK:
        print("retry process Get")
        time.sleep(1)
        response = requests.get(url=url, params= params)
        data_json = response.json()
        count = count + 1
        if count == 3:
            return False, Status.PROCESS_UNKNOWN
    
    return True,data_json["processStatus"]

def process(id,speed,action):
    speed = float(speed)
    # 需要将speed转换
    speed = speed / 100

    count = 0
    # 发送Post请求
    (success,status) = processPost(id,speed,action)
    if not success:
        return False

    (success,status) = processGet(id)
    while action == 0 and (not status in [Status.PROCESS_OFFLINE, Status.PROCESS_READY]):
        count = count + 1
        (success,status) = processGet(id)
        time.sleep(1)
        if count >= 3:
            str = f"流水线{id}加工关闭失败"
            print(str)
            log(LogType.ERROR, str)
            return False
    
    while action == 1 and (not status in [Status.PROCESS_WORKING]):
        count = count + 1
        (success,status) = processGet(id)
        time.sleep(1)
        if count >= 3:
            str = f"流水线{id}加工开启失败"
            print(str)
            log(LogType.ERROR, str)
            return False

    if action == 0:
        str = f"流水线{id}加工关闭正常"
    else:
        str = f"流水线{id}加工开启正常"
    log(LogType.INFO, str)
    print(str)
    return True
