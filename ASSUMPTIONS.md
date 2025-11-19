# System Assumptions and Limitations

## Overview

This document outlines key assumptions, constraints, and limitations of the Stock Trading Decision Support System. Understanding these is critical for proper system use and interpretation of results.

## Data Assumptions

### 1. Historical Data Availability
**Assumption**: Yahoo Finance provides reliable, complete historical OHLCV data

**Limitations**:
- Free data may have gaps or errors
- Delayed data (typically 15-20 minutes)
- Historical data may not include all corporate actions
- Survivorship bias in historical datasets

**Implications**:
- Backtesting results may be optimistic
- Real-time trading performance may differ
- Data validation is essential

### 2. Data Stationarity
**Assumption**: Price patterns and relationships remain relatively stable over time

**Reality**:
- Markets experience regime changes
- Volatility varies significantly
- Correlations are not constant
- Black swan events occur

**Implications**:
- Models may fail during unprecedented events
- Periodic retraining is necessary
- Performance monitoring is critical

### 3. Data Quality
**Assumption**: Input data is accurate and complete

**Potential Issues**:
- Missing data points
- Incorrect prices due to data provider errors
- Unadjusted for splits/dividends
- After-hours trading not included

**Mitigation**:
- Data validation checks
- Multiple data source confirmation
- Outlier detection
- Manual review for critical decisions

## Model Assumptions

### 1. LSTM (Long Short-Term Memory)

**Key Assumptions**:
- Historical patterns repeat
- Sufficient training data available (typically 1000+ samples)
- Patterns are learnable from features
- Past prices contain predictive information

**Limitations**:
- Risk of overfitting to training data
- Requires extensive hyperparameter tuning
- Computationally expensive
- Black box nature (limited interpretability)
- May not generalize to new market conditions

**Best For**:
- Medium-term predictions (1-10 days)
- Complex pattern recognition
- Non-linear relationships

### 2. GRU (Gated Recurrent Unit)

**Key Assumptions**:
- Similar to LSTM but with simpler architecture
- Faster training with comparable performance
- Patterns can be captured with fewer parameters

**Limitations**:
- Same overfitting risks as LSTM
- Less capacity than LSTM for very complex patterns
- Requires significant training data
- May underperform LSTM on very long sequences

**Best For**:
- Faster training iterations
- When computational resources are limited
- Similar use cases to LSTM

### 3. Ensemble Approach

**Assumption**: Combining multiple models reduces individual model weaknesses

**Method**: Weighted average of LSTM and GRU predictions (0.50, 0.50)

**Limitations**:
- All models may fail simultaneously in extreme conditions
- Optimal weighting changes over time
- No guarantee of improvement over best single model

## Technical Indicators Assumptions

### 1. RSI (Relative Strength Index)
**Assumption**: Overbought (>70) and oversold (<30) levels predict reversals

**Limitations**:
- Strong trends can keep RSI extreme for extended periods
- Levels may need adjustment per stock
- Divergences are subjective

### 2. MACD (Moving Average Convergence Divergence)
**Assumption**: Crossovers and divergences signal trend changes

**Limitations**:
- Lagging indicator
- False signals in ranging markets
- Parameter sensitivity

### 3. Bollinger Bands
**Assumption**: Prices revert to mean; bands contain ~95% of price action

**Limitations**:
- Breakouts can continue beyond bands
- Band width varies with volatility
- No directional information alone

## Trading Strategy Assumptions

### 1. Market Efficiency
**Assumption**: Markets are inefficient enough for ML models to find patterns

**Reality**:
- Markets are semi-efficient
- Easy patterns are quickly arbitraged away
- Competition from sophisticated algorithms

**Implications**:
- Edge is small and may erode over time
- High transaction costs can eliminate profits
- Continuous adaptation required

### 2. Transaction Costs
**Assumption**: Typical transaction costs

**Default Values**:
- Commission: $0 (many brokers now zero commission)
- Slippage: 0.1% per trade
- Spread: Variable by stock liquidity

**Limitations**:
- Slippage can be much higher for:
  - Large orders
  - Low liquidity stocks
  - Volatile market conditions
  - Market orders at open/close
- Hidden costs (market impact, opportunity cost)

### 3. Order Execution
**Assumption**: Signals can be executed at predicted prices

**Reality**:
- Delay between signal and execution
- Price may move unfavorably
- Partial fills possible
- Rejected orders

**Implications**:
- Backtesting overestimates performance
- Need buffer for execution uncertainty
- Real-time monitoring essential

### 4. Position Sizing
**Assumption**: Recommended position sizes are always executable

**Limitations**:
- Account size constraints
- Fractional shares may not be available
- Margin requirements
- Risk limits

## Risk Management Assumptions

### 1. Stop-Loss Orders
**Assumption**: Stop-losses execute at set price

**Reality**:
- May execute at worse price (slippage)
- Gaps can jump over stop-loss
- After-hours movements
- Flash crashes

**Implications**:
- Actual losses may exceed stop-loss level
- Need additional risk controls
- Position sizing is critical

### 2. Diversification
**Assumption**: Diversification reduces risk

**Limitations**:
- Correlations increase during market stress
- Systematic risk affects all stocks
- Over-diversification dilutes returns

