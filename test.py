# Test suite for SocialNetwork.py
import networkx

from helpers import *
from SocialNetwork import SocialNetwork
from inspect import getframeinfo, stack

TESTCOUNT = 0
PASSCOUNT = 0
FAILTESTS = []
verbose = True

def unittest(did_pass):
    """
    Print the result of a unit test.
    :param did_pass: a boolean representing the test
    :return: None
    """

    global PASSCOUNT, TESTCOUNT, FAILTESTS
    TESTCOUNT += 1
    caller = getframeinfo(stack()[1][0])
    name = caller.code_context[0].strip()[9:-1]
    linenum = caller.lineno
    if did_pass:
        msg = f'Test {name} at line {linenum} passed.'
        PASSCOUNT += 1
    else:
        msg = f'Test {name} at line {linenum} FAILED.'
        FAILTESTS.append(name)
    if verbose: print(msg)

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
    s = SocialNetwork(n=2, selfloops=False)
    s2 = networkx.Graph()
    s2.add_nodes_from(range(2))
    return s[0] == s2[0]

def test_0_05():
    # Test the __getitem__ method against the graph implementation on non-empty graph.
    s = SocialNetwork(n=2, selfloops=False)
    s.add_edge(0, 1)
    s2 = networkx.Graph()
    s2.add_nodes_from(range(2))
    s2.add_edge(0, 1)
    return s[0] == s2[0]

# The 1 run of tests is for ensuring that basic graph functionality is working correctly.
# See:
#   isgraph(), isdigraph(), ismultigraph(), ismultidigraph()
#   property(), properties()

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
    return s.props('abc', 'xyz') == [10, 20]

def test_1_10():
    # Check that properties() throws error at the correct time.
    try:
        s = SocialNetwork()
        p = s.props('abc')
        return False
    except UndefinedPropertyError: return True
    except: return False

def test_1_11():
    # Make sure that property() overwrites values correctly.
    s = SocialNetwork()
    s.prop(abc=10)
    s.prop(abc=20)
    return s.prop('abc') == 20

def test_1_12():
    # Make sure graphs default to undirected.
    s = SocialNetwork()
    return not s.prop('directed')

def test_1_13():
    # Make sure graphs default to symmetric.
    s = SocialNetwork()
    return s.prop('symmetric')

def test_1_14():
    # Make sure graphs default to having self-loops.
    s = SocialNetwork()
    return s.prop('selfloops')

def test_1_15():
    # Make sure Graphs with no edges that are supposed to have all selfloops actually do.
    s = SocialNetwork(n=5, selfloops=True)
    for i in s:
        if i not in s[i]:
            return False
    return True

def test_1_16():
    # Make sure Graphs with no edges that are not supposed to have selfloops actually don't.
    s = SocialNetwork(n=5, selfloops=False)
    for i in s:
        if i in s[i]:
            return False
    return True

def test_1_17():
    # Make sure that populated Graphs that are supposed to have all selfloops actually do.
    s = SocialNetwork(n=5, topology='random', selfloops=True)
    for i in s:
        if i not in s[i]:
            return False
    return True

def test_1_18():
    # Make sure that populated Graphs that are supposed to have no selfloops actually don't.
    s = SocialNetwork(n=5, topology='random', selfloops=False)
    for i in s:
        if i in s[i]:
            return False
    return True

def test_1_19():
    # Make sure that self-loops aren't removed by disconnect() when selfloops = True in Graph
    s = SocialNetwork(n=1)
    s.disconnect(0, 0)
    return 0 in s[0]

def test_1_20():
    # Make sure that self-loops can't be added by connect() when self-loops = False in Graph.
    s = SocialNetwork(n=1, selfloops=False)
    s.connect(0, 0)
    return 0 not in s[0]

def test_1_21():
    # Make sure DiGraphs with no edges that are supposed to have all selfloops actually do.
    s = SocialNetwork(n=5, directed=True, selfloops=True)
    for i in s:
        if i not in s[i]:
            return False
    return True

def test_1_22():
    # Make sure DiGraphs with no edges that are not supposed to have selfloops actually don't.
    s = SocialNetwork(n=5, directed=True, selfloops=False)
    for i in s:
        if i in s[i]:
            return False
    return True

def test_1_23():
    # Make sure that populated DiGraphs that are supposed to have all selfloops actually do.
    s = SocialNetwork(n=5, directed=True, topology='random', selfloops=True)
    for i in s:
        if i not in s[i]:
            return False
    return True

def test_1_24():
    # Make sure that populated graphs that are supposed to have no selfloops actually don't.
    s = SocialNetwork(n=5, directed=True, topology='random', selfloops=False)
    for i in s:
        if i in s[i]:
            return False
    return True

def test_1_25():
    # Make sure that self-loops aren't removed by disconnect() when selfloops = True in Graph
    s = SocialNetwork(n=1, directed=True)
    s.disconnect(0, 0)
    return 0 in s[0]

def test_1_26():
    # Make sure that self-loops can't be added by connect() when self-loops = False in Graph.
    s = SocialNetwork(n=1, directed=True, selfloops=False)
    s.connect(0, 0)
    return 0 not in s[0]

# The 2 run of tests is for ensuring that functionality around edge weights and other distribution-based attributes
# is working correctly.

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
    return s.prop('weight_mean') == 0. and s.prop('weight_stdev') == 1.

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
    # Make sure that constant weights are initialized to default properly.
    s = SocialNetwork(n=100, topology='random', weight_dist='constant')
    for i in s:
        for j in s[i]:
            if s[i][j]['weight'] != 1.0:
                return False
    return True

def test_2_21():
    # Make sure that constant weights are initialized to provided value properly.
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

def test_2_23():
    # Make sure default resistance distribution is blank.
    # Certainty and confidence call the same method, so they are not tested individually.
    return SocialNetwork().prop('resistance_dist') == '-'

def test_2_24():
    # Make sure default mean and stdev are assigned correctly for default normal distribution.
    s = SocialNetwork(resistance_dist='normal')
    return s.prop('resistance_mean') == .5 and s.prop('resistance_stdev') == .1

def test_2_25():
    # Make sure that distribution parameter is set when a constant is provided.
    s = SocialNetwork(resistance_const=.2)
    return s.prop('resistance_dist') == 'constant'

def test_2_26():
    # Throw error when mean is outside of the range [0, 1] for restricted parameters like resistance.
    try:
        s = SocialNetwork(resistance_dist='normal', resistance_mean=2)
        return False
    except IncompatiblePropertyError:
        return True

def test_2_27():
    # Make sure that user-provided max and min values get overwritten.
    s = SocialNetwork(resistance_dist='normal', resistance_max=5., resistance_min=-5.)
    return s.prop('resistance_max') == 1. and s.prop('resistance_min') == 0.

