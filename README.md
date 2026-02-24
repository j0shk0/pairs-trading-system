# pairs-trading

- [About](#About)
- [Features](#Features)
- [What is Pairs Trading?](#what-is-pairs-trading?)
- [Prerequisites](#Prerequisites)
- [Usage](#Usage)
- [License](#License)
- [Disclaimer](#Disclaimer)


# About 

Please first have a look at the [Disclaimer](#Disclaimer)

This is an implementation of a Pairs Trading System written in Python. The Trading System interacts directly with the [Trader-Workstation (TWS)](https://www.interactivebrokers.ie/en/trading/tws.php) from [Interactive Brokers](https://www.interactivebrokers.ie/en/home.php). The Project focuses on the technical side and serves an educational purpose only.

I intentionally kept certain parts of the System very rudimentary as this is a prototype and will be further refined by time.

# Features

The Trading System will create its own SQLite file, and respective Tables to store its trades and signals that were generated. It will remember which signals were used for its positions if the bot is switch off.

First of all the Model will generate Signals. In the second step those Signals will be analyzed and if possible executed. You can change the Variables in `constant.py` to influence how much capital is allocated on how many different trades. In the last step the Portfolio will try to optimize itself by looking into the opportunity costs of signals that could not be followed because all capital was already allocated and compares them with the potential of its current positions.

The Trading System is build out of different parts, including an Alpha Model, Execution Model, a Portfolio Model. Each Instance will print to the Terminal to inform the user about its most recent actions.

<p align="center">
  <img src="https://github.com/user-attachments/assets/04dc37af-c78e-49b1-b407-45532cbbec33" />
</p>

<h1 id="what-is-pairs-trading?">What is Pairs Trading ?</h1>

Pairs Trading is theoretically a market independent trading strategy. Market independence means that, even in scenarios where the broader market loses value (e.g., due to economic downturns), the strategy aims to generate positive returns by exploiting market inefficiencies, provided the assumptions and pair selection are sound. Such returns are referred to as alpha returns, as they are represented by the intercept in the Capital Asset Pricing Model (CAPM) regression.

<p align="center">
  <img src="https://github.com/user-attachments/assets/1ce93171-2ba3-436f-aa90-5934801b5523" width="300"/>
</p>

In the CAPM framework, stock returns `R_s` can be explained as a function of market returns `R_m` relative to the risk-free rate `R_f`. While the CAPM has been subject to debate, it remains an influential model for understanding stock performance. Alpha, derived from the intercept of the CAPM regression, refers to returns that are uncorrelated with market movements and is widely used as a measure of excess returns.

Pairs trading involves recognizing pairs, i.e. a collection of different stocks whose prices are related to each other so that a deviation from their equilibrium can be exploited. This can be achieved by selling `stock_a` when its price is overvalued in terms of `stock_b`, while buying `stock_b` at the same time to profit from the reversion to their equilibrium.

One effective method to identify suitable pairs is cointegration, which helps quantify the long-term statistical relationship between two assets. As the internet provides an abundance of further information around this topic (for free) I would encourage the curious reader to continue with one of the other resources.

# Prerequisites

One major requirement is an Account at Interactive Brokers that is sufficiently funded to be eligible to receive Market Data. Besides that there are a couple of dependencies.

A `.txt` file is included in the folder `env`, enabling the reproduction of my environment explained [here](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#building-identical-conda-environments).

Beyond that, it is required to create a file named `personal_constants.py`, including a variable called `ACCOUNT_NUMBER` of your Paper Trading Account.

**CAUTION** the Pairs in the code have no durable relationship at all. They are only in there for demostrational purposes.

# Usage

Python 3.11.5 or higher is recommended as I used this version for the development. The Program will only run if TWS is set up correctly to allow interactions with a Program. Please disable `API > Setting > Read-Only API`.

If all requirements above are fullfilled you can log into your Paper Trading Account and run the Program from a simultaneously open Terminal. Please make sure to `cd` to the directory where the clone of this Repository is stored and run it through the command `python pairs-trading`, after selecting the conda environment.

It is safe to end the program manually via `ctrl + c`.

# License

This project is licensed by the GNU Licence. Please visit [LICENSE](docs/LICENSE.md) for further information.

# Disclaimer

This trading bot is provided solely for educational and informational purposes and is not intended as financial or investment advice. All decisions made by the bot are automated and provided "as is" without any warranty. Users should not rely on the bot's outputs for making real-world trading or investment decisions. Consultation with a qualified financial advisor is recommended for any trading or investment activities. The creators of this bot assume no responsibility for any losses or damages resulting from its use. The Bot must not be used in a live Trading Environment of interactive Broker. Usage is only allowed in Paper Trading Accounts.
