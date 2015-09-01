import sys
import pymongo as mg
import re
import urllib, urllib2

cli = mg.MongoClient()
tbl = cli.bookask.list
books = []
if len(sys.argv) < 2:
    # get all books in mongo
    for item in tbl.find({'page_size':None}):
        books.append(item['bid'])
else:
    books = sys.argv[1:]

re_bookpage = re.compile('bookpage-proc')
re_maxpage = re.compile('max=["\'](\d+)')
for bid in books:
    bid = int(bid)
    url = 'http://www.bookask.com/book/page/%s/1.html' %(bid)
    for line in urllib2.urlopen(url):
        if re_bookpage.search(line) != None:
            out = re_maxpage.search(line)
            if None != out:
                print bid, out.group(1)
                print tbl.find_one_and_update({'bid':bid}, {'$set':{'page_size':int(out.group(1))}}, return_document=mg.collection.ReturnDocument.AFTER)