def test_2_28():
    # Make sure normalized weights get initialized to sum to 1 in Graph.
    s = SocialNetwork(n=10, topology='random', saturation=.2, weight_dist='constant',
                      normalize=True)
    d = s.prop('normalized_weights')
    for i in s:
        if abs(sum(d[i].values()) - 1.) > .000001:
            return False
    return True

def test_2_29():
    # Make sure normalized weights get initialized to sum to 1 in DiGraph.
    s = SocialNetwork(n=10, topology='random', saturation=.2, weight_dist='constant',
                      normalize=True, directed=True)
    d = s.prop('normalized_weights')
    for i in s:
        if abs(sum(d[i].values()) - 1.) > .000001:
            return False
    return True

def test_2_30():
    # Make sure normalized weights get initialized to sum to 1 in MultiGraph.
    s = SocialNetwork(n=10, topology='random', saturation=.2, weight_dist='constant',
                      normalize=True, multiedge=True)
    d = s.prop('normalized_weights')
    for i in s:
        if abs(sum(d[i].values()) - 1.) > .000001:
            return False
    return True

def test_2_31():
    # Make sure normalized weights get initialized to sum to 1 in MultiDiGraph.
    s = SocialNetwork(n=10, topology='random', saturation=.2, weight_dist='constant',
                      normalize=True, multiedge=True, directed=True)
    d = s.prop('normalized_weights')
    for i in s:
        if abs(sum(d[i].values()) - 1.) > .000001:
            return False
    return True

def test_2_32():
    # Make sure normalized weights get initialized to sum to 1 in asymmetric Graph.
    s = SocialNetwork(n=10, topology='random', saturation=.2, weight_dist='constant',
                      normalize=True, symmetric=False)
    d = s.prop('normalized_weights')
    for i in s:
        if abs(sum(d[i].values()) - 1.) > .000001:
            return False
    return True

def test_2_33():
    # Make sure normalized weights get initialized to sum to 1 in asymmetric DiGraph.
    s = SocialNetwork(n=10, topology='random', saturation=.2, weight_dist='constant',
                      normalize=True, directed=True, symmetric=False)
    d = s.prop('normalized_weights')
    for i in s:
        if abs(sum(d[i].values()) - 1.) > .000001:
            return False
    return True

def test_2_34():
    # Make sure normalized weights get initialized to sum to 1 in asymmetric MultiGraph.
    s = SocialNetwork(n=10, topology='random', saturation=.2, weight_dist='constant',
                      normalize=True, multiedge=True, symmetric=False)
    d = s.prop('normalized_weights')
    for i in s:
        if abs(sum(d[i].values()) - 1.) > .000001:
            return False
    return True

def test_2_35():
    # Make sure normalized weights get initialized to sum to 1 in asymmetric MultiDiGraph.
    s = SocialNetwork(n=10, topology='random', saturation=.2, weight_dist='constant',
                      normalize=True, multiedge=True, directed=True, symmetric=False)
    d = s.prop('normalized_weights')
    for i in s:
        if abs(sum(d[i].values()) - 1.) > .000001:
            return False
    return True

def test_2_36():
    # Check that normalized weights are updated appropriately when edges are added in Graph.
    s = SocialNetwork(n=2, weight_dist='constant', normalize=True)
    s.connect(0, 1)
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1]

def test_2_37():
    # Check that normalized weights are updated appropriately when edges are deleted in Graph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True)
    s.connect(0, 1)
    s.connect(0, 2)
    s.disconnect(0, 1)
    d = s.prop('normalized_weights')
    return 1 not in d[0] and 0 not in d[1] and 2 in d[0] and 0 in d[2]

def test_2_38():
    # Check that normalized weights are updated appropriately when edges are added in DiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, normalize=True)
    s.connect(0, 1)
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1]

def test_2_39():
    # Check that normalized weights are updated appropriately when edges are added in asymmetric DiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, symmetric=False, normalize=True)
    s.connect(0, 1)
    d = s.prop('normalized_weights')
    return 1 not in d[0] and 0 in d[1]

def test_2_40():
    # Check that normalized weights are updated appropriately when edges are added in asymmetric DiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, symmetric=False, normalize=True)
    s.connect(0, 1)
    s.connect(1, 0)
    s.disconnect(0, 1)
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 not in d[1]

def test_2_41():
    # Check that normalized weights are updated appropriately when edges are added in MultiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1)
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1]

def test_2_42():
    # Check that normalized weights are updated appropriately when edges are added in MultiGraph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.connect(0, 2)
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1] and 2 in d[0] and 0 in d[2] and d[0][1] > d[0][2]

def test_2_43():
    # Check that normalized weights are updated appropriately when edges are deleted in MultiGraph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1)
    s.connect(0, 2)
    s.disconnect(0, 1)
    d = s.prop('normalized_weights')
    return 1 not in d[0] and 0 not in d[1] and 2 in d[0] and 0 in d[2]

def test_2_44():
    # Check that normalized weights are updated appropriately when edges are deleted in MultiGraph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.connect(0, 2)
    s.disconnect(0, 1, 'a')
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1] and 2 in d[0] and 0 in d[2] and d[0][1] == d[0][2]

def test_2_45():
    # Check that normalized weights are updated appropriately when edges are deleted in MultiGraph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.connect(0, 2)
    s.disconnect(0, 1, 'a')
    s.disconnect(0, 1, 'b')
    d = s.prop('normalized_weights')
    return 1 not in d[0] and 0 not in d[1] and 2 in d[0] and 0 in d[2]

def test_2_46():
    # Check that normalized weights are updated appropriately when edges are added in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1)
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1] and d[1][0] == d[0][1]

def test_2_47():
    # Check that normalized weights are updated appropriately when edges are added in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1)
    s.connect(0, 1)
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1] and d[1][0] == d[0][1]

def test_2_48():
    # Check that normalized weights are updated appropriately when edges are deleted in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1)
    s.disconnect(0, 1)
    d = s.prop('normalized_weights')
    return 1 not in d[0] and 0 not in d[1]

def test_2_49():
    # Check that normalized weights are updated appropriately when edges are deleted in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1)
    d = s.prop('normalized_weights')
    return 1 not in d[0] and 0 not in d[1]

def test_2_50():
    # Check that normalized weights are updated appropriately when edges are deleted in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1, 'a')
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1] and d[1][0] == d[0][1]

def test_2_51():
    # Check that normalized weights are updated appropriately when edges are added in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1)
    s.connect(1, 0)
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1] and d[1][0] == d[0][1]

def test_2_52():
    # Check that normalized weights are updated appropriately when edges are added in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1)
    s.connect(0, 1)
    s.connect(1, 0)
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1] and d[1][0] > d[0][1]

