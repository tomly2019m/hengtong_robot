from cmd import grab,loosen
from robotflow_v2.constants.Constants import *
if __name__ == '__main__':
    # 解析输入参数 获取到robot id 和 workpiece id
    arm_id = '106'
    # workpiece_current_position = 'arm2-belt01'
    workpiece_current_position = 'arm2-ship2'
    #workpiece_target_position = 'arm2-ship1'
    workpiece_target_position = 'arm2-belt02'
    print(GRAB[workpiece_current_position])
    print(LOOSEN[workpiece_target_position])

    (task_status,position) = grab(arm_id,workpiece_current_position)


    (task_status,position) = loosen(arm_id,workpiece_target_position)
    # print(task_status)
    # print(position)
