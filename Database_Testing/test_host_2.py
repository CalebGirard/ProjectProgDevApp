import Database, asyncio

async def main():
    username = input("Username: ")
    database = Database.Database(username,True)
    await database.init()
    print(database.code)
    await database.setPath("users:lxs:cash",200)
    print(database.data)
    await database.set("Test1",1)
    while True:
        await asyncio.sleep(5)

# Tests

asyncio.run(main())