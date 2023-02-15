# Social Network Class

import networkx as nx
from warnings import warn

class SocialNetwork: #, nx.MultiDiGraph, nx.MultiGraph, nx.Graph):

    def __init__(self, props={}):
        '''
        Initializes a SocialNetwork object based on the given properties.
        :param props: a dictionary of named properties; can be empty

        List of named properties accepted by the class:
        _______________________________________________
        - 'directed': bool - - - whether edges are directed or not
        - 'multiedge': bool - - - whether multiedges are allowed or not
        - 'selfloops': bool - - - whether selfloops are present
        '''
        props = self.validate_properties(props)

        # Set up base class depending on input parameters
        dir, mult = props['directed'], props['multiedge']
        if not dir and not mult:
            self.instance = nx.Graph()
            self.prop(graphtype = 'graph')
        elif dir and not mult:
            self.instance = nx.DiGraph()
            self.prop(graphtype = 'digraph')
        elif not dir and mult:
            self.instance = nx.MultiGraph()
            self.prop(graphtype = 'multigraph')
        elif dir and mult:
            self.instance = nx.MultiDiGraph()
            self.prop(graphtype = 'multidigraph')

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

    def validate_properties(self, props):
        '''
        Verifies that all input properties are admissible.
        Uses default values to fill in missing necessary properties.
        :param props: (possibly empty) dictionary of named properties
        :return: a sanitized property dictionary
        '''
        if 'directed' not in props:
            props['directed'] = False
        if 'multiedge' not in props:
            props['multiedge'] = False
        if 'selfloops' not in props:
            props['selfloops'] = True
        return props

    def prop(self, *args, **kwargs):
        '''
        Multi-purpose getter, setter, and display method.
        Usages:
            No arguments - prints a list of all named properties and their values
            One regular argument - returns the value of the property by the given name, error if none exists
            One or more keyword arguments - sets property values of all provided named properties

            CANNOT accept args and kwargs at the same time.  Functionality is mutually exclusive.
            CANNOT accept multiple arguments when used as a getter.  Returns exactly one value.
            DOES NOT do any checks before overwriting a previously defined property value.
        :param args: a single property name
        :param kwargs: one or more named properties with values
        :return: a single property value if used as a getter; None if used as a setter or display
        '''

        # No input.  Print all property name/value pairs.
        if not (args or kwargs):
            print()
            for key in self.instance.graph.keys():
                print(f'{key}: {self.prop(key)}')

        # Caller tried to get and set values at the same time.  Throw an error.
        elif args and kwargs:
            msg = 'Method SocialNetwork.prop() can only be used as a getter or a setter at one time.\n'
            msg += '  Use EITHER myvar = mynetwork.prop(propertyname)\n    OR mynetwork.prop(propertname = value)'
            raise TypeError(msg)

        # Caller asked for more than one property to be returned.  Throw an error.
        elif args and len(args) > 1:
            raise TypeError('Expects a single input argument when used as a getter.')

        # Caller provided a single getter argument.  Try to return the property.
        # Throw an error if it doesn't exist.
        elif args:
            arg = args[0]
            if arg not in self.instance.graph:
                raise KeyError(f'No property named [{arg}] found.')
            return self.instance.graph[arg]

        # Caller provided a dict of named properties.  Set the values of each one.
        # WARNING: WILL OVERWRITE ANY EXISTING PROPERTY VALUE IF YOU TELL IT TO.
        elif kwargs:
            if any([key in self.instance.graph for key in kwargs]):
                warn(f'One or more existing graph properties will be overwritten.')
            for key in kwargs:
                self.instance.graph[key] = kwargs[key]

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

