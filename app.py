import pylab
import numpy
import random


def stdDev(X):
    """Assumes that X is a list of numbers.
    Returns the standard deviation fo X"""
    mean = float (sum(X)) / len(X)
    tot = 0.0
    for x in X:
        tot += (x-mean)**2
    return (tot / len(X))**0.5 #Square root of mean difference


def CV(X):
    mean = sum (X) / float(len(X))
    try:
        return stdDev(X) / mean
    except ZeroDivisionError:
        return float('nan')


class Location(object):

    def __init__(self, x, y):
        """x and y are floats"""
        self.x = x
        self.y = y

    def move(self, deltaX, deltaY):
        """deltaX and deltaY are floats"""
        return Location(self.x + deltaX, self.y + deltaY)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def distFrom(self, other):
        ox = other.x
        oy = other.y
        xDist = self.x - ox
        yDist = self.y - ox
        return (xDist**2 + yDist**2)**0.5

    def __str__(self):
        return '<'+str(self.x) + ', ' + str(self.y) + '>'


class Field(object):

    def __init__(self):
        self.drunks = {}

    def addDrunk(self, drunk, loc):
        if drunk in self.drunks:
            raise ValueError('Duplicate drunk')
        else:
            self.drunks[drunk] = loc

    def moveDrunk(self, drunk):
        if drunk not in self.drunks:
            raise ValueError('Drunk not in field')
        xDist, yDist = drunk.takeStep()
        currentLocation = self.drunks[drunk]
        #use move method of Location to get new location
        self.drunks[drunk] = currentLocation.move(xDist, yDist)

    def getLoc(self, drunk):
        if drunk not in self.drunks:
            raise ValueError('Drunk not in field')
        return self.drunks[drunk]



class OddField(Field):
    def __init__(self, numHoles, xRange, yRange):
        Field.__init__(self)
        self.wormholes = {}
        for w in range(numHoles):
            x = random.randint(-xRange, xRange)
            y = random.randint(-yRange, yRange)
            newX = random.randint(-xRange, xRange)
            newY = random.randint(-yRange, yRange)
            newLoc = Location(newX, newY)
            self.wormholes[(x,y)] = newLoc

    def moveDrunk(self, drunk):
        Field.moveDrunk(self, drunk)
        x = self.drunks[drunk].getX()
        y = self.drunks[drunk].getY()
        if (x, y) in self.wormholes:
            self.drunks[drunk] = self.wormholes[(x, y)]


class Drunk(object):
    def __init__(self, name = None):
        """Assumes name is a str"""
        self.name = name

    def __str__(self):
        if self != None:
            return self.name
        return 'Anonymous'


class UsualDrunk(Drunk):
    def takeStep(self):
        stepChoices = [(0.0, 1.0), (0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)]
        return random.choice(stepChoices)


class ColdDrunk(Drunk):
    def takeStep(self):
        stepChoices = [(0.0, 1.0), (0.0, -2.0), (1.0, 0.0), (-1.0, 0.0)]
        return random.choice(stepChoices)


class EWDrunk(Drunk):
    def takeStep(self):
        stepChoices = [(1.0, 0.0), (-1.0, 0.0)]
        return random.choice(stepChoices)


def walk(f, d, numSteps):
    """Assumes: f is a Field, d is a Drunk, and numSteps is an int >= 0.
    Moves d numSteps times, and returns the difference between
    the final location and the location at the start of the walk. """
    start = f.getLoc(d)
    for s in range(numSteps):
        f.moveDrunk(d)
    return start.distFrom(f.getLoc(d))


def simWalks(numSteps, numTrials, dClass):
    """Assums numSteps an int >= 0, numTrials an int > 0,
    d class a subclass of Drunk
    Simulates numTrials walks of numSteps steps each.
    Returns a list of the final distances for each trails"""

    Homer = dClass()
    origin = Location(0.0, 0.0)
    distances = []
    for t in range (numTrials):
        f = Field()
        f.addDrunk(Homer, origin) #adds a Homer to a field at point origin
        distances.append(walk(f, Homer, numSteps))
    return distances


def drunkTest(walkLengths, numTrials, dClass):
    """"Assumes walkLengths a sequence of intes >= 0
    numTrials an int > 0, dClass a sublcass of Drunk.
    For each number of steps in walkLengths, runs simWalks with
    numTrials walks and prints results"""
    for numSteps in walkLengths:
        distances = simWalks(numSteps, numTrials, dClass)
        print dClass.__name__, 'random walk of', numSteps, 'steps.'
        print ' Mean = ', sum(distances)/len(distances), '\n', ' CV = ', CV(distances)
        print ' Max = ', max(distances), 'Min = ', min(distances)


