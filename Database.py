import asyncio,json,time,requests,redis
import pandas as pd
import websockets as ws

SERVER = "0x1.lxsdev.net"

class Database:
    def __init__(self, host:bool=False):
        self.host = host
        self.connected = False
        self.data = redis.Redis("localhost", port=6379, decode_responses=True)
        self.webs = None
        self.code = None
        self.token = None
        self.nextSignalingRoomExtendTime = None
        self.signalingQueue = asyncio.Queue()
        self.connections = {}

    def setValue(self,key:str,value):
        if self.host:
            pass
        else:
            pass

    def getValue(self,key:str):
        if self.host:
            pass
        else:
            pass

    def addDataframe(self,name:str,dataframe):
        if not self.host:
            return False

    def removeDataframe(self,name:str):
        if not self.host:
            return False

    async def signalingRecv(self):
        pass

    async def signalingWaitFor(self,type:str):
        pass

    async def startWaitForConnections(self):
        if not self.host:
            return
        code = requests.get("https://"+SERVER+"/create",timeout=3)
        if code.status_code != 200:
            return False
        self.code = code.json()["RoomID"]
        self.token = code.json()["OwnerToken"]
        self.webs = await ws.connect("wss://"+SERVER+"/ws?id="+self.code+"&token="+self.token)
        data = json.loads(await self.webs.recv())
        if data["type"] == "successful_connection":
            self.signalRecv = asyncio.create_task(self.signalingRecv())
            return True
        else:
            await self.webs.close()
            self.webs = None
            return False

    async def stopWaitingForConnections(self):
        if not self.host:
            return

    async def connectToDatabase(self,code:str):
        if self.host:
            return

    def killDatabase(self):
        if not self.host:
            return
        self.data.close()