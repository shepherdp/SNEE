# Social Network Class

'''
This iteration of the SocialNetwork class is designed to work as seamlessly with NetworkX as possible.
Previous designs made heavy use of that library's functionality, but this design is meant to remain as
closely intertwined with the underlying models as possible.
'''
import networkx as nx
import numpy as np
import random

from copy import deepcopy
from warnings import warn

from helpers import *

# Dictionary to hold parameter definitions for different agent types.
# Fields are:
#   homophily: determines an agent's satisfaction based on neighbors
#              Options: 'homophilic', 'heterophilic', 'halfphilic', or float representing
#                       optimal agreement percentage
#   conformity: determines an agent's update trajectory
#               Options: 'conforming', 'rebelling', 'gravit_attract', 'gravit_attract_repel'
#   bound: determines whether confidence bound is used in opinion update
#          Options: True, False
#   update_method: determines how an agent updates its opinion
#   num_influencers: determines how many neighbors are considered when updating
#                    Options: integer
#                             if integer > number of neighbors
default = {'homophily': 'homophilic',
           'conformity': 'conforming',
           'bound': False,
           'update_method': False,
           'num_influencers': 'max',
           'sim_max': 1.
           }

MODELS = {'default': default}

# A dictionary to hold verifier objects for each named property.
# These objects throw an error if the user provided an invalid value.

PROPSELECT = {# used in initial setup of graph structure
              'n': POSNUM,                    # number of nodes
              'directed': TF,                 # directed edges?
              'multiedge': TF,                # multiedges allowed?
              'symmetric': TF,                # directed edges must be symmetric?
              'selfloops': TF,                # self-loops included?
              'saturation': PROB,             # average percent of the network each node is connected to
              'topology': ['-', 'complete', 'cycle', 'random',
                           'scale free', 'small world', 'star', 'barbell'],

              # used to govern edge weight distributions
              'weight_dist': DISTS,
              'weight_mean': SYMNUM,
              'weight_stdev': SYMNUM,
              'weight_const': SYMNUM,
              # weights are not restricted between 0 and 1 or between -1 and 1, so we need explicit boundaries
              'weight_min': SYMNUM,
              'weight_max': SYMNUM,
              'resistance_dist': DISTS,
              'resistance_min': PROB,
              'resistance_max': PROB,
              'resistance_mean': PROB,
              'resistance_stdev': PROB,
              'resistance_const': PROB,
              'certainty_dist': DISTS,
              'certainty_min': PROB,
              'certainty_max': PROB,
              'certainty_mean': PROB,
              'certainty_stdev': PROB,
              'certainty_const': PROB,
              'confidence_dist': DISTS,
              'confidence_min': PROB,
              'confidence_max': PROB,
              'confidence_mean': PROB,
              'confidence_stdev': PROB,
              'confidence_const': PROB,
              'sim_max': PROB,
              'dimensions': ['continuous', 'binary', 'categorical'],
              'category_transitions': {},
              'num_dimensions': POSNUM,
              'initialize_at_extremes': TF,
              'visibility': ['hidden', 'random', 'visible'],
              'normalize': TF,
              'distance': ['hamming', 'euclidean', 'cosine'],
              'layout': ['spring', 'circle', 'spiral', 'random', 'shell'],
              'num_influencers': POSNUM,
              'num_nodes_update': POSNUM,
              'update_method': ['average', 'weighted average', 'transmission', 'majority', 'voter', 'qvoter'],
              'gravity': SYMBIN,
              'p_update': PROB,
              'p_connect': PROB,
              'num_nodes_update': POSNUM,
              'p_disconnect': PROB,
              'thresh_connect': PROB,
              'thresh_disconnect': PROB,
              'num_nodes_connect': POSNUM,
              'num_nodes_disconnect': POSNUM,
              'num_connections': POSNUM,
              'num_disconnections': POSNUM
              }

