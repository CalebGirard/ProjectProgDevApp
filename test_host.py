import Database, asyncio

async def main():
    username = input("Username: ")
    database = Database.Database(username,True)
    await database.openRoom()
    print(database.code)
    while True:
        await asyncio.sleep(0.04)

asyncio.run(main())