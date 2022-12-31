from toolz.curried import *
from typing import Dict
import numpy as np
import pandas as pd


def withdraw(amount: float,
             cum_inflation: float,
             weights: Dict[str, float],
             portfolio: Dict[str, float],
             tax: float = 0.15):

    total = sum(portfolio.values())
    withdraw_amount = amount * (1 + cum_inflation) / (1 - tax)

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

    return dict(zip(input_df.columns, np.linalg.solve(X, Y)))


def evolve_period(withdraw_amount: float,
                  portfolio: Dict[str, float],
                  growth_per_asset: Dict[str, float],
                  cum_inflation: float,
                  weights: Dict[str, float],
                  tax: float,
                  should_rebalance: bool):
    withdraw_result = withdraw(withdraw_amount,
                               cum_inflation=cum_inflation,
                               weights=weights,
                               portfolio=portfolio,
                               tax=tax)

    updated_portfolio = thread_first(
        withdraw_result.get("portfolio"),
        partial(grow, asset_growth=growth_per_asset),
        partial(rebalance, weights=weights, tax=tax) if should_rebalance else identity
    )

    return {
        "withdraw_amount": withdraw_result.get("amount"),
        "portfolio": updated_portfolio
    }


def simulate_evolution(df: pd.DataFrame,
                       portfolio: Dict[str, float],
                       inflation_col: str,
                       rebalance_col: str,
                       weights: Dict[str, float],
                       withdraw_rate: float = 0.04,
                       tax: float = 0.15):
    monthly_amount = withdraw_rate * sum(portfolio.values()) / 12
    cum_inflation = 0
    updated_portfolio = portfolio
    log = []
    index_name = df.index.name

    for index, row in df.iterrows():
        cum_inflation = (cum_inflation + 1) * (row[inflation_col] + 1) - 1

        result = evolve_period(monthly_amount,
                               portfolio=updated_portfolio,
                               growth_per_asset=row.to_dict(),
                               cum_inflation=cum_inflation,
                               weights=weights,
                               tax=tax,
                               should_rebalance=row[rebalance_col])

        updated_portfolio = result.get("portfolio")

        log.append(merge(updated_portfolio,
                         {"cum_inflation": cum_inflation,
                          "withdraw_amount": result.get("withdraw_amount"),
                          "balance": sum(updated_portfolio.values()),
                          index_name: index}))

    return (pd.DataFrame(log)
            .set_index(index_name)
            .round(2)
            .assign(initial_balance_infl_adj=lambda d: sum(portfolio.values()) * (d["cum_inflation"] + 1)))