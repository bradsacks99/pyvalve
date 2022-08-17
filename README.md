# pyvalve
Asyncio python clamav client library


## Usage Examples

Ping
```
pvs = await PyvalveNetwork()
response = await pvs.ping()
```
ClamAv will respond with "PONG"

Scanning

```
pvs = await PyvalveNetwork()
response = await pvs.scan(path)
```

Stream Scanning
```
from io import BytesIO
from aiofile import AIOFile

buffer = BytesIO()
async with AIOFile('some/file', 'r') as file_pointer:
    line = await file_pointer.read_bytes()
    buffer.write(line)
    buffer.seek(0)
response = await pvs.instream(buffer)
```

## Documentation

### _class_ Pyvalve()
Bases: `object`

Pyvalve base class

#### set_persistant_connection(persist)
Set persistent connection


* **Parameters**

    **bool** (*persist*) – persistent connection True/False



* **Return type**

    `None`



#### set_stream_buffer(length)
Set stream buffer


* **Parameters**

    **int** (*length*) – Desired stream buffer in bytes



* **Return type**

    `None`


#### _async_ allmatchscan(path)
Send allmatchscan command


* **Parameters**

    **str** (*path*) – Path to file/directory to be scanned



* **Returns**

    Response from clamav



* **Return type**

    str



* **Raises**

    **PyvalveScanningError** – If path is not found



#### _async_ contscan(path)
Send constscan command


* **Parameters**

    **str** (*path*) – Path to file/directory to be scanned



* **Returns**

    Response from clamav



* **Return type**

    str



* **Raises**

    **PyvalveScanningError** – If path is not found


#### _async_ instream(buffer)
Send a stream to clamav


* **Parameters**

    **buffer** (*BinaryIO*) – a buffer object



* **Returns**

    Response from clamav



* **Return type**

    str



* **Raises**

    
    * **PyvalveConnectionError** – If connection is broken


    * **PyvalveStreamMaxLength** – If stream size limit exceeded



#### _async_ multiscan(path)
Send multiscan command


* **Parameters**

    **str** (*path*) – Path to file/directory to be scanned



* **Returns**

    Response from clamav



* **Return type**

    str



* **Raises**

    **PyvalveScanningError** – If path is not found



#### _async_ ping()
Send ping command


* **Returns**

    Response from clamav



* **Return type**

    str



#### _async_ reload()
Send reload command


* **Returns**

    Response from clamav



* **Return type**

    str



#### _async_ scan(path)
Send scan command


* **Parameters**

    **str** (*path*) – Path to file/directory to be scanned



* **Returns**

    Response from clamav



* **Return type**

    str



* **Raises**

    **PyvalveScanningError** – If path is not found



#### _async_ shutdown()
Send shutdown command


* **Returns**

    Response from clamav



* **Return type**

    str


#### _async_ stats()
Send stats command


* **Returns**

    Response from clamav



* **Return type**

    str



#### _async_ version()
Send version command


* **Returns**

    Response from clamav



* **Return type**

    str


### _class_ PyvalveNetwork(host='localhost', port=3310, timeout=None)
Bases: `Pyvalve`

Asyncio Clamd network client


#### _async_ \__init__(host='localhost', port=3310, timeout=None)
PyvalveNetwork Constructor


* **Parameters**

    
    * **str** (*host*) – host address for clamav


    * **int** (*timeout*) – listening port for clamav


    * **int** – socket timemout


### _class_ PyvalveSocket(socket='/tmp/clamd.socket', timeout=None)
Bases: `Pyvalve`

Asyncio Clamd socket client


#### _async_ \__init__(socket='/tmp/clamd.socket', timeout=None)
PyvalveSocket Constructor


* **Parameters**

    
    * **str** (*socket*) – Path to socket file


    * **int** (*timeout*) – socket timemout



## Exceptions

### _exception_ PyvalveError()
Bases: `Exception`

Pyvalve exception base class

### _exception_ PyvalveConnectionError()
Bases: `PyvalveError`

Exception communicating with clamd

### _exception_ PyvalveResponseError()
Bases: `PyvalveError`

Exception processing response

### _exception_ PyvalveScanningError()
Bases: `PyvalveError`

Exception scanning. Could be path not found.

### _exception_ PyvalveStreamMaxLength()
Bases: `PyvalveResponseError`

Exception using INSTREAM with a buffer
length > StreamMaxLength in /etc/clamav/clamd.conf
