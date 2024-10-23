import time
import requests
from typing_extensions import NamedTuple, Self, TypeVar,Any

T = TypeVar("T")


class RunningAbility(NamedTuple):
    abilityName: str
    IPCPort: int
    abilityPort: int
    status: str
    last_update: int
    abilityId: int
    abilityInstanceId: int

    ip: str = ""
    "并非为消息包所必须"

    @staticmethod
    def from_json(d: dict,ip : str = "") -> Self:
        return RunningAbility(**d,ip=ip)

    def show(self, message=None) -> Self:
        if message:
            print(message)
        print(self)
        return self

    def connect(self) -> Self:
        if(self.status == "RUNNING"): return self
        assert len(self.ip) >0
        #print(self.IPCPort)
        new_info = abilityRequest(
            self.ip,
            cmd="connect",
            abilityName=self.abilityName,
            abilityId=self.abilityId,
            abilityInstanceId=self.abilityInstanceId,
            connectPort=self.IPCPort)
        # return RunningAbility.from_json( new_info.json(),ip=self.ip)
        return getAbilityRunningInfo(self.abilityInstanceId, self.ip, "RUNNING")
    def terminate(self) -> Self:
        assert len(self.ip) >0
        new_info = abilityRequest(
            self.ip,
            cmd="terminate",
            abilityName=self.abilityName,
            abilityId=self.abilityId,
            abilityInstanceId=self.abilityInstanceId,
            connectPort=self.IPCPort)
        # return RunningAbility.from_json( new_info.json(),ip=self.ip)
        terminate_msg = getAbilityRunningInfo(self.abilityInstanceId, self.ip, "TERMINATE")
        if checkExist(self.ip, terminate_msg.abilityInstanceId) == False:
            return terminate_msg
        raise Exception("failed to terminate ability")

    def put_desire(self, desire: Any) -> Self:
        url = f"http://{self.ip}:8080/api/AbilityDesireUpdate"
        payload = {"abilityInstanceId": self.abilityInstanceId,
                   "abilityPort": self.abilityPort,
                   "desire": desire}
        response = requests.post(url=url, json=payload)
        if not response.ok:
            raise Exception("failed to update desire: " + response.text)
        return self
    
    def get_status(self):
        url = f"http://{self.ip}:8080/api/AbilityStatus?abilityInstanceId=" + str(self.abilityInstanceId)
        response = requests.get(url=url)
        # print(response.text)
        if not response.ok:
            raise Exception("failed to get status: " + response.text)
        return response


class AbilitySupport(NamedTuple):
    id: int
    level: int
    name: str
    depends: Any

    ip: str= ""
    "并非为消息包所必须"

    @staticmethod
    def from_json(json: dict,ip: str) -> Self:
        return AbilitySupport(
            id=json["id"],
            level=json["level"],
            name=json["name"],
            depends=json.get("depends"),
            ip=ip)

    def spawn(self, id: int = 0) -> RunningAbility:
        """启动一个新能力"""
        ability_info = abilityRequest(
            self.ip,
            cmd="start",
            abilityName=self.name,
            abilityId=self.id,
            abilityInstanceId=id,
            connectPort=0)
        #return RunningAbility.from_json(ability_info.json(),ip=self.ip)
        return getAbilityRunningInfo(id, self.ip, "STANDBY")


def abilitySupport(addr: str) -> list[AbilitySupport]:
    """查看框架总体的 ability support"""
    assert isinstance(addr, str)
    url = f"http://{addr}:8080/api/AbilitySupport"
    json = requests.get(url=url).json()
    if json is None:
        return []
    assert isinstance(json, list)
    # print(json)
    return [AbilitySupport.from_json(x,ip=addr) for x in json]


def abilitySupportForName(addr: str, name: str) -> list[AbilitySupport]:
    return [ability
            for ability in abilitySupport(addr)
            if ability.name == name]


def mustUnique(lst: list[T]) -> T:
    # if len(lst) == 1:
    #     return lst[0]
    # for x in lst:
    #     print(x)
    # raise Exception("list in ambiguous")
    return lst[0]

def mustSameIp(list: list[AbilitySupport], ip: str) -> AbilitySupport:
    for ability in list:
        #print(ability.depends)
        if str(ability.depends).count(ip) == 2:
            return ability
    raise Exception("no target ability")


def abilityRunning(addr: str) -> list[RunningAbility]:
    assert isinstance(addr, str)
    url = f"http://{addr}:8080/api/AbilityRunning"
    json = requests.get(url=url).json()
    if json is None:
        return []
    assert isinstance(json, list)
    return [RunningAbility.from_json(entry,ip=addr) for entry in json]

def getAbilityRunningInfo(instanceId: int, framework_addr: str, dest_status: str) -> RunningAbility:
    for i in range(0, 20):
        exist_flag = False
        abilities = abilityRunning(framework_addr)
        for a in abilities:
            if a.abilityInstanceId == instanceId:
                if a.status == dest_status:
                    return a
                exist_flag = True
        if exist_flag == False and dest_status == "TERMINATE":
            return RunningAbility("target", 0, 0, "TERMINATE", 0, 0, 0, framework_addr)
        time.sleep(1)
    raise Exception("ability start failed")

def checkExist(framework_addr: str, abilityInstanceId: str):
    flag = False
    for i in range(0, 20):
        abilities = abilityRunning(framework_addr)
        flag = False
        for a in abilities:
            if a.abilityInstanceId == abilityInstanceId:
                flag = True
        if flag == False :
            return False
        time.sleep(1)
    return True

def abilityRequest(
    connectIP: str,
    *,
    abilityName: str,
    cmd: str,
    connectPort: int,
    abilityId: str,
    abilityInstanceId: int = 0
):
    """请求能力启动，如果http执行失败，则抛出异常。成功时，返回http报文"""
    payload = {
        "abilityName": abilityName,
        "cmd": cmd,
        "connectIP": connectIP,
        "connectPort": connectPort,
        "abilityId": abilityId,
        "abilityInstanceId": abilityInstanceId}
    url = f"http://{connectIP}:8080/api/AbilityRequest"
    response = requests.post(url=url, json=payload)
    if not response.ok:
        raise Exception(response.text)
    return response
