---
name: research-notebooks
description: "Research Notebook Best Practices. Use when: Setting up Jupyter/research notebook workflows for quantitative research; Ensuring reproducibility in strategy research and backtesting; Designing visualization standards for research output."
---

# Research Notebook Best Practices

## When to Activate
- Setting up Jupyter/research notebook workflows for quantitative research
- Ensuring reproducibility in strategy research and backtesting
- Designing visualization standards for research output
- Organizing research pipelines from data ingestion through signal generation to evaluation
- Implementing version control and documentation standards for research code

## Core Concepts

### Research Notebook Structure

**Standard Notebook Template:**
```
1. Title and Hypothesis
   - Clear statement of what is being tested
   - Expected outcome and success criteria defined upfront

2. Setup
   - Import statements
   - Configuration (date ranges, tickers, parameters)
   - Random seed setting
   - Data source specification

3. Data Loading and Validation
   - Load data with explicit source attribution
   - Data quality checks (missing values, outliers, splits/dividends)
   - Summary statistics and date range confirmation

4. Exploratory Analysis
   - Descriptive statistics
   - Distribution plots
   - Correlation analysis
   - Regime identification

5. Signal Construction
   - Feature engineering
   - Signal generation
   - Signal analysis (distribution, autocorrelation, decay)

6. Backtest Execution
   - Strategy logic implementation
   - Transaction cost model
   - Results computation

7. Evaluation
   - Performance metrics (Sharpe, drawdown, hit rate)
   - Walk-forward or cross-validation results
   - Statistical significance tests

8. Conclusions
   - Does the evidence support the hypothesis?
   - What are the limitations?
   - Next steps for research
```

**Anti-Patterns to Avoid:**
```
- Running cells out of order (breaks reproducibility)
- Modifying cells after seeing results (hidden selection bias)
- No markdown documentation between code cells
- Giant notebooks (>500 lines) that try to do everything
- Hardcoded file paths or credentials
- No version control for notebook state
- Presenting only successful experiments (survivorship bias in research)
```

### Reproducibility

**Random Seed Management:**
```python
# Set seeds at the TOP of every notebook
import numpy as np
import random

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# If using PyTorch/TensorFlow:
# torch.manual_seed(SEED)
# torch.cuda.manual_seed_all(SEED)

# If using sklearn with randomized components:
# Pass random_state=SEED to all estimators

# Document why this seed was chosen (or that it is arbitrary)
# Test with 2-3 different seeds to ensure results are not seed-dependent
```

**Data Versioning:**
```
Problem: research conducted on a dataset that gets updated/corrected later
cannot be reproduced with the original data.

Solutions:
1. Snapshot data with timestamp at download
   - Store as: data/prices_20240115_snapshot.parquet
   - Record data source URL and download time

2. Use data versioning tools
   - DVC (Data Version Control): git-like versioning for large files
   - Quilt: versioned data packages
   - LakeFS: git for data lakes

3. Checksum verification
   - Compute and store SHA256 hash of input data
   - Verify hash at notebook start: if mismatch, warn researcher

4. Point-in-time databases
   - Use as-of queries: "what was known on date X?"
   - Prevents lookahead bias in fundamental data
   - Sources: Quandl/Nasdaq Data Link, Bloomberg point-in-time
```

**Environment Management:**
```
Document the exact environment:
- Python version
- Package versions (pip freeze > requirements.txt)
- OS and hardware (affects floating point reproducibility)

Best practice:
- requirements.txt or environment.yml per project
- Docker containers for critical research
- Virtual environments (venv, conda) per project — never use system Python

Notebook header should include:
import sys
print(f"Python: {sys.version}")
print(f"NumPy: {np.__version__}")
print(f"Pandas: {pd.__version__}")
# etc.
```

### Visualization Standards

**Mandatory Charts for Strategy Research:**
```
1. Equity Curve
   - Cumulative returns (log scale recommended)
   - Include benchmark for comparison
   - Shade drawdown periods
   - Mark regime changes (if applicable)

2. Drawdown Chart
   - Underwater curve (% from peak)
   - Duration of each drawdown annotated
   - Horizontal lines at key thresholds (-10%, -20%)

3. Rolling Performance
   - Rolling 12-month Sharpe ratio
   - Rolling 12-month return
   - Shows performance stability over time

4. Return Distribution
   - Histogram with normal overlay
   - QQ plot to assess tail behavior
   - Skewness and kurtosis annotated

5. Monthly Return Heatmap
   - Years on Y-axis, months on X-axis
   - Color-coded returns
   - Shows seasonality and year-by-year consistency

6. Signal Analysis
   - Signal distribution (histogram)
   - Signal autocorrelation (ACF/PACF)
   - Signal vs forward return scatter plot
```

