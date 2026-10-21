import Database, asyncio

async def main():
    username = input("Username: ")
    database = Database.Database(username)
    code = input("Room code: ")
    await database.connectToDatabase(code)
    while True:
        data = await asyncio.to_thread(input, f"{username} > ")
        await database.sendAsClient(data)

asyncio.run(main())