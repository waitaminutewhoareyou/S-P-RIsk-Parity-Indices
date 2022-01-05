Portfolio replication of S&P Risk Parity.
The replciated curve looks very similar to the actual
S&P Risk Parity Index.

# Comparison Graph
![](result/img/comparison.jpg)

# Correlation table
|                        |   Replicated | S&P Risk Parity Index |   Equal Weighting |
|:-----------------------|-------------:|----------------------:|------------------:|
| Replicated             |         1    |                  0.99 |              0.87 |
| S&P Risk Parity Index  |         0.99 |                     1 |              0.87 |
| Equal Weighting        |         0.87 |                  0.87 |              1    |


# Performance Metrics
Performance metrics of monthly rebalancing

```plaintext
Start                        2019-01-01 00:00:00
End                          2021-12-10 00:00:00
Duration                      1074 days 00:00:00
Return (Ann.) [%]                      25.341031
Volatility (Ann.) [%]                  14.674006
Information Ratio                       1.726933
Final AUM [unitless]                    1.744624
AUM Peak [$]                            1.770347
Final Return [%]                       74.462383
Max. Drawdown [%]                     -10.593964
Max. Drawdown Duration         244 days 00:00:00
Avg. Drawdown Duration          95 days 03:00:00
Max. Underwater Duration       359 days 00:00:00
Total Underwater Duration      613 days 00:00:00
```