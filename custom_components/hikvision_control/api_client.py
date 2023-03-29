from hikvisionapi import AsyncClient
from httpx import HTTPStatusError

from .exceptions import CannotConnect, InvalidAuth


class ApiClient:
    def __init__(self, url: str, username: str, password: str) -> None:
        self.client = None
        self.url = url
        self.username = username
        self.password = password
        self.connected = False

    async def connect(self):
        self.connected = False
        try:
            self.client = AsyncClient(self.url, self.username, self.password)
            self.connected = True
        except HTTPStatusError as ex:
            if ex.response.status == 401:
                raise InvalidAuth()
            raise CannotConnect()
        except:
            raise CannotConnect()

    async def ensure_connected(self):
        if self.connected:
            return
        await self.connect()

    async def get_camera_name(self):
        await self.ensure_connected()
        response = await self.client.System.deviceInfo(method="get")
        return response["DeviceInfo"]["deviceName"]

    async def get_ir_mode(self):
        await self.ensure_connected()
        response = await self.client.Image.channels[1].irCutFilter(method="get")
        return response["IrcutFilter"]["IrcutFilterType"]

    async def set_ir_mode(self, mode):
        await self.ensure_connected()
        payload = f'<?xml version="1.0" encoding="UTF-8"?><IrcutFilter version="2.0" xmlns="http://www.hikvision.com/ver20/XMLSchema"><IrcutFilterType>{mode}</IrcutFilterType></IrcutFilter>'
        await self.client.Image.channels[1].IrcutFilter(method="put", data=payload)
