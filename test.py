from tsr import withdraw, rebalance
import numpy as np


def test_withdraw():

    amount = 100
    inflation = 0.01
    tax = 0.05
    portfolio = {"selic": 500, "sp500": 500}

    # Test Unbalanced portfolio
    weights = {"selic": 0.6, "sp500": 0.4}

    expected_amount = 100 * (1 + inflation)
    expected_port = {'selic': 500, 'sp500': 500 - expected_amount / (1 - tax)}

    result = withdraw(amount, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "unbalanced portfolio not working"
    assert result.get("portfolio") == expected_port, "unbalanced portfolio not working"

    # Test balanced portfolio
    weights = {"selic": 0.5, "sp500": 0.5}

    expected_amount = 100 * (1 + inflation)
    expected_port = {'selic': 500 - expected_amount / (1 - tax), 'sp500': 500}

    result = withdraw(amount, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "balanced portfolio not working"
    assert result.get("portfolio") == expected_port, "balanced portfolio not working"

    # Test 1 asset portfolio
    portfolio = {"sp500": 1000}
    weights = {"sp500": 1.0}

    expected_amount = 100 * (1 + inflation)
    expected_port = {'sp500': 1000 - expected_amount / (1 - tax)}

    result = withdraw(amount, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "1 asset portfolio not working"
    assert result.get("portfolio") == expected_port, "1 asset portfolio not working"

    # Test 3 asset portfolio
    portfolio = {"selic": 500, "sp500": 300, "bovespa": 200}
    weights = {"selic": 0.5, "sp500": 0.25, "bovespa": 0.25}

    expected_amount = amount * (1 + inflation)
    expected_port = {"selic": 500, "sp500": 300-expected_amount / (1 - tax), "bovespa": 200}

    result = withdraw(amount, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "3 asset portfolio not working"
    assert result.get("portfolio") == expected_port, "3 asset portfolio not working"

    # Emptying one asset
    portfolio = {"selic": 950, "sp500": 50}
    weights = {"selic": 0.99, "sp500": 0.01}

    expected_amount = 100 * (1 + inflation)
    expected_port = {"selic": 950 - (expected_amount/(1 - tax) - 50), "sp500": 0.0}

    result = withdraw(amount, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "emptying not working"
    assert result.get("portfolio") == expected_port, "emptying not working"


def test_rebalance():
    def check_rebalance(old_p, new_p, w, tax):
        amount_withdrawn = sum([
            old_p.get(asset) - new_p.get(asset)
            for asset in old_p.keys()
            if w.get(asset) - old_p.get(asset) / sum(old_p.values()) < 0
        ])

        tax_payed = (sum(old_p.values()) - sum(new_p.values()))

        assert np.isclose(tax_payed, amount_withdrawn * tax)

        new_w = {asset: np.round(amount / sum(new_p.values()), 5) for asset, amount in new_p.items()}
        assert new_w == w

    portfolio = {"sp500": 50000, "selic": 10000, "bova": 40000}
    weights = {"sp500": 0.6, "selic": 0.3, "bova": 0.1}
    tax = 0.15

    check_rebalance(portfolio, rebalance(portfolio, weights, tax), weights, tax)

    portfolio = {"sp500": 50000, "selic": 10000}
    weights = {"sp500": 0.6, "selic": 0.4}
    tax = 0.15

    check_rebalance(portfolio, rebalance(portfolio, weights, tax), weights, tax)