PROPDEFAULTS = {'n': 0,
                'directed': False,
                'multiedge': False,
                'symmetric': True,
                'selfloops': True,
                'topology': '-',
                'saturation': .1,
                'weight_dist': '-',
                'weight_const': 1.,
                'weight_mean': 0.,
                'weight_stdev': 1.,
                'weight_min': 0.,
                'weight_max': 1.,
                'resistance_dist': '-',
                'resistance_min': 0.,
                'resistance_max': 1.,
                'resistance_mean': .5,
                'resistance_stdev': .1,
                'resistance_const': 0.,
                'certainty_dist': '-',
                'certainty_min': 0.,
                'certainty_max': 1.,
                'certainty_mean': .5,
                'certainty_stdev': .1,
                'certainty_const': 1.,
                'confidence_dist': '-',
                'confidence_min': 0.,
                'confidence_max': 1.,
                'confidence_mean': .5,
                'confidence_stdev': .1,
                'confidence_const': 1.,
                'num_dimensions': 1,
                'dimensions': 'binary',
                'initialize_at_extremes': True,
                'visibility': 'visible',
                'type_dist': {'default': 1.},
                'agent_models': MODELS,
                'normalized_weights': {},
                'normalize': False,
                'sim_max': 1.,
                'layout': 'spring',
                'gravity': 1.,
                'p_update': 1.,
                'p_connect': 0.,
                'p_disconnect': 0.,
                'num_nodes_update': MAXINT_32,
                'num_nodes_connect': MAXINT_32,
                'num_nodes_disconnect': MAXINT_32,
                'num_connections': 1,
                'num_disconnections': 1,
                'num_influencers': MAXINT_32,
                'thresh_connect': 0,
                'thresh_disconnect': 1,
                'update_method': 'average',
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

        kwargs = self._validate_properties(**kwargs)
        self._init_instance(**kwargs)
        self.prop(**kwargs)
        self._generate_nodes()
        self._init_diffusion_space()
        self._init_masks()
        self._generate_edges()
        if self.prop('normalize'):
            self.prop(normalized_weights={i: {} for i in self.nodes()})
        for i in range(self.number_of_nodes()):
            self._update_normalized_edge_weights(i)
        self._init_certainty()
        self._init_confidence()
        self._init_resistance()
        self._load_agent_models()
        self._init_agent_types()

        # print(kwargs)

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
        Calls parent class to iterate through nodes

        :return: yields each node in the graph
        '''
        for i in self.instance:
            yield i

    def __len__(self):
        '''
        Returns the number of nodes in the current graph.

        :return: number of nodes
        '''
        return self.number_of_nodes()

    def __str__(self):
        '''
        Returns the parent class string representation.

        :return: string representation
        '''
        return self.instance.__str__()

    def _init_instance(self, **kwargs):
        '''
        Initializes a NetworkX graph instance of the appropriate type as the base class.

        :param kwargs: A series of named arguments
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
        Checks whether a given named value falls within the given parameters defined at the top of this file.

        :param name: the name of the property to check
        :param val: the value provided for that property
        :return: True if the value is acceptable, otherwise False
        '''
        return val in PROPSELECT[name] if name in PROPSELECT else True

    def _has_property(self, name):
        '''
        Checks whether the NetworkX graph has a property by a certain name

        :param name: the name of the property
        :return: True if the property exists, False otherwise
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
        if kwargs['weight_dist'] != '-':
            kwargs['normalize'] = True
        kwargs = self._validate_probability_distribution('resistance', **kwargs)
        kwargs = self._validate_probability_distribution('certainty', **kwargs)
        kwargs = self._validate_probability_distribution('confidence', **kwargs)

        # Iterate through default values for properties
        for key in PROPDEFAULTS:

            # If kwargs is missing a property, fill it in
            if key not in kwargs:
                kwargs[key] = deepcopy(PROPDEFAULTS[key])

            # Otherwise, check that the property value is admissible, and if not throw an error
            elif not self._check_property(key, kwargs[key]):
                val = kwargs[key]
                msg = f'Invalid value for property [{key}]: {val} (type: {type(val)})'
                msg += f'\nValue must be in: {PROPSELECT[key]}'
                raise InvalidPropertyError(msg)

        # If any distribution is set to empty, remove the other properties corresponging to it to avoid clutter
        for tag in ['weight', 'resistance', 'certainty', 'confidence']:
            if kwargs[f'{tag}_dist'] in ['-', 'uniform', 'normal']:
                if f'{tag}_const' in kwargs: del kwargs[f'{tag}_const']
            if kwargs[f'{tag}_dist'] in ['-', 'constant']:
                if f'{tag}_min' in kwargs: del kwargs[f'{tag}_min']
                if f'{tag}_max' in kwargs: del kwargs[f'{tag}_max']
            if kwargs[f'{tag}_dist'] in ['-', 'constant', 'uniform']:
                if f'{tag}_min' in kwargs: del kwargs[f'{tag}_mean']
                if f'{tag}_max' in kwargs: del kwargs[f'{tag}_stdev']

        return kwargs

    def _validate_custom_range_distribution(self, tag, **kwargs):
        '''
        Ensures that kwargs dictionary is outfitted with proper parameters to initialize a distribution of values
        over some range that is not 0 to 1.

        :param tag: a string representing the characteristic to validate parameters for
        :param kwargs: a dictionary of named properties
        :return: modified version of kwargs
        '''
        # Take care of specific special cases -- e.g. if a tag_min and tag_max
        # are provided, but not a tag_mean, then tag_mean will be set to their
        # average.

        # If no distribution is given, set to blank unless a constant is provided.
        if f'{tag}_dist' not in kwargs:
            if f'{tag}_const' in kwargs:
                kwargs[f'{tag}_dist'] = 'constant'
            else:
                kwargs[f'{tag}_dist'] = PROPDEFAULTS[f'{tag}_dist']
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
                kwargs[f'{tag}_min'] = PROPDEFAULTS[f'{tag}_min']
                kwargs[f'{tag}_max'] = PROPDEFAULTS[f'{tag}_max']
            elif kwargs[f'{tag}_dist'] == 'normal':
                kwargs[f'{tag}_min'] = MININT_32
                kwargs[f'{tag}_max'] = MAXINT_32
                kwargs[f'{tag}_mean'] = PROPDEFAULTS[f'{tag}_mean']
                kwargs[f'{tag}_stdev'] = PROPDEFAULTS[f'{tag}_stdev']
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
                kwargs[f'{tag}_min'] = PROPDEFAULTS[f'{tag}_min']
                kwargs[f'{tag}_max'] = PROPDEFAULTS[f'{tag}_max']

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
        Ensures that kwargs dictionary is outfitted with proper parameters to initialize a probability distribution.

        :param tag: a string representing the characteristic to validate parameters for
        :param kwargs: a disctionary of named properties
        :return:
        '''
        # Take care of specific special cases -- e.g. if a tag_min and tag_max
        # are provided, but not a tag_mean, then tag_mean will be set to their
        # average.

        # If no distribution is given, set to blank
        if f'{tag}_dist' not in kwargs:
            if f'{tag}_const' in kwargs:
                kwargs[f'{tag}_dist'] = 'constant'
            else:
                kwargs[f'{tag}_dist'] = PROPDEFAULTS[f'{tag}_dist']
                return kwargs

        # Automatically set min and max to 0 and 1
        # Check for mean and stdev for normal distribution
        hasmean = f'{tag}_mean' in kwargs
        hasstdev = f'{tag}_stdev' in kwargs

        kwargs[f'{tag}_min'] = 0
        kwargs[f'{tag}_max'] = 1

        if kwargs[f'{tag}_dist'] == 'normal':
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

        # Blank graph.
        if topology == '-':
            pass

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

        elif topology == 'barbell':
            edges = nx.barbell_graph(int(n/2)-1, 1).edges()

        # Add generated edges to graph structure
        for (u, v) in edges:
            self.connect(u, v)

        # Add self loops if needed
        if self.prop('selfloops'):
            for i in range(self.prop('n')):
                self.connect(i, i)

    def _generate_edge_weights(self, label=None):
        '''
        Generate edge weights based on the distribution and parameters specified by the user.

        :param label: an optional edge label
        :return: None
        '''
        e = list(self.edges())
        d = self.prop('weight_dist')
        if d == 'constant':
            weights = self._generate_constant_values(len(e), 'weight')
        elif d == 'uniform':
            weights = self._generate_uniform_values(len(e), 'weight')
        elif d == 'normal':
            weights = self._generate_normal_values(len(e), 'weight')
        for i in range(len(e)):
            u, v = e[i]
            weight = weights[i]
            self._init_edge_weight(u, v, weight, label)

    def _generate_edge_weight(self, u, v, label=None):
        '''
        Generate edge weights based on the distribution and parameters specified by the user.

        :param u: the source node
        :param v: the destination node
        :param label: an optional edge label
        :return: None
        '''
        d = self.prop('weight_dist')
        if d == '-':
            return
        if d == 'constant':
            weight = self._generate_constant_values(1, 'weight')[0]
        elif d == 'uniform':
            weight = self._generate_uniform_values(1, 'weight')[0]
        elif d == 'normal':
            weight = self._generate_normal_values(1, 'weight')[0]
        self._init_edge_weight(u, v, weight, label)

    def _generate_constant_values(self, numvals, tag):
        '''

        :param numvals:
        :param tag:
        :return:
        '''
        return np.full(numvals, self.prop(f'{tag}_const'))

    def _generate_uniform_values(self, numvals, tag):
        '''

        :param numvals:
        :param tag:
        :return:
        '''
        lo, hi = self.props(f'{tag}_min', f'{tag}_max')
        return np.random.uniform(lo, hi, numvals)

    def _generate_normal_values(self, numvals, tag):
        ret = []
        lo, hi = self.props(f'{tag}_min', f'{tag}_max')
        mu, sigma = self.props(f'{tag}_mean', f'{tag}_stdev')

        # Generate random numbers 50 at a time to fill up the array.
        while True:
            for w in np.random.normal(mu, sigma, 50):
                if len(ret) == numvals:
                    return ret
                if lo <= w <= hi:
                    ret.append(w)

    def _init_edge_weight(self, u, v, weight, label=None):
        '''
        Assign weight to edge (u, v).

        :param u: endpoint of the weighted edge
        :param v: endpoint of the weighted edge
        :param weight: weight for edge u, v
        :param label: an optional edge label
        :return: None
        '''
        if self.prop('multiedge'):
            if label is None:
                label = self.new_edge_key(u, v)
            self[u][v][label]['weight'] = weight
        else:
            self[u][v]['weight'] = weight

    def _update_normalized_edge_weights(self, u):
        '''
        Update the 'normalized_weights' property of node u to reflect the fractional influence of each of its
        neighbors.  Note that in MultiGraphs and MultiDiGraphs, multiple edges from the same neighbor are considered
        in total for that neighbor.

        :param u: the node to update neighbor weights for
        :return: None
        '''

        # Exit if graph doesn't require normalized weights
        if not self.prop('normalize'):
            return

        # Exit if weight distribution is blank
        if self.prop('weight_dist') == '-':
            return

        d = {}
        nbrs = self.neighbors(u) if not self.prop('directed') else self.predecessors(u)

        # Iterate through neighbors of u and add up their respective total weights
        for nbr in nbrs:
            d[nbr] = 0
            if self.prop('multiedge'):
                for label in self[nbr][u]:
                    d[nbr] += self[nbr][u][label]['weight']
            else:
                d[nbr] += self[nbr][u]['weight']

        # Return if no neighbors
        if not d:
            return

        # Assign each neighbor its total weight / the total incoming weight to u
        total = sum(d.values())
        for nbr in d:
            d[nbr] /= total
        self.instance.graph['normalized_weights'][u] = d

    def _init_certainty(self):
        d = self.prop('certainty_dist')
        if d == '-':
            return
        self.prop(certainty={})
        if d == 'constant':
            vals = self._generate_constant_values(self.prop('n'), 'certainty')
        elif d == 'uniform':
            vals = self._generate_uniform_values(self.prop('n'), 'certainty')
        elif d == 'normal':
            vals = self._generate_normal_values(self.prop('n'), 'certainty')
        for i, node in enumerate([key for key in self.nodes]):
            self.instance.graph['certainty'][node] = vals[i]


    def _init_confidence(self):
        d = self.prop('confidence_dist')
        if d == '-':
            return
        self.prop(confidence={})
        if d == 'constant':
            vals = self._generate_constant_values(self.prop('n'), 'confidence')
        elif d == 'uniform':
            vals = self._generate_uniform_values(self.prop('n'), 'confidence')
        elif d == 'normal':
            vals = self._generate_normal_values(self.prop('n'), 'confidence')
        for i, node in enumerate([key for key in self.nodes]):
            self.instance.graph['confidence'][node] = vals[i]

    def _init_resistance(self):
        d = self.prop('resistance_dist')
        if d == '-':
            return
        self.prop(resistance={})
        if d == 'constant':
            vals = self._generate_constant_values(self.prop('n'), 'resistance')
        elif d == 'uniform':
            vals = self._generate_uniform_values(self.prop('n'), 'resistance')
        elif d == 'normal':
            vals = self._generate_normal_values(self.prop('n'), 'resistance')
        for i, node in enumerate([key for key in self.nodes]):
            self.instance.graph['resistance'][node] = vals[i]

    def _init_diffusion_space(self):
        '''
        Initialize a dictionary to represent the diffusion values of nodes in the network.
        Can be any number of dimensions, governed by the 'num_dimensions' property.

        :return: None
        '''
        mynodes = list(self.nodes())
        n = len(mynodes)
        k = self.prop('num_dimensions')
        d = {}
        matrix = []

        # If diffusion space is binary OR it is continuous but needs to be initialized at maximal and minimal values,
        # set all entries to -1 or 1.
        if self.prop('dimensions') == 'binary' or (self.prop('initialize_at_extremes') and
                                                   self.prop('dimensions') == 'continuous'):
            for i in range(k):
                vec = [1 for j in range(n // 2)] + [-1 for j in range(n // 2)]
                while len(vec) < n:
                    vec.append(random.choice([-1, 1]))
                random.shuffle(vec)
                matrix.append(vec)

        # Otherwise, set them to random real values in the range [-1, 1].
        elif self.prop('dimensions') == 'continuous':
            matrix = [[2 * rnd.random() - 1 for j in range(n)]
                      for i in range(k)]

        elif self.prop('dimensions') == 'categorical':
            matrix = self._init_transmission_values()

        matrix = np.array(matrix).T

        row = 0
        for node in mynodes:
            d[node] = list(matrix[row])
            row += 1

        # Set the attribute 'diffusion_space' to a numpy representation of the matrix.
        self.prop(diffusion_space=d)

    def _init_masks(self):
        '''
        Initialize dictionary for visibility values.
        If node i knows what node j's value in dimension k is, then
        self.prop('masks')[i][j][k] is that value, otherwise it is 0.

        :return: None
        '''

        mynodes = list(self.nodes())
        n = len(mynodes)
        k = self.prop('num_dimensions')

        # Set 'masks' attribute to a new dictionary with blank dictionaries for each node.
        self.prop(masks={i: {} for i in range(n)})

        # Each node knows its own diffusion values if selfloops are enforced.
        for node in mynodes:
            if self.prop('selfloops'):
                self.instance.graph['masks'][node][node] = [1 for d in range(k)]

    def _init_transmission_values(self):
        n = self.number_of_nodes()
        K = self.prop('num_dimensions')
        if not self._has_property('category_dist'):
            self.prop(category_dist={'': 1.})

        d = self.prop('category_dist')

        # Make sure type distribution sums to 1
        if abs(sum([d[key] for key in d]) - 1.) > .000001:
            raise InvalidPropertyError('Agent type proportions must sum to 1.')

        matrix = []
        for k in range(K):
            vec = []
            max_num = 0
            max_t = ''
            nums = {}

            for t in d:
                nums[t] = int(d[t] * n)

                # This is just to correct any off-by-ones when we get done filling the vector.
                if nums[t] >= max_num:
                    max_num = nums[t]
                    max_t = t

                # Append nums[t] copies of this category's string representation to the vector.
                for i in range(nums[t]):
                    vec.append(t)

            # Make sure that the rounding above didn't leave us short an element.
            while len(vec) < n:
                nums[max_t] += 1
                vec.append(max_t)

            # Randomly shuffle values.
            rnd.shuffle(vec)
            matrix.append(vec)

        return matrix

    def _init_agent_types(self):
        """
        Distribute agent types among the nodes, governed by the property 'type_dist'.

        :return: None
        """
        mynodes = list(self.nodes())
        n = len(mynodes)
        self.prop(types={})
        types = []
        self.prop(indexes_by_type={})

        # If no distribution is given, make all nodes default types.
        if not self._has_property('type_dist'):
            self.prop(type_dist={'default': 1.})

        max_num = 0
        max_t = ''

        nums = {}
        d = self.prop('type_dist')

        # Make sure type distribution sums to 1
        if abs(sum([d[key] for key in d]) - 1.) > .000001:
            raise InvalidPropertyError('Agent type proportions must sum to 1.')

        # Iterate through provided types.
        for t in d:

            self.instance.graph['indexes_by_type'][t] = []
            nums[t] = int(d[t] * n)

            # This is just to correct any off-by-ones when we get done filling the type vector.
            if nums[t] >= max_num:
                max_num = nums[t]
                max_t = t

            # Append nums[t] copies of this type's string representation to the vector.
            for i in range(nums[t]):
                types.append(t)

        # Make sure that the rounding above didn't leave us short an element.
        while len(types) < n:
            nums[max_t] += 1
            types.append(max_t)

        # Randomly shuffle agent types.
        rnd.shuffle(types)

        # Update indexes_by_type property for quick retrieval of all agents of a particular type.
        for node, idx in zip(mynodes, range(n)):
            t = types[idx]
            self.instance.graph['types'][node] = t
            self.instance.graph['indexes_by_type'][t].append(node)

    def _load_agent_models(self):
        """
        Load each agent type into the relevant list for use when updating diffusion space.

        :return: None
        """
        models = self.prop('agent_models')
        if not models:
            return

        for modelname in models:
            model = models[modelname]
            MODELS[modelname] = model

            if model['homophily'] == 'homophilic':
                HOMOPHILIC.append(modelname)
            elif model['homophily'] == 'heterophilic':
                HETEROPHILIC.append(modelname)
            elif model['homophily'] == 'mesophilic':
                MESOPHILIC.append(modelname)

            if model['conformity'] == 'conforming':
                CONFORMING.append(modelname)
            elif model['conformity'] == 'rebelling':
                REBELLING.append(modelname)

    def get_view(self, u, v):
        '''
        Return a vector representing what u knows of v's diffusion values.

        :param u: the observing node
        :param v: the observed node
        :return: a vector of diffusion values
        '''
        k = self.prop('num_dimensions')

        # Return all zeroes if u and v are not friends
        if u not in self[v]:
            return [0 for i in range(k)]

        v_vals = self.prop('diffusion_space')[v]
        return [v_vals[i] if self.prop('masks')[u][v][i] == 1 else 0 for i in range(k)]

    def get_neighborhood_view(self, u):
        '''
        Return a list of individual neighbor views for node u.

        :param u: the node observing its neighborhood
        :return: a list containing u's view of each of its neighbors
        '''
        return {v: self.get_view(u, v) for v in self[u]} if not self.prop('directed') \
            else {v: self.get_view(u, v) for v in self.predecessors(u)}

    def reset_view(self, u, v, visibility='hidden'):
        '''
        Reset the view agent v has of agent u.

        :param u: The agent who will be viewed differently
        :param v: The agent whose view should be reset
        :param visibility: What parameter to use to determine new visible diffusion values
        :return: None
        '''

        # Do not reset view if u == v or if u and v are not connected
        if u == v or v not in self[u]:
            return

        K = self.prop('num_dimensions')
        sym = all(self.props('directed', 'symmetric')) or (not self.prop('directed'))

        self.instance.graph['masks'][v][u] = [0 for i in range(K)]
        if sym: self.instance.graph['masks'][u][v] = [0 for i in range(K)]

        if visibility == 'random':
            for k in range(K):
                self.instance.graph['masks'][v][u][k] = rnd.choice([0, 1])
                if sym: self.instance.graph['masks'][u][v][k] = rnd.choice([0, 1])
        elif visibility == 'visible':
            for k in range(K):
                self.instance.graph['masks'][v][u][k] = 1
                if sym: self.instance.graph['masks'][u][v][k] = 1

    def hide(self, u, v, k):
        '''
        Node u hides value in dimension k from node v.

        :param u: The hiding node
        :param v: The node being hidden from
        :param k: The dimension to be hidden
        :return: None
        '''
        if v not in self[u] or u == v:
            return
        self.instance.graph['masks'][v][u][k] = 0

    def hide_all(self, u, v):
        '''
        Node u hides all diffusion values from node v.

        :param u: The hiding node
        :param v: The node being hidden from
        :return: None
        '''
        if v not in self[u] or u == v:
            return
        for i in range(self.prop('num_dimensions')):
            self.instance.graph['masks'][v][u][i] = 0

    def reveal(self, u, v, k):
        '''
        Node u reveals value in dimension k from node v.

        :param u: The revealing node
        :param v: The node being revealed to
        :param k: The dimension to be revealed
        :return: None
        '''
        if v not in self[u]:
            return
        self.instance.graph['masks'][v][u][k] = 1

    def reveal_all(self, u, v):
        '''
        Node u reveals all diffusion values to node v.

        :param u: The revealing node
        :param v: The node being revealed to
        :return: None
        '''
        if v not in self[u]:
            return
        for i in range(self.prop('num_dimensions')):
            self.instance.graph['masks'][v][u][i] = 1

    def broadcast(self, u, k):
        '''
        Node u reveals its value in dimension k to all neighbors

        :param u: the broadcasting node
        :param k: the dimension to be broadcast
        :return: None
        '''
        for v in self[u]:
            self.reveal(u, v, k)

    def broadcast_all(self, u):
        '''
        Node u reveals its values in all dimensions to all neighbors

        :param u: the broadcasting node
        :return: None
        '''
        for v in self[u]:
            self.reveal_all(u, v)

    def nocast(self, u, k):
        '''
        Node u hides its value in dimension k from all neighbors

        :param u: the nocasting node
        :param k: the dimension to be nocast
        :return: None
        '''
        for v in self[u]:
            self.hide(u, v, k)

    def nocast_all(self, u):
        '''
        Node u hides its values in all dimensions from all neighbors

        :param u: the nocasting node
        :return: None
        '''
        for v in self[u]:
            self.hide_all(u, v)

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
                warn('One or more existing graph properties will be overwritten.')
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

    def get_influencers(self, u):
        '''

        :param u:
        :return:
        '''
        nbrs = self.get_neighborhood_view(u)
        # nbridxs = list(self.predecessors(u)) if self.prop('directed') else list(self.neighbors(u))
        if u in nbrs:
            del nbrs[u]

        # If using confidence bound, trim out neighbors who do not produce enough reward
        if self.prop('confidence_dist') != '-':
            nbrs = {nbr: self.get_view(u, nbr) for nbr in nbrs if self.reward(u, nbr) >= (1 - self.prop('confidence')[u])
                    or u == nbr}

        if self.prop('num_influencers') > len(nbrs):
            num_influencers = len(nbrs)
        else:
            num_influencers = min(self.prop('num_influencers'), len(nbrs))

        nbrkeys = [key for key in nbrs if key != u]
        random.shuffle(nbrkeys)
        nbrs = {nbr: self.get_view(u, nbr) for nbr in nbrkeys[:num_influencers]}
        if self.prop('selfloops'):
            nbrs[u] = self.get_view(u, u)

        return nbrs

    def get_local_average(self, u, weighted=False):
        """

        :param u: The node whose neighborhood should be averaged
        :param weighted:
        :return:
        """
        nbrs = self.get_influencers(u)

        # Unweighted average
        if self.prop('weight_dist') == '-' or not weighted:
            ret = self.simple_average(nbrs)
        else:
            weights = self.prop('normalized_weights')[u]
            w = {i: weights[i] for i in nbrs}
            total = sum(w.values())
            for key in w:
                w[key] /= total
            ret = self.weighted_average(nbrs, w)
        return ret

    def connect(self, u, v, label=None, p=1., **kwargs):
        '''
        Add an optionally labeled edge from u to v with probability p.

        :param u: The source node of the edge
        :param v: The destination node of the edge
        :param label: The label to apply to the edge -- optional
        :param p: The probability to create the edge
        :param kwargs: Any other named parameters to be passed through to NetworkX
        :return: A list of edges added, either equal to [(u, v)] or [(u, v), (v, u)]
                 List will contain all labeled edges if multiedges are allowed
        '''

        ret = []

        # Do not add the edge if it is a selfloop and those are not allowed
        if (u == v) and (not self.prop('selfloops')):
            return []

        # Add edge with probability p
        if coin_flip(p):

            if (not self.prop('directed')) and (u > v):
                temp = u
                u = v
                v = temp

            # If the object is a MultiGraph or MultiDiGraph, connect a labeled multiedge
            if self.prop('multiedge'):
                ret = self.connect_multi(u, v, label, **kwargs)

            # Otherwise, create an unlabeled edge
            else:
                # Create the edge and add a weight based on the desired weighting scheme

                ret.append((u, v))
                self.add_edge(u, v, **kwargs)
                if 'weight' not in kwargs:
                    self._generate_edge_weight(u, v)

                # Add symmetric edge and generate weight if necessary
                if all(self.props('symmetric', 'directed')):
                    ret.append((v, u))
                    self.add_edge(v, u, **kwargs)
                    if 'weight' not in kwargs:
                        self._generate_edge_weight(v, u)

            # Reset the relevant masks and normalized weights if necessary.
            # These features are 1-per-node, so they can be handled here whether the graph allows multiedges or not.
            self.reset_view(u, v, visibility=self.prop('visibility'))
            self._update_normalized_edge_weights(u)
            self._update_normalized_edge_weights(v)

        return ret

    def connect_multi(self, u, v, label=None, **kwargs):
        '''
        Handles creating a new edge in MultiGraph or MultiDigraph

        :param u: The source node
        :param v: The destination node
        :param label: The label to apply to the edge -- optional
        :param kwargs: Any other named parameters to be passed through to NetworkX
        :return: A list of added edges of the form (u, v, label)
        '''

        ret = []

        # If no label is provided, get a new one
        if label is None:
            label = self.new_edge_key(u, v)

        # Add the edge and generate a weight
        self.add_edge(u, v, label, **kwargs)
        if 'weight' not in kwargs:
            self._generate_edge_weight(u, v, label)
        ret.append((u, v, label))

        # Add a symmetric edge if necessary
        if all(self.props('symmetric', 'directed')):
            self.add_edge(v, u, label, **kwargs)
            if 'weight' not in kwargs:
                self._generate_edge_weight(v, u, label)
            ret.append((v, u, label))

        return ret

    def disconnect(self, u, v, label=None, p=1.):
        '''
        Remove an optionally labeled edge from u to v with probability p.

        :param u: The source node of the edge
        :param v: The destination node of the edge
        :param label: The label of the edge to be removed -- optional
        :param p: The probability to delete the edge
        :return: A list of edges removed, either equal to [(u, v)] or [(u, v), (v, u)]
                 List will contain all labeled edges if multiedges are allowed
        '''

        ret = []

        # If the edge is a selfloop and selfloops must be maintained, return
        if (u == v) and (self.prop('selfloops')):
            return

        if (not self.prop('directed')) and (u > v):
            temp = u
            u = v
            v = temp

        # Remove the edge with probability p
        if coin_flip(p):

            # If the object is a MultiGraph or MultiDiGraph, delete a labeled multiedge
            if self.ismultigraph() or self.ismultidigraph():
                ret = self.disconnect_multi(u, v, label)

            # Otherwise, simply remove the edge, update masks, and if necessary renormalize edge weights
            else:
                ret.append((u, v))
                self.remove_edge(u, v)
                del self.instance.graph['masks'][v][u]
                if self.prop('normalize'):
                    del self.instance.graph['normalized_weights'][v][u]

                # Remove symmetric edge if necessary
                if all(self.props('symmetric', 'directed')):
                    ret.append((v, u))
                    self.remove_edge(v, u)

                # If mask visibility and weights are mutual, then delete the symmetric counterparts
                if all(self.props('symmetric', 'directed')) or not self.prop('directed'):
                    del self.instance.graph['masks'][u][v]
                    if self.prop('normalize'):
                        del self.instance.graph['normalized_weights'][u][v]

            # No need to reset view here because we delete the mask from u to v (and possibly from v to u) above,
            # and no other views are changed by this edge deletion.
            # However, we do need to renormalize edge weights.
            self._update_normalized_edge_weights(u)
            self._update_normalized_edge_weights(v)

        return ret

    def disconnect_multi(self, u, v, label=None):
        '''
        Handles deleting an optionally labeled edge in MultiGraph or MultiDigraph.
        If no label is provided and there are multiple edges from u to v, then all of them will be deleted.

        :param u: The source node
        :param v: The destination node
        :param label: The label of the edge to delete -- optional
        :return: A list of removed edges of the form (u, v, label)
        '''

        ret = []

        # If there is a label provided, only remove the edge with that label
        if label is not None:
            if (u, v, label) not in self.edges:
                return
            ret.append((u, v, label))
            self.remove_edge(u, v, label)

            # Remove symmetric edge if necessary
            if all(self.props('symmetric', 'directed')):
                ret.append((v, u, label))
                self.remove_edge(v, u, label)

        # If no label was provided, assume that all edges from u to v need to be removed.
        else:
            ret = [(u, v, mylabel) for mylabel in self[u][v]]
            if all(self.props('symmetric', 'directed')):
                ret.extend([(v, u, mylabel) for mylabel in self[v][u]])
            # Empty out the edge list from u to v and, if necessary, v to u
            while v in self[u]:
                self.remove_edge(u, v)
                if all(self.props('symmetric', 'directed')):
                    self.remove_edge(v, u)

        # If u and v are now not connected, remove masks and normalized weights
        if v not in self[u]:
            del self.instance.graph['masks'][v][u]
            if self.prop('normalize'):
                del self.instance.graph['normalized_weights'][v][u]

            # If necessary, also remove symmetric mask and normalized weight
            if all(self.props('symmetric', 'directed')) or not self.prop('directed'):
                del self.instance.graph['masks'][u][v]
                if self.prop('normalize'):
                    del self.instance.graph['normalized_weights'][u][v]

        return ret

    def nextstate_voter(self, u):
        '''

        :param u: The node to update
        :return: None
        '''
        myvals = self.prop('diffusion_space')[u]
        K = self.prop('num_dimensions')
        next_state = []
        nbrs = self.get_influencers(u)

        # Iterate over each dimension
        for k in range(K):
            curr = myvals[k]
            nbrvals = [nbrs[nbr][k] for nbr in nbrs]
            if all([i == nbrvals[0] for i in nbrvals]):
                curr = nbrvals[0]
            next_state.append(curr)
        return next_state

    def nextstate_majority(self, u):
        '''

        :param u: The node to update
        :return: None
        '''
        myvals = self.prop('diffusion_space')[u]
        K = self.prop('num_dimensions')
        next_state = []
        nbrs = self.get_influencers(u)

        # Iterate over each dimension
        for k in range(K):
            curr = myvals[k]
            nbrvals = [nbrs[nbr][k] for nbr in nbrs]
            valprops = {}
            for val in nbrvals:
                if val in valprops:
                    valprops[val] += 1
                else:
                    valprops[val] = 1
            total = len(list(valprops.keys()))
            for val in valprops:
                if valprops[val] / total > .5:
                    curr = val
            next_state.append(curr)
        return next_state

    def nextstate_plurality(self, u):
        '''

        :param u: The node to update
        :return: None
        '''
        myvals = self.prop('diffusion_space')[u]
        K = self.prop('num_dimensions')
        next_state = []
        nbrs = self.get_influencers(u)

        for k in range(K):
            curr = myvals[k]
            nbrvals = [nbrs[nbr][k] for nbr in nbrs]
            valprops = {}
            for val in nbrvals:
                if val in valprops:
                    valprops[val] += 1
                else:
                    valprops[val] = 1
            total = len(list(valprops.keys()))
            maxval = None
            maxprop = 0.
            for val in valprops:
                if valprops[val] / total > maxprop:
                    maxval = val
                    maxprop = valprops[val] / total
            if maxval is None:
                next_state.append(curr)
            else:
                next_state.append(maxval)
        return next_state

    def next_state_transmission(self, u):
        '''

        :param u:
        :return:
        '''
        myvals = self.prop('diffusion_space')[u]
        K = self.prop('num_dimensions')
        next_state = []
        nbrs = self.get_influencers(u)
        model = self.prop('transmission_probs')

        # Iterate over each dimension
        for k in range(K):
            curr = myvals[k]

            # If there are no transitions from the current state, just append that state
            if model[curr] == {}:
                next_state.append(curr)
            else:
                changed = False

                # Try to update states through contact first
                if 'contact' in model[curr]:
                    nbrvals = [nbrs[nbr][k] for nbr in nbrs]
                    for i in nbrvals:
                        if i not in model[curr]['contact']:
                            continue
                        cond, p = model[curr]['contact'][i]
                        if coin_flip(p):
                            next_state.append(cond)
                            changed = True
                            break

                if changed:
                    continue

                # If no change is made through contact, check for automatic transitions
                if 'auto' in model[curr]:
                    for i in model[curr]['auto']:
                        p = model[curr]['auto'][i]
                        if coin_flip(p):
                            next_state.append(i)
                            changed = True
                            break

                if not changed:
                    next_state.append(curr)

        return next_state

    def nextstate_average(self, u):
        if self.prop('update_method') == 'average':
            local_avg = self.get_local_average(u)
        elif self.prop('update_method') == 'wt. avg.':
            local_avg = self.get_local_average(u, weighted=True)
        myvals = self.prop('diffusion_space')[u]
        K = self.prop('num_dimensions')
        next_state = []
        t = self.prop('types')[u]
        for k in range(K):
            diff = local_avg[k] - myvals[k]
            if (t in CONFORMING and local_avg[k] * myvals[k] < 0) or\
               (t in REBELLING and local_avg[k] * myvals[k] >= 0):
                if self._has_property('resistance'):
                    if abs(local_avg[k]) > self.prop('resistance')[u]:
                        next_state.append(myvals[k] + (diff * self.prop('gravity')))
                    else:
                        next_state.append(myvals[k])
                else:
                    if t in CONFORMING:
                        next_state.append(myvals[k] + (diff * self.prop('gravity')))
                    else:
                        next_state.append(0 - (myvals[k] + (diff * self.prop('gravity'))))
            else:
                next_state.append(myvals[k] + (diff * self.prop('gravity')))

        if self.prop('dimensions') == 'continuous':
            ret = []
            for val in next_state:
                if val < -1:
                    ret.append(-1)
                elif val > 1:
                    ret.append(1)
                else:
                    ret.append(round(val, 2))
            return ret

        elif self.prop('dimensions') == 'binary':
            ret = []
            for i in range(len(next_state)):
                if next_state[i] == 0 and self.prop('gravity') >= 0:
                    ret.append(myvals[i])
                elif next_state[i] == 0 and self.prop('gravity') < 0:
                    ret.append(0 - myvals[i])
                elif next_state[i] < 0:
                    ret.append(-1)
                else:
                    ret.append(1)
            return ret

    def simple_average(self, d):
        '''

        :param d:
        :return:
        '''
        ret = []
        for k in range(self.prop('num_dimensions')):
            vec = [d[i][k] for i in d]
            if not vec:
                ret.append(0.)
            else:
                ret.append(sum(vec) / len(vec))
        return ret

    def weighted_average(self, d, w):
        '''

        :param d:
        :param w:
        :return:
        '''
        ret = []
        for k in range(self.prop('num_dimensions')):
            total = 0
            for key in d:
                total += d[key][k] * w[key]
            ret.append(round(total, 2))
        return ret

    def update(self):
        '''

        :return:
        '''
        if self.prop('p_update') == 0:
            return []
        numupdates = min(self.prop('num_nodes_update'), self.prop('n'))
        mynodes = list(self.nodes())
        if numupdates < len(mynodes):
            random.shuffle(mynodes)

        # print('Before: ', self.prop('diffusion_space'))
        upd = self.prop('update_method')
        next_states = {}
        for i, node in enumerate(mynodes):
            if i >= numupdates:
                break
            if coin_flip(self.prop('p_update')):
                if not self.get_influencers(node):
                    next_states[node] = self.prop('diffusion_space')[node]
                elif upd in ['average', 'wt. avg.']:
                    next_states[node] = self.nextstate_average(node)
                elif upd == 'voter':
                    next_states[node] = self.nextstate_voter(node)
                elif upd == 'majority':
                    next_states[node] = self.nextstate_majority(node)
                elif upd == 'plurality':
                    next_states[node] = self.nextstate_plurality(node)
                elif upd == 'transmission':
                    next_states[node] = self.next_state_transmission(node)

        for node in next_states:
            self.instance.graph['diffusion_space'][node] = next_states[node]

        # print('After: ', self.prop('diffusion_space'))

    def reward(self, u, v, raw=False):
        '''
        Calculate the reward node u gets from node v

        :param u: The receiving node
        :param v: The neighbor of the receiving node
        :param raw: Whether to take masking and connectedness into account
        :return: reward value in the range [0, 1]
        '''

        # Get distance between u and v, taking masks into account
        if raw:
            d = dist(self.prop('diffusion_space')[u], self.prop('diffusion_space')[v],
                     self.prop('distance'))
        else:
            d = dist(self.prop('diffusion_space')[u], self.get_view(u, v),
                     self.prop('distance'))

        # Get the % similarity that maximizes u's reward
        # print(self.prop('agent_models'))
        maxval = self.prop('agent_models')[self.prop('types')[u]]['max_sim']

        # If totally homophilic, return 1 - distance
        if maxval == 1.:
            return 1 - d

        # If totally heterophilic, the distance is the same as the reward
        elif maxval == 0.:
            return d

        # Otherwise, return linear reward based on sim_max and the boundaries [0, 1]
        elif d >= maxval:
            p = (d - maxval) / (1 - maxval)
            return 1 - p
        elif d < maxval:
            p = (maxval - d) / maxval
            return 1 - p

    def get_positions(self):
        '''

        :return:
        '''
        layout = self.prop('layout')
        pos = None
        if layout == 'spring':
            pos = nx.spring_layout(self)
        elif layout == 'circle':
            pos = nx.circular_layout(self)
        elif layout == 'spiral':
            pos = nx.spiral_layout(self)
        elif layout == 'random':
            pos = nx.random_layout(self)
        elif layout == 'shell':
            pos = nx.shell_layout(self)
        else:
            warn(f'Layout {layout} not supported.  Defaulting to spiral.')
            pos = nx.spring_layout(self)
        return np.array(list(pos.values())).T if pos else None

    def get_weights(self):
        d = {}
        if self.isgraph() or self.isdigraph():
            for u, v in self.edges:
                d[(u, v)] = self[u][v]['weight']
        elif self.ismultigraph() or self.ismultidigraph():
            for u, v, label in self.edges:
                d[(u, v, label)] = self[u][v][label]['weight']
        return d

    def get_connections(self):
        '''

        :return:
        '''
        if self.prop('p_connect') == 0:
            return []
        ret = []
        allnodes = list(self.nodes())
        mynodes = self.get_n_random_nodes(self.prop('num_nodes_connect'))
        num_c = self.prop('num_connections')
        for node in mynodes:
            possible = [i for i in allnodes if i not in self[node] and  i != node and
                        self.reward(node, i) >= self.prop('thresh_connect')]
            random.shuffle(possible)
            possible = possible[:num_c]
            for c in possible:
                ret.extend(self.connect(node, c, p=self.prop('p_connect')))
        return ret

    def get_disconnections(self):
        '''

        :return:
        '''
        if self.prop('p_disconnect') == 0:
            return []
        ret = []
        mynodes = self.get_n_random_nodes(self.prop('num_nodes_disconnect'))
        num_d = self.prop('num_disconnections')
        for node in mynodes:
            if self.isgraph() or self.ismultigraph():
                nbrs = list(self.neighbors(node))
            else:
                nbrs = list(self.successors(node))
            possible = [j for j in nbrs if self.reward(node, j, raw=True) < self.prop('thresh_disconnect') and j != node]
            if not possible:
                continue
            random.shuffle(possible)
            possible = sorted(possible[:num_d])
            for c in possible:
                ret.extend(self.disconnect(node, c, p=self.prop('p_disconnect')))
        return ret

    def get_n_random_nodes(self, num):
        '''

        :param num:
        :return:
        '''
        mynodes = list(self.nodes())
        n = len(mynodes)
        if num > n:
            num = n
        if num == n:
            return mynodes
        random.shuffle(mynodes)
        return mynodes[:num]

    def step(self):
        '''

        :return:
        '''
        rmv = self.get_disconnections()
        self.update()
        add = self.get_connections()
        return rmv, add

    # Method aliases
    prop = property
    props = properties