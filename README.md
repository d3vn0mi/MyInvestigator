# PhoneNumberInvestigator (PNI)

**by [d3vn0mi](https://github.com/d3vn0mi)**

> An open-source OSINT toolkit for investigating phone numbers, emails, and names across the internet.

---

## Overview

PhoneNumberInvestigator is a powerful reconnaissance tool designed for security researchers, OSINT analysts, and investigators. It aggregates publicly available data from multiple internet sources to build intelligence profiles based on phone numbers, email addresses, and names.

## Features

- **Phone Number Investigation** — Carrier detection, line type, geographic location, format validation, reputation database scraping (WhoCalledMe, 800notes, SpamCalls, NumLookup), search engine dorking via DuckDuckGo
- **Email Investigation** — Syntax validation, MX record checks, disposable email detection, Have I Been Pwned breach lookup, paste site searches, Gravatar profile discovery, GitHub commit search, social media correlation
- **Name Search** — Name parsing & normalization, username generation, social media enumeration across 9 platforms (GitHub, Twitter/X, Instagram, Reddit, LinkedIn, Pinterest, Medium, Dev.to, Keybase), search engine intelligence
- **Wayback Machine Integration** — CDX API search and full-text archive search across all query types
- **Modular Architecture** — Abstract `Source` base class with plug-in sources, async execution via aiohttp, SQLite result caching with TTL, per-source rate limiting with retry
- **Export & Reporting** — Rich terminal tables, JSON, CSV, and dark-themed HTML reports
- **CLI** — `pni phone`, `pni email`, `pni name`, `pni investigate` commands with format and output options

## Tech Stack

- **Language:** Python 3.10+
- **CLI:** Click + Rich (colored terminal output)
- **Async HTTP:** aiohttp
- **Phone Parsing:** phonenumbers
- **Web Scraping:** BeautifulSoup4 + lxml
- **Caching:** aiosqlite (SQLite)
- **Data Sources:** Wayback Machine, DuckDuckGo, HIBP, Gravatar, GitHub API, WhoCalledMe, SpamCalls, NumLookup, NumLookupAPI, and more

## Installation

```bash
git clone https://github.com/d3vn0mi/PhoneNumberInvestigator.git
cd PhoneNumberInvestigator
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

```bash
# Investigate a phone number
pni phone +1234567890

# Investigate an email
pni email user@example.com

# Search by name
pni name "John Doe"

# Full investigation (all modules)
pni investigate --phone +1234567890 --email user@example.com --name "John Doe"

# Output as JSON
pni phone +1234567890 --format json

# Save reports to a directory
pni email user@example.com --output ./reports

# Verbose mode
pni phone +1234567890 -v
```

## Legacy Script

The original standalone script `phone_osint_v4.py` is still available for direct use:

```bash
python phone_osint_v4.py +31645161166 --delay 2 --output ./reports
```

## Project Structure

```
PhoneNumberInvestigator/
├── pni/                         # Main package
│   ├── core/                    # Core engine
│   │   ├── models.py            # Query, SourceResult, InvestigationResult
│   │   ├── source.py            # Abstract Source base class
│   │   ├── investigator.py      # Orchestrator — dispatches to sources
│   │   ├── cache.py             # SQLite async cache with TTL
│   │   └── rate_limiter.py      # Token-bucket rate limiter with retry
│   ├── modules/                 # Investigation modules
│   │   ├── phone/               # Phone: analyzer, local source, dorks, reputation
│   │   ├── email/               # Email: analyzer, local source, breach, social
│   │   └── name/                # Name: analyzer, local source, search, social
│   ├── sources/                 # Cross-module data sources
│   │   └── wayback.py           # Wayback Machine CDX + full-text search
│   ├── reports/                 # Report generation
│   │   └── html_report.py       # Dark-themed HTML report generator
│   ├── formatters.py            # Table, JSON, CSV output formatters
│   └── cli.py                   # Click CLI entry point
├── tests/                       # Test suite (27 tests)
├── phone_osint_v4.py            # Legacy standalone script
├── .github/workflows/ci.yml     # GitHub Actions CI
├── pyproject.toml               # Package config & dependencies
├── ROADMAP.md                   # Development roadmap
├── LICENSE                      # MIT License
└── README.md
```

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## Contributing

Contributions are welcome! Please read the roadmap in [ROADMAP.md](ROADMAP.md) to see planned work and where help is needed.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push to the branch and open a Pull Request

## Disclaimer

This tool is intended for **authorized security research and OSINT investigations only**. Users are responsible for ensuring their use complies with applicable laws and regulations. Do not use this tool to harass, stalk, or violate the privacy of individuals. Always obtain proper authorization before conducting investigations.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

**d3vn0mi** | [GitHub](https://github.com/d3vn0mi)
