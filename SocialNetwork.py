# Social Network Class

'''
This iteration of the SocialNetwork class is designed to work as seamlessly with NetworkX as possible.
Previous designs made heavy use of that library's functionality, but this design is meant to remain as
closely intertwined with the underlying models as possible.
'''
import networkx
import networkx as nx
import numpy as np

from warnings import warn

from helpers import *

# A dictionary to hold verifier objects for each named property.
# These objects throw an error if the user provided an invalid value.

PROPSELECT = {# used in initial setup of graph structure
              'n': POSNUM,                    # number of nodes
              'directed': TF,                 # directed edges?
              'multiedge': TF,                # multiedges allowed?
              'symmetric': TF,                # directed edges must be symmetric?
              'selfloops': TF,                # self-loops included?
              'saturation': PROB,             # average percent of the network each node is connected to
              'topology': ['', 'complete', 'cycle', 'random',
                           'scale free', 'small world', 'star'],

              # used to govern edge weight distributions
              'weight_dist': DISTS,
              'weight_mean': SYMNUM,
              'weight_stdev': SYMNUM,
              'weight_const': SYMNUM,
              # weights are not restricted between 0 and 1 or between -1 and 1, so we need explicit boundaries
              'weight_min': SYMNUM,
              'weight_max': SYMNUM,
              }

PROPDEFAULTS = {'n': 0,
                'directed': False,
                'multiedge': False,
                'symmetric': True,
                'selfloops': True,
                'topology': '',
                'saturation': .1,
                'weight_dist': 'constant',
                'weight_const': 1.,
                'weight_mean': .5,
                'weight_stdev': .1,
                'weight_min': 0.,
                'weight_max': 1.,
                }