def test_2_53():
    # Check that normalized weights are updated appropriately when edges are deleted in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1)
    s.disconnect(0, 1)
    d = s.prop('normalized_weights')
    return 1 not in d[0] and 0 not in d[1]

def test_2_54():
    # Check that normalized weights are updated appropriately when edges are deleted in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1)
    s.connect(0, 1)
    s.disconnect(0, 1)
    d = s.prop('normalized_weights')
    return 1 not in d[0] and 0 not in d[1]

def test_2_55():
    # Check that normalized weights are updated appropriately when edges are deleted in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1, 'a')
    s.connect(1, 0, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1, 'a')
    d = s.prop('normalized_weights')
    return 1 in d[0] and 0 in d[1] and d[0][1] == d[1][0]

# The 3 run of tests is for ensuring that functionality around edge addition and removal is working correctly.

def test_3_00():
    # Test edge addition in Graph.
    s = SocialNetwork(n=2)
    s.connect(0, 1)
    return 1 in s[0] and 0 in s[1]

def test_3_01():
    # Test edge addition in symmetric DiGraph.
    s = SocialNetwork(n=2, directed=True)
    s.connect(0, 1)
    return 1 in s[0] and 0 in s[1]

def test_3_02():
    # Test edge addition in asymmetric DiGraph.
    s = SocialNetwork(n=2, directed=True, symmetric=False)
    s.connect(0, 1)
    return 1 in s[0] and 0 not in s[1]

def test_3_03():
    # Test edge deletion in Graph.
    s = SocialNetwork(n=2)
    s.connect(0, 1)
    s.disconnect(0, 1)
    return 1 not in s[0] and 0 not in s[1]

def test_3_04():
    # Test edge deletion in symmetric DiGraph.
    s = SocialNetwork(n=2, directed=True)
    s.connect(0, 1)
    s.disconnect(0, 1)
    return 1 not in s[0] and not 0 in s[1]

def test_3_05():
    # Test edge deletion in asymmetric DiGraph.
    s = SocialNetwork(n=2, directed=True, symmetric=False)
    s.connect(0, 1)
    s.connect(1, 0)
    s.disconnect(1, 0)
    return 1 in s[0] and 0 not in s[1]

def test_3_06():
    # Add edge without label when trying to use label in Graph.
    s = SocialNetwork(n=2)
    s.connect(0, 1, 'a')
    return 1 in s[0]

def test_3_07():
    # Add edge without label when trying to use label in Graph.
    s = SocialNetwork(n=2)
    s.connect(0, 1, 'a')
    return 1 in s[0]

def test_3_08():
    # Add edge without label when trying to use label in symmetric DiGraph.
    s = SocialNetwork(n=2, directed=True)
    s.connect(0, 1, 'a')
    return 1 in s[0] and 0 in s[1]

def test_3_09():
    # Add edge without label when trying to use label in symmetric DiGraph.
    s = SocialNetwork(n=2, directed=True, symmetric=False)
    s.connect(0, 1, 'a')
    return 1 in s[0] and 0 not in s[1]

def test_3_10():
    # Make sure no problems arise when trying to add a duplicate edge in Graph.
    s = SocialNetwork(n=2, selfloops=False)
    s.connect(0, 1)
    s.connect(0, 1)
    return len(s.edges) == 1

def test_3_11():
    # Make sure no problems arise when trying to add a duplicate edge in Graph.
    s = SocialNetwork(n=2, selfloops=False)
    s.connect(0, 1)
    s.connect(1, 0)
    return len(s.edges) == 1

def test_3_12():
    # Make sure no problems arise when trying to add a duplicate edge in asymmetric DiGraph.
    s = SocialNetwork(n=2, directed=True, selfloops=False, symmetric=False)
    s.connect(0, 1)
    s.connect(0, 1)
    return len(s.edges) == 1

def test_3_13():
    # Make sure no problems arise when trying to add a duplicate edge in symmetric DiGraph.
    s = SocialNetwork(n=2, directed=True, selfloops=False)
    s.connect(0, 1)
    s.connect(0, 1)
    s.connect(1, 0)
    return len(s.edges) == 2

def test_3_14():
    # Throw an error when trying to remove a nonexistent edge from a Graph.
    s = SocialNetwork(n=2)
    try:
        s.disconnect(0, 1)
        return False
    except networkx.NetworkXError:
        return True

def test_3_15():
    # Throw an error when trying to remove a nonexistent edge from a DiGraph.
    s = SocialNetwork(n=2, directed=True)
    try:
        s.disconnect(0, 1)
        return False
    except networkx.NetworkXError:
        return True

def test_3_16():
    # Test edge addition in MultiGraph.
    s = SocialNetwork(n=2, multiedge=True)
    s.connect(0, 1)
    return 1 in s[0] and 0 in s[1]

def test_3_17():
    # Test edge addition in MultiGraph.
    s = SocialNetwork(n=2, multiedge=True)
    s.connect(0, 1)
    return len(s[0][1]) == 1

def test_3_18():
    # Test multiedge addition in MultiGraph.
    s = SocialNetwork(n=2, multiedge=True)
    s.connect(0, 1)
    s.connect(0, 1)
    return len(s[0][1]) == 2

def test_3_19():
    # Test edge addition in symmetric MultiDiGraph.
    s = SocialNetwork(n=2, multiedge=True, directed=True)
    s.connect(0, 1)
    return 1 in s[0] and 0 in s[1]

def test_3_20():
    # Test multiedge addition in symmetric MultiDiGraph.
    s = SocialNetwork(n=2, multiedge=True, directed=True, selfloops=False)
    s.connect(0, 1)
    s.connect(0, 1)
    return len(s[0][1]) == 2 and len(s[1][0]) == 2

def test_3_21():
    # Test multiedge addition in symmetric MultiDiGraph.
    s = SocialNetwork(n=2, multiedge=True, directed=True, selfloops=False, symmetric=False)
    s.connect(0, 1)
    s.connect(0, 1)
    return len(s[0][1]) == 2 and (0 not in s[1])

def test_3_22():
    # Test edge deletion in MultiGraph.
    s = SocialNetwork(n=2, multiedge=True)
    s.connect(0, 1, 'a')
    s.disconnect(0, 1, 'a')
    return 1 not in s[0] and 0 not in s[1]

def test_3_23():
    # Test single multiedge deletion in MultiGraph.
    s = SocialNetwork(n=2, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1, 'a')
    return 'a' not in s[0][1] and 'b' in s[0][1]

def test_3_24():
    # Test all multiedge deletion in MultiGraph.
    s = SocialNetwork(n=2, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1)
    return 1 not in s[0]

def test_3_25():
    # Test edge deletion in symmetric MultiDiGraph.
    s = SocialNetwork(n=2, directed=True, multiedge=True)
    s.connect(0, 1, 'a')
    s.disconnect(0, 1, 'a')
    return 1 not in s[0] and 0 not in s[1]

