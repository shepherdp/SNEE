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
#                    Options: integer or 'max'
#                             if integer > number of neighbors, defaults to max
default = {'homophily': 'homophilic',
           'conformity': 'conforming',
           'bound': False,
           'update_method': False,
           'num_influencers': 'max'
           }

AGENT_PROPS = {'default': default}

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
              'resistance_dist': DISTS,
              'resistance_mean': PROB,
              'resistance_stdev': PROB,
              'certainty_dist': DISTS,
              'certainty_mean': PROB,
              'certainty_stdev': PROB,
              'confidence_dist': DISTS,
              'confidence_mean': PROB,
              'confidence_stdev': PROB,
              'dimensions': ['continuous', 'binary'],
              'num_dimensions': POSNUM,
              'initialize_at_extremes': TF,
              'visibility': ['hidden', 'random', 'visible'],
              'normalize': TF
              }

PROPDEFAULTS = {'n': 0,
                'directed': False,
                'multiedge': False,
                'symmetric': True,
                'selfloops': True,
                'topology': '',
                'saturation': .1,
                'weight_dist': '-',
                'weight_const': 1.,
                'weight_mean': 0.,
                'weight_stdev': 1.,
                'weight_min': 0.,
                'weight_max': 1.,
                'resistance_dist': '-',
                'resistance_mean': .5,
                'resistance_stdev': .1,
                'certainty_dist': '-',
                'certainty_mean': .5,
                'certainty_stdev': .1,
                'confidence_dist': '-',
                'confidence_mean': .5,
                'confidence_stdev': .1,
                'num_dimensions': 1,
                'dimensions': 'binary',
                'initialize_at_extremes': False,
                'visibility': 'visible',
                'type_dist': {'default': 1.},
                'agent_types': AGENT_PROPS,
                'normalized_weights': {},
                'normalize': False
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
            if kwargs[f'{tag}_dist'] == '-':
                if f'{tag}_const' in kwargs: del kwargs[f'{tag}_const']
                if f'{tag}_min' in kwargs: del kwargs[f'{tag}_min']
                if f'{tag}_max' in kwargs: del kwargs[f'{tag}_max']
                if f'{tag}_mean' in kwargs: del kwargs[f'{tag}_mean']
                if f'{tag}_stdev' in kwargs: del kwargs[f'{tag}_stdev']

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
        if topology == '':
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

        # Add generated edges to graph structure
        for (u, v) in edges:
            self.connect(u, v)

        # Add self loops if needed
        if self.prop('selfloops'):
            for i in range(self.prop('n')):
                self.connect(i, i)

    def _generate_edge_weight(self, u, v, label=None):
        '''
        Generate a single edge weight according to the graph's designated weight distribution.

        :param u: endpoint of the weighted edge
        :param v: endpoint of the weighted edge
        :param label: an optional edge label
        :return: None
        '''
        d = self.prop('weight_dist')
        if d == 'constant':
            self._init_constant_edge_weight(u, v, label)
        elif d == 'uniform':
            self._init_uniform_edge_weight(u, v, label)
        elif d == 'normal':
            self._init_normal_edge_weight(u, v, label)

    def _generate_edge_weights(self, label=None):
        '''
        Generate edge weights based on the distribution and parameters specified by the user.

        :param label: an optional edge label
        :return: None
        '''
        e = self.edges()
        for u, v in e:
            self._generate_edge_weight(u, v, label)

    def _init_constant_edge_weight(self, u, v, label=None):
        '''
        Assign constant weight to edge (u, v).

        :param u: endpoint of the weighted edge
        :param v: endpoint of the weighted edge
        :param label: an optional edge label
        :return: None
        '''
        if self.prop('multiedge'):
            if label is None:
                label = self.new_edge_key(u, v)
            self[u][v][label]['weight'] = self.prop('weight_const')
        else:
            self[u][v]['weight'] = self.prop('weight_const')

    def _init_uniform_edge_weight(self, u, v, label=None):
        '''
        Assign uniform random weight to edge (u, v).

        :param u: endpoint of the weighted edge
        :param v: endpoint of the weighted edge
        :param label: an optional edge label
        :return: None
        '''
        lo, hi = self.props('weight_min', 'weight_max')
        if self.prop('multiedge'):
            if label is None:
                label = self.new_edge_key(u, v)
            self[u][v][label]['weight'] = np.random.uniform(lo, hi)
        else:
            self[u][v]['weight'] = np.random.uniform(lo, hi)

    def _init_normal_edge_weight(self, u, v, label=None):
        '''
        Assigns normally distributed weight to edge (u, v).

        :param u: endpoint of the weighted edge
        :param v: endpoint of the weighted edge
        :param label: an optional edge label
        :return: None
        '''

        # Get max, min, mean, and stdev values
        lo, hi = self.props('weight_min', 'weight_max')
        mu, sigma = self.props('weight_mean', 'weight_stdev')

        # Generate random numbers
        weight = np.random.normal(mu, sigma, 1)[0]

        # Lock weights within admissible range
        # NOTE: if, e.g., stdev is very high relative to the range [lo, hi], then it is possible that a lot of values
        # will clump up at the extremes of your range.  User beware!
        if weight < lo: weight = lo
        if weight > hi: weight = hi

        if self.prop('multiedge'):
            if label is None:
                label = self.new_edge_key(u, v)
            self[u][v][label]['weight'] = weight
        else:
            self.instance[u][v]['weight'] = weight

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

    def _init_diffusion_space(self):
        '''
        Initialize a matrix to represent the diffusion values of nodes in the network.
        Can be any number of dimensions, governed by the 'num_dimensions' property.

        :return: None
        '''
        n = self.number_of_nodes()
        k = self.prop('num_dimensions')
        matrix = []

        # If diffusion space is binary OR it is continuous but needs to be initialized at maximal and minimal values,
        # set all entries to -1 or 1.
        if self.prop('dimensions') == 'binary' or self.prop('initialize_at_extremes'):
            for i in range(k):
                vec = [1. for j in range(n//2)] + [-1. for j in range(n//2)]
                while len(vec) < n:
                    vec.append(random.choice([-1., 1.]))
                random.shuffle(vec)
                matrix.append(vec)

        # Otherwise, set them to random real values in the range [-1, 1].
        elif self.prop('dimensions') == 'continuous':
            matrix = [[2 * rnd.random() - 1 for j in range(n)]
                      for i in range(k)]

        # Set the attribute 'diffusion_space' to a numpy representation of the matrix.
        self.prop(diffusion_space=np.array(matrix).T)

    def _init_masks(self):
        '''
        Initialize dictionary for visibility values.
        If node i knows what node j's value in dimension k is, then
        self.prop('masks')[i][j][k] is that value, otherwise it is 0.

        :return: None
        '''

        n = self.number_of_nodes()
        k = self.prop('num_dimensions')

        # Set 'masks' attribute to a new dictionary with blank dictionaries for each node.
        self.prop(masks={i: {} for i in range(n)})

        # Each node knows its own diffusion values if selfloops are enforced.
        for i in range(n):
            if self.prop('selfloops'):
                self.instance.graph['masks'][i][i] = [1 for d in range(k)]

    def _init_agent_types(self):
        """
        Distribute agent types among the nodes, governed by the properties 'agent_types' and 'type_dist'.

        :return: None
        """

        n = self.number_of_nodes()
        self.prop(types=[])
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
                self.instance.graph['types'].append(t)

        # Make sure that the rounding above didn't leave us short an element.
        while len(self.prop('types')) < n:
            nums[max_t] += 1
            self.instance.graph['types'].append(max_t)

        # Randomly shuffle agent types.
        rnd.shuffle(self.instance.graph['types'])
        mytypes = self.prop('types')

        # Update indexes_by_type property for quick retrieval of all agents of a particular type.
        for i in range(len(mytypes)):
            self.instance.graph['indexes_by_type'][mytypes[i]].append(i)

    def load_agent_types(self):
        """
        Load each agent type into the relevant list for use when updating diffusion space.

        :return: None
        """
        models = self.prop('agent_models')
        if not models:
            return

        for modelname in models:
            model = models[modelname]
            AGENT_PROPS[modelname] = model

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
        return {v: self.get_view(u, v) for v in self[u]}

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

    def get_local_average(self, u, weighted=False, v=True):
        """

        :param u:
        :param weighted:
        :return:
        """

        if weighted:
            result = self.prop('normalized_weights').T[u].dot(self.prop('masks')[u]).round(decimals=2)
            return result
        else:
            result = self.prop('normalized_weights').T[u].dot(self.prop('masks')[u]).round(decimals=6)
            return result

    def connect(self, u, v, label=None, p=1., **kwargs):
        '''

        :param u:
        :param v:
        :param label:
        :param p:
        :param kwargs:
        :return: None
        '''
        if (u == v) and (not self.prop('selfloops')):
            return
        if coin_flip(p):
            if self.prop('multiedge'):
                self.connect_multi(u, v, label, **kwargs)
            else:
                self.add_edge(u, v, **kwargs)
                self._generate_edge_weight(u, v)
                if all(self.props('symmetric', 'directed')):
                    self.add_edge(v, u, **kwargs)
                    self._generate_edge_weight(v, u)
            self.reset_view(u, v, visibility=self.prop('visibility'))
            self._update_normalized_edge_weights(u)
            self._update_normalized_edge_weights(v)

    def connect_multi(self, u, v, label=None, **kwargs):
        '''

        :param u:
        :param v:
        :param label:
        :param kwargs:
        :return: None
        '''
        if label is None:
            label = self.new_edge_key(u, v)
        self.add_edge(u, v, label, **kwargs)
        self._generate_edge_weight(u, v, label)
        if all(self.props('symmetric', 'directed')):
            self.add_edge(v, u, label, **kwargs)
            self._generate_edge_weight(v, u, label)

    def disconnect(self, u, v, label=None, p=1.):
        '''

        :param u:
        :param v:
        :param label:
        :param p:
        :return:
        '''
        if (u == v) and (self.prop('selfloops')):
            return
        if coin_flip(p):
            if self.ismultigraph() or self.ismultidigraph():
                self.disconnect_multi(u, v, label)
            else:
                self.remove_edge(u, v)
                del self.instance.graph['masks'][v][u]
                if self.prop('normalize'):
                    del self.instance.graph['normalized_weights'][v][u]
                if all(self.props('symmetric', 'directed')):
                    self.remove_edge(v, u)
                if all(self.props('symmetric', 'directed')) or not self.prop('directed'):
                    del self.instance.graph['masks'][u][v]
                    if self.prop('normalize'):
                        del self.instance.graph['normalized_weights'][u][v]
            self.reset_view(u, v, visibility=self.prop('visibility'))
            self._update_normalized_edge_weights(u)
            self._update_normalized_edge_weights(v)

    def disconnect_multi(self, u, v, label=None):
        '''

        :param u:
        :param v:
        :param label:
        :return:
        '''
        if label is not None:
            self.remove_edge(u, v, label)
            notconnected = v not in self[u]
            if notconnected:
                del self.instance.graph['masks'][v][u]
                if self.prop('normalize'):
                    del self.instance.graph['normalized_weights'][v][u]
            if all(self.props('symmetric', 'directed')):
                self.remove_edge(v, u, label)
            if notconnected:
                if all(self.props('symmetric', 'directed')) or not self.prop('directed'):
                    del self.instance.graph['masks'][u][v]
                    if self.prop('normalize'):
                        del self.instance.graph['normalized_weights'][u][v]
        else:
            while v in self[u]:
                self.remove_edge(u, v)
                if all(self.props('symmetric', 'directed')):
                    self.remove_edge(v, u)
            del self.instance.graph['masks'][v][u]
            if self.prop('normalize'):
                del self.instance.graph['normalized_weights'][v][u]
            if all(self.props('symmetric', 'directed')) or not self.prop('directed'):
                del self.instance.graph['masks'][u][v]
                if self.prop('normalize'):
                    del self.instance.graph['normalized_weights'][u][v]

    def update_voter(self, u):
        '''
        Updates diffusion values of node u based on q = self.prop('num_voters').
        If max(q, degree of u) neighbors of node u all agree, then u takes their opinion.
        Otherwise, it flips its opinion with probability self.prop('p_update').
        If q = 1, then u automatically copies the neighbor's value.
        NOTE: Only defined for binary diffusion space.

        :param u: The node to update
        :return: None
        '''
        pass

    def update_majority(self, u):
        '''
        Updates diffusion values of node u based on the average opinion of its neighbors.
        If a strict majority of neighbors disagree with u, then u flips its value.  Else it stays the same.
        NOTE: Only defined for binary diffusion space.

        :param u: The node to update
        :return: None
        '''
        pass

    def update_simple_average(self, u):
        '''

        :param u:
        :return:
        '''
        pass

    def update_weighted_average(self, u):
        '''

        :param u:
        :return:
        '''
        pass

    def update(self):
        '''

        :return:
        '''
        pass

    # Method aliases
    prop = property
    props = properties