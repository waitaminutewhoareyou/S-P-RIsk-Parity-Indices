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
### Monthly Rebalancing

```plaintext
Start                                2012-01-04 00:00:00
End                                  2022-01-03 00:00:00
Duration                              3652 days 00:00:00
Return (Ann.) [%]                               6.060919
Volatility (Ann.) [%]                           6.524049
Information Ratio                               0.929012
Final AUM [unitless]                            1.844498
AUM Peak [$]                                    1.851624
Final Return [%]                               84.449819
Max. Drawdown [%]                             -10.847945
Max. Drawdown Duration                 427 days 00:00:00
Avg. Drawdown Duration       117 days 20:52:10.434782608
Max. Underwater Duration               463 days 00:00:00
Total Underwater Duration             2588 days 00:00:00
```
### Daily Rebalancing
```plaintext
Start                                2012-01-04 00:00:00
End                                  2022-01-03 00:00:00
Duration                              3652 days 00:00:00
Return (Ann.) [%]                              13.085124
Volatility (Ann.) [%]                           13.71663
Information Ratio                               0.953961
Final AUM [unitless]                            3.594435
AUM Peak [$]                                    3.622377
Final Return [%]                              243.334415
Max. Drawdown [%]                             -21.331295
Max. Drawdown Duration                 427 days 00:00:00
Avg. Drawdown Duration       119 days 05:13:02.608695652
Max. Underwater Duration               463 days 00:00:00
Total Underwater Duration             2590 days 00:00:00
```