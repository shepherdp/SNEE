# Test suite for SocialNetwork.py
import networkx

from helpers import *
from SocialNetwork import SocialNetwork
from inspect import getframeinfo, stack


import matplotlib.pyplot as plt


TESTCOUNT = 0
PASSCOUNT = 0
def unittest(did_pass):
    """
    Print the result of a unit test.
    :param did_pass: a boolean representing the test
    :return: None
    """

    global PASSCOUNT, TESTCOUNT
    TESTCOUNT += 1
    caller = getframeinfo(stack()[1][0])
    linenum = caller.lineno
    if did_pass:
        msg = "Test at line {0} ok.".format(linenum)
        PASSCOUNT += 1
    else:
        msg = ("Test at line {0} FAILED.".format(linenum))
    print(msg)

# The 0 run of tests is for ensuring that overridden built-ins behave correctly
# with the class.

def test_0_00():
    # Make sure object is created with empty parameters without errors.
    try:
        s = SocialNetwork()
        return True
    except:
        return False
def test_0_01():
    # Test the len() function on empty graph.
    s = SocialNetwork()
    return len(s) == 0

def test_0_02():
    # Test the len() function on non-empty graph.
    s = SocialNetwork(n=10)
    return len(s) == 10

def test_0_03():
    # Test the __iter__ method against the Graph implementation.
    s = SocialNetwork(n=10)
    s2 = networkx.Graph()
    s2.add_nodes_from(range(10))
    list1, list2 = [i for i in s], [i for i in s2]
    return list1 == list2

def test_0_04():
    # Test the __getitem__ method against the graph implementation on empty graph.
    s = SocialNetwork(n=2)
    s2 = networkx.Graph()
    s2.add_nodes_from(range(2))
    return s[0] == s2[0]

def test_0_05():
    # Test the __getitem__ method against the graph implementation on non-empty graph.
    s = SocialNetwork(n=2)
    s.add_edge(0, 1)
    s2 = networkx.Graph()
    s2.add_nodes_from(range(2))
    s2.add_edge(0, 1)
    return s[0] == s2[0]

def test_1_00():
    # Check that default constructor creates Graph object.
    return SocialNetwork().isgraph()

def test_1_01():
    # Check that constructor with parameter undirected creates Graph object.
    return SocialNetwork(directed=False).isgraph()

def test_1_02():
    # Check that constructor creates DiGraph object.
    return SocialNetwork(directed=True).isdigraph()

def test_1_03():
    # Check that constructor creates MultiGraph object.
    return SocialNetwork(multiedge=True).ismultigraph()

def test_1_04():
    # Check that constructor creates MultiDiGraph object.
    return SocialNetwork(directed=True, multiedge=True).ismultidigraph()

def test_1_05():
    # Check that constructor creates graph with no nodes.
    return SocialNetwork().number_of_nodes() == 0

def test_1_06():
    # Check that constructor creates graph with correct number of nodes.
    return SocialNetwork(n=10).number_of_nodes() == 10

def test_1_07():
    # Check that property() gives back correct value.
    s = SocialNetwork()
    s.prop(abc=10)
    return s.prop('abc') == 10

def test_1_08():
    # Check that property() throws a KeyError at the right time.
    s = SocialNetwork()
    try:
        p = s.prop('abc')
        return False
    except KeyError: return True
    except: return False

def test_1_09():
    # Check that properties() gives back correct values.
    s = SocialNetwork()
    s.properties(abc=10, xyz=20)
    return s.properties('abc', 'xyz') == [10, 20]

def test_1_10():
    # Check that properties() throws error at the correct time.
    try:
        s = SocialNetwork()
        p = s.properties('abc')
        return False
    except UndefinedPropertyError: return True
    except: return False

def test_1_11():
    # Make sure that property() overwrites values correctly.
    s = SocialNetwork()
    s.property(abc=10)
    s.property(abc=20)
    return s.property('abc') == 20

def test_1_12():
    return True

def test_1_13():
    return True

def test_1_14():
    return True

def test_1_15():
    return True

