from cmd import *

def open():
    success = camera("112", 1)
    if not success:
        pass

    success = camera("113", 1)
    if not success:
        pass

    success = camera("114", 1)
    if not success:
        pass

    success = camera("115", 1)
    if not success:
        pass


def close():
    success = camera("112", 0)
    if not success:
        pass

    success = camera("113", 0)
    if not success:
        pass

    success = camera("114", 0)
    if not success:
        pass

    success = camera("115", 0)
    if not success:
        pass

if __name__ == '__main__':
#     cameraAbility("112")
#     cameraStart("112")
#     cameraConnect("112")
#     cameraDesire("112")
#
#     cameraStart("113")
#     cameraConnect("113")
#     cameraDesire("113")
#
#     cameraStart("114")
#     cameraConnect("114")
#     cameraDesire("114")
#
#     cameraStart("115")
#     cameraConnect("115")
#     cameraDesire("115")
#
#     cameraDisconnect("112")
#     cameraDisconnect("113")
#     cameraDisconnect("114")
#     cameraDisconnect("115")
    
#     camera("112",1)
#     camera("113",1)
#     camera("114",1)
#     camera("115",1)

    camera("112",0)
    camera("113",0)
    camera("114",0)
    camera("115",0)

#     open()
    # close()
