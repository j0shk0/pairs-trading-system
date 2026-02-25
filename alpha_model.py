"""
This Module contains the functions that are need to determine if a 
trading opportunity based on the strategy is present.
"""
import copy
import math

def generate_signals(pairs, threshold):
    """
    Function to do the calculation generating a signal.
    :param pairs: A Pairs class object carrying all the necessary data.
    """
    new_signals = {}
    pairs_traded = {}

    for pair in pairs:
        const, slope = pair.equation
        estimate = const + slope * pair.quotes_b.dict()["ask"]

        # Calculate the Divergence from the estimation and Ask-price to get the residual and divide by estimate.
        delta = (pair.quotes_a.dict()["ask"] - estimate) / estimate

        if delta > threshold:

            # Assign priority based on strength of deviation.
            deviation = abs(delta)
            print(f"\033[32mALPHA MODEL\033[0m : Deviation = {deviation}; Stock_a = {pair.quotes_a}; Stock_b = {pair.quotes_b};")

            # We save the sign to find the correct trade direction later.
            sign = math.copysign(1, delta)
            ticker_a, ticker_b = pair.tickers

            pairs_traded[ticker_a] = pair
            pairs_traded[ticker_b] = pair

            # new_signals will contain all the information for future evaluation of the Signal.
            new_signals[pair.tickers] = (deviation,
                                         sign,
                                         pair,
                                         {
                                             ticker_a: copy.copy(pair.quotes_a),
                                             ticker_b: copy.copy(pair.quotes_b)
                                         },
                                         const,
                                         slope,
                                         threshold)

    return new_signals, pairs_traded

