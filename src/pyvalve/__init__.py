#!/usr/bin/env python
""" Pyvalve clamd client library """
import asyncio
import struct
import codecs
from io import BytesIO, BufferedReader
from typing import List, BinaryIO
from asyncinit import asyncinit
from aiopathlib import AsyncPath

__version__ = "0.1.3"
DEBUG = 0

def print_(msg: str) -> None:
    """
        Debug print
        :param str msg: The message
    """
    if DEBUG == 1:
        print(msg)

class PyvalveError(Exception):
    """ Pyvalve exception base class """

class PyvalveResponseError(PyvalveError):
    """ Exception processing response """

class PyvalveScanningError(PyvalveError):
    """ Exception scanning. Could be path not found. """

class PyvalveStreamMaxLength(PyvalveResponseError):
    """
    Exception using INSTREAM with a buffer
    length > StreamMaxLength in /etc/clamav/clamd.conf
    """

class PyvalveConnectionError(PyvalveError):
    """ Exception communicating with clamd """

# pylint: disable=too-few-public-methods
class Connection():
    """ Connection class """
    def __init__(self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter):
        """ Constructor"""
        self.reader = reader
        self.writer = writer

@asyncinit
class Pyvalve():
    """ Pyvalve base class """
    async def __init__(self):
        """ Constructor """
        self.conn: Connection = None
        self.stream_buffer = 1024
        self.persistant_connection = False

    def set_connection(self,  conn: Connection) -> None:
        """
        Set connection

        :param conn Connection: A connection object
        """
        self.conn = conn

    def set_stream_buffer(self,  length: int) -> None:
        """
        Set stream buffer

        :param length int: Desired stream buffer in bytes
        """
        self.stream_buffer = length

    def set_persistant_connection(self,  persist: bool) -> None:
        """
        Set persistent connection

        :param persist bool: persistent connection True/False
        """
        self.persistant_connection = persist

    async def ping(self) -> str:
        """
        Send ping command

        :return: Response from clamav
        :rtype: str
        """
        return await self.send_command('PING')

    async def stats(self) -> str:
        """
        Send stats command

        :return: Response from clamav
        :rtype: str
        """
        return await self.send_command('STATS')

    async def version(self) -> str:
        """
        Send version command

        :return: Response from clamav
        :rtype: str
        """
        return await self.send_command('VERSION')

    async def reload(self) -> str:
        """
        Send reload command

        :return: Response from clamav
        :rtype: str
        """
        return await self.send_command('RELOAD')

    async def shutdown(self) -> str:
        """
        Send shutdown command

        :return: Response from clamav
        :rtype: str
        """
        return await self.send_command('SHUTDOWN')

    async def scan(self, path: str) -> str:
        """
        Send scan command

        :param path str: Path to file/directory to be scanned
        :return: Response from clamav
        :rtype: str
        :raises PyvalveScanningError: If path is not found
        """
        if not await self.check_path(path):
            raise PyvalveScanningError(f'Path not found: {path}')
        return await self.send_command('SCAN', path)

    async def contscan(self, path: str) -> str:
        """
        Send constscan command

        :param path str: Path to file/directory to be scanned
        :return: Response from clamav
        :rtype: str
        :raises PyvalveScanningError: If path is not found
        """
        if not await self.check_path(path):
            raise PyvalveScanningError(f'Path not found: {path}')
        return await self.send_command('CONTSCAN', path)

    async def multiscan(self, path: str) -> str:
        """
        Send multiscan command

        :param path str: Path to file/directory to be scanned
        :return: Response from clamav
        :rtype: str
        :raises PyvalveScanningError: If path is not found
        """
        if not await self.check_path(path):
            raise PyvalveScanningError(f'Path not found: {path}')
        return await self.send_command('MULTISCAN', path)

    async def allmatchscan(self, path: str) -> str:
        """
        Send allmatchscan command

        :param path str: Path to file/directory to be scanned
        :return: Response from clamav
        :rtype: str
        :raises PyvalveScanningError: If path is not found
        """
        if not await self.check_path(path):
            raise PyvalveScanningError(f'Path not found: {path}')
        return await self.send_command('ALLMATCHSCAN', path)

    async def send_command(self,
        msg: str,
        *args: str) -> str:
        """
        Send a command to clamav

        :param str msg: The command
        :param list args: Command arguments
        :return: Response from clamav
        :rtype: str
        :raises PyvalveResponseError: If clamav responds with an error
        """
        await self.get_connection()

        jargs = ''
        if args:
            jargs = ' ' + ' '.join(args)

        message = f'n{msg}{jargs}\n'
        print_(f'Send: {message}')

        self.conn.writer.write(message.encode('utf-8'))

        await self.conn.writer.drain()
        data = await self.conn.reader.read()
        data_dec: str = data.decode().strip()

        if "ERROR" in data_dec:
            raise PyvalveResponseError(data_dec)
        print_(f'Received: {data_dec}')

        await self.close()

        return data_dec

    async def instream(self, buffer: BinaryIO) -> str:
        """
        Send a stream to clamav

        :param BinaryIO buffer: a buffer object
        :return: Response from clamav
        :rtype: str
        :raises PyvalveConnectionError: If connection is broken
        :raises PyvalveStreamMaxLength: If stream size limit exceeded
        """
        await self.get_connection()

        self.conn.writer.write('nINSTREAM\n'.encode('utf-8'))

        def read_chunks(file_object: BinaryIO, size: int):
            """ Read chunks generator """
            while True:
                chunk = file_object.read(size)
                if not chunk:
                    break
                yield chunk

        try:
            with buffer as buffer_pointer:
                for chunk in read_chunks(buffer_pointer, self.stream_buffer):
                    size = struct.pack(b'!L', len(chunk))
                    self.conn.writer.write(size + chunk)

            print_("Printed chunks. Closing out request.")
            self.conn.writer.write(struct.pack(b'!L', 0))

            print_("Done writing stream. Check results")

            data = await self.conn.reader.read()

            data_dec: str = data.decode().strip()
            if "INSTREAM size limit exceeded" in data_dec:
                raise PyvalveStreamMaxLength(data_dec)

            await self.conn.writer.drain()

            print_(f'Received: {data_dec}')
            print_('Close the connection')
            await self.close()

        except BrokenPipeError as exp:
            raise PyvalveConnectionError(exp) from exp

        return data_dec

    async def close(self) -> None:
        """ Close the stream """
        if self.persistant_connection:
            print_('Persist the connection')
            return None
        print_('Close the connection')
        self.conn.writer.close()
        await self.conn.writer.wait_closed()

    async def check_path(self, path: str) -> bool:
        """
        Check scanning path

        :param path str: Path to file/directory to be scanned
        """
        print_(f'Checking path {path}')
        chk_path = AsyncPath(path)

        return await chk_path.exists()

    async def get_connection(self):
        """ Place holder get_connection method """
        raise NotImplementedError("Must override get_connection")

