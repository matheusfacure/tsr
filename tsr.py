from toolz.curried import *
from typing import Dict
import numpy as np
import pandas as pd


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


def rebalance(portfolio: Dict[str, float],
              weights: Dict[str, float],
              tax: float = 0.15):
    assert len(portfolio) == len(weights)
    assert np.isclose(sum(weights.values()), 1)
    assert portfolio.keys() == weights.keys()

    all_assets_w = pd.DataFrame(weights, index=["weight"])
    all_assets = pd.DataFrame(portfolio, index=["amount_0"])

    w_diff = (
            all_assets_w - all_assets.rename(index={"amount_0": "weight"}) / sum(portfolio.values())
    ).rename(index={"weight": "weight_diff"})

    input_df = pd.concat([all_assets, all_assets_w, w_diff])

    X = np.diag((1 / input_df.loc["weight"]).values) + (input_df.loc["weight_diff"] < 0).values.T * (-tax)
    Y = np.ones(len(portfolio)) * input_df.loc["amount_0"].sum() - tax * (
            input_df.loc["amount_0"] * (input_df.loc["weight_diff"] < 0)).sum()

    return dict(zip(input_df.columns, np.linalg.solve(X, Y).round(2)))
