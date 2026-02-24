"""
This module enables the program to share the connection to tws.
"""

from ib_insync import IB

ib = IB()

async def build_connection():
    # Connect to TWS through ib_insync.
   await ib.connectAsync("127.0.0.1", 7497, clientId=16)

