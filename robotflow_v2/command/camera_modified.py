import time
from robotflow_v2.command.framework import mustUnique, abilitySupportForName, \
    abilityRunning, RunningAbility


def cameraStart(framework_addr: str, *, rpiId: int, abilityInstanceId=0) -> RunningAbility:
    ability_support = mustUnique(
        [a for a in abilitySupportForName(
            framework_addr,
            name="camera")
         if (str(rpiId) in str(a.depends))])
    ability = ability_support.spawn(abilityInstanceId)
    return ability

def ensureCameraOpen(camera_ability: RunningAbility) -> bool:
    retry_count = 0
    while True:
        res = camera_ability.get_status().json()
        print(res)
        if res["status"]["switch"] == True:
            return True
        retry_count += 1
        if retry_count > 10:
            return False
        time.sleep(0.5)



def ensureActivate(framework_addr: str,*, rpiId: int):
    print("查看现有能力")
    abilities = abilityRunning(framework_addr)
    for a in abilities:
        if a.abilityName != 'camera':
            continue
        if a.status == "STANDBY":
            a.connect().show("能力connect完毕").put_desire({"switch": True}).show("put desire 完毕")
            return True
        if a.status == "RUNNING":
            a.put_desire({"switch": True}).show("put desire 完毕")
            return True
    print("无现有相机能力，尝试启动新能力")
    camera_ability = cameraStart(framework_addr, rpiId = rpiId,abilityInstanceId=rpiId)\
        .show("能力start完毕")\
        .connect()\
        .show("能力connect完毕")\
        .put_desire({"switch": True})\
        .show("能力设置desire完毕")
    print("camera now pushing stream")
    return ensureCameraOpen(camera_ability)

def ensureTerminate(framework_addr: str,*, rpiId: int) -> bool:
    abilities = abilityRunning(framework_addr)
    for a in abilities:
        if a.abilityName != 'camera':
            continue
        a.terminate().show()
    return True

ON = 1
OFF = 0

IP_of_id = {112: "192.168.1.211",113: "192.168.1.212",114: "192.168.1.213",115: "192.168.1.215"}

def camera(cam_id, action) -> bool:
    addr = IP_of_id[cam_id]
    action = ON if  int(action) == 1 else OFF
    if action == ON:
        return ensureActivate(addr,rpiId=cam_id)
    else:
        return ensureTerminate(addr,rpiId=cam_id)
    
# if __name__ == '__main__':
#     from sys import argv
#     cam_id = int(argv[1])
#     addr = IP_of_id[cam_id]
#     action = ON if  int(argv[2]) == 1 else OFF
#     if action == ON:
#         ensureActivate(addr,rpiId=cam_id)
#     else:
#         ensureTerminate(addr,rpiId=cam_id)
    
    # cameraStart(argv[1], rpiId = int(argv[2]))\
    #     .show("能力start完毕")\
    #     .connect()\
    #     .show("能力connect完毕")\
    #     .put_desire({"switch": True})\
    #     .show("能力设置desire完毕")
