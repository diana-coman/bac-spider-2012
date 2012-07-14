import urllib
import urllib2
from urllib import urlencode

import cPickle as pickle
import logging
import os
import random
import time
import urlparse
import cookielib

START_PAGE_NO = 1
END_PAGE_NO = 20019

OUTPUT_DIR = 'data'


def dump_remaining_pages(pages):
    logging.info("Dumping remaining pages")
    with open('pages.pickle', 'wb') as f:
        return pickle.dump(pages, f)

def load_remaining_pages():
    logging.info("loading pages from pages.pickle")
    with open('pages.pickle', 'rb') as f:
        return pickle.load(f)

def generate_pages():
    logging.info("generating pages")
    page_pattern = r'''http://bacalaureat.edu.ro/Pages/TaraRezultMedie.aspx?Poz=%(no)d'''
    pages = [page_pattern % {'no': i} for i in range(START_PAGE_NO, END_PAGE_NO+1)]
    random.shuffle(pages)
    return pages

def get_pages():
    if os.path.exists('pages.pickle'):
        return load_remaining_pages()
    return generate_pages()

def create_destination(page):
    global OUTPUT_DIR

    page_name = "page_" + page.rsplit('=', 1)[1] + ".htm"
    dst_dir = os.path.join(OUTPUT_DIR, 'pages')
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    dst = os.path.join(dst_dir, page_name)
    return dst

def retrieve_page(page, dst):
    #base form fields
    eventtarget_field = (r'__EVENTTARGET', r'')
    eventargument_field = (r'__EVENTARGUMENT', r'')
    lastfocus_field = (r'__LASTFOCUS', r'')

    #simulate a browser in case the website refuses access to spiders
    headers = {
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
        'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPSHandler(debuglevel=1))

    rq = urllib2.Request(page, urlencode([]), headers)
    f = opener.open(rq)

    try:
        fout = open(dst, 'w')
    except:
        print('Could not write to file\n')

    fout.writelines(f.readlines())
    fout.close()

def main():
    logging.info("getting pages")
    pages = get_pages()

    
    page = None # 
    try:
        while pages:
            page = pages.pop()
            dst = create_destination(page)
            logging.info("Retrieving %s" % (page,))
            retrieve_page(page, dst)
         
            logging.info("Pausing")
            time.sleep(random.random()*0.25)
    except:
        dump_remaining_pages(pages + [page])
        raise

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)-15s %(message)s',
                        level=logging.DEBUG)
    main()

