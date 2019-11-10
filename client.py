import asyncio


HOST = 'localhost'
PORT = 9095


async def tcp_echo_client(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    

    while True:
            data = await reader.read(1024)
            print(f'SERVER: {data.decode()}')
            message = input()
            writer.write(message.encode())
            await writer.drain()
            if message == 'exit' or data =='':
                data = await reader.read(18)
                print(f'SERVER: До свидания! Надеюсь, еще увидимся!')
                writer.close()
                break
    

    # await writer.wait_closed()

if __name__ == "__main__":
   
    asyncio.run(tcp_echo_client(HOST, PORT))