def test_1_16():
    return True

def test_1_17():
    return True

def test_1_18():
    return True

def test_1_19():
    return True

def test_1_20():
    return True

# This section tests various functionality around edge weights and other distribution-based attributes.
def test_2_00():
    # Make sure that blank distribution is recorded correctly.
    return SocialNetwork().prop('weight_dist') == '-'
def test_2_01():
    # Make sure no errors are thrown when all inputs are provided and good.
    s = SocialNetwork(weight_dist='normal', weight_min=-1, weight_max=1,
                      weight_mean=0, weight_stdev=.1)
    return True

def test_2_02():
    # Make sure no errors are thrown and mean calculated correctly when no mean is provided.
    s = SocialNetwork(weight_dist='normal', weight_min=-1, weight_max=1,
                      weight_stdev=.1)
    return s.prop('weight_mean') == 0.

def test_2_03():
    # Make sure no errors are thrown and mean calculated correctly when no mean is provided.
    s = SocialNetwork(weight_dist='normal', weight_min=0, weight_max=1,
                      weight_stdev=.1)
    return s.prop('weight_mean') == .5

def test_2_04():
    # When no parameters are provided, mean and stdev should default to standard normal.
    s = SocialNetwork(weight_dist='normal')
    return s.prop('weight_mean') == 0 and s.prop('weight_stdev') == 1
def test_2_05():
    # Throw error when max is provided, but not min.
    try:
        s = SocialNetwork(weight_dist='normal', weight_max=1)
        return False
    except IncompatiblePropertyError:
        return True

def test_2_06():
    # Throw error when min is provided, but not max.
    try:
        s = SocialNetwork(weight_dist='normal', weight_min=0)
        return False
    except IncompatiblePropertyError:
        return True

def test_2_07():
    # Throw an error if only mean is provided.
    try:
        s = SocialNetwork(weight_dist='normal', weight_mean=0)
        return False
    except IncompatiblePropertyError:
        return True

def test_2_08():
    # Throw an error if only standard deviation is provided.
    try:
        s = SocialNetwork(weight_dist='normal', weight_stdev=0)
        return True
    except:
        return False

def test_2_09():
    # Throw an error if min > max.
    try:
        s = SocialNetwork(weight_dist='normal', weight_min=1, weight_max=0)
        return False
    except IncompatiblePropertyError:
        return True

def test_2_10():
    # Throw an error if mean > max.
    try:
        s = SocialNetwork(weight_dist='normal', weight_min=0, weight_max=1,
                          weight_mean=2)
        return False
    except IncompatiblePropertyError:
        return True

def test_2_11():
    # Throw an error if mean < min.
    try:
        s = SocialNetwork(weight_dist='normal', weight_min=0, weight_max=1,
                          weight_mean=-1)
        return False
    except IncompatiblePropertyError:
        return True

def test_2_12():
    # Make sure that providing only mean and standard deviation works.
    try:
        s = SocialNetwork(weight_dist='normal', weight_mean=0, weight_stdev=1)
        return True
    except:
        return False

def test_2_13():
    # Make sure that providing min and max but no standard deviation works.
    try:
        s = SocialNetwork(weight_dist='normal', weight_min=0, weight_max=1)
        return s.prop('weight_stdev') == .1 and s.prop('weight_mean') == .5
    except:
        return False

def test_2_14():
    # Make sure that providing min and max but no standard deviation works.
    try:
        s = SocialNetwork(weight_dist='normal', weight_min=-1, weight_max=1)
        return s.prop('weight_stdev') == .2 and s.prop('weight_mean') == 0
    except:
        return False

def test_2_15():
    # Make sure that providing min and max but no standard deviation works.
    try:
        s = SocialNetwork(weight_dist='uniform')
        return s.prop('weight_min') == 0 and s.prop('weight_max') == 1
    except:
        return False

def test_2_16():
    # Make sure min and max bounds work for normal distribution.
    s = SocialNetwork(n=100, topology='random', weight_dist='normal',
                      weight_min=-1, weight_max=1)
    for i in s:
        for j in s[i]:
            if s[i][j]['weight'] > 1 or s[i][j]['weight'] < -1:
                return False
    return True

