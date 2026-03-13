"""
This module enables the program to share the connection to tws.
"""

from ib_async import IB
from constants import PORT

ib = IB()


async def build_connection():
    # Connect to TWS through ib_async.
    await ib.connectAsync("127.0.0.1", PORT, clientId=16)
    ib.reqMarketDataType(3)
