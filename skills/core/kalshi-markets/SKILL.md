---
name: kalshi-markets
description: Kalshi prediction market data (prices, odds, orderbooks, trades). Use for prediction markets, Kalshi, betting odds, election/sports betting, market forecasts.
---

# kalshi-markets

## 🎯 Triggers
**USE:** prediction markets, Kalshi, betting odds, forecast markets, election betting, market probabilities
**SKIP:** general knowledge (use built-in)

## Scripts (use via script_run)

**Status & Discovery:**
- `status.py` - Is Kalshi operational?
- `markets.py` - Browse all markets
- `search.py "keyword"` - Find markets by keyword
- `events.py` - List event groups
- `series_list.py` - Browse templates (~6900)

**Market Details:**
- `market.py TICKER` - Market details (positional arg)
- `orderbook.py TICKER` - Bid/ask prices (positional arg)
- `trades.py --ticker X` - Recent trades (flag)
- `event.py EVENT_TICKER` - Event details (positional arg)
- `series.py SERIES_TICKER` - Series info (positional arg)

## Usage
**Pattern:** `script_run kalshi-markets <script> --json [args]`
**Always use:** `--json` flag for structured output
**Help:** `script_help kalshi-markets <script>` shows options
