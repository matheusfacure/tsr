# Taxa Segura de Retirada

## Aviso / Disclaimer:
 
O conteúdo deste repositório é apenas uma pesquisa e não deve ser tomado como recomendação de investimento. Por favor, consulte um profissional de investimento certificado antes de investir seu dinheiro. 


## Dados

### IPCA
Dados do IPCA **mensal**, obtido no site do
[IBGE](https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html?=&t=series-historicas)

### Câmbio

Dados diários do cambio Dolar -> Real, obtido no site [br.investing.com](https://br.investing.com/currencies/usd-brl-historical-data)

### Selic
Dados da Selic over anual, obtida no site do [IPEA](http://www.ipeadata.gov.br/exibeserie.aspx?serid=38402). A taxa foi convertida para o valor **mensal** usando a função

```python
def annual_to_monthly_rate(r):
    return ((1 + r)**(1/12)) - 1
```

### SP500
Dados diários do preço do SP500 (SPX), obtidos no site [www.investing.com](https://www.investing.com/indices/us-spx-500-historical-data). 