def test_3_26():
    # Test single multiedge deletion in symmetric MultiDiGraph.
    s = SocialNetwork(n=2, directed=True, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1, 'a')
    return 'a' not in s[0][1] and 'b' in s[0][1] and 'a' not in s[1][0] and 'b' in s[1][0]

def test_3_27():
    # Test all multiedge deletion in symmetric MultiDiGraph.
    s = SocialNetwork(n=2, directed=True, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1)
    return 1 not in s[0] and 0 not in s[1]

def test_3_28():
    # Test edge deletion in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, directed=True, multiedge=True, symmetric=False)
    s.connect(0, 1, 'a')
    s.connect(1, 0, 'a')
    s.disconnect(0, 1, 'a')
    return 1 not in s[0] and 0 in s[1]

def test_3_29():
    # Test single multiedge deletion in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, directed=True, multiedge=True, symmetric=False)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1, 'a')
    return 'a' not in s[0][1] and 'b' in s[0][1] and 0 not in s[1]

def test_3_30():
    # Test all multiedge deletion in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, directed=True, multiedge=True, symmetric=False)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.connect(1, 0, 'a')
    s.connect(1, 0, 'b')
    s.disconnect(0, 1)
    return 1 not in s[0] and len(s[1][0]) == 2

def test_3_31():
    # Make sure edges don't get added with connection probability = 0 in Graph
    s = SocialNetwork(n=2)
    s.connect(0, 1, p=0)
    return 1 not in s[0] and 0 not in s[1]

def test_3_32():
    # Make sure edges don't get deleted with disconnection probability = 0 in Graph
    s = SocialNetwork(n=2)
    s.connect(0, 1)
    s.disconnect(0, 1, p=0)
    return 1 in s[0] and 0 in s[1]

def test_3_33():
    # Make sure edges don't get added with connection probability = 0 in symmetric DiGraph
    s = SocialNetwork(n=2, directed=True)
    s.connect(0, 1, p=0)
    return 1 not in s[0] and 0 not in s[1]

def test_3_34():
    # Make sure edges don't get deleted with disconnection probability = 0 in symmetric DiGraph
    s = SocialNetwork(n=2, directed=True)
    s.connect(0, 1)
    s.disconnect(0, 1, p=0)
    return 1 in s[0] and 0 in s[1]

def test_3_35():
    # Make sure edges don't get added with connection probability = 0 in asymmetric DiGraph
    s = SocialNetwork(n=2, directed=True, symmetric=False)
    s.connect(0, 1, p=0)
    return 1 not in s[0]

def test_3_36():
    # Make sure edges don't get deleted with disconnection probability = 0 in asymmetric DiGraph
    s = SocialNetwork(n=2, directed=True, symmetric=False)
    s.connect(0, 1)
    s.disconnect(0, 1, p=0)
    return 1 in s[0]

def test_3_37():
    # Make sure edges don't get added with connection probability = 0 in MultiGraph
    s = SocialNetwork(n=2, multiedge=True)
    s.connect(0, 1, p=0)
    return 1 not in s[0] and 0 not in s[1]

def test_3_38():
    # Make sure edges don't get deleted with disconnection probability = 0 in MultiGraph
    s = SocialNetwork(n=2, multiedge=True)
    s.connect(0, 1)
    s.disconnect(0, 1, p=0)
    return 1 in s[0] and 0 in s[1]

def test_3_39():
   # Make sure edges don't get added with connection probability = 0 in symmetric MultiDiGraph
   s = SocialNetwork(n=2, multiedge=True, directed=True)
   s.connect(0, 1, p=0)
   return 1 not in s[0] and 0 not in s[1]

def test_3_40():
    # Make sure edges don't get deleted with disconnection probability = 0 in symmetric MultiDiGraph
    s = SocialNetwork(n=2, multiedge=True, directed=True)
    s.connect(0, 1)
    s.disconnect(0, 1, p=0)
    return 1 in s[0] and 0 in s[1]

def test_3_41():
   # Make sure edges don't get added with connection probability = 0 in asymmetric MultiDiGraph
   s = SocialNetwork(n=2, multiedge=True, directed=True, symmetric=False)
   s.connect(0, 1, p=0)
   return 1 not in s[0]

def test_3_42():
    # Make sure edges don't get deleted with disconnection probability = 0 in asymmetric MultiDiGraph
    s = SocialNetwork(n=2, multiedge=True, directed=True, symmetric=False)
    s.connect(0, 1)
    s.disconnect(0, 1, p=0)
    return 1 in s[0]

def test_3_43():
    # Throw an error when trying to remove a nonexistent edge from a MultiGraph.
    s = SocialNetwork(n=2, multiedge=True)
    try:
        s.disconnect(0, 1)
        return False
    except KeyError:
        return True

def test_3_44():
    # Throw an error when trying to remove a nonexistent edge from a symmetric MultiDiGraph.
    s = SocialNetwork(n=2, multiedge=True, directed=True)
    try:
        s.disconnect(0, 1)
        return False
    except KeyError:
        return True

def test_3_45():
    # Throw an error when trying to remove a nonexistent edge from an asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, multiedge=True, directed=True, symmetric=False)
    try:
        s.disconnect(0, 1)
        return False
    except KeyError:
        return True

def test_3_46():
    # Throw an error when trying to delete a single multiedge with the wrong label in a MultiGraph.
    s = SocialNetwork(n=2, multiedge=True)
    s.connect(0, 1, 'a')
    e = s.disconnect(0, 1, 'b')
    if not e:
        return True
    return False

# The 4 run of tests is for ensuring that functionality around masks is working correctly.

def test_4_01():
    # Check that masks are updated appropriately when edges are added in Graph.
    s = SocialNetwork(n=2, weight_dist='constant', normalize=True)
    s.connect(0, 1)
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1]

def test_4_02():
    # Check that masks are updated appropriately when edges are deleted in Graph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True)
    s.connect(0, 1)
    s.connect(0, 2)
    s.disconnect(0, 1)
    d = s.prop('masks')
    return 1 not in d[0] and 0 not in d[1] and 2 in d[0] and 0 in d[2]

def test_4_03():
    # Check that masks are updated appropriately when edges are added in DiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, normalize=True)
    s.connect(0, 1)
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1]

def test_4_04():
    # Check that masks are updated appropriately when edges are added in asymmetric DiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, symmetric=False, normalize=True)
    s.connect(0, 1)
    d = s.prop('masks')
    return 1 not in d[0] and 0 in d[1]

def test_4_05():
    # Check that masks are updated appropriately when edges are added in asymmetric DiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, symmetric=False, normalize=True)
    s.connect(0, 1)
    s.connect(1, 0)
    s.disconnect(0, 1)
    d = s.prop('masks')
    return 1 in d[0] and 0 not in d[1]

