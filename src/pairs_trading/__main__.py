import asyncio as aio
import signal
from functools import partial
from eventkit import Event

from .core import alpha_model
from .core.async_execution_model import ExecutionModelSingleton
from .infrastructure import async_logger as log
from .infrastructure.async_data_connector import Pair
from .core.async_portfolio_model import Portfolio
from .infrastructure.async_connection import ib, build_connection
from .config.constants import (
    BUDGET,
    CURRENCY,
    PAIRS_TRADED,
)
from .infrastructure.EventBus import BusSingleton as EventBus
from .config.personal_constants import ACCOUNT_NUMBER


def shutdown(signum, frame):
    """
    Handles the application shutdown process by disconnecting resources and stopping
    the event loop.
    """
    print("\r", end="", flush=True)  # clears the ^C from the line
    try:
        ib.disconnect()
    except Exception as e:
        print(f"\033[33mWARNING\033[0m: during shutdown: {e}")
    try:
        loop = aio.get_running_loop()
        for task in aio.all_tasks(loop):
            task.cancel()
    except RuntimeError:
        pass
    print("ciao.")


async def connect_pairs(pairs):
    await aio.gather(*[pair.connect_data() for pair in pairs])


async def main():

    # TODO we might parse the pairs from a file.
    test_pairs = [
        Pair(("AAPL", "MSFT"), CURRENCY, (1, 0)),
        Pair(("CELH", "MNST"), CURRENCY, (1, 0)),
        Pair(("RIVN", "LCID"), CURRENCY, (1, 0)),
    ]

    # Register the shutdown handler for SIGINT (Ctrl+C).
    signal.signal(signal.SIGINT, shutdown)

    # Initialize the components of the application.
    await build_connection()
    await log.initialize_logger()
    portfolio = Portfolio(
        account_number=ACCOUNT_NUMBER, slots=PAIRS_TRADED, budget=BUDGET
    )
    await portfolio.initialize()

    # TODO maybe this must be the last thing to be done or we add a start event.
    await connect_pairs(test_pairs)
    for pair in test_pairs:
        EventBus.listen(
            partial(alpha_model.generate_signal, pair), pair.quotes_a.updateEvent
        )
        EventBus.listen(
            partial(alpha_model.generate_signal, pair), pair.quotes_b.updateEvent
        )

    # Register all Events and event listeners.
    EventBus.listen(build_connection, ib.disconnectedEvent)

    generate_signals_event = Event("GeneratedSignalEvent")
    EventBus.add_custom_event("GeneratedSignalEvent", generate_signals_event)
    EventBus.listen(
        portfolio.analyze_signal, generate_signals_event
    )
    EventBus.listen(
        log.log_signal, generate_signals_event
    )

    portfolio_change_event = Event("PortfolioAdjustmentEvent")
    EventBus.add_custom_event("PortfolioAdjustmentEvent", portfolio_change_event)
    EventBus.listen(
        ExecutionModelSingleton.execute_portfolio_adjustments, portfolio_change_event
    )

    while True:
        try:
            await aio.sleep(1)
        except aio.CancelledError:
            break

if __name__ == "__main__":
    aio.run(main())
else:
    raise ImportError("THE MODULE __main__.py IS NOT INTENDED TO BE IMPORTED")
