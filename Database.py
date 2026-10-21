import asyncio,json,time,requests
import pandas as pd
import websockets as ws
import aiortc
from aiortc import RTCSessionDescription, RTCPeerConnection

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
        self.clientPc = None

    # Signaling Module

    async def signalRecv(self):
        while self.sigRoomRunning:
            data = await self.webs.recv()
            data = json.loads(data)
            #print(data)
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
        while self.sigRoomRunning and len(self.connections.keys()) < 4:
            await self.sigWait("user_joined")
            ice = await self.sigIceGather()
            config = aiortc.RTCConfiguration(ice)
            pc = aiortc.RTCPeerConnection(configuration=config)
            channel = pc.createDataChannel("sync_data")
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            payload = {
                "username": self.username,
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
            await self.webs.send(json.dumps(payload))
            data = await self.sigWait("relay")
            data = json.loads(data["data"])
            self.handleChannel(channel, data["username"])
            await pc.setRemoteDescription(RTCSessionDescription(data["sdp"],data["type"]))
            self.connections[data["username"]] = pc
            self.channels[data["username"]] = channel

    async def sigIceGather(self):
        creds = requests.get("https://"+SERVER+"/turn-cred?username="+self.username)
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
        data = await self.sigWait("relay")
        data = json.loads(data["data"])
        ice = await self.sigIceGather()
        config = aiortc.RTCConfiguration(ice)
        pc = aiortc.RTCPeerConnection(configuration=config)
        @pc.on("datachannel")
        def on_datachannel(channel):
            self.handleChannel(channel, data["username"])
        await pc.setRemoteDescription(RTCSessionDescription(data["sdp"],data["type"]))
        offer = await pc.createAnswer()
        await pc.setLocalDescription(offer)
        payload = {
            "username":self.username,
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
        await self.webs.send(json.dumps(payload))
        self.sigRoomRunning = False
        self.clientPc = pc
        return True

    # Request Module

    async def get(self, key):
        pass

    async def set(self, key, value):
        pass

    async def opData(self, key, value , op):
        pass
    
    # Networking Module 

    def handleChannel(self, channel, username):
        if self.host:
            self.channels[username] = channel
        else:
            self.channels[self.username] = channel

        if channel.readyState != "open":
            @channel.on("open")
            def on_open():channel.send("Connection established!")
        else:
            channel.send("Connection established!")

        @channel.on("message")
        def on_message(message):
            print(f"Received: {message}")

    async def sendAsHost(self, data, username:str):
        self.channels[username].send(data)

    async def sendAsClient(self, data):
        if self.host or not self.clientPc:
            return
        self.channels[self.username].send(data)

    async def broadcast(self, data, excep=None):
        if not self.host:
            return
        for user in self.connections.keys():
            if user != excep:
                await self.sendAsHost(data,user)

    async def disconnect(self):
        if self.host or not self.clientPc:
            return
        self.clientPc.close()

    def killDatabase(self):
        if not self.host:
            return
        self.data.close()

