import random
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd


def retry_with_backoff(
    func,
    logger,
    max_retries=5,
    base_delay=1,
    max_delay=30,
    exceptions=(Exception,),
    jitter=True,
):
    """
    Retries a function with exponential backoff if it raises specified
     exceptions.

    Parameters:
    - func: The function to execute.
    - max_retries: Maximum number of retries before giving up.
    - base_delay: Initial delay between retries in seconds.
    - max_delay: Maximum delay between retries in seconds.
    - exceptions: A tuple of exception classes that trigger a retry.
    - jitter: Whether to add random jitter to the delay to avoid thundering
      herd problem.
    - logger: Optional logger object with .warning() and .error() methods.
      Falls back to print if None.

    Returns:
    - The return value of func if successful.

    Raises:
    - The last exception raised by func if all retries fail.
    """
    func_name = func.__name__
    attempt = 0
    while attempt <= max_retries:
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries:
                msg = f"""Max retries reached.
                  Function '{func_name}' failed with exception: {e}"""
                if logger:
                    logger.error(msg)
                else:
                    print(msg)
                raise
            else:
                delay = min(max_delay, base_delay * (2**attempt))
                if jitter:
                    delay = delay * (
                        0.5 + random.random() / 2
                    )  # random between 50% and 100% of delay
                msg = f"""Attempt {attempt + 1} for function '{func_name}'
                  failed with {e}. Retrying in {delay:.2f} seconds..."""
                if logger:
                    logger.warning(msg)
                else:
                    print(msg)
                time.sleep(delay)
                attempt += 1


def get_ndaq_tickers():
    """
    Returns a list of current NASDAQ-100 tickers by scraping from Wikipedia.
    
    This function scrapes the NASDAQ-100 Wikipedia page to get the most up-to-date
    list of ticker symbols. It includes error handling and fallback to a hardcoded list.
    
    Returns:
        list: A list of strings, where each string is a NASDAQ-100 ticker symbol.
    """
    try:
        # Scrape NASDAQ-100 from Wikipedia
        url = "https://en.wikipedia.org/wiki/NASDAQ-100"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table with NASDAQ-100 components
        # Look for tables that contain ticker symbols
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        tickers = []
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    text = cell.get_text(strip=True)
                    # Look for ticker symbols (typically 1-5 uppercase letters)
                    if text and len(text) <= 5 and text.isupper() and text.isalpha():
                        # Filter out common non-ticker text
                        if text not in ['TICKER', 'SYMBOL', 'COMPANY', 'NAME', 'WEIGHT']:
                            tickers.append(text)
        
        # Remove duplicates and sort
        tickers = sorted(list(set(tickers)))
        
        # Validate we got a reasonable number of tickers (NASDAQ-100 should have ~100)
        if len(tickers) >= 80 and len(tickers) <= 120:
            print(f"Successfully scraped {len(tickers)} NASDAQ-100 tickers from Wikipedia")
            return tickers
        else:
            print(f"Warning: Got {len(tickers)} tickers, expected ~100. Using fallback list.")
            return get_ndaq_tickers_fallback()
            
    except Exception as e:
        print(f"Error scraping NASDAQ-100 tickers: {e}")
        print("Using fallback hardcoded list...")
        return get_ndaq_tickers_fallback()


def get_ndaq_tickers_fallback():
    """
    Fallback function that returns a hardcoded list of NASDAQ-100 tickers.
    Used when web scraping fails.
    
    Returns:
        list: A list of strings, where each string is a NASDAQ-100 ticker symbol.
    """
    # Updated NASDAQ-100 tickers as of 2024
    # This is used as a fallback when web scraping fails
    return [
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "NFLX", "ADBE",
        "CRM", "PEP", "COST", "AVGO", "CSCO", "TMUS", "INTC", "AMD", "QCOM", "INTU",
        "HON", "ISRG", "GILD", "MDLZ", "ADP", "PYPL", "REGN", "VRTX", "ABNB", "KLAC",
        "SNPS", "PANW", "CDNS", "MU", "ORLY", "MNST", "KDP", "LRCX", "ASML", "CHTR",
        "MAR", "MELI", "FTNT", "CTAS", "ODFL", "PAYX", "ROST", "IDXX", "BIIB", "FAST",
        "VRSK", "WDAY", "DXCM", "CPRT", "XEL", "PCAR", "ALGN", "SIRI", "MRVL", "ZS",
        "LCID", "JD", "PDD", "BIDU", "NTES", "TCOM", "WBA", "EA", "UBER",
        "LYFT", "DASH", "RIVN", "PLTR", "SNOW", "CRWD", "OKTA", "TEAM", "SPOT",
        "PINS", "SNAP", "BYND", "PTON", "DOCU", "RBLX", "ZM"
    ]


if __name__ == "__main__":
    ...
