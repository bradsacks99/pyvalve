""" Test class for Pyvalve """
import asyncio
import pytest
from io import BytesIO

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from src.pyvalve import Connection, Pyvalve, PyvalveSocket,  PyvalveNetwork, PyvalveResponseError, PyvalveConnectionError, PyvalveScanningError
from unittest import mock


@pytest.fixture(autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_send_command():
    # test a basic command
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

    pvs = await Pyvalve()
    result = await pvs.check_path('abc/123')
    assert result is False

    with mock.patch('src.pyvalve.AsyncPath.exists') as mock_exists:

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

@pytest.mark.asyncio
async def test_socket_get_connection():


    # test we raise the right errors
    with pytest.raises(PyvalveConnectionError):
        pvs = await PyvalveSocket()
        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        writer.is_closing = mock.Mock(return_value=True)
        conn = Connection(reader, writer)
        pvs.set_connection(conn)
        pvs.set_persistant_connection(True)
        await pvs.get_connection()

    # test we raise the right errors
    with mock.patch('src.pyvalve.asyncio.open_unix_connection', side_effect=FileNotFoundError('mocked error')):
        with pytest.raises(PyvalveConnectionError) as exc:
            pvs = await PyvalveSocket()
            await pvs.get_connection()
            assert exc.value.message == 'mocked error'

    # test we raise the right errors
    with mock.patch('src.pyvalve.asyncio.open_unix_connection', side_effect=Exception('mocked error')):
        with pytest.raises(PyvalveConnectionError) as exc:
            pvs = await PyvalveSocket()
            await pvs.get_connection()
            assert exc.value.message == 'mocked error'

@pytest.mark.asyncio
async def test_network_get_connection():


    # test we raise the right errors
    with pytest.raises(PyvalveConnectionError):
        pvs = await PyvalveNetwork()
        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        writer.is_closing = mock.Mock(return_value=True)
        conn = Connection(reader, writer)
        pvs.set_connection(conn)
        pvs.set_persistant_connection(True)
        await pvs.get_connection()

    # test we raise the right errors
    with mock.patch('src.pyvalve.asyncio.open_connection', side_effect=Exception('mocked error')):
        with pytest.raises(PyvalveConnectionError) as exc:
            pvs = await PyvalveNetwork()
            await pvs.get_connection()
            assert exc.value.message == 'mocked error'

@pytest.mark.asyncio
async def test_ping():
    # test ping command
    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)


    conn.reader.feed_data(b'PONG\n')
    conn.reader.feed_eof()

    result = await pvs.ping()

    assert result == 'PONG'

@pytest.mark.asyncio
async def test_stats():
    # test stats command
    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)


    conn.reader.feed_data(b'STATS\nI like big stats and I cannot lie\n')
    conn.reader.feed_eof()

    result = await pvs.stats()

    assert 'big stats' in result

@pytest.mark.asyncio
async def test_stats():
    # test stats command
    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)


    conn.reader.feed_data(b'STATS\nI like big stats and I can not lie\n')
    conn.reader.feed_eof()

    result = await pvs.stats()

    assert 'big stats' in result

@pytest.mark.asyncio
async def test_version():
    # test version command
    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)


    conn.reader.feed_data(b'VERSION:\n1.1\n')
    conn.reader.feed_eof()

    result = await pvs.version()

    assert '1.1' in result

@pytest.mark.asyncio
async def test_reload():
    # test reload command
    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)


    conn.reader.feed_data(b'RELOADING\n')
    conn.reader.feed_eof()

    result = await pvs.reload()

    assert 'RELOADING' in result

@pytest.mark.asyncio
async def test_shutdown():
    # test shutdown command
    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)


    conn.reader.feed_data(b'SHUTTING DOWN\n')
    conn.reader.feed_eof()

    result = await pvs.shutdown()

    assert 'SHUTTING DOWN' in result

@pytest.mark.asyncio
async def test_scan():
    # test scan command

    with mock.patch('src.pyvalve.AsyncPath.exists') as mock_exists:
        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        conn = Connection(reader, writer)
        future = asyncio.Future()
        future.set_result(True)
        mock_exists = mock.AsyncMock(return_value=future)

        pvs = await Pyvalve()
        pvs.get_connection = mock.AsyncMock(return_value=conn)
        pvs.set_connection(conn)


        conn.reader.feed_data(b'Received: /tmp/eicar.com.txt: Win.Test.EICAR_HDB-1 FOUND\n')
        conn.reader.feed_eof()

        result = await pvs.scan('/tmp/eicar.com.txt')

        assert 'Win.Test.EICAR_HDB-1 FOUND' in result

    with pytest.raises(PyvalveScanningError) as exc:

        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        conn = Connection(reader, writer)

        pvs = await Pyvalve()
        pvs.get_connection = mock.AsyncMock(return_value=conn)
        pvs.check_path = mock.AsyncMock(return_value=False)
        pvs.set_connection(conn)

        result = await pvs.scan('/tmp/eicar.com.txt')

        assert '/tmp/eicar.com.txt' in exc.value.message