**Chart Formatting Standards:**
```
- Title: descriptive, includes asset and date range
- Axis labels: always labeled with units
- Legend: always present if multiple series
- Date format: YYYY-MM-DD on x-axis
- Font size: minimum 12pt for readability
- Color palette: colorblind-friendly (viridis, Set2)
- Grid: light gray, aids reading values
- Figure size: minimum 10x6 inches for presentations
- Save as both PNG (presentations) and SVG/PDF (papers)
- DPI: 150 for screen, 300 for print
```

### Result Documentation

**Metrics Reporting Standard:**
```
Performance Summary:
- CAGR (annualized return)
- Volatility (annualized)
- Sharpe Ratio (annualized, excess return / volatility)
- Sortino Ratio (downside deviation only)
- Maximum Drawdown (% from peak)
- Maximum Drawdown Duration (days/months)
- Calmar Ratio (CAGR / max drawdown)
- Win Rate (% of positive return periods)
- Profit Factor (gross profit / gross loss)
- Average Win / Average Loss ratio
- Number of trades
- Average holding period

Always report:
- Time period (start date, end date)
- Frequency (daily, weekly, monthly)
- Benchmark comparison
- Transaction cost assumptions
- Whether returns are gross or net
- Whether compounding is arithmetic or geometric
```

**Research Log:**
```
Maintain a running log of ALL experiments, not just successful ones:

Date: 2024-01-15
Hypothesis: RSI(14) mean reversion on SPY works on 5-min bars
Result: Sharpe 0.3, not significant after costs
Notes: Transaction costs dominate at this frequency
Next: Test on daily bars or reduce trading frequency

Date: 2024-01-18
Hypothesis: RSI(14) mean reversion on SPY daily bars
Result: Sharpe 1.1, passes walk-forward at WFE=0.65
Notes: Promising, but performance concentrated in high-vol regimes
Next: Add vol regime filter, test on other ETFs

Tracking failed experiments prevents:
- Re-testing the same idea months later
- Underestimating the number of trials for DSR calculation
- Team members duplicating failed research
```

### Version Control for Notebooks

**Git Best Practices:**
```
Problem: Jupyter notebooks are JSON files with embedded output
- Diffs are unreadable (binary image data, execution counts)
- Merge conflicts are nightmare to resolve
- Output bloats repository size

Solutions:
1. nbstripout: automatically strip output on commit
   pip install nbstripout
   nbstripout --install  # sets up git filter
   Only source code is committed; outputs regenerated on execution

2. Jupytext: pair notebooks with plain Python scripts
   Sync .ipynb with .py (percent format)
   Version control the .py file
   .ipynb in .gitignore (regenerated from .py)

3. Papermill: parameterize notebooks for batch execution
   Execute notebooks with different parameters programmatically
   Store results separately from notebook code

4. Review process:
   - Review .py diffs (readable, standard code review)
   - Re-run notebook to verify outputs match claims
   - CI/CD pipeline can auto-run notebooks on merge
```

### Research Pipeline Design

**Pipeline Stages:**
```
Stage 1: Data Pipeline
  Input: raw data sources (APIs, databases, files)
  Process: download, clean, validate, store
  Output: clean, versioned datasets
  Cadence: daily or on-demand

Stage 2: Feature Pipeline
  Input: clean data
  Process: compute features, signals, indicators
  Output: feature matrix with timestamps
  Cadence: daily, synced with data pipeline

Stage 3: Research Pipeline
  Input: feature matrix
  Process: hypothesis testing, backtesting, walk-forward
  Output: research notebooks, performance reports
  Cadence: ad-hoc (researcher-driven)

Stage 4: Deployment Pipeline
  Input: validated strategy code
  Process: convert notebook logic to production code
  Output: production-ready strategy module
  Cadence: on strategy approval

Separation of concerns:
- Data pipeline team maintains data quality
- Research uses data pipeline outputs (never raw data directly)
- Production code is NEVER a Jupyter notebook
- Notebook insights are translated into clean, tested Python modules
```

**Notebook to Production Translation:**
```
Research notebook: exploratory, messy, visual, single-use
Production code: clean, tested, modular, runs daily

Translation checklist:
[ ] Extract strategy logic into functions/classes
[ ] Remove all hardcoded values (use config files)
[ ] Add type hints and docstrings
[ ] Write unit tests for each function
[ ] Add error handling and logging
[ ] Remove visualization code (separate monitoring dashboard)
[ ] Add input validation (handle missing data, wrong types)
[ ] Performance test (can it run within time constraints?)
[ ] Code review by someone who did NOT write the notebook
```

## Methodology

### Starting a New Research Project
1. **Create a new directory** with standardized structure (data/, notebooks/, src/, tests/, configs/)
2. **Set up environment** — virtual env, requirements.txt, seed configuration
3. **Write the hypothesis** first — before loading any data
4. **Define success criteria** — what Sharpe, what statistical test, what significance level?
5. **Load and validate data** — quality checks, date range confirmation
6. **Explore** — EDA notebook with no optimization or backtesting
7. **Build signal** — separate notebook for signal construction
8. **Backtest** — separate notebook for strategy evaluation
9. **Validate** — walk-forward, CPCV, Monte Carlo in separate notebook
10. **Document** — conclusions, limitations, next steps

