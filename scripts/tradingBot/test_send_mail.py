#!/usr/bin/env python3
"""
Main runner for Congress Trading scraper Test.
"""

import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from database import read_all_trades
from tradingbot_client import safe_send_mail, trades_to_block_text, filter
from config import ADMIN

def main():
    now = datetime.now()
    print(now.strftime("%Y-%m-%d %H:%M:%S"))
    print("run test read db")

    data = read_all_trades()
    df_data = pd.DataFrame(data)

    recent_trades = filter(df_data)
    count = len(recent_trades)

    if count < 1:
        return

    # Convert to list of dicts for mailing
    dict_data = recent_trades.to_dict(orient="records")
    md_table = trades_to_block_text(dict_data)

    if dict_data:  # Only send mail if there are new trades
        print("run test send mail to admin")
        safe_send_mail(
            subject="[Scraper Test]",
            body=md_table,
            to_addr=ADMIN
        )
    else:
        print("No trades in the last 2 weeks.")

