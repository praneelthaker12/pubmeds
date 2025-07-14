import math
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from time import sleep
import csv
import argparse
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
API_KEY = "a3cb042f9e1f2ddfc4dea24c6a32e910ec09"  # Replace with your own key
MAX_IDS = 300
MAX_WORKERS = 10

csv_lock = threading.Lock()

def searchBioTechAndPharma(query, fileName):
    filterQuery = f"{query} AND ((biotech[Affiliation]) OR (pharmaceutical[Affiliation]))"
    search(filterQuery, fileName)

def search(query, fileName):
   
    print(f"  Query: {query}")
        
    # Fetch total no. of results
    noOfResults = getSearchResultCount(query)
    print(f"  Total Results: {noOfResults}")
    
    #Fetch search results and write
    executeFetchAndWrite(query, noOfResults, fileName)
    
    
def getSessionWithRetries() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def callSearchQueryAPI(query, startOffset):
    session = getSessionWithRetries()
    
    params = {
            "db": "pubmed",
            "term": query,
            "retstart": startOffset,
            "retmax": MAX_IDS,
            "retmode": "json",
            "api_key": API_KEY
    }
    
    try:
        response = session.get(f"{BASE_URL}esearch.fcgi", params=params, timeout=30)
        response.raise_for_status()
           
        return response
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return

def getSearchResultCount(query) -> int:
    data = callSearchQueryAPI(query, 0)
    if not data:
        return 0
    
    totalResults = data.json().get("esearchresult", {}).get("count", [])
    try:
        return int(totalResults)
    except (ValueError, TypeError):
        return 0

def searchyQueryForIds(query: str, startOffset: int) -> List[str]:
    data = callSearchQueryAPI(query, startOffset)
    if not data:
        return []
    
    ids = data.json().get("esearchresult", {}).get("idlist", [])
    return ids

def getPaperDetailsByIds(medIds: List[str]) -> List[Dict[str, str]]:
    session = getSessionWithRetries()
    
    try:
        details = session.get(
            f"{BASE_URL}efetch.fcgi",
            params={
                "db": "pubmed", 
                "id": ",".join(medIds), 
                "api_key": API_KEY
            },
            timeout=30
        )
        details.raise_for_status()
        return details

    except Exception as e:
        print(f"❌ EPost failed: {e}")
        return []

def writeToCsv(data: List[Dict[str, str]], writer):
    if not data:
        print("⚠️ No data to write.")
        return
    
    writer.writerows(data)        
    print(f"📁 CSV saved to: {filename}")
      
def getStartOffsets(total_records):
    ## Keeping max records to 10k as esearch APIs supports till 10k records only
    return list(range(0, 10000, MAX_IDS))
        
def executeFetchAndWrite(query, totalCount: int, fileName):
    print("Please wait: Fetching records")

    if fileName:
        with open(fileName, mode="w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["PubmedID","Title","Publication Year","Corresponding Author Email","All Author Emails","All Affiliations"])  # adjust fields
            writer.writeheader()

            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = []
                for startOffset in getStartOffsets(totalCount):
                    futures.append(executor.submit(fetchAndWrite, query, startOffset, writer))
                for future in concurrent.futures.as_completed(futures):
                    future.result()  # to raise exceptions if any
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = []
                for startOffset in getStartOffsets(totalCount):
                    futures.append(executor.submit(fetchAndWrite, query, startOffset, null))
                for future in concurrent.futures.as_completed(futures):
                    future.result()  # to raise exceptions if any
    
def fetchAndWrite(query, startOffset, writer):
    ids = searchyQueryForIds(query, startOffset)
    
    paperDetails = getPaperDetailsByIds(ids)
    soup = BeautifulSoup(paperDetails.content, "xml")
    articles = soup.find_all("PubmedArticle")
    
    with csv_lock:
        paperDetailsToWrite = []
        paper = {}
        for article in articles:
            try:
                pmid = article.find("PMID").text.strip()
                title_tag = article.find("ArticleTitle")
                title = title_tag.text.strip() if title_tag else "No title"

                # Extract publication year
                pub_year = "Unknown"
                pub_date = article.find("PubDate")
                if pub_date:
                    year = pub_date.find("Year")
                    medline = pub_date.find("MedlineDate")
                    if year:
                        pub_year = year.text.strip()
                    elif medline:
                        pub_year = medline.text.strip()

                affiliations = set()
                all_emails = []

                # Process authors
                for author in article.find_all("Author"):
                    name_parts = []
                    for tag in ["ForeName", "LastName", "Initials"]:
                        part = author.find(tag)
                        if part:
                            name_parts.append(part.text.strip())
                    name = " ".join(name_parts) if name_parts else "Unknown"

                    for aff in author.find_all("AffiliationInfo"):
                        aff_text = aff.text.strip()
                        affiliations.add(aff_text)

                        if "@" in aff_text:
                            for word in aff_text.split():
                                if "@" in word and "." in word:
                                    email = word.strip(";,.:()[]{}<>\"'")
                                    all_emails.append(f"{name} <{email}>")

                corr_email = all_emails[0] if all_emails else "Not available"

                paper = {
                    "PubmedID": pmid,
                    "Title": title,
                    "Publication Year": pub_year,
                    "Corresponding Author Email": corr_email,
                    "All Author Emails": "; ".join(all_emails) or "None",
                    "All Affiliations": "; ".join(sorted(affiliations)) or "N/A"
                }
                
                paperDetailsToWrite.append(paper)
            
            except Exception as e:
                print(f"⚠️ Skipped article: {e}")
                continue
        
        if writer:
            writer.writerows(paperDetailsToWrite)
        else:
            print(paperDetailsToWrite)
            
    