### Research Review Checklist
```
Before sharing results:
[ ] All cells run top-to-bottom without error (restart kernel and run all)
[ ] Random seeds set and documented
[ ] Data version/snapshot documented
[ ] All parameter choices justified (not arbitrary)
[ ] Transaction costs included and realistic
[ ] No lookahead bias (verified data alignment)
[ ] Statistical significance assessed (not just point estimates)
[ ] Benchmark comparison included
[ ] Limitations explicitly stated
[ ] Failed experiments documented in research log
[ ] Notebook is under 300 lines of code (split if larger)
```

## Examples

### Example 1: Research Directory Structure
```
project-momentum-etfs/
  README.md                    # Project description and hypothesis
  requirements.txt             # Exact package versions
  config.yaml                  # Parameters, date ranges, tickers
  data/
    raw/                       # Original downloaded data (read-only)
    processed/                 # Cleaned, aligned data
    checksums.json             # SHA256 hashes of all data files
  notebooks/
    01_data_exploration.ipynb   # EDA, no optimization
    02_signal_construction.ipynb # Feature engineering
    03_backtest.ipynb           # Strategy backtest
    04_validation.ipynb         # Walk-forward, CPCV, Monte Carlo
    05_robustness.ipynb         # Parameter sensitivity, alternative assets
  src/
    data_loader.py             # Reusable data loading functions
    signals.py                 # Signal computation functions
    backtest_engine.py         # Backtest execution logic
    metrics.py                 # Performance metric calculations
  tests/
    test_signals.py            # Unit tests for signal logic
    test_backtest.py           # Unit tests for backtest engine
  research_log.md              # Running log of all experiments
```

### Example 2: Notebook Header Template
```python
"""
Research Notebook: Momentum Signal on ETF Universe
Hypothesis: 12-month price momentum predicts next-month ETF returns
Author: [Name]
Date: 2024-01-15
Data: CRSP ETF returns, 2005-2024
Version: 1.2 (added transaction costs)
"""

# --- Setup ---
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SEED = 42
np.random.seed(SEED)

# Configuration
CONFIG = {
    'start_date': '2005-01-01',
    'end_date': '2024-01-01',
    'lookback_months': 12,
    'rebalance_freq': 'monthly',
    'transaction_cost_bps': 10,
    'n_quantiles': 5,
    'data_file': '../data/processed/etf_returns_v2.parquet',
    'data_checksum': 'a1b2c3d4...',  # SHA256
}

# Environment
import sys
print(f"Python: {sys.version}")
print(f"NumPy: {np.__version__}, Pandas: {pd.__version__}")

# Success criteria (defined BEFORE analysis):
# Sharpe > 0.5, WFE > 0.5, significant at p < 0.10 after DSR adjustment
```

### Example 3: Research Log Entry
```
## Experiment Log: Momentum ETF Strategy

### 2024-01-15 — Experiment 1
Hypothesis: 12-month momentum, top quintile long, bottom quintile short
Parameters: lookback=12, rebalance=monthly, cost=10bps
Result: Sharpe=0.82, Max DD=18%, 245 trades over 19 years
WFE: 0.61 (3-year rolling IS, 6-month OOS)
Notes: Reasonable but momentum crash in 2009 caused 35% drawdown
Status: Promising, continue investigation

### 2024-01-17 — Experiment 2
Hypothesis: Add volatility scaling (inverse vol weighting)
Parameters: same as Exp 1, plus vol_lookback=60 days
Result: Sharpe=0.95, Max DD=14%, improved risk-adjusted returns
WFE: 0.58 (slightly lower — vol scaling adds a parameter)
Notes: Reduced momentum crash drawdown by 40%
Status: Better than Exp 1, investigate further

### 2024-01-20 — Experiment 3 (FAILED)
Hypothesis: Use 6-month momentum instead of 12-month
Parameters: lookback=6, everything else same as Exp 2
Result: Sharpe=0.35, not significant
Notes: Short-term momentum has higher turnover and lower signal quality
Status: Rejected, stick with 12-month lookback

Total trials: 3 (need to account for all in DSR calculation)
```

## Quality Gate

Before considering research complete, verify:

- [ ] Notebook runs top-to-bottom without error after kernel restart
- [ ] Random seeds are set and results are deterministic across runs
- [ ] Data source and version are explicitly documented with checksums
- [ ] Hypothesis was written before analysis began (no post-hoc rationalization)
- [ ] Success criteria were defined before running backtests
- [ ] All experiments (including failures) are logged with trial count for DSR
- [ ] Visualizations follow formatting standards (labeled axes, legends, appropriate scale)
- [ ] Transaction costs are realistic and included in all performance metrics
- [ ] Statistical significance is assessed beyond point estimates
- [ ] Notebook code is clean enough that another researcher can understand it without explanation
- [ ] Research log is updated with conclusions and next steps
- [ ] Code that will be used in production is extracted into tested Python modules, not left in notebooks
