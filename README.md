# PhoneNumberInvestigator

**by [d3vn0mi](https://github.com/d3vn0mi)**

> An open-source OSINT toolkit for investigating phone numbers, emails, and names across the internet.

---

## Overview

PhoneNumberInvestigator is a powerful reconnaissance tool designed for security researchers, OSINT analysts, and investigators. It aggregates publicly available data from multiple internet sources to build intelligence profiles based on phone numbers, email addresses, and names.

## Features (Planned)

- **Phone Number Lookup** — Carrier detection, line type, geographic location, format validation, and reputation scoring
- **Email Investigation** — Breach database checks, domain analysis, social media correlation, and deliverability verification
- **Name Search** — Public records aggregation, social media discovery, and cross-reference correlation
- **Multi-Source Scraping** — Pulls data from the Wayback Machine, public APIs, search engines, data breach databases, social platforms, and more
- **Modular Architecture** — Plugin-based source system for easy extension
- **Export & Reporting** — JSON, CSV, and HTML report generation
- **CLI + API** — Usable from the command line or as a Python library

## Tech Stack

- **Language:** Python 3.10+
- **Framework:** Click (CLI), aiohttp (async HTTP)
- **Data Sources:** Wayback Machine, NumVerify, HunterIO, Have I Been Pwned, public search engines, and more
- **Storage:** SQLite for local caching, optional PostgreSQL for persistent storage

## Installation

```bash
git clone https://github.com/d3vn0mi/PhoneNumberInvestigator.git
cd PhoneNumberInvestigator
pip install -e .
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
```

## Project Structure

```
PhoneNumberInvestigator/
├── pni/                     # Main package
│   ├── core/                # Core engine and orchestration
│   ├── modules/             # Investigation modules
│   │   ├── phone/           # Phone number investigation
│   │   ├── email/           # Email investigation
│   │   └── name/            # Name search
│   ├── sources/             # Data source plugins
│   │   ├── wayback.py       # Wayback Machine integration
│   │   ├── numverify.py     # NumVerify API
│   │   ├── hunterio.py      # Hunter.io API
│   │   ├── hibp.py          # Have I Been Pwned
│   │   ├── google.py        # Google dorking
│   │   └── social.py        # Social media scrapers
│   ├── reports/             # Report generation
│   └── cli.py               # CLI entry point
├── tests/                   # Test suite
├── docs/                    # Documentation
├── ROADMAP.md               # Development roadmap
├── LICENSE                  # MIT License
└── README.md
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
