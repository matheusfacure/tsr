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


def rebalance(portifolio, weights, tax=0.15):
    assert len(portifolio) == len(weights)
    assert np.isclose(sum(weights.values()), 1)

    all_assets = pd.DataFrame(portifolio, index=[0])
    all_assets_w = pd.DataFrame(weights, index=[0])

    w_diff = all_assets_w - all_assets / sum(portifolio.values())

    A_top = np.concatenate([
        -np.ones(len(portifolio) - 1).reshape(-1, 1) / all_assets_w.values[0][0],
        1 / all_assets_w.values[0][1:] * np.identity(len(portifolio) - 1)
    ], axis=1)

    last_row = np.array([1 / all_assets_w.values[0][0]] + list(np.zeros(len(portifolio) - 1))) - tax * (
                w_diff.values[0] < 0)

    A = np.concatenate([A_top, last_row.reshape(1, -1)])

    Y = np.array(
        list(np.zeros(len(portifolio) - 1)) +
        [all_assets.values[0].sum() - np.sum((w_diff.values[0] < 0) * all_assets.values[0] * tax)]
    )

    return dict(zip(all_assets.columns, np.linalg.solve(A, Y).round(2)))

