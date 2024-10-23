from cmd import preview
import time

def open():
    success = preview("117","112","121","131",1)
    if not success:
        pass

    success = preview("117","113","121","132",1)
    if not success:
        pass

    success = preview("117","114","121","133",1)
    if not success:
        pass

    success = preview("117","115","121","134",1)
    if not success:
        pass


def close():
    success = preview("117","112","121","131",0)
    if not success:
        pass

    success = preview("117","113","121","132",0)
    if not success:
        pass

    success = preview("117","114","121","133",0)
    if not success:
        pass

    success = preview("117","115","121","134",0)
    if not success:
        pass

if __name__ == '__main__':
    open()
    time.sleep(10)
    close()

