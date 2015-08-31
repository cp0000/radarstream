#!/usr/bin/python

import urllib2
import sqlite3
import requests
import time
from bs4 import BeautifulSoup
from weibo import APIClient


global sqlite_file
sqlite_file = '/opt/dev/radarstream/bugdb'


def setupWeibo ():
    print 'set up weibo access_token ...'
    user_agent = ( 
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) '
        'Chrome/20.0.1132.57 Safari/536.11'
        )

    session = requests.session()
    session.headers['User-Agent']   = user_agent
    session.headers['Host']         = 'api.weibo.com'

    api_key         = '2959986135'
    api_secret      = 'f6148b1b6af3baa327c543a12b4c98b6'
    callback_url    = 'http://cp0000.github.io'

    client          = APIClient(app_key=api_key, app_secret=api_secret, redirect_uri=callback_url)
    access_token    = '2.00JoploBrbn_OD9765fad696I7EQFD'
    expires         = '1598191620'
    client.set_access_token(access_token, expires)
    return client;


def initDB ():
    print 'initDB ...'
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS
                      bugs(id INTEGER PRIMARY KEY, bugid TEXT, status TEXT, originator TEXT, product TEXT, title TEXT)''')
    db.commit()

def find (bugid):
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    cursor.execute('''SELECT bugid FROM bugs WHERE bugid =? ''', (bugid,))
    bug=cursor.fetchone ()
    return bug;

def insert (bugid, status, originator, product, title):
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    cursor.execute('''INSERT INTO bugs(bugid, status, originator, product, title)
                      VALUES(?,?,?,?,?)''', (bugid, status, originator, product, title))

    db.commit()

def spider (client):
    print 'start spider ...'
    request = urllib2.Request('http://openradar.appspot.com/')
    # request.add_header('User-Agent', 'hello_client')
    user_agent = ( 
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) '
        'Chrome/20.0.1132.57 Safari/536.11'
        )
    request.add_header('User-Agent', user_agent)
    page    = urllib2.urlopen(request)

    soup    = BeautifulSoup(page)
    buglist = [tr.findAll('td') for tr in soup.findAll('tr')]

    results = [];
    dic     = {};

    newbuglist =  buglist[::-1] #reverse

    for bug in newbuglist:
        if len (bug) == 5:
            numbers = bug[0].get_text().split('://');
            dic['Number']       = numbers[1];

            bugInfo = find (numbers[1]);

            if bugInfo:
                print bugInfo
            else:
                dic['Status']       = bug[1].get_text();
                dic['Originator']   = bug[2].get_text();
                dic['Product']      = bug[3].get_text();
                dic['Title']        = bug[4].get_text();
                results.append({dic['Number']: dic});

                #tweek
                content =  dic['Title'] + '\n' + 'Originator:' + dic['Originator'] + '\n' + 'Product:' + dic['Product'] + '\n' + 'http://www.openradar.appspot.com/' + dic['Number']

                print content
                client.statuses.update.post(status=content)
                insert (dic['Number'], dic['Status'], dic['Originator'], dic['Product'], dic['Title']);
                time.sleep(60*3) 

if __name__=='__main__':
    client = setupWeibo ();
    initDB ();
    spider (client);



