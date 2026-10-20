import asyncio,json,time,requests,redis
import pandas as pd
import websockets as ws
import aiortc

SERVER = "0x1.lxsdev.net"
TURNSERVER = "turn:turn.lxsdev.net:3487"

class Database:
    def __init__(self,username:str, host:bool=False,):
        # Global
        self.username = username
        self.host = host
        self.connected = False

        # Data Subscription Module
        self.subInfo = {}

        # Requests
        self.requestQueue = asyncio.Queue()
        self.data = redis.Redis("localhost", port=6379, decode_responses=True)
        
        # Signaling 
        self.webs = None
        self.code = None
        self.token = None
        self.sigRoomExp = None
        self.sigRoomRunning = False
        self.sigQueue = asyncio.Queue()

        # Networking 
        self.connections = {}

    # Signaling Module

    async def signalRecv(self):
        while self.sigRoomRunning:
            data = await self.webs.recv()
            data = json.loads(data)
            await self.sigQueue.put(data)

    async def sigWait(self, type:str):
        while self.sigRoomRunning: 
            data = await self.sigQueue.get()
            self.sigQueue.task_done()
            if data["type"] == "expired":
                self.sigRoomRunning = False
            elif data["type"] == type:
                return data

    async def handleConnections(self):
        while self.sigRoomRunning:
            await self.sigWait("user_joined")
            ice = await self.sigIceGather()
            pc = aiortc.RTCPeerConnection(ice)
            await self.webs.send(json.dumps(ice))

    async def sigIceGather(self):
        creds = requests.get(SERVER+"/turn-cred?username="+self.username)
        if creds.status_code != 200:
            return False
        creds = creds.json()
        ice = [
            RTCIceServer(urls=[creds["uris"][0]]),
            RTCIceServer(
                urls=[creds["uris"][1]],
                username=creds["username"],
                credential=creds["password"]
            )
        ]
        return ice

    async def openRoom(self):
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
            self.sigRoomRunning = True
            asyncio.create_task(self.signalRecv())
            asyncio.create_task(self.handleConnections())
            return True
        else:
            self.sigRoomRunning = False
            await self.webs.close()
            self.webs = None
            return False

    async def connectToDatabase(self,code:str):
        if self.host:
            return

    # Data Subscription Module

    async def handleSub(self):
        pass

    async def sub(self, key):
        pass

    async def unSub(self, key):
        pass
    
    async def forceUpdate(self):
        pass

    # Request Module

    async def get(self, key):
        pass

    async def set(self, key, value):
        pass

    async def opData(self, key, value , op):
        pass
    
    # Networking Module 

    async def handleRECV(self):
        pass

    async def send(self, data):
        pass

    async def disconnect(self):
        pass

    def killDatabase(self):
        if not self.host:
            return
        self.data.close()