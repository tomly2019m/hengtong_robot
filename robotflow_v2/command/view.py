import requests
import time
import json


class Reader:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = f'http://{self.host}:{self.port}/db/query'
        self.param = {}

    def exec(self, sql: str) -> str:
        self.param["q"] = sql
        response = requests.get(self.url, self.param)
        return response.text

    '''
        从资源视图获取机器人位置信息
        返回值 元组 位置信息 x,y,z
    '''
    def get_resource_items_by_id(self, resource, reader):
        sql = 'select * from ResourcePool where id = \'' + resource + '\''
        print(sql)

        # 解析返回结果
        # TODO: 异常处理
        result_str = reader.exec(sql)
        print(result_str)
        # 检查results是否为空
        results = json.loads(result_str)
        columns = results["results"][0]["columns"]
        values = results["results"][0]["values"]

        for index in range(len(values)):
            if values[index][1] == resource:
                print('Found Value ' + values[index][9] + ' of ' + values[index][1])
                return values[index][9]

        return ''

    '''
        从资源视图获取资源信息
    '''
    def get_resource_by_id(self, resource, reader):
        sql = 'select * from ResourcePool where id = \'' + resource + '\''
        print(sql)

        # 解析返回结果
        # TODO: 异常处理
        result_str = reader.exec(sql)
        print(result_str)
        # 检查results是否为空
        results = json.loads(result_str)
        columns = results["results"][0]["columns"]
        values = results["results"][0]["values"]

        for index in range(len(values)):
            if values[index][1] == resource:
                print('Found Value ' + values[index][9] + ' of ' + values[index][1])
                return values[index]

class Writer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = f'http://{self.host}:{self.port}/db/execute'
        self.header = {'Content-Type': 'application/json'}

    def exec(self, sql: str) -> str:
        json = [sql]
        response = requests.post(self.url, headers=self.header, json=json)
        return response.text

    def update_task_param(self, params, results, writer):
        for output in params['Outputs']:
            if output['Name'] in results:
                output['Value'] = results[output['Name']]
                sql = 'update TaskParam set data' + '=\'' + str(output['Value']) + '\',dataType=\'' + output[
                    'Type'] + '\' where taskId=\'' + params['TaskID'] + '\' and name=\'' + output[
                          'Name'] + '\' and serviceID=\'' + params['ServiceID'] + '\''
                print(sql)
                print(writer.exec(sql))

    def update_task_info(self, params, writer):
        sql = 'update TaskInfo set state=\'COMPLETED\',endTime=\'' + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                   time.localtime()) + ('\' where '
                                                                                                        'taskId=\'') + \
              params['ActionID'] + '\' and serviceID=\'' + params['ServiceID'] + '\''
        print(sql)
        print(writer.exec(sql))

    def set_task_completed(self, params, writer):
        sql = 'update TaskInfo set state=\'COMPLETED\',endTime=\'' + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                   time.localtime()) + ('\' where '
                                                                                                        'taskId=\'') + \
              params['ActionID'] + '\' and serviceID=\'' + params['ServiceID'] + '\''
        print(sql)
        print(writer.exec(sql))

    def set_task_error(self, params, writer):
        sql = 'update TaskInfo set state=\'ERROR\',endTime=\'' + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                   time.localtime()) + ('\' where '
                                                                                                        'taskId=\'') + \
              params['ActionID'] + '\' and serviceID=\'' + params['ServiceID'] + '\''
        print(sql)
        print(writer.exec(sql))

    '''
        用于释放机器人位置资源
    '''
    def releaseMutex(self, resource, ref, writer):
        sql = 'update ResourcePool set ref = ref + ' + str(ref) + ' where id = \'' + resource + '\''
        print(sql)
        print(writer.exec(sql))

    '''
        用于释放机器人位置资源
    '''
    def releaseResource(self, resource, ref, writer):
        sql = 'update ResourcePool set ref = 0,assigned = \'\', status = \'IDLE\', mutex = \'\'  ' + ' where id = \'' + resource + '\''
        print(sql)
        print(writer.exec(sql))

class View:
    def __init__(self):
        self.reader = Reader('127.0.0.1',4001)
        self.writer = Writer('127.0.0.1',4001)

    '''
        用于释放机器人位置资源
    '''
    def releaseMutex(self, resource, ref):
        resource_list = self.reader.get_resource_by_id(resource,self.reader)
        cur_ref = int(resource_list[8])
        if cur_ref + int(ref) > 0:
            self.writer.releaseMutex(resource,ref,self.writer)
        else:
            self.writer.releaseResource(resource,ref,self.writer)
