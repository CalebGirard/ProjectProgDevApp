import asyncio,json,time,requests
import pandas as pd
import websockets as ws
import aiortc
from aiortc import RTCSessionDescription, RTCPeerConnection
from pandas import DataFrame
import logging

SERVER = "0x1.lxsdev.net"
TURNSERVER = "turn:turn.lxsdev.net:3478"

class Database:
    def __init__(self,username:str, host:bool=False):
        # Global
        self.username = username
        self.host = host
        self.data = {}
        self.canSend = False

        # Requests
        self.requestQueue = asyncio.Queue()
        self.waitQueue = asyncio.Queue()
        
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

    async def init(self):
        asyncio.create_task(self.handleRequests())
        await self.openRoom()

    # Signaling Module

    async def signalRecv(self):
        while self.sigRoomRunning:
            try:
                data = await self.webs.recv()
                data = json.loads(data)
                #print(data)
                await self.sigQueue.put(data)
            except:pass

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
            print("New client attempting to connect...")
            ice = await self.sigIceGather()
            config = aiortc.RTCConfiguration(ice)
            pc = aiortc.RTCPeerConnection(configuration=config)
            channel = pc.createDataChannel("sync_data")
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            while pc.iceGatheringState != "complete":
                await asyncio.sleep(0.05)
            payload = {
                "username": self.username,
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
            await self.webs.send(json.dumps(payload))
            data = await self.sigWait("relay")
            data = json.loads(data["data"])
            await pc.setRemoteDescription(RTCSessionDescription(data["sdp"],data["type"]))
            self.handleChannel(channel, data["username"])
            self.connections[data["username"]] = pc
            self.channels[data["username"]] = channel
            print("New client successfully connected!")

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
        def on_datachannel(channel):
            self.channels[self.username] = channel
            self.handleChannel(channel, self.username)
        pc.remove_all_listeners("datachannel")
        pc.on("datachannel", on_datachannel)
        await pc.setRemoteDescription(RTCSessionDescription(data["sdp"],data["type"]))
        offer = await pc.createAnswer()
        await pc.setLocalDescription(offer)
        while pc.iceGatheringState != "complete":
            await asyncio.sleep(0.05)
        payload = {
            "username":self.username,
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
        await self.webs.send(json.dumps(payload))
        self.clientPc = pc
        self.sigRoomRunning = False
        return True

    # Request Module

    async def getPath(self, path:str):
        pass

    async def setPath(self,path:str):
        pass

    async def get(self, key:str):
        return self.data.get(key)

    async def set(self, key:str, value):
        if self.host:
            self.data[key] = value
            await self.broadcast(json.dumps({"type":"sync","data":{"key":key,"value":value}}))
        elif self.clientPc:
            await self.sendAsClient(json.dumps({"type":"set","username":self.username,"data":{"key":key,"value":value}}))

    async def opData(self, key:str, value , op:str):
        if self.host:
            try:
                if op == "+":
                    self.data[key] += value
                elif op == "-":
                    self.data[key] -= value
                elif op == "*":
                    self.data[key] *= value
                elif op == "/":
                    self.data[key] /= value
                elif op == "//":
                    self.data[key] //= value
                elif op == "%":
                    self.data[key] %= value
                await self.broadcast(json.dumps({"type":"sync","data":{"key":key,"value":self.data[key]}}))
                return True
            except Exception as e:
                print("Op data error ->",e)
                return False
        elif self.clientPc:
            await self.sendAsClient(json.dumps({"type":"op_data","username":self.username,"data":{"key":key,"value":value,"op":op}}))

    async def setDataframe(self, key:str, dataframe:Dataframe):
        if not self.host:
            return

    async def getDataframe(self, key:str):
        return self.data.get(key)

    async def opDataframe(self, key:str, value):
        pass

    
    # Networking Module 

    def handleChannel(self, channel, username:str):
        if self.host:
            self.channels[username] = channel
        if channel.readyState != "open":
            @channel.on("open")
            def on_open():
                if self.host:
                    channel.send(json.dumps({"type":"init_sync","data":self.data}))
                else:
                    self.canSend = True
                    self.channels[self.username] = channel
        else:
            if self.host:
                channel.send(json.dumps({"type":"init_sync","data":self.data}))
            else:
                self.canSend = True
                self.channels[self.username] = channel

        @channel.on("message")
        def on_message(message):
            try:
                message = json.loads(message)
            except:
                message = {"type": "raw", "data": message}

            if self.host:
                self.requestQueue.put_nowait(message)
            else:
                self.waitQueue.put_nowait(message)
                self.netProcess(message)

    async def sendAsHost(self, data, username:str):
        self.channels[username].send(data)

    async def sendAsClient(self, data):
        if self.host or not self.clientPc:
            return
        while not self.canSend:
            await asyncio.sleep(0.03)
        self.channels[self.username].send(data)

    async def broadcast(self, data, excep:str=None):
        if not self.host:
            return
        for user in self.connections.keys():
            if user != excep:
                await self.sendAsHost(data,user)

    async def handleRequests(self):
        while True:
            data = await self.requestQueue.get()
            self.requestQueue.task_done()
            try:
                user = data["username"]
                if data["type"] == "set":
                    key = data["data"]["key"]
                    value = data["data"]["value"]
                    await self.set(key,value)
                elif data["type"] == "op_data":
                    key = data["data"]["key"]
                    value = data["data"]["value"]
                    op = data["data"]["op"]
                    await self.opData(key,value,op)
                elif data["type"] == "disconnect":
                    user = data["username"]
                    self.sendAsHost({"type":"conf"},user)
                    self.connections[user].close()
                    del self.connections[user]
                    del self.channels[user]
            except:
                pass

    async def netWait(self,type):
        while True:
            data = await self.waitQueue.get()
            self.waitQueue.task_done()
            if data["type"] == type:
                return data

    def netProcess(self,data):
        if self.host:
            return
        if data["type"] == "sync":
            print("received sync ->",data)
            self.data[data["data"]["key"]] = data["data"]["value"]
        elif data["type"] == "database_close":
            asyncio.create_task(self.disconnect(False))
            print("Database closed...")
        elif data["type"] == "init_sync":
            self.data = data["data"]
            print("Database initiated ...")

    async def disconnect(self,notify:bool=True):
        if self.host or not self.clientPc:
            return
        if notify:
            self.sendAsClient(json.dumps({"type":"disconnect","username":self.username}))
            await self.netWait("conf")
        self.clientPc.close()
        self.canSend = False

    def killDatabase(self):
        if not self.host:
            return
        self.broadcast(json.dumps({"type":"database_close"}))

    # Utilities

    def splitPath(self, path:str, validate:bool=True):
        path = [p in path.split(":")]
        for i in len(path):
            dt = self.data.get(path[i])
            if not dt:
                return None
        return path
            