class PyvalveSocket(Pyvalve):
    """
    Asyncio Clamd socket client
    """
    async def __init__(self, # type: ignore[misc]
        socket: str = "/tmp/clamd.socket",
        timeout: int = None):
        """
            PyvalveSocket Constructor

            :param socket str: Path to socket file
            :param timeout int: socket timemout
        """
        await super().__init__()
        self.socket = socket
        self.timeout = timeout

    async def get_connection(self) -> None:
        """
            Get a socket connection

            :raises PyvalveConnectionError: If Pyvalve cannot connect to clamav
        """
        if self.conn and self.persistant_connection:
            if self.conn.writer.is_closing():
                raise PyvalveConnectionError("Persitant connection no longer available")
        try:
            reader, writer = await asyncio.open_unix_connection(
                path = self.socket,
                ssl_handshake_timeout = self.timeout
            )
            self.set_connection(Connection(reader, writer))
        except FileNotFoundError as exc:
            raise PyvalveConnectionError(f"socket file not found: {self.socket}") from exc
        except Exception as exc:
            raise PyvalveConnectionError(str(exc)) from exc

class PyvalveNetwork(Pyvalve):
    """
    Asyncio Clamd network client
    """
    async def __init__(self, # type: ignore[misc]
        host: str = "localhost",
        port: int = 3310,
        timeout: int = None):
        """
        PyvalveNetwork Constructor

        :param host str: host address for clamav
        :param port int: listening port for clamav
        :param timeout int: socket timemout
        """
        await super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout

    async def get_connection(self) -> None:
        """
        Get a network connection

        :raises PyvalveConnectionError: If Pyvalve cannot connect to clamav
        """
        if self.conn and self.persistant_connection:
            if self.conn.writer.is_closing():
                raise PyvalveConnectionError("Persitant connection no longer available")
        try:
            reader, writer = await asyncio.open_connection(
                host = self.host,
                port = self.port,
                ssl_handshake_timeout = self.timeout
            )
            self.set_connection(Connection(reader, writer))
        except Exception as exc:
            raise PyvalveConnectionError(str(exc)) from exc
