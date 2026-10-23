import Database, asyncio

async def main():
    username = input("Username: ")
    database = Database.Database(username,True)
    await database.init()
    print(database.code)
    await database.set("Test_Variable",True)
    await database.set("Test1",1)
    counter = 0
    while True:
        await asyncio.sleep(5)
        counter  = await database.get("Test1") + 1
        await database.set("Test1", counter)
        print(await database.get("Test1"))

#Test

asyncio.run(main())