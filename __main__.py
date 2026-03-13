from async_data_connector import Pair
from async_tws_connection import ib, build_connection
import async_execution_model as execution_model
import alpha_model
import async_logger as log
from constants import (
    PAIRS_TRADED,
    BUDGET,
    CURRENCY,
    THRESHOLD,
)
from personal_constants import ACCOUNT_NUMBER
from async_portfolio_model import Portfolio
import asyncio as aio


# For all Pairs a subscription to the data from TWS has to be made when the program starts.
async def connect_pairs(pairs):
    await aio.gather(*[pair.connect_data() for pair in pairs])


async def main():
    # The log will not be pushed to the repo, so it must be ensured that it exists before the program can start.
    await build_connection()
    await log.initialize_logger()

    portfolio = Portfolio(
        account_number=ACCOUNT_NUMBER, slots=PAIRS_TRADED, budget=BUDGET
    )
    await portfolio.initialize()

    # For further explanation about the Pairs class, please refer to the data_connector module.
    test_pairs = [
        Pair(("AAPL", "MSFT"), CURRENCY, (1, 1)),
        Pair(("META", "TSLA"), CURRENCY, (1, 1)),
        Pair(("GM", "CPNG"), CURRENCY, (1, 1)),
    ]

    await connect_pairs(test_pairs)

    while True:
        """
        The logic follows iteratively that same pattern.

        1. Generate new Signals for each of the Pairs that are currently traded.
        2. The Signals generated in 1. have to be evaluated by the portfolio.analyze_signals method.
        3. During the analysis, instructions about what the new positions should look like, were created.
           Those will be directed to the Execution Model in the next step.
        4. In the last step, current positions and Signals that could not be followed, because the maximum amount of trades
           we want to be in at the same time was reached, will be analyzed and the portfolio adjusted if a position fullfilled its
           predicted potential or if the position is blocking a better opportunity.
        """
        signals = alpha_model.generate_signals(test_pairs, threshold=THRESHOLD)
        portfolio_changes = portfolio.analyze_signals(signals)
        await execution_model.execute_portfolio_adjustments(
            portfolio, portfolio_changes
        )
        new_adjustments = portfolio.optimize()
        await execution_model.execute_portfolio_adjustments(portfolio, new_adjustments)


if __name__ == "__main__":
    aio.run(main())
else:
    raise ImportError("THE MODULE __main__.py IS NOT INTENDED TO BE IMPORTED")
