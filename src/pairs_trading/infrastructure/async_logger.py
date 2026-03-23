"""
This Module contains the Logger class, an integral for all logging operations in this project.
"""

import aiosqlite
import asyncio as aio
import os
import time
from ..config.constants import PATH, DATABASE_NAME, THRESHOLD

current_time = time.strftime("%Y-%m-%d %H:%M:%S")


async def initialize_logger():
    if not os.path.exists(PATH / DATABASE_NAME):
        async with aiosqlite.connect(PATH / DATABASE_NAME) as log:
            try:
                create_table1 = f"""CREATE TABLE Signals(Time SmallDateTime, Deviation double, Sign int, Ticker_a char(15), 
                                    Ticker_b Char(15), Const double, Slope double, Threshold double);"""
                create_table2 = f"CREATE TABLE Trades(Time SmallDateTime, Type char(15), Action char(5), Quantity int, Stock char(15), Price double);"
                tasks = [
                    aio.create_task(log.execute(create_table1)),
                    aio.create_task(log.execute(create_table2)),
                ]
                await aio.gather(*tasks)
                await log.commit()
                print(
                    "\033[32mLOGGER\033[0m: Database was created with tables 'Trades' and 'Signals'"
                )
            except aiosqlite.OperationalError as e:
                print(
                    "\033[32mLOGGER\033[0m: Something went wrong with the creation of tables or database itself."
                )
                print(e)
    else:
        print("\033[32mLOGGER\033[0m : Database ready;")


async def log_trade(
    trade_type: str, action: str, quantity: int, stock_ticker: str, price: int
):
    """
    This function used by the execution model logs all trades that were sent to IBKR.
    :param trade_type: The type of the Trade is usually MARKETS (Market Order) or LIMIT (Limit Order).
    :param action : BUY or SELL
    :param quantity: The quantity of shares traded.
    :param stock_ticker: The ticker of the stock traded.
    :param price: The Price of the asset executed.
    """

    try:
        async with aiosqlite.connect(PATH / DATABASE_NAME) as log:
            execution_command = (
                f"INSERT INTO Trades (Time, Type, Action, Quantity, Stock, Price)"
                f"VALUES (?, ?, ?, ?, ?, ?)"
                ""
            )
            values = (current_time, trade_type, action, quantity, stock_ticker, price)
            await log.execute(execution_command, values)
            await log.commit()
            print(f"LOG : New Trade of {stock_ticker} written in Table Trades;")
    except aiosqlite.OperationalError as e:
        print(
            "\033[32mLOGGER\033[0m : Writing trade data to database not successful;", e
        )


async def log_signal(new_signal: tuple):
    """
    Logs a new trading signal to the database.

    The `log_signal` function asynchronously inserts a new trading signal into the database
    table `Signals`. In case of database operational errors, an error message is printed to
    the console.

    :param new_signal: A tuple containing the signal data.
        It includes:
        - deviation: The numeric value representing the signal's deviation.
        - sign: The sign of the deviation (positive or negative).
        - pair: The trading pair as a tuple consisting of ticker_a and ticker_b.
        - quotes: Ticker objects representing the current quotes for the pair.
        - const: A constant value or regression.
        - slope: The slope related to the signal trend.
    :raises aiosqlite.OperationalError: If an operational error occurs while interacting with
        the database.
    """

    deviation, sign, pair, quotes, const, slope = new_signal

    try:
        async with aiosqlite.connect(PATH / DATABASE_NAME) as log:
            execution_command = (
                f"INSERT INTO Signals (Time, Deviation, Sign, Ticker_a, Ticker_b, Const, Slope, Threshold)"
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                ""
            )
            await log.execute(
                execution_command,
                (
                    current_time,
                    deviation,
                    sign,
                    pair.ticker_a,
                    pair.ticker_b,
                    const,
                    slope,
                    THRESHOLD,
                ),
            )
            await log.commit()
            print(
                f"\033[32mLOGGER\033[0m : New Signal of {pair.ticker_a}/{pair.ticker_b} written in Table Signals;"
            )
    except aiosqlite.OperationalError as e:
        print(
            "\033[32mLOGGER\033[0m : Writing signal data to database not successful;", e
        )
