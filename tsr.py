from toolz.curried import *
from typing import Dict


def withdraw(r: float,
             inflation: float,
             weights: Dict[str, float],
             portfolio: Dict[str, float],
             tax: float = 0.15):

    total = sum(portfolio.values())
    withdraw_amount = total * r * (1 + inflation) / (1 - tax)

    w_diff = {a: (w / total) - weights.get(a) for a, w in portfolio.items()}
    w_diff = sorted(w_diff.items(), key=lambda x: x[1], reverse=True)

    total_to_withdraw = withdraw_amount
    updated_portfolio = dict()

    for asset, _ in w_diff:
        to_withdraw = min(total_to_withdraw, portfolio.get(asset))
        updated_portfolio[asset] = portfolio.get(asset) - to_withdraw
        total_to_withdraw -= to_withdraw

    return {"amount": withdraw_amount * (1 - tax),
            "portfolio": updated_portfolio}


def grow(portfolio: Dict[str, float],
         asset_growth: Dict[str, float]):
    return {asset: value*(1+asset_growth.get(asset))
            for asset, value in portfolio.items()}


def rebalance(portfolio, weights, tax=0.15):
    total = sum(portfolio.values())
    w_diff = {a:(w/total)-weights.get(a) for a, w in portfolio.items()}
    withdraw_from = max(w_diff, key=w_diff.get)
    withdraw_to = min(w_diff, key=w_diff.get)
    
    A1 = portfolio.get(withdraw_from)
    A2 = total - A1
    w1 = weights.get(withdraw_from)
    
    A1_ = (A1+A2-A1*tax)/((1/w1) - tax)
    A2_ = A1_/w1 - A1_
    
    return {withdraw_from: A1_, withdraw_to: A2_}