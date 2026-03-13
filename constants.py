"""
This file contains all constants that need to be set, except personal constants explained in the README.md.
"""

# General
# -------

# Port
PORT = 4002

# The Currency traded
CURRENCY = "USD"

# The value of the whole portfolio
BUDGET = 500_000.00

# Amount of thed slots which is essentially the divisor of budget to determine the capital allocated to a trade.
PAIRS_TRADED = 10

PATH = "./pairs-trading/dbs/"

DATABASE_NAME = "trading_log.db"

DB_SETUP_TIMEOUT = 5

GENERIC_TIMEOUT = 3

THRESHOLD = 0

MARKET_DATA_TYPE = 3

# Trading Cost
# ------------
"""
Please make sure the fees fit to your Situation.
As far as I am informed for Paper Trading, FIXED is assumed.
Also, I am based in Germany and Trading Costs AND Regulatory Fees could be different in other countrys.

Source (21.11.2024) : https://www.interactivebrokers.ie/en/pricing/commissions-stocks.php
"""

# Per Order minimum cost are 1.00 for shares (FIXED)
# Careful, for fractional shares its different.
MINIMUM_TRADE_COST = 1.00

# Per Order max cost is 1% of the trade value
MAX_TRADE_COST_PCT = 0.01

# Max absolute value per trade in USD
# However in case of partial execution each execution is considered one trade.
MAX_TRADE_COST_ABS = 8.30

COST_PER_SHARE = 0.005

# Regulatory Fees
# ---------------

# SEC Transaction Fee: USD 0.0000278 * Value of Aggregate Sales
SEC_TRANS_FEE = 0.0000278

# FINRA Trading Activity Fee: USD 0.000166 * Quantity Sold
FINRA_TRADING_ACTIVITY_FEE = 0.000166

# FINRA Consolidated Audit Trail Fees: USD 0.000048 * Quantity to 0.0000729 * Quantity
FINRA_AUDIT_FEES = 0.0000729

# Clearing Fees
# -------------
NSCC_DTC_FEES = 0.00020

# Pass through Fees
# -----------------
# NYSE Pass Through Fees: Commissions * 0.000175
NYSE_PASS_THROUGH = 0.000175
# FINRA Pass Through Fees: Commissions * 0.000565
FINRA_PASS_THROUGH = 0.000565
