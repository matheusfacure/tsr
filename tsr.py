from toolz.curried import *


def withdraw(r, inflation, weights, portfolio, tax=0.15):
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


def grow(portfolio, selic, sp500, dolar):
    return thread_first(
        portfolio,
        update_in(keys=["sp500"], func=lambda x: x*(1+sp500)*(1+dolar)),
        update_in(keys=["selic"], func=lambda x: x*(1+selic))
    )


def rebalance(portfolio, weights, tax=0.15):
    
    if any([v>0 for v in weights.values()]):
        return portfolio
    
    total = sum(portfolio.values())
    w_diff = {a:(w/total)-weights.get(a) for a, w in portfolio.items()}
    withdraw_from = max(w_diff, key=w_diff.get)
    withdraw_to = min(w_diff, key=w_diff.get)
    
    A1 = portfolio.get(withdraw_from)
    A2 = total - A1
    w1 = weights.get(withdraw_from)
    
    A1_ = (A1+A2-A1*tx)/((1/w1) - tax)
    A2_ = A1_/w1 - A1_
    
    return {withdraw_from: A1_, withdraw_to: A2_}