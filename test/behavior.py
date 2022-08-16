""" 
Test against a real clamd, with real data 
This is used for internal testing.

"""
import asyncio
from io import BytesIO
from aiofile import async_open, AIOFile, LineReader
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from src import PyvalveNetwork, PyvalveSocket

data_bin = os.path.dirname(os.path.abspath(__file__)) + '/data_bin'

async def main():
    """ Test """
    pvs = await PyvalveNetwork()
    pvs.set_persistant_connection(False)
    response = await pvs.ping()
    print(response)
    response = await pvs.stats()
    print(response)
    response = await pvs.version()
    print(response)
    response = await pvs.scan(data_bin)
    print(response)
    response = await pvs.contscan(data_bin)
    print(response)
    response = await pvs.multiscan(data_bin)
    print(response)
    response = await pvs.allmatchscan(data_bin)
    print(response)


    # Test stream
    buffer = BytesIO()
    async with AIOFile(f'{data_bin}/eicar.com.txt', 'r') as file_pointer:
        line = await file_pointer.read_bytes()
        buffer.write(line)
        buffer.seek(0)
    response = await pvs.instream(buffer)
    print(response)

    # Test stream
    buffer = BytesIO()
    async with AIOFile(
        f'{data_bin}/opensnitch_1.4.0.rc2-1_amd64.deb',
        'r') as file_pointer:
        line = await file_pointer.read_bytes()
        buffer.write(line)
        buffer.seek(0)
    response = await pvs.instream(buffer)
    print(response)

    try:
        # Test stream with file that's to big
        buffer = BytesIO()
        async with AIOFile(
            f'{data_bin}/kali-linux-2021.2-virtualbox-amd64.ova',
            'r') as file_pointer:
            line = await file_pointer.read_bytes()
            buffer.write(line)
            buffer.seek(0)
        response = await pvs.instream(buffer)
        print(response)
    except:
        pass

    # Test stream with a possitive
    buffer = BytesIO()
    async with AIOFile(
        f'{data_bin}/eicar.com.txt',
        'r') as file_pointer:
        line = await file_pointer.read_bytes()
        buffer.write(line)
        buffer.seek(0)
    response = await pvs.instream(buffer)
    print(response)

    response = await pvs.reload()
    print(response)
    response = await pvs.shutdown()
    print(response)

if __name__ == '__main__':
    asyncio.run(main())
