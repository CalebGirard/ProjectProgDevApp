import asyncio,json,time,requests
import pandas as pd
import websockets as ws

SERVER = "0x1.lxsdev.net"

class Database:
    def __init__(self, host=False):
        self.host = host
        self.connected = False
        self.data = None
        self.webs = None
        self.code = None
        self.token = None
        self.nextSignalingRoomExtendTime = None
        self.signalingQueue = asyncio.Queue()

    async def signalingRecv(self):
        pass

    async def signalingWaitFor(self,type:str):
        pass

    async def waitForConnections(self):
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
        pass

    async def connectToDatabase(self,code:str):
        if self.host:
            return
        
        pass