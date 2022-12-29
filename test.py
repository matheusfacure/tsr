from tsr import withdraw, grow


def test_withdraw():

    wr = 0.1
    inflation = 0.01
    tax = 0.05
    portfolio = {"selic": 500, "sp500": 500}

    # Test Unbalanced portfolio
    weights = {"selic": 0.6, "sp500": 0.4}

    expected_amount = 1000 * wr * (1 + inflation)
    expected_port = {'selic': 500, 'sp500': 500 - expected_amount / (1 - tax)}

    result = withdraw(wr, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "unbalanced portfolio not working"
    assert result.get("portfolio") == expected_port, "unbalanced portfolio not working"

    # Test balanced portfolio
    weights = {"selic": 0.5, "sp500": 0.5}

    expected_amount = 1000 * wr * (1 + inflation)
    expected_port = {'selic': 500 - expected_amount / (1 - tax), 'sp500': 500}

    result = withdraw(wr, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "balanced portfolio not working"
    assert result.get("portfolio") == expected_port, "balanced portfolio not working"

    # Test 1 asset portfolio
    portfolio = {"sp500": 1000}
    weights = {"sp500": 1.0}

    expected_amount = 1000 * wr * (1 + inflation)
    expected_port = {'sp500': 1000 - expected_amount / (1 - tax)}

    result = withdraw(wr, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "1 asset portfolio not working"
    assert result.get("portfolio") == expected_port, "1 asset portfolio not working"

    # Test 3 asset portfolio
    portfolio = {"selic": 500, "sp500": 300, "bovespa": 200}
    weights = {"selic": 0.5, "sp500": 0.25, "bovespa": 0.25}

    expected_amount = 1000 * wr * (1 + inflation)
    expected_port = {"selic": 500, "sp500": 300-expected_amount / (1 - tax), "bovespa": 200}

    result = withdraw(wr, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "3 asset portfolio not working"
    assert result.get("portfolio") == expected_port, "3 asset portfolio not working"

    # Emptying one asset
    portfolio = {"selic": 950, "sp500": 50}
    weights = {"selic": 0.99, "sp500": 0.01}

    expected_amount = 1000 * wr * (1 + inflation)
    expected_port = {"selic": 950 - (expected_amount/(1 - tax) - 50), "sp500": 0.0}

    result = withdraw(wr, inflation, weights, portfolio, tax=tax)

    assert result.get("amount") == expected_amount, "emptying not working"
    assert result.get("portfolio") == expected_port, "emptying not working"


def test_withdraw():
    grow()