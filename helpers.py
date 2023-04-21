import random as rnd

from scipy.spatial import distance
import tkinter as tk
import numpy as np
import time
import matplotlib.pyplot as plt
from random import shuffle

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

def dist(vec1, vec2, metric):
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
    if metric == 'hamming':
        return distance.hamming(distvec1, distvec2)
    elif metric == 'euclidean':
        return distance.euclidean(distvec1, distvec2)
    elif metric == 'cosine':
        return distance.cosine(distvec1, distvec2)

def xor(c1, c2):
    '''
    Returns the exclusive or of two truth values

    :param c1: the first value
    :param c2: the second value
    :return: c1 XOR c2
    '''
    return (c1 or c2) and not (c1 and c2)

def sample(mylist, num):
    try:
        return rnd.sample(mylist, num)
    except:
        return rnd.sample(mylist, len(mylist))

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
METRICS = ['-', 'betweenness', 'closeness', 'clustering', 'degree']
MAXINT_32 = 2147483647
MININT_32 = -2147483647

# Objects to make life easier when getting input within a certain range
PROB = Bound(0., 1.)
POSNUM = Bound(0, MAXINT_32)
SYMNUM = Bound(-MAXINT_32, MAXINT_32)
SYMBIN = Bound(-1., 1.)

# Lists to hold agents in different categories.
CONFORMING = []#'default']
REBELLING = []

HOMOPHILIC = ['default']
HETEROPHILIC = []
MESOPHILIC = []

class ToolTip(object):
    """
    This creates a tool tip for any given widget, so when you hover your mouse it displays any and all relevant information regarding it.
    """
    def __init__(self, widget, text='widget info'):
        """The initiator contructs the tooltip, binding widgets and creating variables to be used and defined later."""
        self.waittime = 500     #miliseconds
        self.wraplength = 300   #pixels
        self.widget = widget
        self.text = text
        self.bg = 'white'
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
        self.label = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        """Calls upon unschedule, and checks if id is already set. In which it will execute the cancel parameter of self.widget.
        It sets self.id to the self.widget property filling in parameters with other self properties, even calling for the showyip ptoprtyu."""
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def show(self, event=None):
        """Shows the conxtext tool tip on the screen, using a top level invisile window to hold the label serving as a parent to the tool tip."""
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        self.label = tk.Label(self.tw, text=self.text, justify='left',
                              background=self.bg, relief='solid', borderwidth=1,
                              wraplength=self.wraplength)
        self.label.pack(ipadx=1)

    def hide(self):
        """Sets the topwindow to variable to the property which is set to none. If its active, it will be destroyed."""
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()

    def update(self, text, bg):
        self.text = text
        self.bg = bg

TOOLTIP = {'n': {'normal': '''param \'n\': (int) number of nodes in the graph.
This parameter must be a positive integer.
Floating-point inputs will be rounded down.''',
                 'error': '''This value must be a positive integer.'''},
           'symmetric': {'normal': '''param \'symmetric\': (bool) whether edge symmetry is enforced.
Only applicable to directed graphs; undirected graphs are symmetric by default.
Symmetric directed edges may have different weights from each other.'''},
           'directed': {'normal': '''param \'directed\': (bool) whether graph edges are directed.'''},
           'multiedge': {'normal': '''param \'multiedge\': (bool) whether multiple edges are allowed with the same source and destination nodes.'''},
           'selfloops': {'normal': '''param \'selfloops\': (bool) whether self-edges are enforced.
If true, self-edges cannot be deleted.  If false, they cannot be added.'''},
           'topology': {'normal': '''param \'topology\': (str) which generation algorithm to use for creating edges.'''},
           'saturation': {'normal': '''param \'saturation\': (float) the initial average node degree across the network.'''},
           'weight_dist': {'normal': '''param \'weight_dist\': (str) the distribution from which to draw edge weights.'''},
           'weight_mean': {'normal': '''param \'weight_mean\': (str) the mean of the weight distribution; only applicable for weight_dist=\'normal\'.''',
                           'error': '''This value must be between weight_min and weight_max.'''},
           'weight_stdev': {'normal': '''param \'weight_stdev\': (str) the standard deviation of the weight distribution; only applicable for weight_dist=\'normal\'.''',
                            'warn': '''Value is set high relative to min, max, and mean.  Distribution may not be as expected.'''},
           'weight_min': {'normal': '''param \'weight_min\': (str) the minimum of the weight distribution; only applicable for weight_dist=\'normal\' or \'uniform\'.''',
                          'error': '''This value must be strictly less than weight_max and (if applicable) weight_mean.'''},
           'weight_max': {'normal': '''param \'weight_max\': (str) the maximum of the weight distribution; only applicable for weight_dist=\'normal\' or \'uniform\'.''',
                          'error': '''This value must be strictly greater than weight_min and (if applicable) weight_mean.'''},
           'normalize': {'normal': '''param \'normalize\': (bool) whether to normalize edge weights.'''},
           'layout': {'normal': '''param \'layout\': (str) the layout algorithm determining the positions of nodes on the screen.'''},
           'speed': {'normal': '''param \'speed\': (int) the speed of the animation.'''},
           'staticpos': {'normal': '''param \'staticpos\': (bool) whether to let node positions change over time.'''},
           'nodesize': {'normal': '''param \'nodesize\': (int) how much to scale the size of nodes by their current value.'''},
           'nodealpha': {'normal': '''param \'nodealpha\': (float) the transparency of nodes.'''},
           'sizenodesby': {'normal': '''param \'sizenodesby\': (str) the parameter by which to size nodes.'''},
           'colornodesby': {'normal': '''param \'colornodesby\': (str) the parameter by which to color nodes.'''},
           'labelnodesby': {'normal': '''param \'labelnodesby\': (str) the parameter by which to label nodes.'''},
           'alphaedgesby': {'normal': '''param \'alphaedgesby\': (str) the parameter by which to size edges.'''},
           'coloredgesby': {'normal': '''param \'coloredgesby\': (str) the parameter by which to color edges.'''},
           'labeledgesby': {'normal': '''param \'labeledgesby\': (str) the parameter by which to label edges.'''},
           'edgealpha': {'normal': '''param \'edgealpha\': (str) the factor by which to scale edge transparency.'''},
           'numplots': {'normal': '''param \'numplots\': (int) the number of additional subplots.'''},
           }
for i in range(1, 7):
    TOOLTIP.update({f'plot{i}data': {'normal': f'''param \'plot{i}data\': (str) the metric to display on the current plot.'''},
                    f'plot{i}color': {'normal': f'''param \'plot{i}color\': (str) the color to display the current metric on its plot.
This setting is overridden if the parameter \'colornodesby\' = \'type\'.'''}})