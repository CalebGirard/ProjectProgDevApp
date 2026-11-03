import Database, asyncio

async def main():
    username = input("Username: ")
    database = Database.Database(username)
    code = input("Room code: ")
    await database.connectToDatabase(code)
    print("Connected!")
    await asyncio.sleep(1)
    await database.sendAsClient("Test Message")
    await database.opData("Test1",10,"+")
    print(await database.getPath("users:lxs:cash"))
    print(database.data)
    while True:
        await asyncio.sleep(0.03)

#Test

asyncio.run(main())