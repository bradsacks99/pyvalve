""" Test class for Pyvalve """
import asyncio
import pytest
from io import BytesIO

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from src import Connection, Pyvalve, PyvalveResponseError, PyvalveConnectionError
from unittest import mock


@pytest.fixture(autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_send_command():
     #test a basic command
    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)


    conn.reader.feed_data(b'PONG\n')
    conn.reader.feed_eof()

    result = await pvs.send_command('PING')

    assert result == 'PONG'

    # test we raise the right errors
    with pytest.raises(PyvalveResponseError):

        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        conn = Connection(reader, writer)

        pvs = await Pyvalve()
        pvs.get_connection = mock.AsyncMock(return_value=conn)
        pvs.set_connection(conn)

        conn.reader.feed_data(b'ERROR: you suck\n')
        conn.reader.feed_eof()

        result = await pvs.send_command('PING')

    # test args
    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)


    conn.reader.feed_data(b'OK\n')
    conn.reader.feed_eof()

    result = await pvs.send_command('SCAN /tmp/nofile')

    writer.write.assert_called_with('nSCAN /tmp/nofile\n'.encode('utf-8'))

@pytest.mark.asyncio

async def test_check_path():

    with pytest.raises(PyvalveConnectionError):
        pvs = await Pyvalve()
        await pvs.check_path('abc/123')

    with mock.patch('src.AsyncPath.exists') as mock_exists:

        future = asyncio.Future()
        future.set_result(True)
        mock_exists = mock.AsyncMock(return_value=future)

        pvs = await Pyvalve()
        await pvs.check_path('abc/123')

@pytest.mark.asyncio
async def test_send_instream():
     #test a basic command
    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)

    buffer = BytesIO()
    buffer.write(os.urandom(2048))
    buffer.seek(0)

    conn.reader.feed_data(b'DONE\n')
    conn.reader.feed_eof()

    result = await pvs.instream(buffer)

    assert result == 'DONE'
