from Helper import Helper
from time import time, sleep
from queue import Queue


class Frontier:
    
    numBackQueues = 10
    frontQueue = Queue()
    backQueue = {}

    def fill_back_queue(self):
        while len(self.backQueue) < self.numBackQueues:

            if not self.frontQueue.empty():
                url = self.frontQueue.get()
            else:
                return -1

            domain = Helper.get_domain(url)
            if domain in self.backQueue:
                self.backQueue[domain][0].put(url)
                self.backQueue[domain][1] = time()
            else:
                self.backQueue[domain] = [Queue(), time()]
                self.backQueue[domain][0].put(url)

    def get(self):
        if len(self.backQueue) < 10:
            self.fill_back_queue()

        next = sorted(self.backQueue.values(), key=lambda x: x[1])[0]

        url = next[0].get()

        domain = Helper.get_domain(url)
        print(str(next[1]+2 - time()))
        if time() < next[1]+2:
            sleep(next[1]+2 - time())

        self.backQueue[domain][1] = time()

        if self.backQueue[domain][0].empty():
            self.backQueue.pop(domain)
            self.fill_back_queue()

        return url

    def put(self, url):
        self.frontQueue.put(url)