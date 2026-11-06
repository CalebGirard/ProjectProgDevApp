import asyncio, json, time, requests
import pandas as pd
import websockets as ws
import aiortc
from aiortc import RTCSessionDescription, RTCPeerConnection
from pandas import DataFrame
import threading
import functools

SERVER = "0x1.lxsdev.net"
TURNSERVER = "turn:turn.lxsdev.net:3478"


def threadsafe(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        coro = fn(self, *args, **kwargs)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run_coroutine_threadsafe(coro, self.loop)
        return asyncio.ensure_future(coro)

    return wrapper


class Database:
    def __init__(self, username: str, host: bool = False):
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

        self.rawMsgCallback = None
        self.connFailedCallback = None
        self.newConnCallback = None
        self.roomReadyCallback = None
        self.bankActionCallback = None

        self.sigRe = False

    async def init(self):
        asyncio.create_task(self.handleRequests())

    # Signaling Module

    async def signalRecv(self):
        if self.sigRe:
            return
        self.sigRe = True
        while self.sigRoomRunning:
            try:
                if not self.webs:
                    await asyncio.sleep(0.1)
                    continue
                data = await self.webs.recv()
                data = json.loads(data)
                await self.sigQueue.put(data)
            except Exception as e:
                if "cannot call recv while another coroutine" in str(e):
                    await asyncio.sleep(0.05)
                    continue
                print("Signal recv error:", e)
                break

    async def sigWait(self, type: str):
        while self.sigRoomRunning:
            # on attend pour un certain type de donner dans la room de signalage et on retourne les donner
            data = await self.sigQueue.get()
            self.sigQueue.task_done()
            if data["type"] == "expired":
                self.sigRoomRunning = False
            elif data["type"] == type:
                return data

    async def handleConnections(self):
        while self.sigRoomRunning and len(self.connections.keys()) < 4:
            # on attend q'un utilisateur rejoin, et on lui envoie notre configuration
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
                "type": pc.localDescription.type,
            }
            await self.webs.send(json.dumps(payload))

            # on attend la configuration de l'utilisateur pour completer la connection
            data = await self.sigWait("relay")
            data = json.loads(data["data"])
            await pc.setRemoteDescription(
                RTCSessionDescription(data["sdp"], data["type"])
            )

            # on ajoutes c'est informations dans le dictionaire
            self.handleChannel(channel, data["username"])
            self.connections[data["username"]] = pc
            self.channels[data["username"]] = channel
            print("New client successfully connected!")

            # si le callback de nouvelle connection est definie, on l'appel
            if self.newConnCallback:
                self.newConnCallback(data["username"])

    async def sigIceGather(self):

        # obtenir la configuration require a aiortc pour la connection en utilisant le serveur de relay

        creds = requests.get(
            "https://" + SERVER + "/turn-cred?username=" + self.username
        )
        if creds.status_code != 200:
            return False
        creds = creds.json()
        ice = [
            aiortc.RTCIceServer(urls=[creds["uris"][0]]),
            aiortc.RTCIceServer(
                urls=[creds["uris"][1]],
                username=creds["username"],
                credential=creds["password"],
            ),
        ]
        return ice

    @threadsafe
    async def openRoom(self):
        if not self.host:
            return

        # on clear les variables pour ouvrir une nouvelle room pour permettre la connection des utilisateur
        self.sigRoomRunning = False
        if self.webs:
            try:
                await self.webs.close()
            except:
                pass
            self.webs = None

        self.connections.clear()
        self.channels.clear()

        # on envoie une requete au serveur de signalage pour creer une room

        code = requests.get("https://" + SERVER + "/create", timeout=3)
        if code.status_code != 200:
            return False
        self.code = code.json()["RoomID"]
        self.token = code.json()["OwnerToken"]

        if self.roomReadyCallback:
            self.roomReadyCallback(self.code, self.token)

        # on se connecte a la room et on peut maintenant attendre les connections des utilisateur

        self.webs = await ws.connect(
            "wss://" + SERVER + "/ws?id=" + self.code + "&token=" + self.token
        )
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

    @threadsafe
    async def connectToDatabase(self, code: str):
        if self.host:
            return

        # On clear les variable pour s'assurer qu'il reste rien d'une conenction anterieur
        self.sigRoomRunning = False
        if self.webs:
            try:
                await self.webs.close()
            except:
                pass
            self.webs = None
        if self.clientPc:
            try:
                self.clientPc.close()
            except:
                pass
            self.clientPc = None
        self.channels.clear()
        self.canSend = False

        # On se connecte au serveur de signalement
        try:
            url = f"wss://{SERVER}/ws?id={code}"
            self.webs = await ws.connect(url)

            raw_msg = await self.webs.recv()
            data = json.loads(raw_msg)

            if data.get("type") != "successful_connection":
                if self.connFailedCallback:
                    self.connFailedCallback()
                return False
        except Exception as e:
            print("Client failed to establish WebSocket connection:", e)
            if self.connFailedCallback:
                self.connFailedCallback()
            return False

        self.sigRoomRunning = True
        asyncio.create_task(self.signalRecv())

        # on attend de recevoir la config du host
        data = await self.sigWait("relay")
        data = json.loads(data["data"])
        ice = await self.sigIceGather()

        # on configure aiortc pour la connection
        config = aiortc.RTCConfiguration(ice)
        pc = aiortc.RTCPeerConnection(configuration=config)

        def on_datachannel(channel):
            self.channels[self.username] = channel
            self.handleChannel(channel, self.username)

        pc.remove_all_listeners("datachannel")
        pc.on("datachannel", on_datachannel)
        await pc.setRemoteDescription(RTCSessionDescription(data["sdp"], data["type"]))
        offer = await pc.createAnswer()
        await pc.setLocalDescription(offer)
        while pc.iceGatheringState != "complete":
            await asyncio.sleep(0.05)
        payload = {
            "username": self.username,
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
        }
        # On peut maintenant envoyer notre propre configuration au host pour terminer la connection
        await self.webs.send(json.dumps(payload))
        self.clientPc = pc
        self.sigRoomRunning = False
        return True

    # Request Module
    def getPath(self, path: str):
        # On parcour le path et retourne la valeur de fin
        dt = self.data
        for p in self.splitPath(path):
            if not isinstance(dt, dict) or p not in dt:
                return None
            dt = dt[p]
        return dt

    @threadsafe
    async def setPath(self, path: str, value):
        if self.host:
            # si c'est le host, on parcour le path, on cherche la valeur et on le set, ensuite on envoie le changement au utilisateurs
            path = self.splitPath(path)
            if not path:
                return None
            dt = self.data
            for p in path[:-1]:
                dt = dt.setdefault(p, {})
            dt[path[-1]] = value
            if self.connections:
                await self.broadcast(
                    json.dumps(
                        {
                            "type": "sync",
                            "data": {"key": path[0], "value": self.data[path[0]]},
                        }
                    )
                )
        elif self.clientPc:
            # si c'est pas le host, on envoie la requete au host
            await self.sendAsClient(
                json.dumps(
                    {
                        "type": "set_path",
                        "username": self.username,
                        "data": {"path": path, "value": value},
                    }
                )
            )

    def get(self, key: str):
        return self.data.get(key)

    @threadsafe
    async def set(self, key: str, value):
        if self.host:
            #Si la database est en mode host, on set et si une connection est fait, on envoie la modification a la connection
            self.data[key] = value
            if self.connections:
                await self.broadcast(
                    json.dumps({"type": "sync", "data": {"key": key, "value": value}})
                )
        elif self.clientPc:
            # Si la database est pas le host, on envoie la requete de modification au host
            await self.sendAsClient(
                json.dumps(
                    {
                        "type": "set",
                        "username": self.username,
                        "data": {"key": key, "value": value},
                    }
                )
            )

    @threadsafe
    async def opData(self, key: str, value, op: str):
        if self.host:
            # Si la database est en mode host, on fait l'op sur la valeur et on envoie le changement au connections
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
                if self.connections:
                    await self.broadcast(
                        json.dumps(
                            {
                                "type": "sync",
                                "data": {"key": key, "value": self.data[key]},
                            }
                        )
                    )
                return True
            except Exception as e:
                print("Op data error ->", e)
                return False
        elif self.clientPc:
            # Si la database n'est pas en mode host, on envoie la requete au host
            await self.sendAsClient(
                json.dumps(
                    {
                        "type": "op_data",
                        "username": self.username,
                        "data": {"key": key, "value": value, "op": op},
                    }
                )
            )

    @threadsafe
    async def setDataframe(self, key: str, dataframe):
        # On converti le dataframe en dictionaire pour faciliter l'envoie par les connections
        dataframe = dataframe.to_dict()

        if self.host:
            # Si la database est en mode host, on met le dataframe dans la base de donner et on envoie la modification au connection
            self.data[key] = dataframe
            if self.connections:
                await self.broadcast(
                    json.dumps(
                        {"type": "sync", "data": {"key": key, "value": dataframe}}
                    )
                )
        elif self.clientPc:
            # Si la database n'est pas en mode host, on envoie la requete au host
            await self.sendAsClient(
                json.dumps(
                    {
                        "type": "set_df",
                        "username": self.username,
                        "data": {"key": key, "df": dataframe},
                    }
                )
            )

    def getDataframe(self, key: str):
        if self.data.get(key):
            # Si le dataframe existe dans la database, il sera en dict donc on le converti et on le retourne
            return pd.DataFrame(self.data.get(key))
        return None

    # Networking Module

    def handleChannel(self, channel, username: str):

        # C'est la fonction qui est lancer initialement pour aiortc, et permet de determiner ce qui ce passe lorsqu'un message est recu, lorsque la conenction est ouverte initalement, etc...

        if self.host:
            # on met la channel (ce quon utilise pour tansmettre les donnes), dans un dictionaire avec le nom d'utilisateur de celui qui a rejoin
            self.channels[username] = channel
        if channel.readyState != "open":

            @channel.on("open")
            def on_open():
                if self.host:
                    # Si un nouvelle connection est ouverte en tant que host, on lui envoie sa copie personnelle de la database
                    channel.send(json.dumps({"type": "init_sync", "data": self.data}))
                else:
                    self.canSend = True
                    self.channels[self.username] = channel
        else:
            if self.host:
                # Si un nouvelle connection est ouverte en tant que host, on lui envoie sa copie personnelle de la database
                channel.send(json.dumps({"type": "init_sync", "data": self.data}))
            else:
                self.canSend = True
                self.channels[self.username] = channel

        @channel.on("message")
        def on_message(message):
            try:
                message = json.loads(message)
            except:
                # Si le message n'est pas du json valide, on appelle la fonction callback rawMsgCallback si elle est definie
                message = {"type": "raw", "data": message}
                if self.rawMsgCallback:
                    self.rawMsgCallback(username, message)

            if self.host:
                # Si c'est le host, on met le message dans la Queue de requetes
                self.requestQueue.put_nowait(message)
            else:
                # Si c'est le host, on met le message dans la Queue de requetes et on process le message
                self.waitQueue.put_nowait(message)
                self.netProcess(message)

    @threadsafe
    async def sendAsHost(self, data, username: str):
        self.channels[username].send(data)

    @threadsafe
    async def sendAsClient(self, data):
        if self.host or not self.clientPc:
            return
        while not self.canSend:
            await asyncio.sleep(0.03)
        self.channels[self.username].send(data)

    @threadsafe
    async def broadcast(self, data, excep: str = None):
        if not self.host:
            return
        # Seulment si c'est le host, on envoie data, a tout le monde sauf celui definie en excep
        for user in self.connections.keys():
            if user != excep:
                try:
                    await self.sendAsHost(data, user)
                except:
                    pass

    async def handleRequests(self):
        while True:
            data = await self.requestQueue.get()
            self.requestQueue.task_done()
            try:
                # on process les requetes envoyer par les utilisateur par exemple un set "key" a 10
                user = data["username"]
                if data["type"] == "set":
                    key = data["data"]["key"]
                    value = data["data"]["value"]
                    await self.set(key, value)
                elif data["type"] == "set_path":
                    path = data["data"]["path"]
                    value = data["data"]["value"]
                    await self.setPath(path, value)
                elif data["type"] == "set_df":
                    key = data["data"]["key"]
                    dataframe = data["data"]["df"]
                    await self.setDataframe(key, dataframe)
                elif data["type"] == "op_data":
                    key = data["data"]["key"]
                    value = data["data"]["value"]
                    op = data["data"]["op"]
                    await self.opData(key, value, op)
                elif data["type"] == "bank_action":
                    if self.bankActionCallback:
                        action = data["data"]["action"]
                        amount = data["data"].get("amount")
                        self.bankActionCallback(user, action, amount)
                elif data["type"] == "disconnect":
                    user = data["username"]
                    self.sendAsHost({"type": "conf"}, user)
                    self.connections[user].close()
                    del self.connections[user]
                    del self.channels[user]
            except:
                pass

    async def netWait(self, type):
        while True:
            # Attendre qu'un certain type de donner arrive et le retourner
            data = await self.waitQueue.get()
            self.waitQueue.task_done()
            if data["type"] == type:
                return data

    def netProcess(self, data):
        if self.host:
            return
        # Seulment si c'est le user, on process les donner envoyer par le host
        if data["type"] == "sync":
            self.data[data["data"]["key"]] = data["data"]["value"]
        elif data["type"] == "database_close":
            asyncio.create_task(self.disconnect(False))
            print("Database closed...")
        elif data["type"] == "init_sync":
            self.data = data["data"]
            print("Database initiated ...")

    @threadsafe
    async def disconnect(self, notify: bool = True):
        if self.host or not self.clientPc:
            return
        if notify:
            self.sendAsClient(
                json.dumps({"type": "disconnect", "username": self.username})
            )
            await self.netWait("conf")
        self.clientPc.close()
        self.canSend = False
        self.data = {}

    def killDatabase(self):
        if not self.host:
            return
        # fermer la database et le dire au users qui sont connecter
        self.broadcast(json.dumps({"type": "database_close"}))
        self.data = {}

    # Utilities

    def splitPath(self, path: str):
        path = path.split(":")
        return path

    def setHost(self, host: bool):
        self.host = host

    def setUsername(self, username: str):
        self.username = username

    def startThread(self):
        # On start le thread pour permettre a une application de continuer a marcher meme lors de l'execution, doit etre la premiere chose fait apres avoir definie une database
        self.loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        # Executer une fonction dans le thread
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.init())
        self.loop.run_forever()

    def run(self, coro):
        # Executer une fonction dans le thread
        return asyncio.run_coroutine_threadsafe(coro, self.loop)