def test_4_06():
    # Check that masks are updated appropriately when edges are added in MultiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1)
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1]

def test_4_07():
    # Check that masks are updated appropriately when edges are added in MultiGraph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.connect(0, 2)
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1] and 2 in d[0] and 0 in d[2]

def test_4_08():
    # Check that masks are updated appropriately when edges are deleted in MultiGraph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1)
    s.connect(0, 2)
    s.disconnect(0, 1)
    d = s.prop('masks')
    return 1 not in d[0] and 0 not in d[1] and 2 in d[0] and 0 in d[2]

def test_4_09():
    # Check that masks are updated appropriately when edges are deleted in MultiGraph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.connect(0, 2)
    s.disconnect(0, 1, 'a')
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1] and 2 in d[0] and 0 in d[2]

def test_4_10():
    # Check that masks are updated appropriately when edges are deleted in MultiGraph.
    s = SocialNetwork(n=3, weight_dist='constant', normalize=True, multiedge=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.connect(0, 2)
    s.disconnect(0, 1, 'a')
    s.disconnect(0, 1, 'b')
    d = s.prop('masks')
    return 1 not in d[0] and 0 not in d[1] and 2 in d[0] and 0 in d[2]

def test_4_11():
    # Check that masks are updated appropriately when edges are added in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1)
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1]

def test_4_12():
    # Check that masks are updated appropriately when edges are added in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1)
    s.connect(0, 1)
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1]

def test_4_13():
    # Check that masks are updated appropriately when edges are deleted in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1)
    s.disconnect(0, 1)
    d = s.prop('masks')
    return 1 not in d[0] and 0 not in d[1]

def test_4_14():
    # Check that masks are updated appropriately when edges are deleted in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1)
    d = s.prop('masks')
    return 1 not in d[0] and 0 not in d[1]

def test_4_15():
    # Check that masks are updated appropriately when edges are deleted in MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True)
    s.connect(0, 1, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1, 'a')
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1]

def test_4_16():
    # Check that masks are updated appropriately when edges are added in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1)
    s.connect(1, 0)
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1]

def test_4_17():
    # Check that masks are updated appropriately when edges are added in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1)
    s.connect(0, 1)
    s.connect(1, 0)
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1]

def test_4_18():
    # Check that masks are updated appropriately when edges are added in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1)
    d = s.prop('masks')
    return 1 not in d[0] and 0 in d[1]

def test_4_19():
    # Check that masks are updated appropriately when edges are deleted in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1)
    s.disconnect(0, 1)
    d = s.prop('masks')
    return 1 not in d[0] and 0 not in d[1]

def test_4_20():
    # Check that masks are updated appropriately when edges are deleted in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1)
    s.connect(0, 1)
    s.disconnect(0, 1)
    d = s.prop('masks')
    return 1 not in d[0] and 0 not in d[1]

def test_4_21():
    # Check that masks are updated appropriately when edges are deleted in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, weight_dist='constant', directed=True, multiedge=True, normalize=True, symmetric=False)
    s.connect(0, 1, 'a')
    s.connect(1, 0, 'a')
    s.connect(0, 1, 'b')
    s.disconnect(0, 1, 'a')
    d = s.prop('masks')
    return 1 in d[0] and 0 in d[1]

def test_4_22():
    # Make sure masks get initialized properly when hidden.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden')
    s.connect(0, 1)
    v = s.get_view(1, 0)
    return sum(v) == 0

def test_4_23():
    # Make sure masks get initialized properly when visible.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible')
    s.connect(0, 1)
    v = s.get_view(1, 0)
    d = s.prop('diffusion_space')[0]
    return v == d

def test_4_24():
    # Make sure reveal works properly in Graph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden')
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][1] and sum(v2) == 0

def test_4_25():
    # Make sure reveal works properly in Graph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden')
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    s.reveal(1, 0, 2)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][1] and sum(v2) == s.prop('diffusion_space')[1][2]

def test_4_26():
    # Make sure reveal works properly in DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', directed=True)
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][1] and sum(v2) == 0

def test_4_27():
    # Make sure reveal works properly in DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', directed=True)
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    s.reveal(1, 0, 2)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][1] and sum(v2) == s.prop('diffusion_space')[1][2]

def test_4_28():
    # Make sure reveal works properly in asymmetric DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', directed=True, symmetric=False)
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    v1 = s.get_view(1, 0)
    return sum(v1) == s.prop('diffusion_space')[0][1] and 1 not in s.prop('masks')[0]

def test_4_29():
    # Make sure reveal works properly in asymmetric DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', directed=True, symmetric=False)
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    s.reveal(1, 0, 2)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][1] and sum(v2) == 0

def test_4_30():
    # Make sure reveal works properly in MultiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True)
    s.connect(0, 1)
    s.reveal(0, 1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][0] and sum(v2) == 0

def test_4_31():
    # Make sure reveal works properly in MultiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True)
    s.connect(0, 1)
    s.reveal(0, 1, 0)
    s.reveal(1, 0, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][0] and sum(v2) == s.prop('diffusion_space')[1][0]

def test_4_32():
    # Make sure reveal works properly in MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True, directed=True)
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][1] and sum(v2) == 0

def test_4_33():
    # Make sure reveal works properly in MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True, directed=True)
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    s.reveal(1, 0, 2)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][1] and sum(v2) == s.prop('diffusion_space')[1][2]

def test_4_34():
    # Make sure reveal works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True, directed=True, symmetric=False)
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    v1 = s.get_view(1, 0)
    return sum(v1) == s.prop('diffusion_space')[0][1] and 1 not in s.prop('masks')[0]

def test_4_35():
    # Make sure reveal works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True, directed=True, symmetric=False)
    s.connect(0, 1)
    s.reveal(0, 1, 1)
    s.reveal(1, 0, 2)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == s.prop('diffusion_space')[0][1] and sum(v2) == 0