@pytest.mark.asyncio
async def test_contscan():
    # test test_contscan command

    with mock.patch('src.pyvalve.AsyncPath.exists') as mock_exists:
        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        conn = Connection(reader, writer)
        future = asyncio.Future()
        future.set_result(True)
        mock_exists = mock.AsyncMock(return_value=future)

        pvs = await Pyvalve()
        pvs.get_connection = mock.AsyncMock(return_value=conn)
        pvs.set_connection(conn)


        conn.reader.feed_data(b'Received: /tmp/eicar.com.txt: Win.Test.EICAR_HDB-1 FOUND\n')
        conn.reader.feed_eof()

        result = await pvs.contscan('/tmp/eicar.com.txt')

        assert 'Win.Test.EICAR_HDB-1 FOUND' in result

    with pytest.raises(PyvalveScanningError) as exc:

        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        conn = Connection(reader, writer)

        pvs = await Pyvalve()
        pvs.get_connection = mock.AsyncMock(return_value=conn)
        pvs.check_path = mock.AsyncMock(return_value=False)
        pvs.set_connection(conn)

        result = await pvs.contscan('/tmp/eicar.com.txt')

        assert '/tmp/eicar.com.txt' in exc.value.message

@pytest.mark.asyncio
async def test_multiscan():
    # test test_multiscan command

    with mock.patch('src.pyvalve.AsyncPath.exists') as mock_exists:
        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        conn = Connection(reader, writer)
        future = asyncio.Future()
        future.set_result(True)
        mock_exists = mock.AsyncMock(return_value=future)

        pvs = await Pyvalve()
        pvs.get_connection = mock.AsyncMock(return_value=conn)
        pvs.set_connection(conn)


        conn.reader.feed_data(b'Received: /tmp/eicar.com.txt: Win.Test.EICAR_HDB-1 FOUND\n')
        conn.reader.feed_eof()

        result = await pvs.multiscan('/tmp/eicar.com.txt')

        assert 'Win.Test.EICAR_HDB-1 FOUND' in result

    with pytest.raises(PyvalveScanningError) as exc:

        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        conn = Connection(reader, writer)

        pvs = await Pyvalve()
        pvs.get_connection = mock.AsyncMock(return_value=conn)
        pvs.check_path = mock.AsyncMock(return_value=False)
        pvs.set_connection(conn)

        result = await pvs.multiscan('/tmp/eicar.com.txt')

        assert '/tmp/eicar.com.txt' in exc.value.message

@pytest.mark.asyncio
async def test_allmatchscan():
    # test test_allmatchscan command

    with mock.patch('src.pyvalve.AsyncPath.exists') as mock_exists:
        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        conn = Connection(reader, writer)
        future = asyncio.Future()
        future.set_result(True)
        mock_exists = mock.AsyncMock(return_value=future)

        pvs = await Pyvalve()
        pvs.get_connection = mock.AsyncMock(return_value=conn)
        pvs.set_connection(conn)


        conn.reader.feed_data(b'Received: /tmp/eicar.com.txt: Win.Test.EICAR_HDB-1 FOUND\n')
        conn.reader.feed_eof()

        result = await pvs.allmatchscan('/tmp/eicar.com.txt')

        assert 'Win.Test.EICAR_HDB-1 FOUND' in result

    with pytest.raises(PyvalveScanningError) as exc:

        reader = asyncio.StreamReader()
        writer = mock.Mock(asyncio.StreamWriter)
        conn = Connection(reader, writer)

        pvs = await Pyvalve()
        pvs.get_connection = mock.AsyncMock(return_value=conn)
        pvs.check_path = mock.AsyncMock(return_value=False)
        pvs.set_connection(conn)

        result = await pvs.allmatchscan('/tmp/eicar.com.txt')

        assert '/tmp/eicar.com.txt' in exc.value.message

@pytest.mark.asyncio
async def test_close():
    # test close command

    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)
    pvs.set_persistant_connection(True)
    result = await pvs.close()
    assert result is None

    reader = asyncio.StreamReader()
    writer = mock.Mock(asyncio.StreamWriter)
    conn = Connection(reader, writer)

    writer.close = mock.Mock(return_value=True)
    future = asyncio.Future()
    future.set_result(True)
    writer.wait_closed = mock.AsyncMock(return_value=future)

    pvs = await Pyvalve()
    pvs.get_connection = mock.AsyncMock(return_value=conn)
    pvs.set_connection(conn)
    result = await pvs.close()
    assert result is None
