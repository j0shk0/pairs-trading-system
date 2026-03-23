"""
This module is testing the async_portfolio_model.py
"""
import pytest
import sqlite3
from src.pairs_trading.config.constants import PATH, DATABASE_NAME

from src.pairs_trading.core.async_portfolio_model import Portfolio

pytest_plugins = ('pytest_asyncio',)

@pytest.mark.asyncio
async def test_portfolio_init():

    portfolio = Portfolio(1234, 10, 1_000_000)
    assert portfolio.account_number == 1234
    assert portfolio.ignored_signals == dict()
    assert portfolio.budget == 1_000_000
    assert portfolio.tws_positions == []
    assert portfolio.pairs_traded == dict()
    assert portfolio.followed_signals == dict()
    assert portfolio.all_slots == 10
    assert portfolio.empty_slots is None
    await portfolio.initialize()

    try:
        if portfolio.portfolio:
            for ticker in list(portfolio.portfolio.keys()):
                # As we only log trades that were actually made we can use the SQLite file as our memory of positions that have
                # been taken in the past.
                with sqlite3.connect(PATH + DATABASE_NAME) as log:
                    cur = log.cursor()
                    execution_command = """SELECT * FROM Signals WHERE Ticker_a = ? OR Ticker_b = ?""" \
                                        """ ORDER BY Time DESC LIMIT 1;"""
                    cur.execute(execution_command, (ticker, ticker))
                    data = cur.fetchone()
                    if data is not None:
                        assert isinstance(portfolio.followed_signals[ticker], tuple)
                    else:
                        with pytest.raises(KeyError):
                            v = portfolio.followed_signals[ticker]
    except sqlite3.OperationalError as e:
        print("\033[32mTEST\033[0m : Signal retrieval failed due to database error during test;")
        print(e)
