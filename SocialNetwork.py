# Social Network Class

import networkx as nx
from warnings import warn

class SocialNetwork: #, nx.MultiDiGraph, nx.MultiGraph, nx.Graph):

    def __init__(self, **kwargs):
        '''
        Initializes a SocialNetwork object based on the given properties.

        :param kwargs: any number of named properties

        List of named properties accepted by the class:
        _______________________________________________
        - 'directed': bool - - - whether edges are directed or not
        - 'multiedge': bool - - - whether multiedges are allowed or not
        - 'selfloops': bool - - - whether selfloops are present
        '''

        self._validate_properties(kwargs)
        self._init_instance(kwargs['directed'], kwargs['multiedge'])

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

    def _init_instance(self, dir, mult):
        '''
        Initializes a NetworkX graph instance of the appropriate type as the base class.

        :param dir: whether or not the graph is directed
        :param mult: whether or not the graph allows multiedges
        :return: None
        '''

        # Set up base class depending on input parameters
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

    def _validate_properties(self, d):
        '''
        Verifies that all input properties are admissible.
        Uses default values to fill in missing necessary properties.

        :param d: (possibly empty) dictionary of named properties
        :return: None
        '''

        if 'directed' not in d: d['directed'] = False
        if 'multiedge' not in d: d['multiedge'] = False
        if 'selfloops' not in d: d['selfloops'] = True

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
            print()
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
        Wrapper for self.property().  Returns a tuple of property values, one for each input property name.

        :param arg: any number of property names
        :param kwargs: one or more named properties with values
        :return: a list of property values if used as a getter; None if used as display or setter only
        '''
        if not (args or kwargs):
            self.property()
        if kwargs:
            self.property(**kwargs)
        if args:
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
