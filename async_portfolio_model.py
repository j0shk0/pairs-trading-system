"""
This module contains the relevant functions to size the current positions that should be taken,
according to the alpha_model properly.
"""

import copy
import sqlite3
from async_data_connector import Pair
from async_tws_connection import ib, build_connection
import async_logger as logger
from constants import PATH, DATABASE_NAME, MINIMUM_TRADE_COST, COST_PER_SHARE, CURRENCY


class Portfolio:
    """
    This class is used for the Portfolio management of the different Pair-Trades.

    The Portfolio class is able to analyze signals and decide if a Signal should be followed and can store signals
    that had to be ignored if there was no free slot. As all positions are intended to produce Alpha I
    decided to use equal weighting. A free slot is an opportunity that a trade can be made.

    The amount of capital allocated to each slot can be calculated through: budget / slots.

    A Portfolio is also able to optimize itself be checking if current performance of a trade already
    fulfilled its expectations or if a trade is blocking a better opportunity. The methods are  greedy
    in the sense that they try to fill all slots by optimizing for what is calculated as the delta
    by the alpha_model (deviation from the equilibrium of two stock), which is effectively the expected
    return because we want to capitalize on the fluctuation of difference of stock prices from their equilibrium.
    """

    def __init__(self, account_number, slots, budget, is_test=False):

        self.empty_slots = None
        self.account_number = account_number
        self.ignored_signals = {}
        self.budget = budget
        self.tws_positions = []
        self.pairs_traded = {}
        self.portfolio = {}
        self.followed_signals = {}
        self.all_slots = slots

    async def initialize(self):
        if ib.portfolio():
            for position in ib.portfolio():
                ticker = position.contract.symbol
                shares = position.position
                self.portfolio[ticker] = shares

        if self.portfolio:
            for ticker in list(self.portfolio.keys()):
                # As we only log trades that were actually made we can use the SQLite file as our memory of positions that have
                # been taken in the past.
                try:
                    with sqlite3.connect(PATH + DATABASE_NAME) as log:
                        cur = log.cursor()
                        execution_command = (
                            """SELECT * FROM Signals WHERE Ticker_a = ? OR Ticker_b = ?"""
                            """ ORDER BY Time DESC LIMIT 1;"""
                        )
                        cur.execute(execution_command, (ticker, ticker))
                        data = cur.fetchone()
                        if data is None:
                            print(
                                f"\033[32mPORTFOLIO MODEL\033[0m : No Signal to retrieve for {ticker};"
                            )
                            self.followed_signals[ticker] = tuple()
                        else:
                            (
                                timestamp,
                                deviation,
                                sign,
                                ticker_a,
                                ticker_b,
                                const,
                                slope,
                                threshold,
                            ) = data
                            pair = Pair((ticker_a, ticker_b), CURRENCY, (slope, const))
                            await pair.connect_data()
                            self.followed_signals[ticker] = (
                                deviation,
                                sign,
                                pair,
                                {
                                    ticker_a: copy.copy(pair.quotes_a),
                                    ticker_b: copy.copy(pair.quotes_b),
                                },
                                const,
                                slope,
                                threshold,
                            )
                            print(
                                f"\033[32mPORTFOLIO MODEL\033[0m : Signal retrieval for {ticker} from {timestamp} successful;"
                            )
                except sqlite3.OperationalError as e:
                    print(
                        "\033[32mPORTFOLIO MODEL\033[0m : Signal retrieval failed due to database error;"
                    )
                    print(e)
        else:
            self.followed_signals = {}
            print(
                "\033[32mPORTFOLIO MODEL\033[0m : No positions in tws detected - No followed signals should be loaded;"
            )
        initial_slot_value = self.all_slots - (len(self.portfolio.keys()) / 2)
        print(
            f"\033[32mPORTFOLIO MODEL\033[0m : Slot value detected with {initial_slot_value};"
        )
        self.empty_slots = copy.copy(
            initial_slot_value
        )  # Each signal involves two stocks.

    def analyze_signals(self, alpha_model_output):
        """
        Receives new signals generated by alpha_model and determines how they will be handled.
        :param alpha_model_output: List of signals generated by the alpha model.
        :return: Execution update (Information for the Execution Model which transactions to do)
        """
        new_signals, pairs = alpha_model_output
        portfolio_adjustment = {}

        # Retrieve and sort the signals generated by the alpha model.
        if isinstance(new_signals, dict):
            signals = list(new_signals.values())
        else:
            signals = new_signals

        if signals == []:
            return {}

        # Get a list of all ticker symbols that are already in the portfolio.
        symbols = [pos for pos in self.portfolio if self.portfolio[pos] > 0]

        # Store the pairs traded by the model to access market data.
        self.pairs_traded.update(pairs)

        signals.sort(key=lambda a: a[0], reverse=True)
        # Calculate the amounts of shares needed for each trade as long as there are still slots open.
        for signal in signals:

            deviation, sign, pair, quotes, const, slope, threshold = signal
            ticker_a, ticker_b = pair.tickers

            # We want to skip signals that involve Stocks that are already in the portfolio.
            # Those signals should be added to the ignored signals immediately.
            if not set(symbols).isdisjoint({ticker_a, ticker_b}):
                self.ignored_signals[pair.export_essentials()[0][0]] = signal
                self.ignored_signals[pair.export_essentials()[0][1]] = signal
                print(
                    f"""\033[32mPORTFOLIO MODEL\033[0m : Signal will be IGNORED - there is a similar trade in progress; """
                    f"""ticker_a = {ticker_a}; ticker_b = {ticker_b};"""
                )
                continue

            # This formula is a result of a linear system of equations that was solved for each amount of shares.
            shares_b = (self.budget / self.all_slots - const * quotes[ticker_a].ask) * (
                1 / (slope * quotes[ticker_a].ask + quotes[ticker_b].ask)
            )
            shares_a = const + slope * shares_b

            if self.empty_slots > 0:
                if sign > 0:
                    portfolio_adjustment[ticker_a] = -1 * int(shares_a)
                    portfolio_adjustment[ticker_b] = int(shares_b)
                else:
                    portfolio_adjustment[ticker_a] = int(shares_a)
                    portfolio_adjustment[ticker_b] = -1 * int(shares_b)
                self.followed_signals[pair.export_essentials()[0][0]] = signal
                self.followed_signals[pair.export_essentials()[0][1]] = signal
                self.empty_slots -= 1
                print(
                    f"""\033[32mPORTFOLIO MODEL\033[0m : New Signal will be ADDED to the Portfolio; """
                    f"""ticker_a = {ticker_a}, with {int(shares_a)} shares; ticker_b = {ticker_b}, with {int(shares_b)} shares;"""
                )
                # Time will be logged by the logger function itself.
                logger.log_signal(
                    deviation, sign, ticker_a, ticker_b, const, slope, threshold
                )
            else:
                self.ignored_signals[pair.export_essentials()[0][0]] = signal
                self.ignored_signals[pair.export_essentials()[0][1]] = signal
                print(
                    f"\033[32mPORTFOLIO MODEL\033[0m : New Signal will be IGNORED - No slot avaliable; ticker_a = {ticker_a}, with {int(shares_a)} shares;"
                    f"ticker_b = {ticker_b}, with {int(shares_b)} shares;"
                )
        return portfolio_adjustment

    def optimize(self):
        # First we gather the current positions directly from TWS if any exist.
        if not ib.portfolio():
            print("\033[32mPORTFOLIO MODEL\033[0m : No Portfolio detected;")
            return (
                {}
            )  # This is crucial because the execution_model requires a dict as input.
        else:
            self.tws_positions = ib.portfolio()

        symbols = [pos.contract.symbol for pos in self.tws_positions]

        current_ignored_signals = list(copy.copy(list(self.ignored_signals.values())))

        if not current_ignored_signals:
            return {}

        # We sort the ignored_signals in descending order (biggest element first) after their "deviation" parameter, the expected return.
        # The reason is of course prioritization.
        current_ignored_signals.sort(key=lambda a: a[0], reverse=True)

        portfolio_adjustment = {}
        signals_to_follow = []

        # We create a set to skip symbols from the symbols list we already looked at.
        visited_symbols = set()

        for symbol in symbols:
            if symbol in visited_symbols:
                continue

            last_signal = self.followed_signals[symbol]

            deviation, sign, pair, quotes, const, slope, threshold = last_signal
            tickers = tuple(quotes.keys())

            absolute_earnings = 0.00
            allocated_capital = self.budget / self.all_slots

            ignored_signals_index = 0
            ticker_a, ticker_b = tickers
            replacement_signal = current_ignored_signals[ignored_signals_index]
            ignored_ticker_a, ignored_ticker_b = tuple(replacement_signal[3].keys())
            opportunity_cost = replacement_signal[0]

            # Signals should only be those considered that involve stocks that are not in the portfolio already.
            # Otherwise, we could run into the situation that we try to replace a position with itself.
            # In this case we set the opportunity cost to 0.
            for signal in current_ignored_signals:
                replacement_signal = current_ignored_signals[ignored_signals_index]
                ignored_ticker_a, ignored_ticker_b = tuple(signal[3].keys())
                if set(symbols).isdisjoint({ignored_ticker_a, ignored_ticker_b}):
                    break
            else:
                print(
                    f"""\033[32mPORTFOLIO MODEL\033[0m : {ticker_a} and {ticker_b} have no alternative signal"""
                    f""" as a replacement that is not their own signal."""
                    f""" Opportunity Costs are therefore zero;"""
                )
                opportunity_cost = 0

            for ticker in tickers:
                visited_symbols.add(ticker)
                index = symbols.index(ticker)

                cost_to_trade = (
                    MINIMUM_TRADE_COST
                    if MINIMUM_TRADE_COST
                    >= (COST_PER_SHARE * self.tws_positions[index].position)
                    else (COST_PER_SHARE * self.tws_positions[index].position)
                )

                pnl_of_trade = self.tws_positions[index].unrealizedPNL

                # Two transactions are necessary because we need to buy and sell.
                absolute_earnings += 2 * cost_to_trade
                absolute_earnings += pnl_of_trade

            # Relative Earnings can now be compared if the match with the expected return so if the reversal is done or not.
            relative_earnings = absolute_earnings / allocated_capital
            potential = deviation - relative_earnings

            if relative_earnings >= deviation:

                print(
                    f"""\033[32mPORTFOLIO MODEL\033[0m : Profitable trade of {ticker_a} and {ticker_b} will be liquidated """
                    f"""as it surpassed it expected return;"""
                )

                # If the unrealized return tops or fulfills the expectations the position should be closed.
                portfolio_adjustment[ticker_a] = 0
                portfolio_adjustment[ticker_b] = 0
                # As the position should be clear we can increase the amount of free slots.
                # If this program will ever run with some kind of concurrency, the state the program is in when this is changed
                # needs to be taken into consideration.
                self.empty_slots += 1

                # The Signal must be removed from the followed signals list.
                self.followed_signals.pop(ticker_a)
                self.followed_signals.pop(ticker_b)
                continue

            elif relative_earnings > 0 and potential < opportunity_cost:
                print(
                    f"""\033[32mPORTFOLIO MODEL\033[0m : Profitable trade of {ticker_a} and {ticker_b} will be liquidated """
                    f"""because it blocks a more profitable trade;"""
                )

                # If the unrealized return tops or fulfills the prognosis the position should be cleared.
                portfolio_adjustment[ticker_a] = 0
                portfolio_adjustment[ticker_b] = 0
                self.empty_slots += (
                    1  # As the position ought to be clear we can increase this.
                )

                signals_to_follow.append(replacement_signal)
                current_ignored_signals.remove(replacement_signal)

                # The Signal must be removed from the followed signals list because it's not followed anymore.
                self.followed_signals.pop(ticker_a)
                self.followed_signals.pop(ticker_b)

                # The replacement Signal must be added to the followed signals list.
                self.followed_signals[ignored_ticker_a] = self.ignored_signals[
                    ignored_ticker_a
                ]
                self.followed_signals[ignored_ticker_b] = self.ignored_signals[
                    ignored_ticker_a
                ]

                # The replacement Signal must be removed from the ignored signals list.
                self.ignored_signals.pop(ignored_ticker_a)
                self.ignored_signals.pop(ignored_ticker_b)
                continue

        # The Model has to calculate the positions size for each signal that should be followed.
        # self.pairs_traded will be updated with {} because the Alpha Model added them already pairs_traded and
        # the purpose of pairs traded is to keep track of the data for each ticker.
        new_positions = self.analyze_signals((signals_to_follow, {}))
        portfolio_adjustment.update(
            new_positions
        )  # This is not the only occasion portfolio_adjustment receives data.

        print("\033[32mPORTFOLIO MODEL\033[0m : Portfolio optimization finished;")

        return portfolio_adjustment
