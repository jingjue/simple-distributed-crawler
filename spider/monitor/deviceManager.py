import os
from typing import List, Union

import rsa

from monitor import *
from base.db.mysql import Device, Mysql
from base.db.dbSlot import Slot


class DeviceC:
    def __init__(self, ip: str, username, password, address, port, **kwargs):
        self.ip = ip
        self.username = username
        self.password = password
        self.address = address
        self.port = port
        self.valid = True

    def to_item(self):
        info = self.to_dict()
        info["password"] = encryption(self.password)
        info["server_id"] = info["ip"] + ":" + str(info["port"])
        return info

    def to_dict(self):
        return {"ip": self.ip, "username": self.username, "address": self.address, "port": self.port, "valid": True}

    def generate_config(self):
        return self.to_dict()

    def __getitem__(self, item):
        return getattr(self, item, False)

    def __setitem__(self, key, value):
        if self[key]:
            setattr(self, key, value)
        else:
            return False


class DeviceManager:
    def __init__(self, paroject_name: str, devices_status: dict, dbslot: Slot):
        """
        ips：启用的设备ip 列表
        """
        self.project_name = paroject_name
        self.dbslot = dbslot
        self.devices_status = devices_status  # 设备状态
        self.devices = self.load_devices(list(self.devices_status.keys()))  # server_id:device

    @property
    def valid_devices(self):
        """
        获取启用的设备
        """
        devices = []
        for ip, status in self.devices_status.items():
            if status and self.devices.get(ip, False):
                devices.append(self.devices[ip])
        return devices

    def add_device_from_server_id(self, server_id: Union[List[str], str]):
        errors = {}
        if isinstance(server_id, str):
            device = self.dbslot.mysql.query("Device", "server_id", server_id)
            if device:
                param = device[0].to_dict()
                param["password"] = decrypt(param["password"])
                self.devices[param["server_id"]] = DeviceC(**param)
                self.devices_status[param["server_id"]] = True
                logger.info(f"添加设备成功 {server_id}")
            else:
                errors[server_id] = f"添加设备失败,数据库中不存在ip:{server_id}"
                logger.warning(errors[server_id])
            return errors
        elif isinstance(server_id, list):
            for one_ip in server_id:
                errors.update(self.add_device_from_server_id(one_ip))
            return errors

    def get_devices_info(self):
        info = {}
        for ip, status in self.devices_status.items():
            info[ip] = self.devices[ip].to_dict()
            info[ip]["status"] = status
        return info

    def update_device_from_params(self, params):
        """
        启用或禁用分布式设备
        """
        errors = {}
        for ip, status in params.items():
            if self.devices_status.get(ip, False):
                self.devices_status[ip] = status
                errors[ip] = f"爬虫项目{self.project_name},启用分布式设备:{ip}"
                logger.info(errors[ip])
            else:
                message = f"爬虫项目{self.project_name}中 不存在设备{ip}"
                logger.warning(message)
                errors[ip] = message
        return errors

    def rm_device_from_ip(self, ip: Union[List[str], str]):
        errors = {}
        if isinstance(ip, str):
            if self.devices_status.get(ip, False):
                self.devices_status.pop(ip)
                self.devices.pop(ip)
            else:
                errors[ip] = f"爬虫项目{self.project_name},不存在分布式设备:{ip}"
                logger.warning(errors[ip])
            return errors
        elif isinstance(ip, list):
            for one_ip in ip:
                errors.update(self.rm_device_from_ip(one_ip))
            return errors

    def to_item(self):
        infos = []
        for device in self.devices.values():
            info = device.to_dict()
            info["password"] = encryption(device.password)
            info["server_id"] = info["ip"] + f":{info['port']}"
            infos.append(Device(**info))
        return infos

    def load_devices(self, ips: List[str] = None):
        devices = {}
        all_server_id = set()
        for device in self.dbslot.mysql.query_device():
            all_server_id.add(device.server_id)
            if device.server_id in ips and device.valid:
                param = device.to_dict()
                param["password"] = decrypt(device.password)
                devices[device.server_id] = DeviceC(**param)
                self.devices_status[device.server_id] = True
        not_exist_ips = set(ips) - set(all_server_id)

        for ip in not_exist_ips:
            self.devices_status.pop(ip)
        return devices

    def save_devices(self):
        for device in self.to_item():
            self.dbslot.mysql.update(device)

    def generate_config(self):
        return self.devices_status

    @classmethod
    def from_params(cls, project_name, params: dict, dbslot):
        """
        params:[ip,...]
        """
        return cls(project_name, params, dbslot)


if __name__ == '__main__':
    dd = {'ip': '180.201.163.246', 'username': 'chase', 'address': '/home/users/CT/pycharmproject/spiders/',
          'port': 6800, 'valid': True,
          'password': '123',
          'server_id': '180.201.163.246:6800'}
    d = DeviceC(**dd)
    dm = DeviceManager("default", {}, Slot(Mysql(logger=logger)))
    d["valid"] = False
    print(dm.dbslot.mysql.update(Device(**d.to_item())))
    # dm.add_device_from_server_id("180.201.163.246:6800")
