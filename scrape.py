# TFRRS Scrape to SQL - Joshua Harmsen
#
# A simple python-based web-scraper to scrape data from track and field
# ranking tables on TFRRS to local SQL tables in tfrrs.db


import sqlite3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

#Datatypes for each column in the table, all VARCHAR for simplicity.
datatypes = {'RANK':'RANK VARCHAR(3)',
             'ATHLETE':'ATHLETE VARCHAR(32) PRIMARY KEY',
             'YEAR':'YEAR VARCHAR(4)',
             'TEAM':'TEAM VARCHAR(24)',
             'TIME':'TIME VARCHAR(8)',
             'MEET':'MEET VARCHAR(64)',
             'MEET_DATE':'MEET_DATE VARCHAR(16)',
             'WIND':'WIND VARCHAR(3)',
             'ATHLETES':'ATHLETES VARCHAR(80) PRIMARY KEY',
             'MARK':'MARK VARCHAR(12)',
             'CONV':'CONV VARCHAR(24)',
             'POINTS':'POINTS VARCHAR(8)'}


if __name__ == '__main__':
    conn = sqlite3.connect('tfrrs.db') #Make SQL connections
    cur = conn.cursor()

    link = 'https://www.tfrrs.org/lists/3191/2021_NCAA_Division_I_Outdoor_Qualifying_(FINAL)?gender=m'
    req = Request(link, headers={'User-Agent': 'Chrome/56.0.2924.76'})

    text = urlopen(req).read()
    soup = BeautifulSoup(text, 'html.parser')
    divs = soup.find_all('div', {'class': 'col-lg-12'})
    #Get the divs containing tables, all of class col-lg-12.

    print('Scraping data...')
    for div in divs:
        event_h3 = div.find_all('h3') #Find headings containing the event data
        if event_h3: #If we have a valid event, not a None, then:
            raw_event = event_h3[0].text
            if '(Men)' in raw_event:
                raw_event = raw_event.replace('(Men)', 'M')
            else:
                raw_event = raw_event.replace('(Women)', 'W')
            raw_event = raw_event.replace(',', '')
            raw_event = raw_event.replace('\'', '')
            event = raw_event.replace(' ', '_')

            table = div.table
            header = table.thead.tr
            col_names = header.find_all('th')
            #Get all column names from the header

            sql_cols = []
            for col_name in col_names:
                col_name = col_name.text
                col_name = col_name[1:len(col_name)-1]
                col_name = col_name.replace(' ', '_')
                sql_cols.append(col_name)
                #Prune column names save them for later SQL statements

            sql_cols[0] = 'RANK' #Update [0] which has no name by default


            #Drop old tables and create new ones, with primary ATHLETE(S) attribute
            cur.execute('DROP TABLE IF EXISTS {}'.format(event))
            if 'ATHLETE' in sql_cols:
                cur.execute('CREATE TABLE {} ({})'.format(event, datatypes['ATHLETE']))
            else:
                cur.execute('CREATE TABLE {} ({})'.format(event, datatypes['ATHLETES']))

            sql_col_string = '('
            for col in sql_cols:
                if col != 'ATHLETE' and col != 'ATHLETES':
                    cur.execute('ALTER TABLE {} ADD COLUMN {}'.format(event, datatypes[col]))
                sql_col_string = sql_col_string + col + ','
            sql_col_string = sql_col_string[:-1] + ')'
            #Build the sql_col_string for inserting into tables later

            num_cols = len(sql_cols)
            rows = table.tbody.find_all('tr')
            for row in rows:
                data = []
                cols = row.find_all('td')
                for col in cols:
                    text = col.text.replace('\'',' ')
                    data.append(text)
                #Build a data string for each row in the table


                stmt = 'INSERT OR IGNORE INTO {} {} VALUES ({})'
                stmt = stmt.format(event, sql_col_string, '\'{}\' ,' * num_cols)
                stmt = stmt.format(*data)
                stmt = stmt[:-2] + ')'
                #Build the insert statement with format() and execute it
                cur.execute(stmt)
                conn.commit()

            print("Finished populating {} table.".format(event))


    print("TFRRS Scrape to SQL complete.")
    conn.commit()
    conn.close()
