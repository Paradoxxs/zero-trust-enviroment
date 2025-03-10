#!/usr/bin/env python

"""
Modbus Client and Server Implementation Script

This script provides a basic implementation of a Modbus TCP client and server using the pymodbus library. It defines two classes, `ClientModbus` and `ServerModbus`, which facilitate Modbus communication for reading and writing data.

Imports:
    - `pymodbus.client.sync.ModbusTcpClient`: Used to create a Modbus TCP client.
    - `pymodbus.server.async.ModbusServerFactory`: Used to create a Modbus server factory.
    - `pymodbus.device.ModbusDeviceIdentification`: Used to define Modbus device identification.
    - `pymodbus.datastore.ModbusSequentialDataBlock`: Used to create a sequential data block for the datastore.
    - `pymodbus.datastore.ModbusSlaveContext`: Used to define the context for a Modbus slave.
    - `pymodbus.datastore.ModbusServerContext`: Used to define the context for the Modbus server.
    - `pymodbus.exceptions.ConnectionException`: Exception handling for connection errors.
    - `pymodbus.transaction.ModbusSocketFramer`: Used to define the Modbus socket framer.

Global Variables:
    - `MODBUS_PORT`: The default port for Modbus communication (5020).

Classes:
    - `ClientModbus`: Inherits from `ModbusTcpClient` and provides methods for reading and writing Modbus registers.
    - `ServerModbus`: Inherits from `ModbusServerFactory` and sets up a Modbus server with a defined context and identity.

Usage:
    - To create a Modbus client, instantiate the `ClientModbus` class with the server address and optional port.
    - To create a Modbus server, instantiate the `ServerModbus` class with the server address and optional port.

Example:
    ```python
    from your_script import ClientModbus, ServerModbus

    # Initialize Modbus client
    client = ClientModbus('127.0.0.1')

    # Read from Modbus address
    data = client.read(0x01)
    print(f"Read data: {data}")

    # Write to Modbus address
    client.write(0x01, 1234)

    # Initialize Modbus server
    server = ServerModbus('127.0.0.1')
    ```

"""

import sys
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.server.async import ModbusServerFactory
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.exceptions import ConnectionException
from pymodbus.transaction import ModbusSocketFramer

# Global Variables
MODBUS_PORT = 5020

class ClientModbus(ModbusTcpClient):
    """
    Modbus TCP Client for reading and writing registers.

    Methods:
        - __init__(address, port=MODBUS_PORT): Initializes the client with the specified address and port.
        - read(addr): Reads a single register from the specified address.
        - readln(addr, size): Reads multiple registers starting from the specified address.
        - write(addr, data): Writes a single register to the specified address.
        - writeln(addr, data, size): Writes multiple registers starting from the specified address.
    """
    
    def __init__(self, address, port=MODBUS_PORT):
        ModbusTcpClient.__init__(self, address, port)

    def read(self, addr):
        regs = self.readln(addr, 1)
        return regs[0]

    def readln(self, addr, size):
        rr = self.read_holding_registers(addr, size)
        if not rr or not rr.registers:
            raise ConnectionException
        regs = rr.registers
        if not regs or len(regs) < size:
            raise ConnectionException
        return regs

    def write(self, addr, data):
        self.write_register(addr, data)

    def writeln(self, addr, data, size):
        self.write_registers(addr, data)

class ServerModbus(ModbusServerFactory):
    """
    Modbus Server Factory for handling Modbus server operations.

    Methods:
        - __init__(address, port=MODBUS_PORT): Initializes the server with the specified address and port.
        - write(addr, data): Writes a single register to the specified address.
        - writeln(addr, data, size): Writes multiple registers starting from the specified address.
        - read(addr): Reads a single register from the specified address.
        - readln(addr, size): Reads multiple registers starting from the specified address.
    """
    
    def __init__(self, address, port=MODBUS_PORT):
        block = ModbusSequentialDataBlock(0x00, [0]*0x3ff)
        store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
        self.context = ModbusServerContext(slaves=store, single=True)
        
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'MockPLCs'
        identity.ProductCode = 'MP'
        identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
        identity.ProductName = 'MockPLC 3000'
        identity.ModelName = 'MockPLC Ultimate'
        identity.MajorMinorRevision = '1.0'

        ModbusServerFactory.__init__(self, self.context, ModbusSocketFramer, identity)
    
    def write(self, addr, data):
        self.context[0x0].setValues(3, addr, [data])
    
    def writeln(self, addr, data, size):
        self.context[0x0].setValues(3, addr, [data])
    
    def read(self, addr):
        return self.context[0x0].getValues(3, addr, count=1)[0]

    def readln(self, addr, size):
        return self.context[0x0].getValues(3, addr, count=1)[0]

if __name__ == '__main__':
    sys.exit(main())
