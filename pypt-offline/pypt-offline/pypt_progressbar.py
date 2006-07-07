class progressBar:
    def __init__(self, minValue = 0, maxValue = 10, totalWidth=12):
        self.progBar = "[]"   # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done 
        self.updateAmount(0)  # Build progress bar string

    def updateAmount(self, newAmount = 0):
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

        # build a progress bar with hashes and spaces
        self.progBar = "[" + '#'*numHashes + ' '*(allFull-numHashes) + "]"

        # figure out where to put the percentage, roughly centered
        percentPlace = (len(self.progBar) / 2) - len(str(percentDone)) 
        percentString = str(percentDone) + "%"

        # slice the percentage into the bar
        self.progBar = self.progBar[0:percentPlace] + percentString + self.progBar[percentPlace+len(percentString):]

    def __str__(self):
        return str(self.progBar)
        
def myReportHook(count, blockSize, totalSize):
    import sys
    global prog
    prog = ""

    if prog == "":
        prog = progressBar(0,totalSize,50)
    #print count, blockSize, totalSize
    #prog = progressBar(0, totalSize, 77)
    prog.updateAmount(count*blockSize)
    sys.stdout.write (str(prog))
    sys.stdout.write ("\r")
    #print count * (blockSize/1024) , "kb of " , (totalSize/1024) , "kb downloaded.\n"
#prog = ""
#sFile = "new.rpm"
#sUrl = "http://ftp.debian.org/debian/dists/unstable/main/binary-i386/Packages.bz2"
#$urllib.urlretrieve(sUrl, sFile, reporthook=myReportHook)    
#print "\n\n"
#temp = urllib2.urlopen(sUrl)
#lastval = int(temp.headers['Content-Length'])
#prog = progressBar(0, lastval, 77)
#
#for x in range(101):
#    prog.updateAmount(x)
#    print prog, "\r", time.sleep(0.5)
#
#data = open(sFile,'wb')
#data.write(temp.read())
#data.close()
#temp.close()