class SocialNetwork:

    def __init__(self, **kwargs):
        '''
        Initializes a SocialNetwork object based on the given properties.

        :param kwargs: any number of named properties

        * List of named properties accepted by the class: *
        _______________________________________________
        - 'directed': bool - - - whether edges are directed or not
        - 'multiedge': bool - - - whether multiedges are allowed or not
        - 'selfloops': bool - - - whether selfloops are present
        - 'symmetric': bool - - - whether edge symmetry is enforced or not


        * List of common NetworkX methods that can be used on SocialNetwork instances: *

        Method Name                                                                          | Limited to
        _____________________________________________________________________________________|_________________________
        edges()                                                                              | all
        neighbors()                                                                          | Graph, MultiGraph
        predecessors                                                                         | DiGraph, MultiDiGraph
        successors                                                                           | DiGraph, MultiDiGraph
        nodes()                                                                              | all

        This class is designed to conditionally inherit from one of the four graph classes from NetworkX:
        Graph, DiGraph, MultiGraph, and MultiDiGraph.  A SocialNetwork object can be any one of these,
        and therefore any method from the class of your choosing can be called directly on a SocialNetwork
        instance.  For example, using

        s = SocialNetwork()
        s.add_nodes_from(range(10))

        will create a NetworkX Graph instance with nodes numbered 0 through 9.  Note that not all NetworkX
        graph classes have all methods in common.  For example, undirected graphs (either multiedged or not)
        have a method called neighbors(), whereas directed graphs have methods called successors() and
        predecessors() to reflect the directionality of the graph.  Calling a method on a SocialNetwork
        instance that is not defined in the preferred base class will throw an error.  User beware.
        '''

        self._iter_idx = 0

        kwargs = self._validate_properties(**kwargs)
        self._init_instance(**kwargs)
        self.prop(**kwargs)
        self._generate_edges()
        self._generate_edge_weights()

    def __getattr__(self, name):
        '''
        General method to call base-class versions of methods when none exist for this class.

        :param name: name of method or attribute
        :return: the return value of the underlying method or attribute
        '''
        return self.instance.__getattribute__(name)

    def __getitem__(self, name):
        '''
        General method to access object indexing of underlying class.

        :param name: key for indexing
        :return: the return value of indexing the underlying object
        '''
        return self.instance.__getitem__(name)

    def __iter__(self):
        '''

        :return:
        '''
        for i in self.instance:
            yield i

    def __len__(self):
        '''

        :return:
        '''
        return self.number_of_nodes()

    def _init_instance(self, **kwargs):
        '''
        Initializes a NetworkX graph instance of the appropriate type as the base class.

        :param dir: whether or not the graph is directed
        :param mult: whether or not the graph allows multiedges
        :return: None
        '''

        # Set up base class depending on input parameters
        dir, mult = kwargs['directed'], kwargs['multiedge']
        if not dir and not mult:
            self.instance = nx.Graph()
            self.prop(graphtype='graph')
        elif dir and not mult:
            self.instance = nx.DiGraph()
            self.prop(graphtype='digraph')
        elif not dir and mult:
            self.instance = nx.MultiGraph()
            self.prop(graphtype='multigraph')
        elif dir and mult:
            self.instance = nx.MultiDiGraph()
            self.prop(graphtype='multidigraph')
        else:
            raise AttributeError('Encountered a problem while creating graph instance.  Aborting.')

    def _check_property(self, name, val):
        '''

        :param name: the name of the property to check
        :param val: the value provided for that property
        :return: True if the value is acceptable, otherwise False
        '''
        return val in PROPSELECT[name] if name in PROPSELECT else True

    def _has_property(self, name):
        '''

        :param name:
        :return:
        '''
        return name in self.instance.graph

    def _get_property(self, name):
        '''
        Retrieves the property value of the given name

        :param name: the name of the property
        :return: the value stored under that name
        '''
        if name not in self.instance.graph:
            raise KeyError(f'No property named [{name}] found.')
        return self.instance.graph[name]

    def _set_property(self, name, value):
        '''
        Sets property name/value pair in self.instance.graph, where self.instance is a NetworkX object.

        :param name: the name of the property
        :param value: the value to set for the property by that name
        :return: None
        '''
        self.instance.graph[name] = value

    def _validate_properties(self, **kwargs):
        """
        Check kwargs for standard properties, and fill in default values if needed.

        :return: None
        """

        kwargs = self._validate_custom_range_distribution('weight', **kwargs)
        kwargs = self._validate_probability_distribution('resistance', **kwargs)
        kwargs = self._validate_probability_distribution('uncertainty', **kwargs)

        for key in PROPDEFAULTS:

            if key not in kwargs:
                kwargs[key] = PROPDEFAULTS[key]
            elif not self._check_property(key, kwargs[key]):
                val = kwargs[key]
                msg = f'Invalid value for property [{key}]: {val} (type: {type(val)})'
                msg += f'\nValue must be in: {PROPSELECT[key]}'
                raise InvalidPropertyError(msg)

        return kwargs

    def _validate_custom_range_distribution(self, tag, **kwargs):
        '''

        :param tag:
        :return:
        '''
        # Take care of specific special cases -- e.g. if a tag_min and tag_max
        # are provided, but not a tag_mean, then tag_mean will be set to their
        # average.

        # If no distribution is given, set to blank unless a constant is provided.
        if f'{tag}_dist' not in kwargs:
            if 'weight_const' in kwargs:
                kwargs[f'{tag}_dist'] = 'constant'
            else:
                kwargs[f'{tag}_dist'] = '-'
                return kwargs

        hasmin = f'{tag}_min' in kwargs
        hasmax = f'{tag}_max' in kwargs
        hasmean = f'{tag}_mean' in kwargs
        hasstdev = f'{tag}_stdev' in kwargs

        # Only distribution name is provided.  Set all values to default
        # Uniform: min 0, max 1
        # Normal: mean 0, stdev 1, min -inf, max inf
        if not any([hasmin, hasmax, hasmean, hasstdev]):
            if kwargs[f'{tag}_dist'] == 'uniform':
                kwargs[f'{tag}_min'] = 0
                kwargs[f'{tag}_max'] = 1
            elif kwargs[f'{tag}_dist'] == 'normal':
                kwargs[f'{tag}_min'] = MININT_32
                kwargs[f'{tag}_max'] = MAXINT_32
                kwargs[f'{tag}_mean'] = 0
                kwargs[f'{tag}_stdev'] = 1
            return kwargs

        # Either a min or max value is defined, but not both, raise an error
        if (hasmin and not hasmax) or (hasmax and not hasmin):
            raise IncompatiblePropertyError(f'Minimum and maximum {tag} must be defined together.')

        # If neither min nor max values are defined, set them to maximal values by default
        if not (hasmin or hasmax):
            if kwargs[f'{tag}_dist'] == 'normal':
                kwargs[f'{tag}_min'] = MININT_32
                kwargs[f'{tag}_max'] = MAXINT_32
            elif kwargs[f'{tag}_dist'] == 'uniform':
                kwargs[f'{tag}_min'] = 0
                kwargs[f'{tag}_max'] = 1

        minval, maxval = kwargs[f'{tag}_min'], kwargs[f'{tag}_max']

        # Both min and max values are defined
        if hasmin and hasmax:

            # If min > max raise an error
            if minval > maxval:
                raise IncompatiblePropertyError(f'Minimum {tag} cannot be greater than maximum {tag}.')

        # Mean value is defined
        if hasmean:

            # If mean > max or mean < min, raise an error
            if kwargs[f'{tag}_mean'] not in Bound(minval, maxval):
                raise IncompatiblePropertyError(f'Mean {tag} must be between minimum and maximum.')

        # No mean value provided; set equal to (min + max) / 2 for normal distribution
        else:
            if kwargs[f'{tag}_dist'] == 'normal':
                kwargs[f'{tag}_mean'] = (minval + maxval) / 2

        # No standard deviation is provided
        if not hasstdev:

            # If no min or max values were provided, do not assume standard deviation; raise an error for normal dist
            if kwargs[f'{tag}_dist'] == 'normal':
                if not (hasmin or hasmax):
                    raise IncompatiblePropertyError('Must provide maximum and minimum weights and/or std. dev.')

                # Otherwise, set standard deviation to 10% of the distance between min and max
                else:
                    kwargs[f'{tag}_stdev'] = (maxval - minval) / 10

        return kwargs

    def _validate_probability_distribution(self, tag, **kwargs):
        '''

        :param tag:
        :return:
        '''
        # Take care of specific special cases -- e.g. if a tag_min and tag_max
        # are provided, but not a tag_mean, then tag_mean will be set to their
        # average.

        # If no distribution is given, set to blank
        if f'{tag}_dist' not in kwargs:
            if 'weight_const' in kwargs:
                kwargs[f'{tag}_dist'] = 'constant'
            else:
                kwargs[f'{tag}_dist'] = '-'
                return kwargs

        # Automatically set min and max to 0 and 1
        # Check for mean and stdev for normal distribution
        hasmean = f'{tag}_mean' in kwargs
        hasstdev = f'{tag}_stdev' in kwargs

        kwargs[f'{tag}_min'] = 0
        kwargs[f'{tag}_max'] = 1

        minval, maxval = 0, 1

        if kwargs['weight_dist'] == 'normal':
            # Mean value is defined
            if hasmean:

                # If mean > max or mean < min, raise an error
                if kwargs[f'{tag}_mean'] not in PROB:
                    raise IncompatiblePropertyError(f'Mean {tag} must be between minimum and maximum.')

            # No mean value provided; set equal to (min + max) / 2 for normal distribution
            else:
                kwargs[f'{tag}_mean'] = .5

            # No standard deviation is provided; set to .1
            if not hasstdev:
                kwargs[f'{tag}_stdev'] = .1

        return kwargs

    def _generate_nodes(self):
        '''
        Create the appropriate number of nodes and add them to the graph.

        :return: None
        '''
        self.add_nodes_from(range(self.prop('n')))

    def _generate_edges(self):
        '''
        Generate randomly distributed edges according to the property 'topology'.

        :return: None
        '''
        topology = self.prop('topology')
        n = self.prop('n')
        sat = self.prop('saturation')
        edges = list()

        self._generate_nodes()

        # Blank graph.
        if topology == '':
            return

        # Erdos-Renyi random graph
        elif topology == 'random':
            if self.prop('symmetric') and self.prop('directed'):
                edges = nx.erdos_renyi_graph(n, sat / 2, directed=True).edges()
            else:
                edges = nx.erdos_renyi_graph(n, sat, directed=self.prop('directed')).edges()

        # Barabasi-Albert scale free graph
        elif topology == 'scale free':
            edges = nx.scale_free_graph(n).edges()

        # Watts-Strogatz small world graph
        elif topology == 'small world':
            if not self._has_property('rewire'): self.prop(rewire=.1)
            if self.prop('directed'):
                edges = nx.watts_strogatz_graph(n, max(int(sat * n * 2), 2), self.prop('rewire')).edges()
            else:
                edges = nx.watts_strogatz_graph(n, max(int(sat * n), 2), self.prop('rewire')).edges()

        # Star graph
        elif topology == 'star':
            edges = nx.star_graph(n).edges()

        # Complete graph
        elif topology == 'complete':
            edges = nx.complete_graph(n).edges()

        # Cycle or ring
        elif topology == 'cycle':
            edges = nx.cycle_graph(n).edges()

        # Add generated edges to graph structure
        for (u, v) in edges:
            # print(u, v, "start of edges")
            self.add_edge(u, v)

            if self.prop('symmetric') and self.prop('directed'):
                self.add_edge(v, u)

        if self.prop('selfloops'):
            for i in range(self.prop('n')):
                self.add_edge(i, i)

    def _generate_edge_weights(self):
        '''

        :return:
        '''

        # TODO: this needs some work to make sure that weird situations don't happen,
        #  like weight_mean < weight_min or weight_mean > weight_max

        d = self.prop('weight_dist')
        e = list(self.edges())
        if d == 'constant':
            self._init_constant_edge_weights(e)
        elif d == 'uniform':
            self._init_uniform_edge_weights(e)
        elif d == 'normal':
            self._init_normal_edge_weights(e)

    def _init_constant_edge_weights(self, e):
        '''

        :return:
        '''
        for i, j in e:
            self[i][j]['weight'] = self.prop('weight_const')

    def _init_uniform_edge_weights(self, e):
        '''

        :return:
        '''
        lo, hi = self.props('weight_min', 'weight_max')
        weights = np.random.uniform(lo, hi, len(e))
        # weights = uniform.rvs(loc=lo, scale=hi-lo, size=len(e))

        for i, (u, v) in enumerate(e):
            self.instance[u][v]['weight'] = weights[i]

    def _init_normal_edge_weights(self, e):
        '''

        :return:
        '''
        lo, hi = self.props('weight_min', 'weight_max')
        mu, sigma = self.props('weight_mean', 'weight_stdev')
        weights = np.random.normal(mu, sigma, len(e))
        for i in range(len(weights)):
            if weights[i] < lo: weights[i] = lo
            if weights[i] > hi: weights[i] = hi

        for i, (u, v) in enumerate(e):
            self.instance[u][v]['weight'] = weights[i]

    def property(self, arg=None, **kwargs):
        '''
        Multi-purpose getter, setter, and display method.
        Usages:
            No arguments - prints a list of all named properties and their values
            One optional positional argument - returns the value of the property by the given name, error if none exists
            One or more keyword arguments - sets property values of all provided named properties
            Positional argument and keyword arguments can be used in the same method call.  It is generally recommended
            that calls to property be used EITHER as a getter OR as a setter, but the two functionalities can be
            invoked simultaneously.

            CANNOT accept multiple arguments when used as a getter.  Returns exactly one value.
            DOES NOT do any checks before overwriting a previously defined property value.

        :param arg: a single property name; None by default
        :param kwargs: one or more named properties with values
        :return: a single property value if used as a getter; None if used as display or setter only
        '''

        # No input.  Print all property name/value pairs.
        if not (arg or kwargs):
            for key in self.instance.graph.keys():
                print(f'{key}: {self.prop(key)}')

        # Caller provided a dict of named properties.  Set the values of each one.
        # WARNING: WILL OVERWRITE ANY EXISTING PROPERTY VALUE IF YOU TELL IT TO.
        if kwargs:
            # Provide a warning if any values are about to be overwritten
            if any([key in self.instance.graph for key in kwargs]):
                warn(f'One or more existing graph properties will be overwritten.')
            # Set new value(s)
            for key in kwargs:
                self.instance.graph[key] = kwargs[key]

        # Caller provided a single getter argument.  Try to return the property.
        # Throw an error if it doesn't exist.
        if arg:
            if arg not in self.instance.graph:
                raise KeyError(f'No property named [{arg}] found.')
            return self.instance.graph[arg]

    def properties(self, *args, **kwargs):
        '''
        Wrapper for self.property().  Returns a list of property values, one for each input property name.

        :param arg: any number of property names
        :param kwargs: one or more named properties with values
        :return: a list of property values if used as a getter; None if used as display or setter only
        '''
        if not (args or kwargs):
            self.property()
        if kwargs:
            self.property(**kwargs)
        if args:
            ret = [self.property(arg) for arg in args if self._has_property(arg)]
            if len(ret) != len(args):
                raise UndefinedPropertyError('One or more requested properties do not exist.')
            return [self.property(arg) for arg in args]

    def isgraph(self):
        '''
        Checks if object is built as nx.Graph.

        :return: True if built from nx.Graph, False otherwise
        '''
        return self.prop('graphtype') == 'graph'

    def isdigraph(self):
        '''
        Checks if object is built as nx.DiGraph.

        :return: True if built from nx.DiGraph, False otherwise
        '''
        return self.prop('graphtype') == 'digraph'

    def ismultigraph(self):
        '''
        Checks if object is built as nx.MultiGraph.

        :return: True if built from nx.MultiGraph, False otherwise
        '''
        return self.prop('graphtype') == 'multigraph'

    def ismultidigraph(self):
        '''
        Checks if object is built as nx.MultiDiGraph.

        :return: True if built from nx.MultiDiGraph, False otherwise
        '''
        return self.prop('graphtype') == 'multidigraph'

    # Method aliases
    prop = property
    props = properties