import Database, asyncio

async def main():
    username = input("Username: ")
    database = Database.Database(username,True)
    await database.openRoom()
    print(database.code)
    while True:
        data = await asyncio.to_thread(input, f"{username} > ")
        await database.broadcast(data)

#Test

asyncio.run(main())