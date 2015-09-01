import sys, os
import requests
import logging
import threading
import time
import random
import pymongo as mg

logging.basicConfig(level=logging.DEBUG,
                  format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    filename='crawler.log',
                 )

usleep = lambda x: time.sleep(x/1000000.0)
class PageCrawler:
    bid = 0
    page_list = []
    st = 0
    threads = []
    pool_size = 0
    url_prefix = ''
    save_dir = ''
    cj = {}

    # const
    MAX_THREAD_NUM = 4
    def __init__(self, bid, page_num):
        self.bid = bid
        self.page_list = range(1, page_num+1)
        self.url_prefix = 'http://www.bookask.com/book/page/img/'+str(bid)+'/%s.html'
        self.save_dir = "./data/"+str(bid)+"/"
        # read cookie dict for a file
        try:
            self.cj = eval(open('cookie.dict', 'r').read())
        except:
            print "load cookie failed, maybe can't download whole book"
        try:
            os.mkdir(self.save_dir, 0755)
        except:
            pass

    def worker(self, page_list):
        logging.debug("Enter worker with list "+','.join(str(x) for x in page_list))
        for pid in page_list:
            #print self.url_prefix %(pid)
            r = requests.get(self.url_prefix %(pid), cookies=self.cj)
            with open(self.save_dir+"%04d.png" %(pid), 'wb') as fp:
                fp.write(r.content)
        logging.debug("Exit worker")
        usleep(1700000)

    def add_thread(self):
        cnt = random.randint(6, 10)
        p_page_list = self.page_list[self.st:self.st+cnt]
        self.st += cnt
        logging.info("bid: %s %s/%s" %(self.bid, self.st, len(self.page_list)))
        self.threads.append(threading.Thread(target=self.worker, args=(p_page_list,)))

    def start(self, count=MAX_THREAD_NUM):
        self.pool_size = count
        for i in range(count):
            self.add_thread()
            if self.st >= len(self.page_list):
                break
        for i in range(len(self.threads)):
            self.threads[i].start()
        page_num = len(self.page_list)
        while len(self.threads) > 0:
            usleep(100000)
            for i in range(len(self.threads)-1, -1, -1):
                if not self.threads[i].isAlive():
                    self.threads.remove(self.threads[i])
            # add new thread to max pool_size
            for i in range(self.pool_size - len(self.threads)):
                if self.st >= len(self.page_list):
                    break
                self.add_thread()
                self.threads[-1].start()

if __name__ == '__main__':
    # get page_num from mongo
    cli = mg.MongoClient()
    tbl = cli.bookask.list
    for i in range(1, len(sys.argv)):
        logging.debug("start downloading book %s %s" %(i, sys.argv[i]))
        item = tbl.find_one({'bid':int(sys.argv[i])})
        if item == None:
            print "not found %s" %(sys.argv[i])
            continue
        page_num = item['page_size']
        bid = item['bid']
        pc = PageCrawler(bid, page_num)
        pc.start()
