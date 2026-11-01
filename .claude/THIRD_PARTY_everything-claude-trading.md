# Third-party content: everything-claude-trading

Source: https://github.com/brainbytes-dev/everything-claude-trading (commit 9a8fcfc, v1.0.0), MIT licensed.
Copied into `.claude/skills`, `.claude/agents` and `.claude/commands`, then pruned: only 29 of the 82 upstream skills were kept
(backtesting rigor, data, execution/microstructure, risk/sizing, the strategy families used here). Deleted: crypto (8), derivatives (10),
portfolio (7), most of macro, and other skills unrelated to a single-instrument intraday futures bot. Also pruned: 9 of 18 agents (derivatives, options, volatility, fixed income, FX, commodities, crypto/DeFi, portfolio
management, regulatory compliance) and 11 of 20 commands (/crypto-analysis, /options-analysis, /vol-analysis, /hedging-plan,
/portfolio-optimize, /macro-outlook, /factor-analysis, /pairs-scan, /correlation-check, /risk-report, /execution-plan).
Lines in kept commands that referred to deleted agents were removed.

Changes made here:
* Each skill got a YAML header (`name`, `description`) generated from its own title and "When to Activate" bullets,
  because the upstream skill files have none and Claude Code needs it to discover them. Skill bodies are unchanged.
* NOT installed: upstream hooks (keyword-warning scripts that fire on almost every edit of trading code), the MCP server
  template (starts third-party npm packages with API keys), upstream CLAUDE.md/AGENTS.md, rules, contexts and examples.

---- LICENSE ----
MIT License

Copyright (c) 2026 Everything Claude Trading Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
