#!/usr/bin/env python3
"""
Table into structured format.
Each parsing strategy is a dedicated function with error handling.
"""

import requests
from requests.adapters import HTTPAdapter, Retry
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import math
from config import URL_BASE

def human_like_scroll(page):
    # Scroll a random amount
    scroll_amount = random.randint(100, 500)
    page.mouse.wheel(0, scroll_amount)
    # Random small delay
    time.sleep(random.uniform(0.2, 0.6))

def human_like_mouse(page, movements=10):
    """Move mouse in non-linear human-like paths."""
    width, height = page.viewport_size['width'], page.viewport_size['height']

    i=0
    for _ in range(movements):
        time.sleep(random.uniform(0.2, 0.9))
        i=i+1;
        if i == 3:
            human_like_scroll(page)
        
        start_x = random.randint(0, width - 1)
        start_y = random.randint(0, height - 1)
        end_x = random.randint(0, width - 1)
        end_y = random.randint(0, height - 1)
        steps = random.randint(20, 50)

        for t in range(steps):
            # normalized time [0,1]
            p = t / steps

            # Bezier-like interpolation with small sine jitter
            x = int(start_x + (end_x - start_x) * p + math.sin(p * math.pi * 4) * random.randint(-3,3))
            y = int(start_y + (end_y - start_y) * p + math.sin(p * math.pi * 4) * random.randint(-3,3))

            page.mouse.move(x, y)
            time.sleep(random.uniform(0.01, 0.03))


def get_spoofed_headers():
    """
    Returns a dictionary with randomized browser-like HTTP headers
    to reduce the chance of being blocked by websites.
    """
    user_agents = [
        # Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]

    languages = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9",
        "en-US,en;q=0.8,fr;q=0.6",
    ]

    return {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": random.choice(languages),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }

def get_spoofed_headers_playwright():
    """Return randomized user-agent and viewport for Playwright."""
    user_agents = [
        # Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    viewports = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
    ]
    return random.choice(user_agents), random.choice(viewports)

class ScrapeError(Exception):
    """Custom exception for scraping errors."""
    def __init__(self, message, html=None):
        super().__init__(message)
        self.html = html  # optional full HTML for debugging


# ---------- Parsing Strategies ----------

def parse_stock_cell(td):
    """
    Parse stock cell into {url, ticker, name}.
    Expected structure:
        <td>
            <a href="...">
                <span><span class="positive">TICKER</span></span>
                <span>Long Name</span>
                <span>Type</span>
            </a>
        </td>
    """
    link = td.find("a")
    if not link:
        raise ScrapeError("Stock cell: <a> not found", html=td)

    url = link.get("href"); 

    if url.startswith("../../"):
        url = URL_BASE + url[6:]
    else:
        print(f"Warning: unexpected URL format: {url}")
        
    spans = link.find_all("span")
    if len(spans) < 2:
        raise ScrapeError("Stock cell: expected at least 2 <span> elements", html=td)

    ticker = spans[0].get_text(strip=True)
    long_name = spans[1].get_text(strip=True)

    return {
        "Stock URL": url,
        "Stock Ticker": ticker,
        "Stock Name": long_name,
    }


def parse_transaction_cell(td):
    """Parse transaction info: type + amount."""
    link = td.find("a")
    if not link:
        raise ScrapeError("Transaction cell: <a> not found", html=td)

    spans = link.find_all("span")
    if len(spans) < 2:
        raise ScrapeError("Transaction cell: expected 2 <span> elements", html=td)

    return {
        "Transaction Type": spans[0].get_text(strip=True),
        "Transaction Amount": spans[1].get_text(strip=True),
    }


def parse_politician_cell(td):
    """Parse politician name and chamber/party."""
    # name
    name_tag = td.select_one("strong.table-sub-link")
    if not name_tag:
        raise ScrapeError("Politician cell: name <strong> not found", html=td)
    
    politician = name_tag.get_text(strip=True)

    # chamber / party
    chamber_span = td.select_one("div.flex-column > span")
    chamber_party = chamber_span.get_text(strip=True) if chamber_span else None
    return {
        "Politician": politician,
        "Chamber/Party": chamber_party,
    }


def parse_simple_cell(td, label):
    """Parse a simple text cell with <a>."""
    text = td.get_text(strip=True)
    if not text:
        raise ScrapeError(f"{label} cell: text not found", html=td)
    return {label: text}


def parse_return_cell(td):
    """Parse return percentage."""
    span = td.find("span")
    if not span:
        raise ScrapeError("Return cell: <span> not found", html=td)
    return {"Return": span.get_text(strip=True)}


# ---------- Main Scraper ----------

def fetch_table_data(url: str, table_class: str):
    """
    Fetch and parse the Congress Trading table.

    Raises ScrapeError with html if parsing fails.
    """
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=2, status_forcelist=[502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))
        headers = get_spoofed_headers()

        # fetch page
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # decode content safely
        try:
            html = response.content.decode(response.encoding or response.apparent_encoding, errors="replace")
        except Exception:
            html = response.text  # fallback

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", {"class": table_class})
        if not table:
            raise ScrapeError(f"Table with class '{table_class}' not found", html=html)

        rows = []
        for tr in table.find("tbody").find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) != 7:
                continue  # skip non-data rows

            row = {}
            row.update(parse_stock_cell(tds[0]))
            row.update(parse_transaction_cell(tds[1]))
            row.update(parse_politician_cell(tds[2]))
            row.update(parse_simple_cell(tds[3], "Filed Date"))
            row.update(parse_simple_cell(tds[4], "Traded Date"))
            row.update(parse_simple_cell(tds[5], "Description"))
            row.update(parse_return_cell(tds[6]))

            rows.append(row)
            
        if not rows:
            raise ScrapeError("No rows parsed from table", html=html)

        return rows

    except requests.exceptions.RequestException as e:
        raise ScrapeError(f"Failed to fetch URL: {e}")


from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def fetch_table_data_headless_browser(url: str, table_class: str):
    try:
        user_agent, viewport = get_spoofed_headers_playwright()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=user_agent,
                viewport=viewport,
            )
            page = context.new_page()
            page.goto(url, timeout=60000)  # wait up to 60s
            
            # Simulate human behavior
            human_like_mouse(page, movements=random.randint(5, 15))
            
            page.wait_for_selector(f"table.{table_class.replace(' ', '.')}")  # ensure table loads

            html = page.content()  # full rendered HTML
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"class": table_class})
        if not table:
            raise ScrapeError(f"Table with class '{table_class}' not found", html=html)

        rows = []
        for tr in table.find("tbody").find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) != 7:
                continue  # skip non-data rows

            row = {}
            row.update(parse_stock_cell(tds[0]))
            row.update(parse_transaction_cell(tds[1]))
            row.update(parse_politician_cell(tds[2]))
            row.update(parse_simple_cell(tds[3], "Filed Date"))
            row.update(parse_simple_cell(tds[4], "Traded Date"))
            row.update(parse_simple_cell(tds[5], "Description"))
            row.update(parse_return_cell(tds[6]))

            rows.append(row)

        return rows

    except Exception as e:
        raise ScrapeError(f"Failed to fetch or parse page: {e}", html=html)

