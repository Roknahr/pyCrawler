class Term:
    freq = 0
    plist = list()

    def getFreq(self):
        return self.freq

    def setFreq(self, frequency):
        self.freq = frequency

    def getPostList(self):
        return self.plist

    def addToPostList(self, term):
        self.plist.append(term)  

    def __init__(self):
        pass

