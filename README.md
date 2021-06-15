# TFRRS-Scrape-to-SQL

A simple python-based web-scraper that pulls data from track and field ranking pages on TFRRS to local SQL tables.

Pulls data from all events into their respective tables with SQL friendly attributes and data entries.

All data types are VARCHAR for simplicity but data manipulation and analysis is still easy with CAST().

By default, the script pulls data from the final NCAA Outdoor 2021 rankings: https://www.tfrrs.org/lists/3191/2021_NCAA_Division_I_Outdoor_Qualifying_(FINAL).
