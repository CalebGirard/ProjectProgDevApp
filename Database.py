import asyncio,json,time,requests
import pandas as pd
import websockets as ws
import aiortc
from aiortc import RTCSessionDescription

SERVER = "0x1.lxsdev.net"
TURNSERVER = "turn:turn.lxsdev.net:3487"

class Database:
    def __init__(self,username:str, host:bool=False,):
        # Global
        self.username = username
        self.host = host
        self.connected = False

        # Requests
        self.requestQueue = asyncio.Queue()
        self.data = {}
        
        # Signaling 
        self.webs = None
        self.code = None
        self.token = None
        self.sigRoomExp = None
        self.sigRoomRunning = False
        self.sigQueue = asyncio.Queue()

        # Networking 
        self.connections = {}
        self.channels = {}

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
            config = aiortc.RTCConfiguration(ice)
            pc = aiortc.RTCPeerConnection(configuration=config)
            offer = await pc.createAnswer()
            await pc.setLocalDescription(offer)
            while pc.iceGatheringState != "complete":
                await asyncio.sleep(0.1)
            payload = {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
            self.webs.send(json.dumps(payload))
            data = await self.sigWait("relay")
            data = json.loads(data["data"])
            await pc.setRemoteDescription(RTCSessionDescription(data["sdp"],data["type"]))
            pc.add_listener("datachannel", lambda channel: self.handleChannel(channel, data["username"]))
            self.connections[data[self.username]] = pc
            

    async def sigIceGather(self):
        creds = requests.get(SERVER+"/turn-cred?username="+self.username)
        if creds.status_code != 200:
            return False
        creds = creds.json()
        ice = [
            aiortc.RTCIceServer(urls=[creds["uris"][0]]),
            aiortc.RTCIceServer(
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
        self.webs = await ws.connect("wss://"+SERVER+"/ws?id="+code)
        data = json.loads(await self.webs.recv())
        if data["type"] != "successful_connection":
            return False
        self.sigRoomRunning = True
        asyncio.create_task(self.signalRecv())
        ice = await self.sigIceGather()
        config = aiortc.RTCConfiguration(ice)
        pc = aiortc.RTCPeerConnection(configuration=config)
        self.channels["sync_channel"] = pc.createDataChannel("sync_channel")
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        while pc.iceGatheringState != "complete":
            await asyncio.sleep(0.1)
        payload = {
            "username":self.username,
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
        data = await self.sigWait("relay")
        data = json.loads(data["data"])
        pc.remoteDescription(RTCSessionDescription(data["sdp"],data["type"]))
        self.webs.send(json.dumps(payload))
        self.sigRoomRunning = False
        return True

    # Request Module

    async def get(self, key):
        pass

    async def set(self, key, value):
        pass

    async def opData(self, key, value , op):
        pass
    
    # Networking Module 

    async def handleChannel(self, channel, username):
        print("Connected Channel with client ->", username)
        self.channels[username] = channel

    async def send(self, data):
        pass

    async def disconnect(self):
        pass

    def killDatabase(self):
        if not self.host:
            return
        self.data.close()