def simAll(drunkTypes, walkLengths, numTrials):
    for dClass in drunkTypes:
        drunkTest(walkLengths, numTrials, dClass)
        print '\n'

class StyleIterator(object):
    def __init__(self, styles):
        self.index = 0
        self.styles = styles

    def nextStyle(self):
        result = self.styles[self.index]
        if self.index == len(self.styles) - 1:
            self.index = 0
        else:
            self.index +=1
        return result


def simDrunk(numTrials, dClass, walkLengths):
    meanDistances = []
    cvDistances = []
    for numSteps in walkLengths:
        print 'Starting simulation of', numSteps, 'steps'
        trials = simWalks (numSteps, numTrials, dClass)
        mean = sum(trials) / float(len(trials))
        meanDistances.append(mean)
        cvDistances.append(CV(trials))
    return (meanDistances, cvDistances)


def simAll(drunkTypes, walkLengths, numTrials):
    styleChoice = StyleIterator(('b-', 'r:', 'm-'))
    for dClass in drunkTypes:
        curStyle = styleChoice.nextStyle()
        print 'Starting simulation of', dClass.__name__
        means, cvs = simDrunk(numTrials, dClass, walkLengths)
        cvMean = sum(cvs)/float(len(cvs))
        pylab.plot(walkLengths, means, curStyle, label=dClass.__name__ + '(CV = ' + str(round(cvMean)) + ')')
        pylab.title('Mean Distance from Origin (' + str(numTrials) + ' trials)')
        pylab.xlabel('Number of Steps')
        pylab.ylabel('Distance from Origin')
        pylab.legend(loc='best')
        pylab.semilogx()
        pylab.semilogy()
    pylab.show()

def getFinalLocs(numSteps, numTrials, dClass):
    locs = []
    d = dClass()
    origin = Location(0, 0)
    for t in range(numTrials):
        f = Field()
        f.addDrunk(d, origin)
        for s in range(numSteps):
            f.moveDrunk(d)
        locs.append(f.getLoc(d))
    return locs

def plotLocs(drunkTypes, numSteps, numTrials):
    styleChoice = StyleIterator(('b+', 'r^', 'mo'))
    for dClass in drunkTypes:
        locs = getFinalLocs(numSteps, numTrials, dClass)
        xVals, yVals = [], []
        for l in locs:
            xVals.append(l.getX())
            yVals.append(l.getY())
        meanX = sum(xVals)/float(len(xVals))
        meanY = sum(yVals)/float(len(yVals))
        curStyle = styleChoice.nextStyle()
        pylab.plot(xVals, yVals, curStyle, label=dClass.__name__ +' Mean loc. = <' + str(meanX) + ', '+str(meanY)+'>')
    pylab.title('Location at End of Walks ('+str(numSteps)+' steps')
    pylab.xlabel('Steps East/West of Origin')
    pylab.ylabel('Steps North/South of Origin')
    pylab.legend(loc='lower left', numpoints=1)
    pylab.show()


def traceWalk(drunkTypes, numSteps):
    styleChoice = StyleIterator(('b^','r+', 'go'))
    #f = Field() #Commented out when OddField is utilized.
    f = OddField(500,200,200) #Replace Field() with the subclass in order to introduce wormholes
    for dClass in drunkTypes:
        d = dClass()
        f.addDrunk(d, Location(0, 0))
        locs = []
        for s in range(numSteps):
            f.moveDrunk(d)
            locs.append(f.getLoc(d))
        xVals = []
        yVals = []
        for l in locs:
            xVals.append(l.getX())
            yVals.append(l.getY())
        curStyle = styleChoice.nextStyle()
        pylab.plot(xVals, yVals, curStyle, label=dClass.__name__)
    pylab.title ('Spots Visited on Walk (' + str(numSteps) + ' steps)')
    pylab.xlabel('Steps East/West of Origin')
    pylab.ylabel('Steps North/South of Origin')
    pylab.legend(loc='lower left', numpoints=1)
    pylab.show()




traceWalk((UsualDrunk, ColdDrunk, EWDrunk), 1000)
plotLocs((UsualDrunk, ColdDrunk, EWDrunk), 100, 200)
simAll((UsualDrunk, ColdDrunk, EWDrunk), (10, 100, 1000, 10000, 100000), 100)
