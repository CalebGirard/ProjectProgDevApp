import Database, asyncio

async def main():
    username = input("Username: ")
    database = Database.Database(username)
    code = input("Room code: ")
    await database.connectToDatabase(code)
    print("Connected!")
    await database.sendAsClient("Test Message")
    await database.opData("Test1",10,"+")
    last = 0
    while True:
        await asyncio.sleep(0.03)
        val = await database.get("Test1")
        if last != val:
            last = val
            print(f"'Test1' is {val}...")

#Test

asyncio.run(main())