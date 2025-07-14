import typer
import pandas as pd
from pubmed_fetcher.fetcher import search_pubmed, fetch_details
from pubmed_fetcher.mod_entry import search, searchBioTechAndPharma
from datetime import datetime


app = typer.Typer(add_completion=False)

@app.command()
def get_papers_list(
    query: str,
    file: str = typer.Option(None, "--file", "-f", help="Optional path to save results as CSV"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Print extra info while running"),
    searchAll: bool = typer.Option(False, "--all", "-a", help="Search all records"),
):
    print(f"Started @ {datetime.now()}")
    if(searchAll):
        search(query, file)
    else:
        searchBioTechAndPharma(query, file)
        
    print(f"Ended @{datetime.now()}")

if __name__ == "__main__":
    app()