**Recommendations**:
- 10-20 stocks for retail portfolios
- Across different sectors
- Monitor correlation changes

### 3. Maximum Drawdown
**Assumption**: Historical maximum drawdown bounds future drawdowns

**Reality**:
- Future drawdowns can exceed historical
- Tail risk is underestimated
- Regime changes occur

**Implications**:
- Plan for worse than backtested results
- Maintain adequate capital buffer
- Have exit strategy

## System Limitations

### 1. Computational Resources
**Constraints**:
- Training deep learning models requires GPU
- Real-time predictions need low latency
- Storage for historical data

**Assumptions**:
- Standard desktop/server environment
- Python 3.8+ with standard libraries
- Sufficient RAM (8GB+ recommended)

### 2. Latency
**Assumption**: Predictions are useful despite latency

**Reality**:
- API calls add delay
- Model inference takes time
- Data fetching has lag

**Implications**:
- Not suitable for high-frequency trading
- Focus on daily/swing trading timeframes
- Real-time optimization needed for intraday

### 3. Scalability
**Current Design**:
- Single-threaded prediction for most components
- Limited concurrent users
- File-based model storage

**Limitations**:
- Not designed for production-scale deployment
- Manual scaling required
- No load balancing

### 4. Reliability
**Assumptions**:
- Users will monitor system actively
- Manual intervention available
- Not mission-critical application

**Reality**:
- Software bugs can occur
- External dependencies may fail
- Network issues affect data

## Market Assumptions

### 1. Liquidity
**Assumption**: Stocks have sufficient liquidity for strategy execution

**Requirements**:
- Minimum daily volume (e.g., 1M shares)
- Reasonable bid-ask spread (<0.5%)
- Depth of order book

**Limitations**:
- Small-cap stocks may not meet criteria
- Liquidity varies throughout trading day
- Exceptional conditions reduce liquidity

### 2. Market Access
**Assumption**: Users have access to:
- Stock market trading account
- Real-time or near-real-time data
- Order execution capabilities

**Limitations**:
- Some markets restricted by geography
- Accredited investor requirements
- Minimum account balances

### 3. Trading Hours
**Assumption**: Signals generated during market hours are actionable

**Considerations**:
- After-hours trading available but limited
- Gap risk overnight
- Different rules for extended hours

## Regulatory and Legal Assumptions

### 1. Compliance
**Assumption**: Users are responsible for regulatory compliance

**User Responsibilities**:
- Know Your Customer (KYC) requirements
- Anti-Money Laundering (AML) rules
- Pattern Day Trader regulations (US)
- Tax reporting obligations

**System Does NOT**:
- Verify user qualifications
- Ensure regulatory compliance
- Provide tax advice
- Report transactions

### 2. Legal Jurisdiction
**Assumption**: System used in compliance with local laws

**Considerations**:
- Securities regulations vary by country
- Some strategies may be restricted
- Data privacy laws (GDPR, etc.)
- Financial advice regulations

## Performance Assumptions

### 1. Backtesting
**Assumptions**:
- Historical data represents future conditions
- Transaction costs are accurately modeled
- No look-ahead bias in implementation

**Reality**:
- Markets change over time
- Hidden costs exist
- Bugs can introduce bias

**Implications**:
- Backtest results are optimistic upper bound
- Live performance typically 20-50% worse
- Continuous validation needed

### 2. Prediction Accuracy
**Realistic Expectations**:
- Direction accuracy: 52-58% (slightly better than random)
- Magnitude accuracy: Wide confidence intervals
- Sharpe ratio: 0.5-1.5 in backtesting

**Unrealistic Expectations**:
- Consistent 70%+ accuracy
- Large daily returns
- No losing periods

### 3. Model Lifetime
**Assumption**: Models need periodic retraining

**Typical Timeline**:
- LSTM/GRU: Monthly to quarterly
- Technical indicators: Parameters adjusted quarterly

**Degradation**:
- Performance decays over time
- Drift detection triggers retraining
- Market regime changes require new models

## Data Privacy and Security

### 1. Data Storage
**Assumption**: Local storage is secure

**User Responsibility**:
- Secure file system
- No sensitive data in logs
- Proper access controls

**System Does NOT**:
- Encrypt stored data by default
- Implement authentication
- Audit access

### 2. API Keys
**Assumption**: Users protect API keys and credentials

**Best Practices**:
- Use environment variables
- Never commit to version control
- Rotate keys regularly

## Future Development Assumptions

### 1. Maintenance
**Assumption**: System requires ongoing maintenance

**Expected Needs**:
- Library version updates
- Bug fixes
- Model retraining
- Feature additions

### 2. Evolution
**Known Limitations to Address**:
- Add more data sources
- Implement reinforcement learning
- Improve risk management
- Add portfolio optimization
- Sentiment analysis integration
- News event impact

## Conclusion

This system is built on numerous assumptions that may not hold in all conditions. Users must:

1. **Understand limitations** before using for real trading
2. **Validate assumptions** against their specific use case
3. **Monitor continuously** for assumption violations
4. **Adapt** as market conditions change
5. **Start small** and scale cautiously

**Remember**: All models are wrong, but some are useful. The key is knowing when and how they are wrong.

---

*This document should be reviewed and updated as the system evolves and new limitations are discovered.*
