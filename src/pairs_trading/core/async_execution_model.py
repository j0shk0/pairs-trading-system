"""
This Module contains the functions necessary to size and place orders on behalf of the Alpha Model.
"""

import copy
import ib_async
from ..core import async_portfolio_model

from ..infrastructure.async_connection import ib, build_connection


class ExecutionModel:

    def __init__(self):
        self.__trades_in_progress = dict()

    @staticmethod
    async def stock_limit_order(contract: ib_async.contract.Stock, limit_price: int, action: str, quantity: int
                          ):
        """
        Wrapper for an ib_async Limit-Order.
        :param contract: The ib_async.contract.Stock Object, necessary for the execution of the order.
        :param limit_price: The desired price.
        :param action: Intention to "BUY" or "SELL".
        :param quantity: The quantity of shares to be bought or sold.
        :return:
        """
        order = ib_async.LimitOrder(action, quantity, limit_price)
        trade = ib.placeOrder(contract, order)
        print(
            f"\033[32mEXECUTION MODEL\033[0m : Limit {action} Order for {quantity} shares of {contract} placed;"
        )

    @staticmethod
    async def stock_market_order(
        contract: ib_async.contract.Stock, action: str, quantity: int
    ):
        """
        Wrapper for an ib_async Market-Order.
        :param contract: The ib_async.contract.Stock Object, necessary for the execution of the order.
        :param action: Intention to "BUY" or "SELL".
        :param quantity: The quantity of shares to be bought or sold.
        :return:
        """
        order = ib_async.MarketOrder(action, quantity)
        trade = ib.placeOrder(contract, order)
        print("\033[32mEXECUTION MODEL\033[0m: Market Order sent.")

        # TODO What happens if the order is not filled? or if the order is cancelled?

    async def execute_portfolio_adjustments(self,
        portfolio_class: async_portfolio_model.Portfolio, portfolio_adjustments: dict
    ):
        """
        Execution of the portfolio_adjustments, given as preferred new position sizes.
        :param portfolio_class: The class of the current Portfolio from the Module async_portfolio_model.py.
        :param portfolio_adjustments: Dictionary with ticker strings as Keys and Position Size as values.
        :return:
        """
        if portfolio_adjustments == {}:
            return "\033[32mEXECUTION MODEL\033[0m : No portfolio adjustments received."

        for ticker, ideal_position_size in portfolio_adjustments.items():

            try:
                old_position_size = portfolio_class.portfolio[ticker]
            except KeyError:
                old_position_size = 0
            # The position_size variable determines the amount of shares of the next trade and the type of action. An action is a buy or a sell.
            # If the position_size is below zero, the old_position_size is too big compared to the ideal_position_size ==> we need a sell. (Equal vice versa).
            position_size = ideal_position_size - old_position_size

            # We have to find out if the involved ticker is ticker_a or ticker_b of the Pair class (for more on Pair class visit data_connector.py)
            pair = portfolio_class.pairs_traded[ticker]
            if pair.ticker_a == ticker:
                contract = pair.contract_a
            else:
                contract = pair.contract_b

            if position_size < 0:
                await self.stock_market_order(contract, "SELL", quantity=abs(position_size))
                try:
                    portfolio_class.portfolio[ticker] += position_size
                except KeyError:
                    portfolio_class.portfolio[ticker] = copy.copy(position_size)
            elif position_size > 0:
                # Caution: If the Model should work with a more complex execution Algorithm Limit-Orders
                # that might need to be canceled, it CAN'T be assumed that the positions size is always completely executed.
                await self.stock_market_order(contract, "BUY", quantity=position_size)

                # If there is not yet a Position size we can safely assign it. If there is one we have to add the size,
                # because sell orders have a negative sign. Buy orders have a positive sign.
                try:
                    portfolio_class.portfolio[ticker] += position_size
                except KeyError:
                    portfolio_class.portfolio[ticker] = copy.copy(position_size)
            else:
                print(
                    f"\033[32mEXECUTION MODEL\033[0m : Zero positional change - no execution necessary for {ticker};"
                )
        return None

ExecutionModelSingleton = ExecutionModel()
