# GUI Class
import matplotlib.pyplot as plt
import networkx as nx
import random

from helpers import ToolTip, TOOLTIP, DISTS, METRICS
import networkx
from SocialNetwork import PROPDEFAULTS, PROPSELECT, SocialNetwork

import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np

import matplotlib.cm as cm

ERRCOLOR = 'pink'
WRNCOLOR = 'moccasin'
OKCOLOR = 'palegreen'
NRMCOLOR = 'white'
COLORS = cm.viridis

class GUI:

    def __init__(self, parent=None):

        self.parent = parent
        self.child = None
        if self.parent is None:
            self.root = tk.Tk()
            self.root.title("Social Network Evolution Engine")

            self.vars = {'n': tk.IntVar(),
                         'directed': tk.BooleanVar(),
                         'symmetric': tk.BooleanVar(),
                         'multiedge': tk.BooleanVar(),
                         'selfloops': tk.BooleanVar(),
                         'normalize': tk.BooleanVar(),
                         'staticpos': tk.BooleanVar(),
                         'topology': tk.StringVar(),
                         'layout': tk.StringVar(),
                         'weight_dist': tk.StringVar(),
                         'speed': tk.IntVar(),
                         'numplots': tk.IntVar(),
                         'dimensions': tk.StringVar(),
                         'num_dimensions': tk.IntVar(),
                         'visibility': tk.StringVar(),
                         'p_connect': tk.DoubleVar(),
                         'p_disconnect': tk.DoubleVar(),
                         'p_update': tk.DoubleVar(),
                         'saturation': tk.DoubleVar(),
                         'weight_min': tk.DoubleVar(),
                         'weight_max': tk.DoubleVar(),
                         'weight_mean': tk.DoubleVar(),
                         'weight_stdev': tk.DoubleVar(),
                         'weight_const': tk.DoubleVar(),
                         'connect_threshold': tk.DoubleVar(),
                         'disconnect_threshold': tk.DoubleVar(),
                         'sizenodesby': tk.StringVar(),
                         'colornodesby': tk.StringVar(),
                         'alphaedgesby': tk.StringVar(),
                         'labelnodesby': tk.StringVar(),
                         'labeledgesby': tk.StringVar(),
                         'coloredgesby': tk.StringVar(),
                         'plot1data': tk.StringVar(),
                         'plot2data': tk.StringVar(),
                         'plot3data': tk.StringVar(),
                         'plot4data': tk.StringVar(),
                         'plot5data': tk.StringVar(),
                         'plot6data': tk.StringVar(),
                         'addnode': tk.StringVar(),
                         'delnode': tk.StringVar(),
                         'addedgefrom': tk.StringVar(),
                         'addedgeto': tk.StringVar(),
                         'deledgefrom': tk.StringVar(),
                         'deledgeto': tk.StringVar(),
                         'addedgelabel': tk.StringVar(),
                         'deledgelabel': tk.StringVar(),
                         'size': tk.DoubleVar(),
                         'edgealpha': tk.DoubleVar(),
                         'nodealpha': tk.DoubleVar(),
                         'gravity': tk.DoubleVar(),
                         'confidence': tk.DoubleVar(),
                         'resistance': tk.DoubleVar(),
                         'update_method': tk.StringVar(),
                         'max_reward': tk.DoubleVar(),
                         'distance': tk.StringVar()}

            for key in self.vars:
                if key in PROPDEFAULTS:
                    self.vars[key].set(PROPDEFAULTS[key])

            self.graph = None
            self.data = {f'ax{i}': None for i in range(7)}
            self.drawing = False

        else:
            self.root = tk.Toplevel(self.parent.root)
            self.root.title('Command Center')
            self.vars = self.parent.vars
            self.graph = self.parent.graph
            self.data = self.parent.data
            self.drawing = self.parent.drawing

        self.tooltips = {}
        self.frames = {}
        self.inputs = {}
        self.labels = {}
        self.buttons = {}
        self.notebook = {}
        self.plot = {'axes':{},
                     'nodesize': 100}
        self.problems = set()

        self._init_panel_frames()
        self._init_notebook()
        self._init_status()

        if not self.parent:
            self._init_plot(None)
        else:
            self.plot = self.parent.plot

        self.invoke_callbacks()

        if self.parent is not None:
            self.root.protocol("WM_DELETE_WINDOW", self.popoff)
        else:
            self.root.mainloop()

    def _init_panel_frames(self):
        if self.root:
            self.frames['window'] = tk.Frame(self.root, padx=5, pady=5)
        else:
            self.frames['window'] = tk.Frame(self, padx=5, pady=5)
        self.frames['window'].grid(padx=5, pady=5, sticky='news')

        self.frames['notebook'] = tk.LabelFrame(self.frames['window'], text='Control Panel', padx=5, pady=5)
        self.frames['notebook'].grid(row=0, column=0, padx=5, pady=5, sticky='news')

        self.frames['status'] = tk.LabelFrame(self.frames['window'], text='Status', padx=5, pady=5)
        self.frames['status'].grid(row=1, column=0, padx=5, pady=5, sticky='sew')

        if self.parent is None:
            self.frames['plot'] = tk.LabelFrame(self.frames['window'], text='Plot', padx=5, pady=5)
            self.frames['plot'].grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky='news')

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        if self.parent is None:
            self.frames['window'].columnconfigure(1, weight=1)
            self.frames['window'].rowconfigure(0, weight=1)
        else:
            self.frames['window'].columnconfigure(0, weight=1)
            self.frames['window'].rowconfigure(0, weight=1)
            self.frames['window'].rowconfigure(1, weight=1)
            self.frames['notebook'].columnconfigure(0, weight=1)
            self.frames['notebook'].rowconfigure(0, weight=1)

    def _init_status(self):

        self._place_labelframe('buttons', self.frames['status'], '')
        self.buttons['construct'] = tk.Button(self.frames['buttons'], text='Construct', width=18, command=self.construct)
        self.buttons['construct'].grid(row=0, column=0, sticky='ew', padx=2, pady=1)
        self.buttons['clear'] = tk.Button(self.frames['buttons'], text='Clear', width=18, command=self.clear)
        self.buttons['clear'].grid(row=0, column=2, sticky='ew', padx=2, pady=1)
        self.buttons['step'] = tk.Button(self.frames['buttons'], text='Step', width=18, command=self.step)
        self.buttons['step'].grid(row=1, column=0, sticky='ew', padx=2, pady=1)

        mytext = 'Pause' if self.drawing else 'Play'
        self.buttons['play'] = tk.Button(self.frames['buttons'], text=mytext, width=18, command=self.play)
        self.buttons['play'].grid(row=1, column=2, sticky='ew', padx=2, pady=1)
        if self.parent:
            self.buttons['popoff'] = tk.Button(self.frames['status'], text='Pop On', command=self.popoff)
            self.buttons['popoff'].pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=1)
        else:
            self.buttons['popoff'] = tk.Button(self.frames['status'], text='Pop Off', command=self.popoff)
            self.buttons['popoff'].pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=1)

        self.labels['status'] = tk.Label(self.frames['status'], text="All good right now.")
        self.labels['status'].pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _init_plot(self, event):
        nsubplots = self.vars['numplots'].get() - 1
        if 'fig' not in self.plot:
            self.plot['fig'] = Figure(figsize=(7, 5), dpi=100)
            self.plot['canvas'] = FigureCanvasTkAgg(self.plot['fig'], master=self.frames['plot'])
            self.plot['canvas'].draw()
            self.plot['toolbar'] = NavigationToolbar2Tk(self.plot['canvas'], self.frames['plot'])
            self.plot['toolbar'].update()
            self.plot['canvas'].get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        else:
            self.plot['fig'].clf()

        ncols = max(1, nsubplots)
        nrows = 3 if nsubplots == 0 else 4

        netplotnums = (1, 3 * ncols)

        axes = ['ax0']
        self.plot['axes']['ax0'] = self.plot['fig'].add_subplot(nrows, ncols, netplotnums)

        num = (3 * ncols) + 1
        if nrows == 4:
            for i in range(ncols):
                self.plot['axes'][f'ax{i+1}'] = self.plot['fig'].add_subplot(nrows, ncols, num)
                axes.append(f'ax{i+1}')
                num += 1

        keys = list(self.plot['axes'].keys())
        for ax in keys:
            if ax not in axes:
                del self.plot['axes'][ax]

        for ax in self.plot['axes']:
            self.plot['axes'][ax].set_xticks([])
            self.plot['axes'][ax].set_yticks([])

        self.plot['fig'].subplots_adjust(bottom=0.025, left=0.025, top=0.975, right=0.975, hspace=0.1, wspace=0.1)
        # plt.autoscale()
        self.plot['canvas'].draw()

        self.set_dataplot_entries()

    def _init_notebook(self):

        if self.root:
            style = ttk.Style(self.root)
        else:
            style = ttk.Style(self)

        style.configure('lefttab.TNotebook', tabposition='wn', tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", padding=[3, 3], font=('Courier', '8'))

        self.notebook['notebook'] = ttk.Notebook(self.frames['notebook'], style='lefttab.TNotebook')

        self.notebook['parameters'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['animation'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['plots'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['evolution'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['edit'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['command'] = ttk.Frame(self.notebook['notebook'])

        self.notebook['notebook'].add(self.notebook['parameters'], text='PRM')
        self.notebook['notebook'].add(self.notebook['animation'], text='ANI')
        self.notebook['notebook'].add(self.notebook['plots'], text='PLT')
        self.notebook['notebook'].add(self.notebook['evolution'], text='EVO')
        self.notebook['notebook'].add(self.notebook['edit'], text='EDT')
        self.notebook['notebook'].add(self.notebook['command'], text='CMD')

        self.notebook['notebook'].grid(padx=5, pady=5, sticky=tk.N + tk.E + tk.S + tk.W)

        self._populate_parameters_tab()
        self._populate_animation_tab()
        self._populate_plots_tab()
        self._populate_evolution_tab()
        self._populate_edit_tab()

    def _populate_parameters_tab(self):

        self._place_labelframe('graph_structure', self.notebook['parameters'], 'Graph Structure')

        self._place_input_label('n', 'graph_structure', 'Nodes: ')
        self._place_input_entry('n', 'graph_structure', col=1)
        self.vars['n'].set(20)
        self.set_trace('n', self.n_callback)
        self.set_tooltip('n')

        self._place_input_checkbutton('symmetric', 'graph_structure', text='Symmetric', row=1, columnspan=2)
        self.set_tooltip('symmetric')
        self._place_input_checkbutton('directed', 'graph_structure', text='Directed', row=2, columnspan=2,
                                      command=self.directed_callback)
        self.set_tooltip('directed')
        self._place_input_checkbutton('selfloops', 'graph_structure', text='Self loops', row=1, col=2, columnspan=2)
        self.set_tooltip('selfloops')
        self._place_input_checkbutton('multiedge', 'graph_structure', text='Multiedges', row=2, col=2, columnspan=2)
        self.set_tooltip('multiedge')

        self._place_labelframe('topology', self.notebook['parameters'], 'Topology')

        self._place_input_label('topology', 'topology', 'Topology: ')
        self.vars['topology'].set('small world')
        self._place_input_optionmenu('topology', 'topology', self.vars['topology'].get(), PROPSELECT['topology'],
                                     col=1, columnspan=3, sticky='ew', command=self.topology_popup)

        self._place_input_label('saturation', 'topology', 'Saturation: ', row=1)
        self._place_input_entry('saturation', 'topology', row=1, col=1)

        self._place_labelframe('edge_weights', self.notebook['parameters'], 'Weights')

        self._place_input_label('weight_dist', 'edge_weights', 'Weights: ')
        self._place_input_optionmenu('weight_dist', 'edge_weights', self.vars['weight_dist'].get(), DISTS, col=1,
                                     columnspan=3, sticky='ew', command=self.weight_dist_callback)

        self._place_input_label('weight_min', 'edge_weights', 'Minimum: ', row=1)
        self._place_input_entry('weight_min', 'edge_weights', row=1, col=1)
        self.set_trace('weight_min', self.weight_minmaxmean_callback)
        self.set_trace('weight_max', self.weight_minmaxmean_callback)
        self.set_trace('weight_mean', self.weight_minmaxmean_callback)
        self.set_trace('weight_stdev', self.weight_stdev_callback)

        self._place_input_label('weight_max', 'edge_weights', 'Maximum: ', row=1, col=2)
        self._place_input_entry('weight_max', 'edge_weights', row=1, col=3)

        self._place_input_label('weight_mean', 'edge_weights', 'Mean: ', row=2)
        self._place_input_entry('weight_mean', 'edge_weights', row=2, col=1)

        self._place_input_label('weight_stdev', 'edge_weights', 'Stdev: ', row=2, col=2)
        self._place_input_entry('weight_stdev', 'edge_weights', row=2, col=3)

        self._place_input_label('weight_const', 'edge_weights', 'Constant: ', row=3)
        self._place_input_entry('weight_const', 'edge_weights', row=3, col=1)

        self._place_input_checkbutton('normalize', 'edge_weights', text='Normalize', row=3, col=2, columnspan=2,
                                      sticky='e')

    def _populate_animation_tab(self):
        self._place_labelframe('animation', self.notebook['animation'], 'Animation')

        self._place_input_label('speed', 'animation', 'Speed: ', row=1, col=0)
        self._place_input_scale('speed', 'animation', 0, 5, 1, length=150, row=1, col=1, columnspan=3)

        self._place_input_label('layout', 'animation', 'Layout: ', row=0, col=0)
        if self.vars['layout'].get() == '':
            self.vars['layout'].set('spring')
        self._place_input_optionmenu('layout', 'animation', self.vars['layout'].get(),
                                     ['spring', 'circle', 'spiral', 'random', 'shell'], row=0, col=1, columnspan=2,
                                     sticky='ew', command=self.update_layout_handler)

        self._place_labelframe('nodes', self.notebook['animation'], 'Nodes')

        self._place_input_checkbutton('staticpos', 'nodes', row=0, col=0, sticky='w', text='Fixed pos.')
        self._place_input_label('size', 'nodes', 'Size: ', row=0, col=1)
        self._place_input_scale('size', 'nodes', 100, 700, 100, length=80, row=0, col=2, columnspan=2, sticky='ew',
                                command=self.resize_nodes)
        self._place_input_label('nodealpha', 'nodes', 'Alpha: ', row=1, col=0)
        if self.parent is not None:
            self.vars['nodealpha'].set(self.parent.vars['nodealpha'].get())
        else:
            self.vars['nodealpha'].set(1.)
        self._place_input_scale('nodealpha', 'nodes', 0, 1, .01, length=70, row=1, col=1, columnspan=2, sticky='ew',
                                command=self.realpha_nodes)
        self._place_input_entry('nodealpha', 'nodes', row=1, col=3, sticky='e')

        self._place_input_label('sizenodesby', 'nodes', 'Size nodes: ', row=2, col=0)
        if self.vars['sizenodesby'].get() == '':
            self.vars['sizenodesby'].set('-')
        self._place_input_optionmenu('sizenodesby', 'nodes', self.vars['sizenodesby'].get(), METRICS, row=2, col=1,
                                     columnspan=3, sticky='ew', command=self.resize_nodes)
        self._place_input_label('colornodesby', 'nodes', 'Color nodes: ', row=3, col=0)
        if self.vars['colornodesby'].get() == '':
            self.vars['colornodesby'].set('-')
        self._place_input_optionmenu('colornodesby', 'nodes', self.vars['colornodesby'].get(),
                                     ['-', 'type', 'diff. space'] + METRICS[1:], row=3, col=1, columnspan=3,
                                     command=self.recolor_nodes, sticky='ew')
        self._place_input_label('labelnodesby', 'nodes', 'Label nodes: ', row=4, col=0)
        if self.vars['labelnodesby'].get() == '':
            self.vars['labelnodesby'].set('-')
        self._place_input_optionmenu('labelnodesby', 'nodes', self.vars['labelnodesby'].get(),
                                     ['-', 'name', 'type', 'diff. space'] + METRICS[1:], row=4, col=1, columnspan=3,
                                     sticky='ew', command=self.relabel_nodes)

        self._place_labelframe('edges', self.notebook['animation'], 'Edges')

        self._place_input_label('edgealpha', 'edges', 'Alpha: ', row=0, col=0)
        if self.parent is not None:
            self.vars['edgealpha'].set(self.parent.vars['edgealpha'].get())
        else:
            self.vars['edgealpha'].set(.2)
        self._place_input_scale('edgealpha', 'edges', 0, 1, .01, length=70, row=0, col=1, columnspan=2,
                                command=self.realpha_edges)
        self._place_input_entry('edgealpha', 'edges', row=0, col=3)

        self._place_input_label('alphaedgesby', 'edges', 'Darken edges: ', row=1, col=0)
        if self.vars['alphaedgesby'].get() == '':
            self.vars['alphaedgesby'].set('-')
        self._place_input_optionmenu('alphaedgesby', 'edges', self.vars['alphaedgesby'].get(), ['-', 'betweenness', 'weight'], row=1, col=1,
                                     columnspan=3, sticky='ew', command=self.realpha_edges)
        self._place_input_label('coloredgesby', 'edges', 'Color edges: ', row=2, col=0)
        if self.vars['coloredgesby'].get() == '':
            self.vars['coloredgesby'].set('-')
        self._place_input_optionmenu('coloredgesby', 'edges', self.vars['coloredgesby'].get(), ['-', 'betweenness', 'weight', 'label'], row=2,
                                     col=1, columnspan=3, sticky='ew')
        self._place_input_label('labeledgesby', 'edges', 'Label edges: ', row=4, col=0)
        if self.vars['labeledgesby'].get() == '':
            self.vars['labeledgesby'].set('-')
        self._place_input_optionmenu('labeledgesby', 'edges', self.vars['labeledgesby'].get(), ['-', 'betweenness', 'weight', 'label'], row=4,
                                     col=1, columnspan=3, sticky='ew')

        # self._place_labelframe('play', self.notebook['animation'], '')
        #
        # self.buttons['play'] = tk.Button(self.frames['play'], text='Play')
        # self.buttons['play'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # self.buttons['step'] = tk.Button(self.frames['play'], text='Step')
        # self.buttons['step'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # self.buttons['pause'] = tk.Button(self.frames['play'], text='Pause')
        # self.buttons['pause'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _populate_plots_tab(self):
        self._place_labelframe('dataplots', self.notebook['plots'], 'Data Plots')

        self._place_input_label('numplots', 'dataplots', '# Plots: ', row=0, col=0)
        self._place_input_scale('numplots', 'dataplots', 1, 7, 1, length=100, row=0, col=1, columnspan=2,
                                command=self._init_plot)
        for i in range(1, 7):
            self._place_input_label(f'plot{i}data', 'dataplots', f'Plot {i}: ', row=i, col=0)
            if self.vars[f'plot{i}data'].get() == '':
                self.vars[f'plot{i}data'].set('-')
            self._place_input_optionmenu(f'plot{i}data', 'dataplots', self.vars[f'plot{i}data'].get(), METRICS, row=i, col=1, columnspan=3,
                                         sticky='ew')

            self.labels[f'plot{i}data'].grid_forget()
            self.inputs[f'plot{i}data'].grid_forget()

    def _populate_evolution_tab(self):
        self._place_labelframe('evolution', self.notebook['evolution'], 'Evolution Parameters')

        self._place_input_label('num_dimensions', 'evolution', 'Dimensions: ')
        self._place_input_entry('num_dimensions', 'evolution', col=1)

        self._place_input_label('dimensions', 'evolution', 'Domain: ', row=1)
        self._place_input_optionmenu('dimensions', 'evolution', self.vars['dimensions'].get(), ['binary', 'continuous'],
                                     row=1, col=1, columnspan=3)

        self._place_input_label('visibility', 'evolution', 'Visibility: ', row=2)
        self._place_input_optionmenu('visibility', 'evolution', self.vars['visibility'].get(), ['visible', 'hidden', 'random'],
                                     row=2, col=1, columnspan=3)

        self._place_labelframe('dynamics', self.notebook['evolution'], 'Dynamics')

        self._place_input_label('p_connect', 'dynamics', 'Pr(+): ')
        self._place_input_scale('p_connect', 'dynamics', 0, 1, .01, col=1, columnspan=2, length=100)
        self._place_input_entry('p_connect', 'dynamics', col=3)

        self._place_input_label('p_disconnect', 'dynamics', 'Pr(-): ', row=1)
        self._place_input_scale('p_disconnect', 'dynamics', 0, 1, .01, row=1, col=1, columnspan=2, length=100)
        self._place_input_entry('p_disconnect', 'dynamics', row=1, col=3)

        self._place_input_label('connect_threshold', 'dynamics', 'Thr(+): ', row=2)
        self._place_input_scale('connect_threshold', 'dynamics', 0, 1, .01, row=2, col=1, columnspan=2, length=100)
        self._place_input_entry('connect_threshold', 'dynamics', row=2, col=3)

        self._place_input_label('disconnect_threshold', 'dynamics', 'Thr(-): ', row=3)
        self._place_input_scale('disconnect_threshold', 'dynamics', 0, 1, .01, row=3, col=1, columnspan=2, length=100)
        self._place_input_entry('disconnect_threshold', 'dynamics', row=3, col=3)

        self._place_labelframe('diffusion', self.notebook['evolution'], 'Diffusion Updates')

        self._place_input_label('p_update', 'diffusion', 'Pr(upd): ', row=0)
        self._place_input_scale('p_update', 'diffusion', 0, 1, .01, row=0, col=1, columnspan=2, length=90)
        self._place_input_entry('p_update', 'diffusion', row=0, col=3)
        self._place_input_label('gravity', 'diffusion', 'Gravity: ', row=1)
        self._place_input_scale('gravity', 'diffusion', -1, 1, .01, row=1, col=1, columnspan=2, length=90)
        self._place_input_entry('gravity', 'diffusion', row=1, col=3)
        self._place_input_label('confidence', 'diffusion', 'Conf.: ', row=2)
        self._place_input_scale('confidence', 'diffusion', 0, 1, .01, row=2, col=1, columnspan=2, length=90)
        self._place_input_entry('confidence', 'diffusion', row=2, col=3)
        self._place_input_label('resistance', 'diffusion', 'Res.: ', row=3)
        self._place_input_scale('resistance', 'diffusion', 0, 1, .01, row=3, col=1, columnspan=2, length=90)
        self._place_input_entry('resistance', 'diffusion', row=3, col=3)

        self._place_input_label('update_method', 'diffusion', 'Updates: ', row=4)
        if self.vars['update_method'].get() == '':
            self.vars['update_method'].set('-')
        self._place_input_optionmenu('update_method', 'diffusion', self.vars['update_method'].get(), ['-', 'voter', 'majority', 'average',
                                                                         'transmission'],
                                     row=4, col=1, columnspan=3, sticky='ew')

        self._place_labelframe('reward', self.notebook['evolution'], 'Reward')

        self._place_input_label('max_reward', 'reward', 'Sim. Max.: ', row=0)
        self._place_input_scale('max_reward', 'reward', 0, 1, .5, row=0, col=1, columnspan=2, length=70)
        self._place_input_entry('max_reward', 'reward', row=0, col=3)
        self._place_input_label('distance', 'reward', 'Distance: ', row=1)
        if self.vars['distance'].get() == '':
            self.vars['distance'].set('hamming')
        self._place_input_optionmenu('distance', 'reward', self.vars['distance'].get(), ['hamming', 'euclidean', 'cosine'],
                                     row=1, col=1, columnspan=3, sticky='ew')

    def _populate_edit_tab(self):
        self._place_labelframe('nodeedit', self.notebook['edit'], 'Nodes')

        self._place_input_label('addnode', 'nodeedit', 'Add: ', row=0, col=0)
        self._place_input_entry('addnode', 'nodeedit', row=0, col=1)
        self.buttons['addnode'] = tk.Button(self.frames['nodeedit'], text='+', width=5)
        self.buttons['addnode'].grid(row=0, column=3, sticky='e')
        self._place_input_label('delnode', 'nodeedit', 'Del: ', row=1, col=0)
        self._place_input_entry('delnode', 'nodeedit', row=1, col=1)
        self.buttons['delnode'] = tk.Button(self.frames['nodeedit'], text='-', width=5)
        self.buttons['delnode'].grid(row=1, column=3, sticky='e')

        self._place_labelframe('edgeedit', self.notebook['edit'], 'Edges')

        self._place_input_label('fromlabel', 'edgeedit', 'From', row=0, col=1, sticky='ew')
        self._place_input_label('fromlabel', 'edgeedit', 'To', row=0, col=2, sticky='ew')
        self._place_input_label('fromlabel', 'edgeedit', 'Label', row=0, col=3, sticky='ew')
        self._place_input_label('addedge', 'edgeedit', 'Add: ', row=1, col=0)
        self._place_input_entry('addedgefrom', 'edgeedit', row=1, col=1)
        self._place_input_entry('addedgeto', 'edgeedit', row=1, col=2)
        self._place_input_entry('addedgelabel', 'edgeedit', row=1, col=3)
        self.buttons['addedge'] = tk.Button(self.frames['edgeedit'], text='+', width=5)
        self.buttons['addedge'].grid(row=1, column=4, sticky='e')
        self._place_input_label('deledge', 'edgeedit', 'Del: ', row=2, col=0)
        self._place_input_entry('deledgefrom', 'edgeedit', row=2, col=1)
        self._place_input_entry('deledgeto', 'edgeedit', row=2, col=2)
        self._place_input_entry('deledgelabel', 'edgeedit', row=2, col=3)
        self.buttons['deledge'] = tk.Button(self.frames['edgeedit'], text='-', width=5)
        self.buttons['deledge'].grid(row=2, column=4, sticky='e')

    def _place_labelframe(self, tag, parent, text):
        self.frames[tag] = tk.LabelFrame(parent, text=text, padx=5, pady=3)
        self.frames[tag].pack(fill=tk.BOTH, padx=5)

    def _place_input_label(self, tag, framename, text, row=0, col=0, sticky='e'):
        self.labels[tag] = tk.Label(self.frames[framename], text=text, padx=2)
        self.labels[tag].grid(row=row, column=col, padx=2, sticky=sticky)

    def _place_input_entry(self, tag, framename, width=5, row=0, col=0, columnspan=1, sticky='w'):
        self.inputs[tag] = tk.Entry(self.frames[framename], textvariable=self.vars[tag], width=width)
        self.inputs[tag].grid(row=row, column=col, columnspan=columnspan, padx=2, sticky=sticky)

    def _place_input_checkbutton(self, tag, framename, row=0, col=0, sticky='w', text=None, columnspan=1,
                                 command=None):
        self.inputs[tag] = tk.Checkbutton(self.frames[framename], variable=self.vars[tag], text=text, padx=2,
                                          command=command)
        self.inputs[tag].grid(row=row, column=col, padx=2, sticky=sticky, columnspan=columnspan)

    def _place_input_optionmenu(self, tag, framename, firstoption, vals, row=0, col=0, columnspan=1, sticky='w',
                                command=None):
        self.inputs[tag] = ttk.OptionMenu(self.frames[framename], self.vars[tag], firstoption, *vals, command=command)
        self.inputs[tag].grid(row=row, column=col, padx=2, columnspan=columnspan, sticky=sticky)

    def _place_input_scale(self, tag, framename, lo, hi, res, length=100, showvalue=False, row=0, col=0,
                           columnspan=1, sticky='ew', command=None):
        self.inputs[tag] = tk.Scale(self.frames[framename], length=length, variable=self.vars[tag], label=None,
                                    resolution=res, orient='horizontal', from_=lo, to=hi, showvalue=showvalue,
                                    command=command)
        self.inputs[tag].grid(row=row, column=col, columnspan=columnspan, padx=5, sticky=sticky)

    def directed_callback(self):
        if not self.vars['directed'].get():
            self.vars['symmetric'].set(True)
            self.disable_vars('symmetric')
        else:
            self.enable_vars('symmetric')

    def n_callback(self, *args):
        try:
            n = self.vars['n'].get()
            if n < 0:
                self.inputs['n'].configure(bg=ERRCOLOR)
                self.tooltips['n'].update(TOOLTIP['n']['error'], ERRCOLOR)
            else:
                if self.inputs['n'].cget('bg') == ERRCOLOR:
                    self.reset_bgcolor(['n'])
                    self.tooltips['n'].update(TOOLTIP['n']['normal'], NRMCOLOR)
        except:
            self.inputs['n'].configure(bg=ERRCOLOR)
            self.tooltips['n'].update(TOOLTIP['n']['error'], ERRCOLOR)

    def weight_minmaxmean_callback(self, *args):

        if self.inputs['weight_mean'].cget('state') == 'disabled':
            # Only compare min and max
            try:
                wmin = self.vars['weight_min'].get()
                wmax = self.vars['weight_max'].get()
            except:
                wmin, wmax = 1, 0
            if wmin >= wmax:
                self.problems.add('weight_min')
                self.problems.add('weight_max')
                self.inputs['weight_min'].configure(bg=ERRCOLOR)
                self.inputs['weight_max'].configure(bg=ERRCOLOR)
            else:
                for tag in ['weight_min', 'weight_max']:
                    if tag in self.problems:
                        self.problems.remove(tag)
                self.reset_bgcolor(['weight_min', 'weight_max'])

        else:
            try:
                wmin = self.vars['weight_min'].get()
                wmax = self.vars['weight_max'].get()
                wmean = self.vars['weight_mean'].get()
            except:
                wmin, wmax, wmean = 0, 1, 2

            if not (wmin < wmean < wmax):
                self.problems.add('weight_mean')
                self.problems.add('weight_min')
                self.problems.add('weight_max')
                self.inputs['weight_min'].configure(bg=ERRCOLOR)
                self.inputs['weight_max'].configure(bg=ERRCOLOR)
                self.inputs['weight_mean'].configure(bg=ERRCOLOR)
            else:
                for tag in ['weight_min', 'weight_max', 'weight_mean']:
                    if tag in self.problems:
                        self.problems.remove(tag)
                self.reset_bgcolor(['weight_min', 'weight_max', 'weight_mean'])

    def weight_stdev_callback(self, *args):
        try:
            wmin = self.vars['weight_min'].get()
            wmax = self.vars['weight_max'].get()
            wmean = self.vars['weight_mean'].get()
            stdev = self.vars['weight_stdev'].get()
        except:
            return

        dist1 = abs(wmean - wmin) / 3
        dist2 = abs(wmax - wmean) / 3

        if stdev > dist1 or stdev > dist2:
            self.problems.add('weight_stdev')
            self.inputs['weight_stdev'].configure(bg=WRNCOLOR)
        else:
            if 'weight_stdev' in self.problems:
                self.problems.remove('weight_stdev')
                self.reset_bgcolor(['weight_stdev'])

    def weight_dist_callback(self, *args):
        d = self.vars['weight_dist'].get()
        if d == '-':
            self.disable_vars('weight_min', 'weight_max', 'weight_mean',
                              'weight_stdev', 'weight_const', 'normalize')
        elif d == 'constant':
            self.disable_vars('weight_min', 'weight_max', 'weight_mean', 'weight_stdev')
            self.enable_vars('weight_const', 'normalize')
        elif d == 'uniform':
            self.disable_vars('weight_mean', 'weight_stdev', 'weight_const')
            self.enable_vars('weight_min', 'weight_max', 'normalize')
            self.weight_minmaxmean_callback()
        elif d == 'normal':
            self.disable_vars('weight_const')
            self.enable_vars('weight_min', 'weight_max', 'weight_mean', 'weight_stdev', 'normalize')
            self.weight_minmaxmean_callback()

    def reset_bgcolor(self, tags, firstcall=True):
        for tag in tags:
            if firstcall:
                self.inputs[tag].configure(bg=OKCOLOR)
            else:
                if self.inputs[tag].cget('bg') != ERRCOLOR:
                    self.inputs[tag].configure(bg=NRMCOLOR)
        if firstcall:
            if self.root:
                self.root.after(500, lambda: self.reset_bgcolor(tags, firstcall=False))
            else:
                self.root.after(500, lambda: self.reset_bgcolor(tags, firstcall=False))

    def popoff(self):
        if self.parent == None and self.child == None:
            self.frames['notebook'].grid_forget()
            self.frames['status'].grid_forget()
            self.child = GUI(self)
        elif self.parent is not None:
            self.parent.frames['notebook'].grid(row=0, sticky='news', padx=5, pady=5)
            self.parent.frames['status'].grid(row=1, sticky='sew', padx=5, pady=5)
            self.parent.invoke_callbacks()
            self.root.withdraw()
        else:
            self.child.root.deiconify()
            self.child.invoke_callbacks()
            self.frames['notebook'].grid_forget()
            self.frames['status'].grid_forget()

    def topology_popup(self, event):
        top = self.vars['topology'].get()

    def disable_vars(self, *vars):
        for var in vars:
            self.inputs[var].configure(state='disabled')

    def enable_vars(self, *vars):
        for var in vars:
            self.inputs[var].configure(state='normal')

    def invoke_callbacks(self):
        self.weight_minmaxmean_callback()
        self.weight_stdev_callback()
        self.weight_dist_callback()
        self.n_callback()
        self.directed_callback()
        self.set_dataplot_entries()

    def set_trace(self, tag, callback):
        self.vars[tag].trace('w', callback)

    def set_dataplot_entries(self):
        if 'fig' not in self.plot:
            return
        nsubplots = self.vars['numplots'].get() - 1
        for i in range(1, 7):
            if i <= nsubplots:
                self.labels[f'plot{i}data'].grid(row=i, column=0)
                self.inputs[f'plot{i}data'].grid(row=i, column=1, columnspan=3, sticky='ew')
            else:
                self.labels[f'plot{i}data'].grid_forget()
                self.inputs[f'plot{i}data'].grid_forget()

    def set_tooltip(self, tag):
        self.tooltips[tag] = ToolTip(self.inputs[tag], TOOLTIP[tag]['normal'])

    def construct(self):
        for i in self.inputs:
            if self.inputs[i].cget('state') == 'normal' and self.inputs[i].cget('bg') == ERRCOLOR:
                print('No good')
                return
        vals = {i: self.vars[i].get() for i in self.vars}
        self.graph = SocialNetwork(n=vals['n'], selfloops=True, topology=vals['topology'],
                                   p_disconnect=1., p_connect=0., thresh_disconnect=.5, num_dimensions=4)
        self.create_plot()

    def get_positions(self):
        if self.graph is None:
            return
        layout = self.vars['layout'].get()
        pos = None
        if 'pos' in self.data['ax0']:
            pos = self.data['ax0']['pos']
        if layout == 'spring':
            return networkx.spring_layout(self.graph, pos=pos)
        elif layout == 'circle':
            return networkx.circular_layout(self.graph, pos=pos)
        elif layout == 'spiral':
            return networkx.spiral_layout(self.graph, pos=pos)
        elif layout == 'shell':
            return networkx.shell_layout(self.graph, pos=pos)
        elif layout == 'random':
            return networkx.spring_layout(self.graph, pos=pos)

    def create_plot(self):
        self.data['ax0'] = {}

        self.data['ax0']['pos'] = self.get_positions()
        pos = self.data['ax0']['pos']
        self.data['ax0']['selflooppos'] = {i: (pos[i][0], pos[i][1] + .05) for i in pos}
        self.data['ax0']['lines'] = {}
        alpha = self.vars['edgealpha'].get()
        sizes = self.get_node_sizes()
        for e in self.graph.edges():
            x, y = [pos[e[0]][0], pos[e[1]][0]], [pos[e[0]][1], pos[e[1]][1]]
            if e[0] == e[1]:
                continue
            #     print('selfloop')
            #     self.data['ax0']['lines'][e] = self.plot['axes']['ax0'].scatter(pos[e[0]][0], pos[e[0]][1] + .05,
            #                                                                     s=sizes[e[0]] * 1.5, facecolors='none',
            #                                                                     edgecolors='k', zorder=0)
            #     continue
            self.data['ax0']['lines'][e], = self.plot['axes']['ax0'].plot(x, y, 'k', alpha=alpha, zorder=0)

        if self.graph.prop('selfloops'):
            self.data['ax0']['selfloops'] = self.plot['axes']['ax0'].scatter(*np.array(list(self.data['ax0']['selflooppos'].values())).T,
                                                                             s=sizes,
                                                                             facecolors='none', edgecolors='k',
                                                                             alpha=alpha, zorder=0)

        self.data['ax0']['nodes'] = self.plot['axes']['ax0'].scatter(*np.array(list(pos.values())).T,
                                                                     zorder=1, s=sizes)
        self.data['ax0']['nodelabels'] = {}
        labels = self.get_node_labels()
        for node in self.graph.nodes:
            self.data['ax0']['nodelabels'][node] = self.plot['axes']['ax0'].annotate(labels[node],
                                                                                     (pos[node][0],
                                                                                      pos[node][1]),
                                                                                      zorder=2)

        self.resize_nodes(None)
        self.realpha_nodes(None)
        self.recolor_nodes(None)
        self.realpha_edges(None)
        self.plot['canvas'].draw_idle()

    def clear(self):
        del self.graph
        self.graph = None
        self.data = {}
        for i in range(7):
            self.plot['axes'][f'ax{i}'].clear()
        self._init_plot(None)

    def get_node_sizes(self):
        if self.graph is None:
            return

        metric = self.vars['sizenodesby'].get()
        rawsizes = np.full(self.graph.prop('n'), self.vars['size'].get())
        if metric == '-':
            return rawsizes
        elif metric == 'betweenness':
            btwn = networkx.betweenness_centrality(self.graph).values()
            return [(a * b)**1.2 + 100 for a, b in zip(rawsizes, btwn)]
        elif metric == 'closeness':
            clsn = networkx.closeness_centrality(self.graph).values()
            return [(a * b)**1.2 + 100 for a, b in zip(rawsizes, clsn)]
        elif metric == 'clustering':
            clst = networkx.clustering(self.graph).values()
            return [(a * b)**1.2 + 100 for a, b in zip(rawsizes, clst)]
        elif metric == 'degree':
            dgr = networkx.degree_centrality(self.graph).values()
            return [(a * b) ** 1.2 + 100 for a, b in zip(rawsizes, dgr)]

    def get_node_labels(self):
        if self.graph is None:
            return
        metric = self.vars['labelnodesby'].get()
        if metric == '-':
            return {node: '' for node in self.graph}
        elif metric == 'name':
            return {node: str(node) for node in self.graph}
        elif metric == 'type':
            return {node: self.graph.prop('types')[node] for node in self.graph}
        elif metric == 'betweenness':
            btwn = networkx.betweenness_centrality(self.graph)
            return {node: round(btwn[node], 3) for node in self.graph}
        elif metric == 'closeness':
            clsn = networkx.closeness_centrality(self.graph)
            return {node: round(clsn[node], 3) for node in self.graph}
        elif metric == 'clustering':
            clst = networkx.clustering(self.graph)
            return {node: round(clst[node], 3) for node in self.graph}
        elif metric == 'degree':
            dgr = networkx.degree_centrality(self.graph)
            return {node: round(dgr[node], 3) for node in self.graph}
        elif metric == 'diff. space':
            return {node: str(self.graph.prop('diffusion_space')[node][1:-1]) for node in self.graph.nodes}

    def get_node_colors(self):
        if self.graph is None:
            return
        metric = self.vars['colornodesby'].get()
        if metric == '-':
            return {node: 'b' for node in self.graph}
        # elif metric == 'type':
        #     return {node: self.graph.prop('types')[node] for node in self.graph}
        elif metric == 'betweenness':
            btwn = networkx.betweenness_centrality(self.graph)
            return {node: COLORS(btwn[node]) for node in self.graph}
        elif metric == 'closeness':
            clsn = networkx.closeness_centrality(self.graph)
            return {node: COLORS(clsn[node]) for node in self.graph}
        elif metric == 'clustering':
            clst = networkx.clustering(self.graph)
            return {node: COLORS(clst[node]) for node in self.graph}
        elif metric == 'degree':
            dgr = networkx.degree_centrality(self.graph)
            return {node: COLORS(dgr[node]) for node in self.graph}

    def relabel_nodes(self, event):
        if self.graph is None:
            return
        labels = self.get_node_labels()
        for node in self.data['ax0']['nodelabels']:
            self.data['ax0']['nodelabels'][node].set_text(labels[node])
        self.plot['canvas'].draw_idle()

    def resize_nodes(self, event):
        if self.graph is None:
            return
        s = self.get_node_sizes()
        if self.graph.prop('selfloops'):
            self.data['ax0']['selfloops'].set_sizes(s)
        self.data['ax0']['nodes'].set_sizes(s)
        self.plot['canvas'].draw_idle()

    def realpha_nodes(self, event):
        if self.graph is None:
            return
        self.data['ax0']['nodes'].set_alpha(self.vars['nodealpha'].get())
        self.plot['canvas'].draw_idle()

    def recolor_nodes(self, event):
        if self.graph is None:
            return
        self.data['ax0']['nodes'].set_color(self.get_node_colors().values())
        self.plot['canvas'].draw_idle()

    def reposition_nodes(self, event):
        if self.graph is None:
            return
        self.data['ax0']['pos'] = self.get_positions()
        pos = np.array(list(self.data['ax0']['pos'].values())).T
        self.data['ax0']['nodes'].set_offsets(np.c_[pos[0], pos[1]])
        if self.graph.prop('selfloops'):
            self.data['ax0']['selflooppos'] = {i: (self.data['ax0']['pos'][i][0], self.data['ax0']['pos'][i][1] + .05)
                                               for i in self.data['ax0']['pos']}
            selflooppos = np.array(list(self.data['ax0']['selflooppos'].values())).T
            self.data['ax0']['selfloops'].set_offsets(np.c_[selflooppos[0], selflooppos[1]])
        for node in self.data['ax0']['nodelabels']:
            self.data['ax0']['nodelabels'][node].set_position((pos[0][node], pos[1][node]))
        self.realpha_nodes(None)
        self.realpha_edges(None)
        self.plot['canvas'].draw_idle()

    def realpha_edges(self, event):
        if self.graph is None:
            return
        alpha = self.vars['edgealpha'].get()
        for line in self.data['ax0']['lines']:
            self.data['ax0']['lines'][line].set_alpha(alpha)
        if self.graph.prop('selfloops'):
            self.data['ax0']['selfloops'].set_alpha(self.vars['edgealpha'].get())
        self.plot['canvas'].draw_idle()

    def reposition_edges(self):
        if self.graph is None:
            return
        pos = np.array(list(self.data['ax0']['pos'].values())).T
        alpha = self.vars['edgealpha'].get()
        for line in self.data['ax0']['lines'].keys():
            self.data['ax0']['lines'][line].set_xdata([pos[0][line[0]], pos[0][line[1]]])
            self.data['ax0']['lines'][line].set_ydata([pos[1][line[0]], pos[1][line[1]]])
            self.data['ax0']['lines'][line].set_alpha(alpha)


    def update_layout_handler(self, event):
        if not self.graph:
            return

        self.reposition_nodes(None)
        self.reposition_edges()

        self.plot['canvas'].draw_idle()

    def remove_edges(self, rmv):
        '''

        :param rmv:
        :return:
        '''
        for e in rmv:
            line = self.data['ax0']['lines'][e]
            self.plot['axes']['ax0'].lines.remove(line)
            del self.data['ax0']['lines'][e]

        self.reposition_nodes(None)
        self.reposition_edges()

        self.plot['canvas'].draw_idle()

    # def add_edges(self, add):
    #     '''
    #
    #     :param add:
    #     :return:
    #     '''
    #     for e in add:
    #         pass
    #         # line = self.data['ax0']['lines'][e]
    #         # self.plot['axes']['ax0'].lines.remove(line)
    #         # del self.data['ax0']['lines'][e]
    #
    #     self.reposition_nodes(None)
    #     self.reposition_edges()
    #
    #     self.plot['canvas'].draw_idle()

    def step(self):
        rmv, add = self.graph.step()
        self.remove_edges(rmv)
        self.resize_nodes(None)
        self.recolor_nodes(None)
        self.relabel_nodes(None)
        # self.add_edges(add)

    def play(self):
        if self.drawing:
            self.drawing = False
            self.buttons['play'].configure(text='Play')
            if self.parent is not None:
                self.parent.drawing = False
                self.parent.buttons['play'].configure(text='Play')
            # Stop animation
        else:
            self.drawing = True
            self.buttons['play'].configure(text='Pause')
            if self.parent is not None:
                self.parent.drawing = True
                self.parent.buttons['play'].configure(text='Pause')
            # animate