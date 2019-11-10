import asyncio
import pickle
import os
from hashlib import md5

HOST = 'localhost'
PORT = 9095
H_FILE = "hosts.pickle"
CHAT = "global.txt" 

async def auth(writer, reader, name):
    """
    Функция аутентификации
    """
    global clients

    print(name)
    if name in clients.keys():
        # проверка нахождения пользователя в файле системы
        user_name =  clients[name][0].decode()

        writer.write(f"Рад вновь вас здесь приветствовать, {user_name}.\nВведите, пожалуйста, пароль, чтобы я точно вас узнал...  ".encode())
        await writer.drain()
        
        while True:
            pas = await reader.read(100)
            h_pas = md5(pas).hexdigest()
            if h_pas == clients[name][1]:
                writer.write("""Ваш пароль верен! \nТеперь я полностью уверен, что зрение меня не подвело, и это вы!""".encode())
                await writer.drain()   
                break

            else:
                writer.write("""Ваш пароль не верен! 
                Повторите попытку и не дайте мне усомниться,что это вы!""".encode())
                await writer.drain()
    else:
        # авторизация нового пользователя 
        writer.write("Здравствуйте, мы с вами не знакомы, но сейчас это исправим ".encode())
        await writer.drain()
        writer.write("\nВведите свое имя: ".encode())
        await writer.drain()
        log = await reader.read(100)
        print(log)
        writer.write("\nВведите пароль, чтобы я в будущем вас точно узнал. ".encode())
        await writer.drain()
        pas = await reader.read(100)
        clients[name] = (log, md5(pas).hexdigest())
        print(clients)

        # вносим нового пользователя в файл для отслеживания
        with open(H_FILE,"wb") as file:
            pickle.dump(clients,file)
        
        writer.write(f"Поздравляю, {log.decode()}, теперь я однозначно тебя узнаю! ".encode())
        await writer.drain()
    

async def down(name, mes:str):
    """
    Запись сообщения в файл
    """
    with open (CHAT,"a") as f:
        print(f"{name}>> {mes.decode()}",file=f)

# async def up():
#     """
#     Возврат всего чата

#     """
async def chat(writer, reader, user, par):
    """
    Функция для общения и доступа к общему чату
    """
    if par == '1':
        writer.write('Введите сообщение, любезнейший: '.encode())
        await writer.drain()
        mes = await reader.read(100)
        print(mes.decode())
        await down(user,mes)
        print("received %s from %s" % (mes.decode(), user))
        

    elif par == '2':
        with open(CHAT,'r') as f:
            for i in f:
                writer.write(i.encode())
                
    else:
        writer.write("Я вас не понял, может, повторите?..".encode())
        await writer.drain()
        



async def handle_echo(reader, writer):
    global clients 

    addr = writer.get_extra_info("peername")
    
    await auth(writer,reader,addr[0])

    writer.write("""\nМеню:
        Введите '1', чтобы написать в общий чат. 
        Если вы захотите просмотреть историю сообщений чата, введите 2. 
        Для выхода введите 'exit'. """.encode())
    await writer.drain()
   
    par = await reader.read(4)
    par_d  = par.decode()
    while par_d != "exit":
        par_d  = par.decode()
        await chat(writer, reader, clients[addr[0]][0].decode(), par_d)
        writer.write("""\nМеню:
        Введите '1', чтобы написать в общий чат. 
        Если вы захотите просмотреть историю сообщений чата, введите 2. 
        Для выхода введите 'exit'. """.encode())
        par = await reader.read(200)

    writer.close()
    



async def main():
    
    server = await asyncio.start_server(handle_echo, HOST, PORT)
    
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    async with server:  
        await server.serve_forever()


if __name__ == "__main__":

    with open (CHAT,"w") as f:
        print("",file=f)
    # проверка на наличие информации в файлеы
    if os.path.getsize(H_FILE) > 0: 
        with open(H_FILE,"rb") as file:
            clients = pickle.load(file)
    else:
        clients = {}     
    asyncio.run(main())