def test_2_17():
    # Make sure min and max bounds work for normal distribution with high standard deviation.
    s = SocialNetwork(n=100, topology='random', weight_dist='normal',
                      weight_min=-1, weight_max=1, weight_stdev=.5)
    for i in s:
        for j in s[i]:
            if s[i][j]['weight'] > 1 or s[i][j]['weight'] < -1:
                return False
    return True

def test_2_18():
    # Make sure min and max bounds work for normal distribution with higher standard deviation.
    s = SocialNetwork(n=100, topology='random', weight_dist='normal',
                      weight_min=-1, weight_max=1, weight_stdev=1)
    for i in s:
        for j in s[i]:
            if s[i][j]['weight'] > 1 or s[i][j]['weight'] < -1:
                return False
    return True

def test_2_19():
    # Make sure min and max bounds work for uniform distribution.
    s = SocialNetwork(n=100, topology='random', weight_dist='uniform',
                      weight_min=-1, weight_max=1)
    for i in s:
        for j in s[i]:
            if s[i][j]['weight'] > 1 or s[i][j]['weight'] < -1:
                return False
    return True

def test_2_20():
    # Make sure that constant weights are initialized to default properly
    s = SocialNetwork(n=100, topology='random', weight_dist='constant')
    for i in s:
        for j in s[i]:
            if s[i][j]['weight'] != 1.0:
                return False
    return True

def test_2_21():
    # Make sure that constant weights are initialized to provided value properly
    s = SocialNetwork(n=100, topology='random', weight_dist='constant', weight_const=5.)
    for i in s:
        for j in s[i]:
            if s[i][j]['weight'] != 5.0:
                return False
    return True

def test_2_22():
    # Make sure that providing a weight constant automatically initializes distribution.
    s = SocialNetwork(n=100, topology='random', weight_const=2)
    if s.prop('weight_dist') != 'constant':
        return False
    for i in s:
        for j in s[i]:
            if s[i][j]['weight'] != 2:
                return False
    return True

def testsuite():
    global PASSCOUNT, TESTCOUNT
    unittest(test_0_00())
    unittest(test_0_01())
    unittest(test_0_02())
    unittest(test_0_03())
    unittest(test_0_04())
    unittest(test_0_05())

    unittest(test_1_00())
    unittest(test_1_01())
    unittest(test_1_02())
    unittest(test_1_03())
    unittest(test_1_04())
    unittest(test_1_05())
    unittest(test_1_06())
    unittest(test_1_07())
    unittest(test_1_08())
    unittest(test_1_09())
    unittest(test_1_10())
    unittest(test_1_11())
    # unittest(test_1_12())
    # unittest(test_1_13())
    # unittest(test_1_14())
    # unittest(test_1_15())
    # unittest(test_1_16())
    # unittest(test_1_17())
    # unittest(test_1_18())
    # unittest(test_1_19())
    # unittest(test_1_20())

    unittest(test_2_00())
    unittest(test_2_01())
    unittest(test_2_02())
    unittest(test_2_03())
    unittest(test_2_04())
    unittest(test_2_05())
    unittest(test_2_06())
    unittest(test_2_07())
    unittest(test_2_08())
    unittest(test_2_09())
    unittest(test_2_10())
    unittest(test_2_11())
    unittest(test_2_12())
    unittest(test_2_13())
    unittest(test_2_14())
    unittest(test_2_15())
    unittest(test_2_16())
    unittest(test_2_17())
    unittest(test_2_18())
    unittest(test_2_19())
    unittest(test_2_20())
    unittest(test_2_21())
    unittest(test_2_22())

    print(f'{PASSCOUNT} / {TESTCOUNT} tests passed.\n')
    if PASSCOUNT == TESTCOUNT:
        print('++ All current tests have passed.  No errors detected. ++')
    else:
        print('-- It appears that some tests have failed.  Please refer to line numbers above. --')
    print()

testsuite()