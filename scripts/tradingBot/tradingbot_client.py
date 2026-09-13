#!/usr/bin/env python3

import os
import pandas as pd
import smtplib
import traceback
import time
import requests
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from database import init_db, insert_new_trades, read_all_trades
from scrapeCongress import fetch_table_data_headless_browser, ScrapeError
from config import DB_FILE, URL_BASE, URL_PAGE, TABLE_CLASS, SMTP_MAIL, SMTP_MAIL_PASSWORD, SUBSCRIBERS, ADMIN
from MQTT.mqtt_client import build_payload as build_sensor_payload


def send_mail(subject: str, body: str, to_addr: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_MAIL
    msg["To"] = to_addr

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_MAIL, SMTP_MAIL_PASSWORD)
        server.send_message(msg)


def safe_send_mail(subject: str, body: str, to_addr: str):
    """Sends mail but logs failure to a file instead of raising an exception."""
    try:
        send_mail(subject, body, to_addr)
    except Exception as e:
        with open("mail_error.log", "a", encoding="utf-8") as f:
            f.write(f"Failed to send mail to {to_addr}: {e}\nBody:\n{body}\n")


def trades_to_block_text(trades):
    lines = []
    for trade in trades:
        url = trade.get("Stock URL", "")
        lines.append(f"------------------")
        lines.append(url)
        for key, value in trade.items():
            if key == "Stock URL":
                continue
            lines.append(f"{key}: {value}")
        lines.append("")
    return "\n".join(lines)


def filter_recent(df_data):
    df_data["Traded Date"] = pd.to_datetime(df_data["Traded Date"], errors="coerce")
    cutoff = datetime.now() - timedelta(weeks=3)
    return df_data[df_data["Traded Date"] >= cutoff]


def run_tradingbot() -> int:
    print("--------------------------------------")
    if not os.path.exists(DB_FILE):
        init_db()

    now = datetime.now()
    print(now.strftime("%Y-%m-%d %H:%M:%S"))
    print("Try Scraping")

    data, new_trades, df, df_filtered = [], [], None, None

    try:
        # 1. Scrape
        data = fetch_table_data_headless_browser(URL_PAGE, TABLE_CLASS)
        #data = read_all_trades()

        # 2. Insert new trades into DB
        print("Insert found data into db")
        new_trades = insert_new_trades(data)
        
        if not new_trades:
            print("No new trades, publishing count 0.")
            return 0

        # 3. Convert & filter
        df = pd.DataFrame(new_trades)
        df_filtered = filter_recent(df)
        count = len(df_filtered)

        if count > 0:
            print("New trades found, sending mails")
            md_table = trades_to_block_text(df_filtered.to_dict(orient="records"))
            body = (
                "This mail was generated automatically!\n\n"
                "The following new trades were reported:\n\n"
                + md_table
                + "\n\nPlease note that this is not investment advice!\n"
                  "The Stock Trading on Congressional Knowledge Act requires U.S. "
                  "Senators and U.S. Representatives to publicly file and disclose "
                  "any financial transaction within 45 days of its occurrence.\n\n"
                  "The trade was made at \"Traded Date\". The trade was made public at \"Filed Date\".\n\n"
                  f"To unsubscribe, please send a mail to {ADMIN}.\n"
                  "Adding/removing from the subscription list currently requires manual work.\n"
                  "You will be notified when it’s done."
            )

            for addr in SUBSCRIBERS:
                safe_send_mail(
                    subject=f"[Scraper Update] {count} new trades",
                    body=body,
                    to_addr=addr
                )
        return count

    except Exception as e:
        import traceback
        debug_info = []
        debug_info.append("Exception occurred:\n" + "".join(traceback.format_exc()))
        debug_info.append("\n--- Debug Variables ---")
        debug_info.append(f"data = {repr(data)}")
        debug_info.append(f"new_trades = {repr(new_trades)}")
        debug_info.append(f"df = {df if df is None else df.head().to_string()}")
        debug_info.append(f"df_filtered = {df_filtered if df_filtered is None else df_filtered.head().to_string()}")
        debug_info.append("\n--- find the downloaded html page on the server as last_failed_page.html---")
        body = "\n".join(debug_info)
        
        print(body)

        # Save HTML if available
        if isinstance(e, ScrapeError) and getattr(e, "html", None):
            with open("last_failed_page.html", "w", encoding="utf-8") as f:
                f.write(e.html)

        safe_send_mail(
            subject="[Scraper Error] Congress Trading",
            body=body,
            to_addr=ADMIN
        )
        print("Scraping failed")
    
    return -1;


def build_payload(device_id: str, num_trades: int) -> dict:
    def validate(value) -> str:
        if not isinstance(value, int) or isinstance(value, bool):
            return "is not an integer"
        if value < 0:
            return "The Bot had an internal failure"
        if value > 10000:
            return "Over 10000 Trades?! The webpage does only show like 100"
        return ""

    return build_sensor_payload(device_id, ("num_trades", num_trades, validate))
