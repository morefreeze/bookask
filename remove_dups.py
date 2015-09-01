import pymongo as mg

cli = mg.MongoClient()
tbl = cli.bookask.list
bids = {}
books = tbl.find()
need_del = []
for book in books:
    if book['bid'] in bids:
        need_del.append(book['_id'])
    else:
        bids[ book['bid'] ] = 1

print need_del
for b_del in need_del:
    tbl.remove(b_del)
