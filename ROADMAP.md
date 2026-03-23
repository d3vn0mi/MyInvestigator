# PhoneNumberInvestigator — Development Roadmap

**Maintained by [d3vn0mi](https://github.com/d3vn0mi)**

This roadmap outlines the concrete development plan for turning PhoneNumberInvestigator into a full-featured OSINT investigation toolkit supporting phone, email, and name reconnaissance.

---

## Phase 1: Foundation (v0.1.0)

**Goal:** Establish the core architecture, CLI skeleton, and first working module.

- [ ] **Project scaffolding**
  - Set up Python package structure (`pni/`)
  - Configure `pyproject.toml` with dependencies (Click, aiohttp, phonenumbers, rich)
  - Set up pytest, flake8, and pre-commit hooks
  - CI/CD pipeline with GitHub Actions (lint, test, build)

- [ ] **Core engine**
  - Abstract `Source` base class with standardized interface
  - `Investigator` orchestrator that dispatches queries to registered sources
  - Async execution engine using `asyncio` + `aiohttp` for parallel source queries
  - Rate limiter and retry logic per source
  - Local SQLite cache to avoid redundant lookups

- [ ] **Phone number module (basic)**
  - Phone number parsing and validation using `phonenumbers` library
  - Carrier detection and line type identification (mobile/landline/VoIP)
  - Geographic region and timezone resolution
  - Number format normalization (E.164, national, international)

- [ ] **CLI skeleton**
  - `pni phone <number>` — basic phone lookup
  - `--format json|table|csv` output options
  - `--verbose` flag for debug output
  - Colored terminal output using `rich`

---

## Phase 2: Data Sources — Phone (v0.2.0)

**Goal:** Integrate external data sources for phone number intelligence.

- [ ] **NumVerify API integration**
  - Carrier, line type, location, and validity from NumVerify
  - API key management via config file or environment variable

- [ ] **Twilio Lookup API**
  - Caller name (CNAM) lookup
  - Carrier and line type cross-verification

- [ ] **Wayback Machine integration**
  - Query Wayback Machine CDX API for archived pages containing the phone number
  - Extract context (page title, surrounding text, URL, snapshot date)
  - Surface historical associations (businesses, listings, ads)

- [ ] **Google dorking engine**
  - Construct targeted Google dork queries for the phone number
  - Parse search results for contextual matches
  - Respect rate limits and implement request throttling

- [ ] **Public directory scrapers**
  - WhitePages, TrueCaller, Sync.me (where legally accessible)
  - Fallback to cached/archived versions via Wayback Machine

---

## Phase 3: Email Investigation Module (v0.3.0)

**Goal:** Full email address investigation capability.

- [ ] **Email validation and parsing**
  - Syntax validation (RFC 5322)
  - MX record verification
  - Disposable email detection (list-based + heuristic)
  - SMTP deliverability check (optional, non-intrusive)

- [ ] **Have I Been Pwned (HIBP) integration**
  - Breach database lookup via HIBP API v3
  - List breaches with dates, data types exposed, and severity
  - Paste search for leaked credentials context

- [ ] **Hunter.io integration**
  - Email verification and confidence scoring
  - Associated domain and organization discovery
  - Related email pattern detection

- [ ] **Wayback Machine — email variant**
  - Search archived pages for email address appearances
  - Extract associated names, organizations, and page context

- [ ] **Social media discovery**
  - Check email registration on major platforms (GitHub, Gravatar, Twitter/X, LinkedIn)
  - Gravatar profile image and metadata extraction
  - GitHub profile and public repo discovery

- [ ] **Domain intelligence**
  - WHOIS lookup for the email's domain
  - DNS records (MX, SPF, DMARC) analysis
  - Domain age and registration history

---

## Phase 4: Name Search Module (v0.4.0)

**Goal:** Search and correlate identity data from a name.

- [ ] **Name parsing and normalization**
  - Handle first/last/middle, nicknames, and aliases
  - Unicode and transliteration support

- [ ] **Public records search**
  - Aggregate data from public directories and people-search engines
  - Cross-reference with phone and email modules for correlation

- [ ] **Social media enumeration**
  - Username generation from name variations
  - Platform existence checks (GitHub, Twitter/X, LinkedIn, Instagram, Reddit, Facebook)
  - Profile metadata extraction where publicly available

- [ ] **Wayback Machine — name variant**
  - Search archived pages for name appearances
  - Extract associated organizations, publications, and contact info

- [ ] **Search engine aggregation**
  - Google, Bing, DuckDuckGo result scraping
  - News article and press mention discovery
  - Academic publication search (Google Scholar)

---

## Phase 5: Cross-Module Correlation (v0.5.0)

**Goal:** Link findings across phone, email, and name modules into unified profiles.

- [ ] **Entity resolution engine**
  - Probabilistic matching to link records across modules
  - Confidence scoring for associations
  - Graph-based relationship mapping

- [ ] **Unified profile builder**
  - Merge findings from all modules into a single identity profile
  - Timeline view of discovered data points
  - Source attribution and confidence indicators

- [ ] **Investigation sessions**
  - Save and resume investigations
  - Session history and audit trail
  - Export full investigation as a case file

---

## Phase 6: Reporting and Export (v0.6.0)

**Goal:** Professional-grade output and reporting.

- [ ] **Report templates**
  - HTML report with interactive elements (collapsible sections, linked sources)
  - PDF generation via WeasyPrint
  - JSON and CSV export for data pipeline integration
  - Markdown report for documentation

- [ ] **Visualization**
  - Relationship graph (entity connections)
  - Timeline of data discoveries
  - Geographic mapping of location data

- [ ] **Alerting and monitoring**
  - Watch mode: re-run investigation on a schedule and alert on changes
  - Webhook notifications for new findings

---

## Phase 7: Advanced Sources and Integrations (v0.7.0)

**Goal:** Expand data source coverage and third-party integrations.

- [ ] **Additional data sources**
  - Shodan — find infrastructure associated with phone/email/name
  - Censys — certificate and host discovery
  - FullContact API — identity enrichment
  - Pipl API — people search
  - Dehashed — breach and leak database
  - IntelX (Intelligence X) — darknet and paste monitoring
  - Spokeo, BeenVerified (where accessible and legal)

- [ ] **Wayback Machine advanced**
  - Full-text search across archived snapshots
  - Track changes to pages mentioning the target over time
  - Screenshot capture of relevant archived pages

- [ ] **Tor and dark web sources (optional)**
  - Paste site monitoring (Pastebin, Ghostbin, etc.)
  - Dark web marketplace mention detection (via IntelX or similar APIs)

- [ ] **API server mode**
  - REST API via FastAPI for programmatic access
  - API key authentication
  - Rate limiting and usage tracking
  - OpenAPI/Swagger documentation

---

## Phase 8: Hardening and Polish (v1.0.0)

**Goal:** Production-ready release.

- [ ] **Security**
  - API key encryption at rest (keyring integration)
  - Proxy and Tor support for anonymous lookups
  - Input sanitization and injection prevention
  - Audit logging of all queries

- [ ] **Performance**
  - Connection pooling and keep-alive
  - Intelligent caching with TTL per source
  - Batch investigation mode (process lists of targets)

- [ ] **Documentation**
  - Full CLI usage guide
  - Source plugin development guide
  - API reference documentation
  - Legal and ethical usage guidelines

- [ ] **Testing**
  - Unit tests for all modules (>80% coverage target)
  - Integration tests with mocked API responses
  - End-to-end CLI tests

- [ ] **Distribution**
  - PyPI package publication
  - Docker image
  - Homebrew formula (macOS)

---

## Future Ideas (Post v1.0)

- Browser extension for in-page lookups
- Maltego transform integration
- Recon-ng module compatibility
- Collaboration features (shared investigations)
- Machine learning for entity resolution and anomaly detection
- Mobile app companion

---

## Contributing

Pick any unchecked item from the roadmap and open an issue or PR. Contributions at any phase are welcome. See [README.md](README.md) for contribution guidelines.

---

**d3vn0mi** | [GitHub](https://github.com/d3vn0mi)