def test_4_36():
    # Make sure reveal_all works properly in Graph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden')
    s.connect(0, 1)
    s.reveal_all(0, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == 0

def test_4_37():
    # Make sure reveal_all works properly in Graph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden')
    s.connect(0, 1)
    s.reveal_all(0, 1)
    s.reveal_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == sum(s.prop('diffusion_space')[1])

def test_4_38():
    # Make sure reveal_all works properly in DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', directed=True)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == 0

def test_4_39():
    # Make sure reveal_all works properly in DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', directed=True)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    s.reveal_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == sum(s.prop('diffusion_space')[1])

def test_4_40():
    # Make sure reveal_all works properly in asymmetric DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', directed=True, symmetric=False)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    v1 = s.get_view(1, 0)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and 1 not in s.prop('masks')[0]

def test_4_41():
    # Make sure reveal_all works properly in asymmetric DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', directed=True, symmetric=False)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    s.reveal_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == 0

def test_4_42():
    # Make sure reveal_all works properly in MultiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == 0

def test_4_43():
    # Make sure reveal_all works properly in MultiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    s.reveal_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == sum(s.prop('diffusion_space')[1])

def test_4_44():
    # Make sure reveal_all works properly in MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True, directed=True)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == 0

def test_4_45():
    # Make sure reveal_all works properly in MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True, directed=True)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    s.reveal_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == sum(s.prop('diffusion_space')[1])

def test_4_46():
    # Make sure reveal_all works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True, directed=True, symmetric=False)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    v1 = s.get_view(1, 0)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and 1 not in s.prop('masks')[0]

def test_4_47():
    # Make sure reveal_all works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='hidden', multiedge=True, directed=True, symmetric=False)
    s.connect(0, 1)
    s.reveal_all(0, 1)
    s.reveal_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == sum(s.prop('diffusion_space')[0]) and sum(v2) == 0

def test_4_48():
    # Make sure hide works properly in Graph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible')
    s.connect(0, 1)
    s.hide(0, 1, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    d1 = s.prop('diffusion_space')[1]
    return sum(v1) == sum(d0) - d0[1] and sum(v2) == sum(d1)

def test_4_49():
    # Make sure hide works properly in Graph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible')
    s.connect(0, 1)
    s.hide(0, 1, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    d1 = s.prop('diffusion_space')[1]
    return sum(v1) == sum(d0) - d0[1] and sum(v2) == sum(d1)

def test_4_50():
    # Make sure hide works properly in DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', directed=True)
    s.connect(0, 1)
    s.hide(0, 1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    d1 = s.prop('diffusion_space')[1]
    return sum(v1) == sum(d0) - d0[0] and sum(v2) == sum(d1)

def test_4_51():
    # Make sure hide works properly in DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', directed=True)
    s.connect(0, 1)
    s.hide(0, 1, 1)
    s.hide(1, 0, 2)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    d1 = s.prop('diffusion_space')[1]
    return sum(v1) == sum(d0) - d0[1] and sum(v2) == sum(d1) - d1[2]

def test_4_52():
    # Make sure hide works properly in asymmetric DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', directed=True, symmetric=False)
    s.connect(0, 1)
    s.hide(0, 1, 1)
    v1 = s.get_view(1, 0)
    d0 = s.prop('diffusion_space')[0]
    return sum(v1) == sum(d0) - d0[1] and 1 not in s.prop('masks')[0]

def test_4_53():
    # Make sure hide works properly in asymmetric DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', directed=True, symmetric=False)
    s.connect(0, 1)
    s.hide(0, 1, 1)
    s.hide(1, 0, 2)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    return sum(v1) == sum(d0) - d0[1] and sum(v2) == 0

def test_4_54():
    # Make sure hide works properly in MultiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True)
    s.connect(0, 1)
    s.hide(0, 1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    d1 = s.prop('diffusion_space')[1]
    return sum(v1) == sum(d0) - d0[0] and sum(v2) == sum(d1)

def test_4_55():
    # Make sure hide works properly in MultiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True)
    s.connect(0, 1)
    s.hide(0, 1, 0)
    s.hide(1, 0, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    d1 = s.prop('diffusion_space')[1]
    return sum(v1) == sum(d0) - d0[0] and sum(v2) == sum(d1) - d1[0]

def test_4_56():
    # Make sure hide works properly in MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True, directed=True)
    s.connect(0, 1)
    s.hide(0, 1, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    d1 = s.prop('diffusion_space')[1]
    return sum(v1) == sum(d0) - d0[1] and sum(v2) == sum(d1)

def test_4_57():
    # Make sure hide works properly in MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True, directed=True)
    s.connect(0, 1)
    s.hide(0, 1, 1)
    s.hide(1, 0, 2)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    d1 = s.prop('diffusion_space')[1]
    return sum(v1) == sum(d0) - d0[1] and sum(v2) == sum(d1) - d1[2]

def test_4_58():
    # Make sure hide works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True, directed=True, symmetric=False)
    s.connect(0, 1)
    s.hide(0, 1, 1)
    v1 = s.get_view(1, 0)
    d0 = s.prop('diffusion_space')[0]
    return sum(v1) == sum(d0) - d0[1] and 1 not in s.prop('masks')[0]

def test_4_59():
    # Make sure hide works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True, directed=True, symmetric=False)
    s.connect(0, 1)
    s.hide(0, 1, 1)
    s.hide(1, 0, 2)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    d0 = s.prop('diffusion_space')[0]
    d1 = s.prop('diffusion_space')[1]
    return sum(v1) == sum(d0) - d0[1] and sum(v2) == 0

def test_4_60():
    # Make sure hide_all works properly in Graph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible')
    s.connect(0, 1)
    s.hide_all(0, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == sum(s.prop('diffusion_space')[1])

def test_4_61():
    # Make sure hide_all works properly in Graph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible')
    s.connect(0, 1)
    s.hide_all(0, 1)
    s.hide_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == 0

def test_4_62():
    # Make sure hide_all works properly in DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', directed=True)
    s.connect(0, 1)
    s.hide_all(0, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == sum(s.prop('diffusion_space')[1])

def test_4_63():
    # Make sure hide_all works properly in DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', directed=True)
    s.connect(0, 1)
    s.hide_all(0, 1)
    s.hide_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == 0

def test_4_64():
    # Make sure hide_all works properly in asymmetric DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', directed=True, symmetric=False)
    s.connect(0, 1)
    s.hide_all(0, 1)
    v1 = s.get_view(1, 0)
    return sum(v1) == 0 and 1 not in s.prop('masks')[0]

def test_4_65():
    # Make sure hide_all works properly in asymmetric DiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', directed=True, symmetric=False)
    s.connect(0, 1)
    s.hide_all(0, 1)
    s.hide_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == 0

def test_4_66():
    # Make sure hide_all works properly in MultiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True)
    s.connect(0, 1)
    s.hide_all(0, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == sum(s.prop('diffusion_space')[1])

def test_4_67():
    # Make sure hide_all works properly in MultiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True)
    s.connect(0, 1)
    s.hide_all(0, 1)
    s.hide_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == 0

def test_4_68():
    # Make sure hide_all works properly in MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True, directed=True)
    s.connect(0, 1)
    s.hide_all(0, 1)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == sum(s.prop('diffusion_space')[1])

def test_4_69():
    # Make sure hide_all works properly in MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True, directed=True)
    s.connect(0, 1)
    s.hide_all(0, 1)
    s.hide_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == 0

def test_4_70():
    # Make sure hide_all works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True, directed=True, symmetric=False)
    s.connect(0, 1)
    s.hide_all(0, 1)
    v1 = s.get_view(1, 0)
    return sum(v1) == 0 and 1 not in s.prop('masks')[0]

def test_4_71():
    # Make sure hide_all works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=2, num_dimensions=3, visibility='visible', multiedge=True, directed=True, symmetric=False)
    s.connect(0, 1)
    s.hide_all(0, 1)
    s.hide_all(1, 0)
    v1 = s.get_view(1, 0)
    v2 = s.get_view(0, 1)
    return sum(v1) == 0 and sum(v2) == 0

def test_4_72():
    # Make sure broadcast works properly in Graph.
    s = SocialNetwork(n=5, num_dimensions=3, visibility='hidden')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v = s.get_view(v, 0)
        if v[0] != cmp or v[1] != 0 or v[2] != 0:
            return False
    return True

def test_4_73():
    # Make sure broadcast works properly in DiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, visibility='hidden')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != cmp or v1[1] != 0 or v1[2] != 0:
            return False
        if v2[0] != 0 or v2[1] != 0 or v2[2] != 0:
            return False
    return True

def test_4_74():
    # Make sure broadcast works properly in DiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, visibility='hidden')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    for v in nbrs:
        s.broadcast(v, 1)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != cmp or v1[1] != 0 or v1[2] != 0:
            return False
        if v2[0] != 0 or v2[1] != s.prop('diffusion_space')[v][1] or v2[2] != 0:
            return False
    return True

def test_4_75():
    # Make sure broadcast works properly in asymmetric DiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, visibility='hidden', symmetric=False)
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != cmp or v1[1] != 0 or v1[2] != 0:
            return False
        if v2[0] != 0 or v2[1] != 0 or v2[2] != 0:
            return False
    return True

def test_4_76():
    # Make sure broadcast works properly in asymmetric DiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, visibility='hidden', symmetric=False)
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    for v in nbrs:
        s.broadcast(v, 1)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != cmp or v1[1] != 0 or v1[2] != 0:
            return False
        if v2[0] != 0 or v2[1] != 0 or v2[2] != 0:
            return False
    return True

def test_4_77():
    # Make sure broadcast works properly in MultiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, multiedge=True, visibility='hidden')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v = s.get_view(v, 0)
        if v[0] != cmp or v[1] != 0 or v[2] != 0:
            return False
    return True

def test_4_78():
    # Make sure broadcast works properly in MultiDiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, multiedge=True, visibility='hidden')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != cmp or v1[1] != 0 or v1[2] != 0:
            return False
        if v2[0] != 0 or v2[1] != 0 or v2[2] != 0:
            return False
    return True

def test_4_79():
    # Make sure broadcast works properly in MultiDiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, multiedge=True, visibility='hidden')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    for v in nbrs:
        s.broadcast(v, 1)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != cmp or v1[1] != 0 or v1[2] != 0:
            return False
        if v2[0] != 0 or v2[1] != s.prop('diffusion_space')[v][1] or v2[2] != 0:
            return False
    return True

def test_4_80():
    # Make sure broadcast works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, multiedge=True, visibility='hidden', symmetric=False)
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != cmp or v1[1] != 0 or v1[2] != 0:
            return False
        if v2[0] != 0 or v2[1] != 0 or v2[2] != 0:
            return False
    return True

def test_4_81():
    # Make sure broadcast works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, multiedge=True, visibility='hidden', symmetric=False)
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.broadcast(0, 0)
    for v in nbrs:
        s.broadcast(v, 1)
    cmp = s.prop('diffusion_space')[0][0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != cmp or v1[1] != 0 or v1[2] != 0:
            return False
        if v2[0] != 0 or v2[1] != 0 or v2[2] != 0:
            return False
    return True

def test_4_82():
    # Make sure nocast works properly in Graph.
    s = SocialNetwork(n=5, num_dimensions=3, visibility='visible')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v = s.get_view(v, 0)
        if v[0] != 0 or v[1] != d0[1] or v[2] != d0[2]:
            return False
    return True

def test_4_83():
    # Make sure nocast works properly in DiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, visibility='visible')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != 0 or v1[1] != d0[1] or v1[2] != d0[2]:
            return False
        if sum(v2) != sum(s.prop('diffusion_space')[v]):
            return False
    return True

def test_4_84():
    # Make sure nocast works properly in DiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, visibility='visible')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    for v in nbrs:
        s.nocast(v, 1)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != 0 or v1[1] != d0[1] or v1[2] != d0[2]:
            return False
        if v2[0] != s.prop('diffusion_space')[v][0] or v2[1] != 0 or v2[2] != s.prop('diffusion_space')[v][2]:
            return False
    return True

def test_4_85():
    # Make sure nocast works properly in asymmetric DiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, visibility='visible', symmetric=False)
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != 0 or v1[1] != d0[1] or v1[2] != d0[2]:
            return False
        if sum(v2) != 0:
            return False
    return True

def test_4_86():
    # Make sure nocast works properly in asymmetric DiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, visibility='visible', symmetric=False)
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    for v in nbrs:
        s.nocast(v, 1)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != 0 or v1[1] != d0[1] or v1[2] != d0[2]:
            return False
        if sum(v2) != 0:
            return False
    return True

def test_4_87():
    # Make sure nocast works properly in MultiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, multiedge=True, visibility='visible')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v = s.get_view(v, 0)
        if v[0] != 0 or v[1] != d0[1] or v[2] != d0[2]:
            return False
    return True

def test_4_88():
    # Make sure nocast works properly in MultiDiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, multiedge=True, visibility='visible')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != 0 or v1[1] != d0[1] or v1[2] != d0[2]:
            return False
        if sum(v2) != sum(s.prop('diffusion_space')[v]):
            return False
    return True
#
def test_4_89():
    # Make sure nocast works properly in MultiDiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, multiedge=True, visibility='visible')
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    for v in nbrs:
        s.nocast(v, 1)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != 0 or v1[1] != d0[1] or v1[2] != d0[2]:
            return False
        if sum(v2) != sum(s.prop('diffusion_space')[v]) - s.prop('diffusion_space')[v][1]:
            return False
    return True

def test_4_90():
    # Make sure nocast works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, multiedge=True, visibility='visible', symmetric=False)
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != 0 or v1[1] != d0[1] or v1[2] != d0[2]:
            return False
        if sum(v2) != 0:
            return False
    return True

def test_4_91():
    # Make sure nocast works properly in asymmetric MultiDiGraph.
    s = SocialNetwork(n=5, num_dimensions=3, directed=True, multiedge=True, visibility='visible', symmetric=False)
    nbrs = [1, 2, 3]
    for v in nbrs:
        s.connect(0, v)
    s.nocast(0, 0)
    for v in nbrs:
        s.nocast(v, 1)
    d0 = s.prop('diffusion_space')[0]
    for v in nbrs:
        v1 = s.get_view(v, 0)
        v2 = s.get_view(0, v)
        if v1[0] != 0 or v1[1] != d0[1] or v1[2] != d0[2]:
            return False
        if sum(v2) != 0:
            return False
    return True

def testsuite():
    global PASSCOUNT, TESTCOUNT, FAILTESTS

    # test_0_*
    unittest(test_0_00())
    unittest(test_0_01())
    unittest(test_0_02())
    unittest(test_0_03())
    unittest(test_0_04())
    unittest(test_0_05())

    # test_1_*
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
    unittest(test_1_12())
    unittest(test_1_13())
    unittest(test_1_14())
    unittest(test_1_15())
    unittest(test_1_16())
    unittest(test_1_17())
    unittest(test_1_18())
    unittest(test_1_19())
    unittest(test_1_20())
    unittest(test_1_21())
    unittest(test_1_22())
    unittest(test_1_23())
    unittest(test_1_24())
    unittest(test_1_25())
    unittest(test_1_26())

    # test_2_*
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
    unittest(test_2_23())
    unittest(test_2_24())
    unittest(test_2_25())
    unittest(test_2_26())
    unittest(test_2_27())
    unittest(test_2_28())
    unittest(test_2_29())
    unittest(test_2_30())
    unittest(test_2_31())
    unittest(test_2_32())
    unittest(test_2_33())
    unittest(test_2_34())
    unittest(test_2_35())
    unittest(test_2_36())
    unittest(test_2_37())
    unittest(test_2_38())
    unittest(test_2_39())
    unittest(test_2_40())
    unittest(test_2_41())
    unittest(test_2_42())
    unittest(test_2_43())
    unittest(test_2_44())
    unittest(test_2_45())
    unittest(test_2_46())
    unittest(test_2_47())
    unittest(test_2_48())
    unittest(test_2_49())
    unittest(test_2_50())
    unittest(test_2_51())
    unittest(test_2_52())
    unittest(test_2_53())
    unittest(test_2_54())
    unittest(test_2_55())

    # test_3_*
    unittest(test_3_00())
    unittest(test_3_01())
    unittest(test_3_02())
    unittest(test_3_03())
    unittest(test_3_04())
    unittest(test_3_05())
    unittest(test_3_06())
    unittest(test_3_07())
    unittest(test_3_08())
    unittest(test_3_09())
    unittest(test_3_10())
    unittest(test_3_11())
    unittest(test_3_12())
    unittest(test_3_13())
    unittest(test_3_14())
    unittest(test_3_15())
    unittest(test_3_16())
    unittest(test_3_17())
    unittest(test_3_18())
    unittest(test_3_19())
    unittest(test_3_20())
    unittest(test_3_21())
    unittest(test_3_22())
    unittest(test_3_23())
    unittest(test_3_24())
    unittest(test_3_25())
    unittest(test_3_26())
    unittest(test_3_27())
    unittest(test_3_28())
    unittest(test_3_29())
    unittest(test_3_30())
    unittest(test_3_31())
    unittest(test_3_32())
    unittest(test_3_33())
    unittest(test_3_34())
    unittest(test_3_35())
    unittest(test_3_36())
    unittest(test_3_37())
    unittest(test_3_38())
    unittest(test_3_39())
    unittest(test_3_40())
    unittest(test_3_41())
    unittest(test_3_42())
    unittest(test_3_43())
    unittest(test_3_44())
    unittest(test_3_45())
    unittest(test_3_46())

    # test_4_*
    unittest(test_4_01())
    unittest(test_4_02())
    unittest(test_4_03())
    unittest(test_4_04())
    unittest(test_4_05())
    unittest(test_4_06())
    unittest(test_4_07())
    unittest(test_4_08())
    unittest(test_4_09())
    unittest(test_4_10())
    unittest(test_4_11())
    unittest(test_4_12())
    unittest(test_4_13())
    unittest(test_4_14())
    unittest(test_4_15())
    unittest(test_4_16())
    unittest(test_4_17())
    unittest(test_4_18())
    unittest(test_4_19())
    unittest(test_4_20())
    unittest(test_4_21())
    unittest(test_4_22())
    unittest(test_4_23())
    unittest(test_4_24())
    unittest(test_4_25())
    unittest(test_4_26())
    unittest(test_4_27())
    unittest(test_4_28())
    unittest(test_4_29())
    unittest(test_4_30())
    unittest(test_4_31())
    unittest(test_4_32())
    unittest(test_4_33())
    unittest(test_4_34())
    unittest(test_4_35())
    unittest(test_4_36())
    unittest(test_4_37())
    unittest(test_4_38())
    unittest(test_4_39())
    unittest(test_4_40())
    unittest(test_4_41())
    unittest(test_4_42())
    unittest(test_4_43())
    unittest(test_4_44())
    unittest(test_4_45())
    unittest(test_4_46())
    unittest(test_4_47())
    unittest(test_4_48())
    unittest(test_4_49())
    unittest(test_4_50())
    unittest(test_4_51())
    unittest(test_4_52())
    unittest(test_4_53())
    unittest(test_4_54())
    unittest(test_4_55())
    unittest(test_4_56())
    unittest(test_4_57())
    unittest(test_4_58())
    unittest(test_4_59())
    unittest(test_4_60())
    unittest(test_4_61())
    unittest(test_4_62())
    unittest(test_4_63())
    unittest(test_4_64())
    unittest(test_4_65())
    unittest(test_4_66())
    unittest(test_4_67())
    unittest(test_4_68())
    unittest(test_4_69())
    unittest(test_4_70())
    unittest(test_4_71())
    unittest(test_4_72())
    unittest(test_4_73())
    unittest(test_4_74())
    unittest(test_4_75())
    unittest(test_4_76())
    unittest(test_4_77())
    unittest(test_4_78())
    unittest(test_4_79())
    unittest(test_4_80())
    unittest(test_4_81())
    unittest(test_4_82())
    unittest(test_4_83())
    unittest(test_4_84())
    unittest(test_4_85())
    unittest(test_4_86())
    unittest(test_4_87())
    unittest(test_4_88())
    unittest(test_4_89())
    unittest(test_4_90())
    unittest(test_4_91())


    # print message
    print(f'{PASSCOUNT} / {TESTCOUNT} tests passed.\n')
    if PASSCOUNT == TESTCOUNT:
        print('++ All current tests have passed.  No errors detected. ++')
    else:
        print('-- It appears that some tests have failed.  Please refer to line numbers above. --')
        print('Tests failed:')
        for t in FAILTESTS:
            print(f'  {t}')
    print()

testsuite()