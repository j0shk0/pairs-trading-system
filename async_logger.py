"""
This Module contains the Logger class, an integral for all logging operations in this project.
"""

import aiosqlite
import asyncio as aio
import os
import time
from constants import PATH, DATABASE_NAME

current_time = time.strftime("%Y-%m-%d %H:%M:%S")


async def initialize_logger():
    if not os.path.exists(PATH + DATABASE_NAME):
        async with aiosqlite.connect(PATH + DATABASE_NAME) as log:
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
    :param trade_type: The type of the Trade so usually MARKET (Market Order) or LIMIT (Limit Order).
    :param action : BUY or SELL
    :param quantity: The amount of shares traded.
    :param stock_ticker: The ticker of the stock traded.
    :param price: The Price of the asset executed.
    """

    try:
        async with aiosqlite.connect(PATH + DATABASE_NAME) as log:
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


async def log_signal(
    deviation: float,
    sign: int,
    ticker_a: str,
    ticker_b: str,
    const: float,
    slope: float,
    threshold: float,
):
    """
    This function used by the alpha model logs all signals generated.
    :param deviation: The Deviation of the two stock prices from their equilibrium.
    :param sign: The sign of the deviation. This is separated to indicate the direction of the deviation.
    :param ticker_a: Ticker of the first Stock.
    :param ticker_b: Ticker of the second Stock.
    """

    try:
        async with aiosqlite.connect(PATH + DATABASE_NAME) as log:
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
                    ticker_a,
                    ticker_b,
                    const,
                    slope,
                    threshold,
                ),
            )
            await log.commit()
            print(
                f"\033[32mLOGGER\033[0m : New Signal of {ticker_a}/{ticker_b} written in Table Signals;"
            )
    except aiosqlite.OperationalError as e:
        print(
            "\033[32mLOGGER\033[0m : Writing signal data to database not successful;", e
        )


"""
I aim to do a full refacotring of the architecture implementing async where possible (and sensible).
As a result of that I need to rewrite each Module by its own and thereby test it in isolation.
"""


async def test_main():
    await initialize_logger()
    await log_signal("6.90902283788843", "1", "AMZN", "CPNG", "1.0", "1.0", "0.0")

    await log_trade("MARKET", "SELL", "211", "AMZN", "210.62")


if __name__ == "__main__":
    # Redefining the PATH for the test so that this file can be run as main
    PATH = r"./dbs/"
    aio.run(test_main())
