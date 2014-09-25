class Term:
    plist = set()

    def getFreq(self):
        return self.freq

    def setFreq(self, frequency):
        self.freq = frequency

    def getPostList(self):
        return self.plist

    def addToPostList(self, term):
        self.plist.add(term)

    def __init__(self):
        self.freq = 1

