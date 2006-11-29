import sys

class progressBar:
    def __init__(self, minValue = 0, maxValue = 10, totalWidth = 12, number_of_threads = 1):
        self.progBar = {}
        for thread in range(number_of_threads):
            self.progBar["Thread-" + str(thread+1)] = ""
        #self.progBar = "[]"   # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done 
        self.updateAmount(0)  # Build progress bar string

    def updateAmount(self, newAmount = 0, thread_name = "Thread-1"):
        if newAmount < self.min: newAmount = self.min
        if newAmount > self.max: newAmount = self.max
        self.amount = newAmount

        # Figure out the new percent done, round to an integer
        diffFromMin = float(self.amount - self.min)
        percentDone = (diffFromMin / float(self.span)) * 100.0
        percentDone = round(percentDone)
        percentDone = int(percentDone)

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2
        numHashes = (percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))
        
        for name in self.progBar.keys():
            if name == thread_name:
               self.progBar[name] =  "[" + '#'*numHashes + ' '*(allFull-numHashes) + "]"
               
               percentPlace = (len(self.progBar[name]) / 2) - len(str(percentDone)) 
               percentString = str(percentDone) + "%"
               
               self.progBar[name] = self.progBar[name][0:percentPlace] + percentString + self.progBar[name][percentPlace+len(percentString):] \
               + " " + str(newAmount/1024) + "KB of " + str(self.max/1024) + "KB"
               
        progress = ""   
        keys = self.progBar.keys()
        keys.sort()
        for name in keys:
            progress += self.progBar[name] + " "
            #print self.progBar[name],
            #sys.stdout.write(self.progBar[name] + "\t")
            sys.stdout.write(progress + "\r")
            #sys.stdout.write("\r")
        
def myReportHook(totalSize, number_of_threads):
    prog = progressBar(0,totalSize,50, number_of_threads)
    return prog