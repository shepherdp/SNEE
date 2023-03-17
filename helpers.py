import random as rnd

from scipy.spatial import distance

# Error message classes
class InvalidPropertyError(Exception):
    pass

class UndefinedPropertyError(Exception):
    pass

class IncompatiblePropertyError(Exception):
    pass

class Bound:
    '''
    A helper class to restrict inputs to be between certain values.
    '''
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def __str__(self):
        return f'range [{self.lo}, {self.hi}]'

    def __contains__(self, item):
        try:
            return self.lo <= item <= self.hi
        except TypeError:
            return False

def coin_flip(p):
    '''
    Returns True p% of the time, False 1-p% of the time.

    :param p: Probability to return True
    :return: Boolean
    '''
    return rnd.random() < p

def dist(vec1, vec2):
    """
    Extract visible dimensions from param:vec2 and compare them to param:vec1.

    :param vec1: perceiving agent's feature vector
    :param vec2: perceived agent's feature vector
    :return: Hamming distance between visible dimensions of param:vec1 and param:vec2
    """
    distvec1 = [vec1[i] for i in range(len(vec1)) if vec2[i] != 0.]
    if not distvec1:
        return 0.
    distvec2 = [vec2[i] for i in range(len(vec2)) if vec2[i] != 0.]
    return distance.hamming(distvec1, distvec2)

# Helpful constants to check data types
BOOL = type(bool())
STR = type(str())
INT = type(int())
FLT = type(float())
LST = type(list())
DCT = type(dict())

# Constants that define possible values for categorical variables
TF = [True, False]
DISTS = ['-', 'constant', 'uniform', 'normal']
MAXINT_32 = 2147483647
MININT_32 = -2147483647

# Objects to make life easier when getting input within a certain range
PROB = Bound(0., 1.)
POSNUM = Bound(0, MAXINT_32)
SYMNUM = Bound(-MAXINT_32, MAXINT_32)
SYMBIN = Bound(-1., 1.)

# Lists to hold agents in different categories.
CONFORMING = ['default']
REBELLING = []

HOMOPHILIC = ['default']
HETEROPHILIC = []
MESOPHILIC = []
