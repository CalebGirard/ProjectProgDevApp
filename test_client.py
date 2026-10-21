import Database, asyncio

async def main():
    username = input("Username: ")
    database = Database.Database(username)
    code = input("Room code: ")
    await database.connectToDatabase(code)
    while True:
        await asyncio.sleep(0.04)

asyncio.run(main())