#!/usr/bin/env python3
"""
Read and write the scraped data
"""

import sqlite3
import hashlib

from config import DB_FILE


def init_db():
    """Create table if not exists."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                url TEXT,
                stock_ticker TEXT,
                stock_name TEXT,
                transaction_type TEXT,
                transaction_amount TEXT,
                politician TEXT,
                chamber_party TEXT,
                filed_date TEXT,
                traded_date TEXT,
                description TEXT,
                return_value TEXT
            )
        """)
        conn.commit()


def make_id(url: str) -> str:
    """Create unique ID from URL using SHA256 hash."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def read_all_trades():
    """Read all trades from DB as list of dicts with same keys as insert_new_trades."""
    keys = [
        "Stock URL", "Stock Ticker", "Stock Name", "Transaction Type",
        "Transaction Amount", "Politician", "Chamber/Party",
        "Filed Date", "Traded Date", "Description", "Return"
    ]
    trades = []
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        for row in conn.execute("SELECT * FROM trades"):
            # row[0] is the UID, skip it
            trade = {k: row[i+1] for i, k in enumerate(keys)}
            trades.append(trade)
    return trades


def insert_new_trades(trades):
    """
    Insert trades into DB if they are new.
    :param trades: list of dicts with at least 'Stock URL'
    :return: list of new trades (dicts) that were inserted
    """
    new_trades = []
    with sqlite3.connect(DB_FILE) as conn:
        for trade in trades:
            uid = make_id(trade["Stock URL"])
            try:
                conn.execute("""
                    INSERT INTO trades VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    uid,
                    trade["Stock URL"],
                    trade["Stock Ticker"],
                    trade["Stock Name"],
                    trade["Transaction Type"],
                    trade["Transaction Amount"],
                    trade["Politician"],
                    trade["Chamber/Party"],
                    trade["Filed Date"],
                    trade["Traded Date"],
                    trade["Description"],
                    trade["Return"],
                ))
                new_trades.append(trade)
            except sqlite3.IntegrityError:
                # already exists (duplicate URL hash)
                pass
        conn.commit()
    return new_trades
