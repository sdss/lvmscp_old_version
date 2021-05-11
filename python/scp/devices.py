#is code is for example _CK 2021/03/30

import asyncio

async def send_message(message):
    reader, writer = await asyncio.open_connection(
        '10.7.45.27', 1112)

    #sclHead = chr(0)+chr(7)
    #sclTail = chr(13)

    #sclStr = sclHead + message.upper() + sclTail

    sclStr = message.upper()
    print(f'Send: {message!r}')
    writer.write(sclStr.encode())
    await writer.drain()

    Reply = await receive_status(reader)
    fin = len(Reply)-1
    #print('status : ', status)
    print(Reply)
    print('reply : ', Reply[7:fin])
    print('Close the connection')
    writer.close()
    await writer.wait_closed()

async def receive_status(areader):
    sclReply = ""
    data = await areader.read(4096)
    recStr = data.decode()
    return recStr

asyncio.run(send_message("@253T?\\"))                            
