# 🧬 PubMed Fetcher CLI Tool

A Python command-line interface (CLI) tool to search and filter PubMed articles based on user queries.  
It extracts only the articles with **at least one author affiliated with a pharmaceutical or biotech company**, and exports the filtered metadata to a clean CSV file.

---

## 📁 Project Structure

```
pubmeds/
├── cli.py                      # Typer-based CLI interface entry point
├── pyproject.toml              # Poetry configuration and script entry declaration
└── pubmed_fetcher/
    ├── __init__.py             # Initializes the module
    └── mod_entry.py              # Contains logic to fetch and filter PubMed articles
```

### 🔍 `fetcher.py`
- `search_pubmed(query: str, retmax=10)` → Queries PubMed and returns a list of article IDs.
- `fetch_details(pubmed_ids: List[str])` → Parses metadata from XML and returns only papers with non-academic (company-affiliated) authors.

### 💻 `cli.py`
- Defines the Typer CLI command: `get-papers-list`
- Accepts arguments like query string, output file name, and a debug flag.
- Uses `pandas` to convert the results into a CSV file.

---

## 📦 Installation Guide

### 🔧 Prerequisites
- Python 3.8 or newer
- [Poetry](https://python-poetry.org/docs/#installation)

### 🚀 Setup Steps

1. Clone the repository:
```bash
git clone (https://github.com/praneelthaker12/pubmeds)
cd pubmed-fetcher
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Run the CLI tool:
```bash
poetry run get-papers-list "your query here" --file output.csv --debug
```

---

## 🧪 Example Usage

```bash
poetry run get-papers-list "covid vaccine development" --file covid_results.csv --debug
```

### Output Sample

| PubmedID | Title | Publication Date | Non-academic Author(s) | Company Affiliation(s) | Corresponding Author Email | All Affiliations |
|----------|-------|------------------|--------------------------|--------------------------|-----------------------------|-------------------|

> CSV output will contain **only relevant articles** with at least one company affiliation.


---

## 🧰 Tools & Libraries Used

| Tool | Purpose |
|------|---------|
| [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | Search and fetch PubMed articles |
| [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) | XML parsing |
| [Typer](https://typer.tiangolo.com/) | Command-line interface |
| [Pandas](https://pandas.pydata.org/) | Data handling and CSV export |
| [Poetry](https://python-poetry.org/) | Python dependency and virtualenv management |


## 🙋‍♂️ Author & Contact

Praneel Thaker
Email: Praneelmthaker@gmail.com
