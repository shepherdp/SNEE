# GUI Class
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import tkinter as tk
import tkinter.ttk as ttk

import random
import tkdial

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

from helpers import ToolTip, TOOLTIP, DISTS, METRICS, xor
from SocialNetwork import PROPDEFAULTS, PROPSELECT, SocialNetwork

catcolors = ['b', 'yellow', 'red', 'green', 'purple', 'orange']

ERRCOLOR = 'pink'
WRNCOLOR = 'moccasin'
OKCOLOR = 'palegreen'
NRMCOLOR = 'white'

# COLORS = cm.viridis
# COLORS = cm.plasma
COLORS = cm.terrain
# COLORS = cm.RdYlGn

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
                         'numtransitions': tk.IntVar(),
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
                         'thresh_connect': tk.DoubleVar(),
                         'thresh_disconnect': tk.DoubleVar(),
                         'sizenodesby': tk.StringVar(),
                         'colornodesby': tk.StringVar(),
                         'labelnodesby': tk.StringVar(),
                         'alphaedgesby': tk.StringVar(),
                         'labeledgesby': tk.StringVar(),
                         'coloredgesby': tk.StringVar(),
                         'addnode': tk.StringVar(),
                         'delnode': tk.StringVar(),
                         'addedgefrom': tk.IntVar(),
                         'addedgeto': tk.IntVar(),
                         'deledgefrom': tk.IntVar(),
                         'deledgeto': tk.IntVar(),
                         'addedgelabel': tk.StringVar(),
                         'deledgelabel': tk.StringVar(),
                         'nodesize': tk.DoubleVar(),
                         'edgealpha': tk.DoubleVar(),
                         'nodealpha': tk.DoubleVar(),
                         'update_method': tk.StringVar(),
                         'distance': tk.StringVar(),
                         'recording': tk.BooleanVar(),
                         'collect_density': tk.BooleanVar(),
                         'collect_betweenness': tk.BooleanVar(),
                         'collect_closeness': tk.BooleanVar(),
                         'collect_clustering': tk.BooleanVar(),
                         'collect_degree': tk.BooleanVar(),
                         'collect_diffspace': tk.BooleanVar(),
                         'collect_avgdiffspace': tk.BooleanVar(),
                         'num_nodes_update': tk.IntVar(),
                         'num_nodes_connect': tk.IntVar(),
                         'num_nodes_disconnect': tk.IntVar(),
                         'num_connections': tk.IntVar(),
                         'num_disconnections': tk.IntVar(),
                         'num_influencers': tk.IntVar(),
                         }

            for i in range(1, 12):
                self.vars[f't_from{i}'] = tk.StringVar()
                self.vars[f't_to{i}'] = tk.StringVar()
                self.vars[f't_cond{i}'] = tk.StringVar()
                self.vars[f't_cond{i}'].set('auto')
                self.vars[f't_cont{i}'] = tk.StringVar()
                self.vars[f't_prob{i}'] = tk.DoubleVar()

            for i in range(1, 10):
                self.vars[f'catperc{i}'] = tk.DoubleVar()
                self.vars[f'catname{i}'] = tk.StringVar()

            for i in range(1, 7):
                self.vars[f'plot{i}data'] = tk.StringVar()
                self.vars[f'plot{i}color'] = tk.StringVar()

            for i in range(1, 4):
                self.vars[f'typename{i}'] = tk.StringVar()
                self.vars[f'typecolor{i}'] = tk.StringVar()
                self.vars[f'max_sim{i}'] = tk.DoubleVar()
                self.vars[f'gravity{i}'] = tk.DoubleVar()
                self.vars[f'resistance{i}'] = tk.DoubleVar()
                self.vars[f'confidence{i}'] = tk.DoubleVar()
                self.vars[f'percent_type{i}'] = tk.DoubleVar()

            for key in self.vars:
                if key in PROPDEFAULTS:
                    self.vars[key].set(PROPDEFAULTS[key])

            self.graph = None
            self.plotobjects = {f'ax{i}': None for i in range(7)}
            dataoptions = ['betweenness', 'closeness', 'density', 'degree', 'clustering', 'diff. space', 'diff. avg.']
            self.data = {metric: None for metric in dataoptions}
            self.drawing = False
            self.anim_id = None
            self.stepnum = 0
            self.num_categories = 0

        else:
            self.root = tk.Toplevel(self.parent.root)
            self.root.title('Command Center')
            self.vars = self.parent.vars
            self.graph = self.parent.graph
            self.plotobjects = self.parent.plotobjects
            self.drawing = self.parent.drawing
            self.anim_id = self.parent.anim_id
            self.data = self.parent.data
            self.stepnum = self.parent.stepnum
            self.num_categories = self.parent.num_categories

        self.tooltips = {}
        self.frames = {}
        self.inputs = {}
        self.labels = {}
        self.buttons = {}
        self.notebook = {}
        self.plot = {'axes':{}}
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
        '''

        :return:
        '''
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
            self.frames['plot'] = tk.LabelFrame(self.frames['window'], text='Visualization Panel', padx=5, pady=5)
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
        '''

        :return:
        '''
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

        self.labels['status'] = tk.Label(self.frames['status'], text='Ready', bg=OKCOLOR)
        self.labels['status'].pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=2, padx=6)

    def _init_plot(self, event):
        '''

        :param event:
        :return:
        '''
        nsubplots = self.vars['numplots'].get() - 1
        if 'fig' not in self.plot:
            self.plot['fig'] = Figure(figsize=(7, 5), dpi=100)
            self.plot['canvas'] = FigureCanvasTkAgg(self.plot['fig'], master=self.frames['plot'])
            self.plot['canvas'].draw()
            # self.plot['toolbar'] = NavigationToolbar2Tk(self.plot['canvas'], self.frames['plot'])
            # self.plot['toolbar'].update()
            self.plot['canvas'].get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        else:
            self.plot['fig'].clf()
            for i in range(1):
                if f'ax{i}' in self.plotobjects:
                    del self.plotobjects[f'ax{i}']
                    self.plotobjects[f'ax{i}'] = {}


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

        self.plot['fig'].subplots_adjust(bottom=0.05, left=0.025, top=0.975, right=0.975, hspace=0.1, wspace=0.1)
        self.plot['canvas'].draw()

        self.set_dataplot_entries()

    def update_subplots(self, event):
        '''

        :param event:
        :return:
        '''
        stored = {}
        if 'ax0' in self.plotobjects:
            if self.plotobjects['ax0'] is not None:
                stored['ax0'] = {i: self.plotobjects['ax0'][i] for i in self.plotobjects['ax0']}

        self._init_plot(None)

        if 'ax0' in stored:
            self.plotobjects['ax0'] = stored['ax0']

        for i in range(1, 7):
            if self.plotobjects[f'ax{i}'] is None:
                continue
            for item in self.plotobjects[f'ax{i}']:
                del item
                self.plotobjects[f'ax{i}'] = None

            self.update_subplot_data(i)

        self.create_plot()

    def _init_notebook(self):
        '''

        :return:
        '''
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
        self.notebook['diffusion'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['transmission'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['edit'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['types'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['output'] = ttk.Frame(self.notebook['notebook'])

        self.notebook['notebook'].add(self.notebook['parameters'], text='PRM')
        self.notebook['notebook'].add(self.notebook['animation'], text='ANI')
        self.notebook['notebook'].add(self.notebook['plots'], text='PLT')
        self.notebook['notebook'].add(self.notebook['evolution'], text='EVO')
        self.notebook['notebook'].add(self.notebook['diffusion'], text='DIF')
        self.notebook['notebook'].add(self.notebook['transmission'], text='TSM')
        self.notebook['notebook'].add(self.notebook['edit'], text='EDT')
        self.notebook['notebook'].add(self.notebook['types'], text='TYP')
        self.notebook['notebook'].add(self.notebook['output'], text='OUT')

        self.notebook['notebook'].grid(padx=5, pady=5, sticky=tk.N + tk.E + tk.S + tk.W)

        self._populate_parameters_tab()
        self._populate_animation_tab()
        self._populate_plots_tab()
        self._populate_evolution_tab()
        self._populate_diffusion_tab()
        self._populate_transmission_tab()
        self._populate_edit_tab()
        self._populate_types_tab()
        self._populate_output_tab()

    def _populate_parameters_tab(self):
        '''

        :return:
        '''
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
        self.set_tooltip('topology')

        self._place_input_label('saturation', 'topology', 'Saturation: ', row=1)
        self._place_input_entry('saturation', 'topology', row=1, col=1)
        self.set_tooltip('saturation')

        self._place_labelframe('edge_weights', self.notebook['parameters'], 'Weights')

        self._place_input_label('weight_dist', 'edge_weights', 'Weights: ')
        self._place_input_optionmenu('weight_dist', 'edge_weights', self.vars['weight_dist'].get(), DISTS, col=1,
                                     columnspan=3, sticky='ew', command=self.weight_dist_callback)

        self._place_input_label('weight_min', 'edge_weights', 'Min.: ', row=1)
        self._place_input_entry('weight_min', 'edge_weights', row=1, col=1)

        self._place_input_label('weight_max', 'edge_weights', 'Max.: ', row=1, col=2)
        self._place_input_entry('weight_max', 'edge_weights', row=1, col=3)

        self._place_input_label('weight_mean', 'edge_weights', 'Mean: ', row=2)
        self._place_input_entry('weight_mean', 'edge_weights', row=2, col=1)

        self._place_input_label('weight_stdev', 'edge_weights', 'Stdev: ', row=2, col=2)
        self._place_input_entry('weight_stdev', 'edge_weights', row=2, col=3)

        self._place_input_label('weight_const', 'edge_weights', 'Constant: ', row=3)
        self._place_input_entry('weight_const', 'edge_weights', row=3, col=1)

        self._place_input_checkbutton('normalize', 'edge_weights', text='Normalize', row=3, col=2, columnspan=2,
                                      sticky='e')

        self.set_trace('weight_min', self.weight_minmaxmean_callback)
        self.set_trace('weight_max', self.weight_minmaxmean_callback)
        self.set_trace('weight_mean', self.weight_minmaxmean_callback)
        self.set_trace('weight_stdev', self.weight_stdev_callback)

        self.set_tooltip('weight_dist')
        self.set_tooltip('weight_max')
        self.set_tooltip('weight_min')
        self.set_tooltip('weight_mean')
        self.set_tooltip('weight_stdev')
        self.set_tooltip('normalize')

    def _populate_animation_tab(self):
        '''

        :return:
        '''
        self._place_labelframe('animation', self.notebook['animation'], 'Animation')

        self._place_input_label('speed', 'animation', 'Speed: ', row=1, col=0)
        self._place_input_scale('speed', 'animation', 0, 5, 1, length=150, row=1, col=1, columnspan=3)
        self.set_tooltip('speed')

        self._place_input_label('layout', 'animation', 'Layout: ', row=0, col=0)
        if self.vars['layout'].get() == '':
            self.vars['layout'].set('spring')
        self._place_input_optionmenu('layout', 'animation', self.vars['layout'].get(),
                                     ['spring', 'circle', 'spiral', 'random', 'shell'], row=0, col=1, columnspan=2,
                                     sticky='ew', command=self.update_layout_handler)
        self.set_tooltip('layout')

        self._place_labelframe('nodes', self.notebook['animation'], 'Nodes')

        self._place_input_checkbutton('staticpos', 'nodes', row=0, col=0, sticky='w', text='Fixed pos.')
        self.set_tooltip('staticpos')
        self._place_input_label('nodesize', 'nodes', 'Size: ', row=0, col=1)
        self._place_input_scale('nodesize', 'nodes', 100, 700, 100, length=80, row=0, col=2, columnspan=2, sticky='ew',
                                command=self.resize_nodes)
        self.set_tooltip('nodesize')
        self._place_input_label('nodealpha', 'nodes', 'Alpha: ', row=1, col=0)
        if self.parent is not None:
            self.vars['nodealpha'].set(self.parent.vars['nodealpha'].get())
        else:
            self.vars['nodealpha'].set(1.)
        self._place_input_scale('nodealpha', 'nodes', 0, 1, .01, length=70, row=1, col=1, columnspan=2, sticky='ew',
                                command=self.realpha_nodes)
        self.set_tooltip('nodealpha')
        self._place_input_entry('nodealpha', 'nodes', row=1, col=3, sticky='e')

        self._place_input_label('labelnodesby', 'nodes', 'Label nodes: ', row=2, col=0)
        if self.vars['labelnodesby'].get() == '':
            self.vars['labelnodesby'].set('-')
        self._place_input_optionmenu('labelnodesby', 'nodes', self.vars['labelnodesby'].get(),
                                     ['-', 'name', 'type', 'diff. space'] + METRICS[1:], row=2, col=1, columnspan=3,
                                     sticky='ew', command=self.relabel_nodes)
        self._place_input_label('sizenodesby', 'nodes', 'Size nodes: ', row=3, col=0)
        if self.vars['sizenodesby'].get() == '':
            self.vars['sizenodesby'].set('-')
        self._place_input_optionmenu('sizenodesby', 'nodes', self.vars['sizenodesby'].get(), METRICS, row=3, col=1,
                                     columnspan=3, sticky='ew', command=self.resize_nodes)
        self._place_input_label('colornodesby', 'nodes', 'Color nodes: ', row=4, col=0)
        if self.vars['colornodesby'].get() == '':
            self.vars['colornodesby'].set('-')
        self._place_input_optionmenu('colornodesby', 'nodes', self.vars['colornodesby'].get(),
                                     ['-', 'type', 'diff. space'] + METRICS[1:], row=4, col=1, columnspan=3,
                                     command=self.recolor_nodes, sticky='ew')
        self.set_tooltip('labelnodesby')
        self.set_tooltip('sizenodesby')
        self.set_tooltip('colornodesby')

        self._place_labelframe('edges', self.notebook['animation'], 'Edges')

        self._place_input_label('edgealpha', 'edges', 'Alpha: ', row=0, col=0)
        if self.parent is not None:
            self.vars['edgealpha'].set(self.parent.vars['edgealpha'].get())
        else:
            self.vars['edgealpha'].set(.2)
        self._place_input_scale('edgealpha', 'edges', 0, 1, .01, length=70, row=0, col=1, columnspan=2,
                                command=self.realpha_edges)
        self.set_tooltip('edgealpha')
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
        self.set_tooltip('alphaedgesby')
        self.set_tooltip('labeledgesby')
        self.set_tooltip('coloredgesby')

        self._place_labelframe('record', self.notebook['animation'], 'Record Simulation')
        self._place_input_checkbutton('recording', 'record', row=0, col=0, sticky='w', text='Recording')
        self.buttons['convert'] = tk.Button(self.frames['record'], text='Convert')
        self.buttons['convert'].grid(row=0, column=3, pady=5, sticky='e')

    def _populate_plots_tab(self):
        '''

        :return:
        '''
        self._place_labelframe('dataplots', self.notebook['plots'], 'Data Plots')

        self._place_input_label('numplots', 'dataplots', '# Plots: ', row=0, col=0)
        self._place_input_scale('numplots', 'dataplots', 1, 7, 1, length=140, row=0, col=1, columnspan=4,
                                command=self.update_subplots)
        self.set_tooltip('numplots')
        button_funcs = {1: self.choose_color_plot1,
                        2: self.choose_color_plot2,
                        3: self.choose_color_plot3,
                        4: self.choose_color_plot4,
                        5: self.choose_color_plot5,
                        6: self.choose_color_plot6}
        for i in range(1, 7):
            self._place_input_label(f'plot{i}data', 'dataplots', f'Plot {i}: ', row=i, col=0)
            if self.vars[f'plot{i}data'].get() == '':
                self.vars[f'plot{i}data'].set('-')
            self._place_input_optionmenu(f'plot{i}data', 'dataplots', self.vars[f'plot{i}data'].get(),
                                         ['-', 'betweenness', 'closeness', 'density', 'degree', 'clustering',
                                          'diff. space', 'diff. avg.'], command=self.check_update_subplots,
                                         row=i, col=1, columnspan=3, sticky='ew')
            self.set_tooltip(f'plot{i}data')
            if self.parent is not None:
                color = self.parent.vars[f'plot{i}color'].get()
            else:
                color = 'black'
            self.vars[f'plot{i}color'].set(color)
            self.buttons[f'plot{i}color'] = tk.Button(self.frames['dataplots'], text='    ', bg=color,
                                                      command=button_funcs[i])
            self.buttons[f'plot{i}color'].grid(row=i, column=3, pady=5, sticky='e')

            self.labels[f'plot{i}data'].grid_forget()
            self.inputs[f'plot{i}data'].grid_forget()
            self.buttons[f'plot{i}color'].grid_forget()

    def _populate_evolution_tab(self):
        '''

        :return:
        '''
        self._place_labelframe('connect_dynamics', self.notebook['evolution'], 'Connection Dynamics')

        self._place_input_label('p_connect', 'connect_dynamics', 'Pr(+): ')
        self._place_input_scale('p_connect', 'connect_dynamics', 0, 1, .01, col=1, columnspan=2, length=100)
        self._place_input_entry('p_connect', 'connect_dynamics', col=3)

        self._place_input_label('thresh_connect', 'connect_dynamics', 'Thr(+): ', row=1)
        self._place_input_scale('thresh_connect', 'connect_dynamics', 0, 1, .01, row=1, col=1, columnspan=2, length=100)
        self._place_input_entry('thresh_connect', 'connect_dynamics', row=1, col=3)

        self._place_input_label('num_connections', 'connect_dynamics', 'Num nodes (+): ', row=2, columnspan=2)
        self._place_input_entry('num_connections', 'connect_dynamics', row=2, col=2)
        self._place_input_label('num_nodes_connect', 'connect_dynamics', '(+) per node: ', row=3, columnspan=2)
        self._place_input_entry('num_nodes_connect', 'connect_dynamics', row=3, col=2)

        self._place_labelframe('disconnect_dynamics', self.notebook['evolution'], 'Disconnection Dynamics')

        self._place_input_label('p_disconnect', 'disconnect_dynamics', 'Pr(-): ')
        self._place_input_scale('p_disconnect', 'disconnect_dynamics', 0, 1, .01, col=1, columnspan=2, length=100)
        self._place_input_entry('p_disconnect', 'disconnect_dynamics', col=3)

        self._place_input_label('thresh_disconnect', 'disconnect_dynamics', 'Thr(-): ', row=1)
        self._place_input_scale('thresh_disconnect', 'disconnect_dynamics', 0, 1, .01, row=1, col=1, columnspan=2, length=100)
        self._place_input_entry('thresh_disconnect', 'disconnect_dynamics', row=1, col=3)

        self._place_input_label('num_disconnections', 'disconnect_dynamics', 'Num nodes (-): ', row=2, columnspan=2)
        self._place_input_entry('num_disconnections', 'disconnect_dynamics', row=2, col=2)
        self._place_input_label('num_nodes_disconnect', 'disconnect_dynamics', '(-) per node: ', row=3, columnspan=2)
        self._place_input_entry('num_nodes_disconnect', 'disconnect_dynamics', row=3, col=2)

    def _populate_diffusion_tab(self):
        '''

        :return:
        '''
        self._place_labelframe('parameters', self.notebook['diffusion'], 'Diffusion Parameters')

        self._place_input_label('num_dimensions', 'parameters', 'Dimensions: ')
        self._place_input_entry('num_dimensions', 'parameters', col=1)

        self._place_input_label('num_nodes_update', 'parameters', 'Num to update: ', row=1)
        self._place_input_entry('num_nodes_update', 'parameters', row=1, col=1)
        self._place_input_label('num_infleuncers', 'parameters', 'Num influencers: ', row=2)
        self._place_input_entry('num_influencers', 'parameters', row=2, col=1)

        self._place_input_label('dimensions', 'parameters', 'Domain: ', row=3)
        self._place_input_optionmenu('dimensions', 'parameters', self.vars['dimensions'].get(), ['binary', 'continuous', 'categorical'],
                                     row=3, col=1, columnspan=3)

        self._place_input_label('visibility', 'parameters', 'Visibility: ', row=4)
        self._place_input_optionmenu('visibility', 'parameters', self.vars['visibility'].get(),
                                     ['visible', 'hidden', 'random'],
                                     row=4, col=1, columnspan=3)

        self._place_labelframe('diffusion', self.notebook['diffusion'], 'Diffusion Updates')

        self._place_input_label('p_update', 'diffusion', 'Pr(upd): ', row=0)
        self._place_input_scale('p_update', 'diffusion', 0, 1, .01, row=0, col=1, columnspan=2, length=90)
        self._place_input_entry('p_update', 'diffusion', row=0, col=3)

        self._place_input_label('update_method', 'diffusion', 'Updates: ', row=4)
        if self.vars['update_method'].get() == '':
            self.vars['update_method'].set('-')
        self._place_input_optionmenu('update_method', 'diffusion', self.vars['update_method'].get(),
                                     ['-', 'voter', 'majority', 'average', 'wt. avg.'],
                                     row=4, col=1, columnspan=3, sticky='ew')

        self._place_input_label('distance', 'diffusion', 'Distance: ', row=1)
        if self.vars['distance'].get() == '':
            self.vars['distance'].set('hamming')
        self._place_input_optionmenu('distance', 'diffusion', self.vars['distance'].get(),
                                     ['hamming', 'euclidean', 'cosine'],
                                     row=1, col=1, columnspan=3, sticky='ew')

        self._place_labelframe('transmission_msg', self.notebook['diffusion'], 'Transmission Model')

        msg = '''For categorical diffusion variables,
you must define a transmission model.
See the TSM tab.'''
        self._place_input_label('transmission_message', 'transmission_msg', msg, row=0)

        self.set_trace('dimensions', self.update_model_callback)

    def _populate_transmission_tab(self):
        '''

        :return:
        '''
        self._place_labelframe('transmission_wait', self.notebook['transmission'], 'Transmission Model')

        msg = '''Your current settings apply to a
judgement aggregation model.  To use
a transmission model, please choose
\'categorical\' as the Domain in the
DIF tab.'''
        self._place_input_label('transmission_wait', 'transmission_wait', msg, row=0, col=0)

        self._place_labelframe('transmission', self.notebook['transmission'], 'Transmission Model')

        self._place_input_label('numtransitions', 'transmission', '# Rules: ', row=0, col=0, columnspan=2)
        self._place_input_scale('numtransitions', 'transmission', 1, 11, 1, length=140, row=0, col=2, columnspan=3,
                                command=self.set_transmission_entries)

        self._place_input_label('t_from_label', 'transmission', 'From', row=1, sticky='w')
        self._place_input_label('t_to_label', 'transmission', 'To', row=1, col=1, sticky='w')
        self._place_input_label('t_cond_label', 'transmission', 'Condition         ', row=1, col=2, sticky='w')
        self._place_input_label('t_contactwith_label', 'transmission', '', row=1, col=3, sticky='w')
        self._place_input_label('t_transmissionprob_label', 'transmission', 'Pr', row=1, col=4, sticky='w')

        for i in range(1, 12):
            self._place_input_entry(f't_from{i}', 'transmission', row=i + 1, col=0, width=4)
            self._place_input_entry(f't_to{i}', 'transmission', row=i + 1, col=1, width=4)
            self._place_input_optionmenu(f't_cond{i}', 'transmission', self.vars[f't_cond{i}'].get(),
                                         ['auto', 'contact'], row=i + 1, col=2,
                                         columnspan=1, sticky='ew', command=self.category_update_callback)
            self._place_input_entry(f't_cont{i}', 'transmission', row=i + 1, col=3, width=4)
            self._place_input_entry(f't_prob{i}', 'transmission', row=i + 1, col=4, width=4)

            self.set_trace(f't_from{i}', self.category_update_callback)
            self.set_trace(f't_to{i}', self.category_update_callback)
            self.set_trace(f't_cont{i}', self.category_update_callback)
            self.set_trace(f't_prob{i}', self.check_transmission_probs)

            self.inputs[f't_from{i}'].grid_forget()
            self.inputs[f't_to{i}'].grid_forget()
            self.inputs[f't_cond{i}'].grid_forget()
            self.inputs[f't_cont{i}'].grid_forget()
            self.inputs[f't_prob{i}'].grid_forget()

        self._place_labelframe('category_distribution', self.notebook['transmission'], 'Distribution')

        self._place_input_label('namecollabel1', 'category_distribution', text='Val', row=0, col=0)
        self._place_input_label('namecollabel2', 'category_distribution', text='Val', row=0, col=2)
        self._place_input_label('namecollabel3', 'category_distribution', text='Val', row=0, col=4)
        self._place_input_label('namecollabel1', 'category_distribution', text='%', row=0, col=1)
        self._place_input_label('namecollabel1', 'category_distribution', text='%', row=0, col=3)
        self._place_input_label('namecollabel1', 'category_distribution', text='%', row=0, col=5)

        for i in range(3):
            for j in range(3):
                self._place_input_label(f'catname{3*i + j + 1}', 'category_distribution', text='   ', row=i + 1, col=2 * j,
                                        var=self.vars[f'catname{3*i + j + 1}'])
                self._place_input_entry(f'catperc{3*i + j + 1}', 'category_distribution', row=i + 1, col=2 * j + 1)

                self.set_trace(f'catname{3*i + j + 1}', self.trace_catname)
                self.set_trace(f'catperc{3 * i + j + 1}', self.trace_catname)

    def _populate_edit_tab(self):
        '''

        :return:
        '''
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
        self._place_input_label('tolabel', 'edgeedit', 'To', row=0, col=2, sticky='ew')
        self._place_input_label('labellabel', 'edgeedit', 'Label', row=0, col=3, sticky='ew')
        self._place_input_label('addedge', 'edgeedit', 'Add: ', row=1, col=0)
        self._place_input_entry('addedgefrom', 'edgeedit', row=1, col=1)
        self._place_input_entry('addedgeto', 'edgeedit', row=1, col=2)
        self._place_input_entry('addedgelabel', 'edgeedit', row=1, col=3)
        self.buttons['addedge'] = tk.Button(self.frames['edgeedit'], text='+', width=5, command=self.add_edge_from_panel)
        self.buttons['addedge'].grid(row=1, column=4, sticky='e')
        self._place_input_label('deledge', 'edgeedit', 'Del: ', row=2, col=0)
        self._place_input_entry('deledgefrom', 'edgeedit', row=2, col=1)
        self._place_input_entry('deledgeto', 'edgeedit', row=2, col=2)
        self._place_input_entry('deledgelabel', 'edgeedit', row=2, col=3)
        self.buttons['deledge'] = tk.Button(self.frames['edgeedit'], text='-', width=5, command=self.remove_edge_from_panel)
        self.buttons['deledge'].grid(row=2, column=4, sticky='e')

    def _populate_types_tab(self):
        '''

        :return:
        '''
        colors = ['blue', 'red', 'green']
        callbacks = [self.choose_color_type1, self.choose_color_type2, self.choose_color_type3]
        funcs = {'max_sim1': self.set_maxsim_1, 'gravity1': self.set_gravity_1,
                 'confidence1': self.set_confidence_1, 'resistance1': self.set_resistance_1,
                 'max_sim2': self.set_maxsim_2, 'gravity2': self.set_gravity_2,
                 'confidence2': self.set_confidence_2, 'resistance2': self.set_resistance_2,
                 'max_sim3': self.set_maxsim_3, 'gravity3': self.set_gravity_3,
                 'confidence3': self.set_confidence_3, 'resistance3': self.set_resistance_3
                 }
        for i in range(1, 4):
            self._place_labelframe(f'type{i}', self.notebook['types'], f'Agent Type {i}')

            self._place_input_label(f'typename{i}', f'type{i}', 'Name', row=0, col=0, sticky='ew')
            self._place_input_entry(f'typename{i}', f'type{i}', width=15, row=0, col=1, columnspan=3)
            if self.parent is not None:
                color = self.parent.vars[f'typecolor{i}'].get()
            else:
                color = colors[i-1]
                self.vars[f'typecolor{i}'].set(color)
            self.buttons[f'typecolor{i}'] = tk.Button(self.frames[f'type{i}'], width=1, text=' ', bg=color,
                                                      command=callbacks[i-1])
            self.buttons[f'typecolor{i}'].grid(row=0, column=3)

            self._place_input_label(f'max_sim{i}', f'type{i}', 'Max Sim', row=1, sticky='ew')
            self._place_input_label(f'gravity{i}', f'type{i}', 'Gravity', row=1, col=1, sticky='ew')
            self._place_input_label(f'confidence{i}', f'type{i}', 'Confid.', row=1, col=2, sticky='ew')
            self._place_input_label(f'resistance{i}', f'type{i}', 'Resist.', row=1, col=3, sticky='ew')

            self.inputs[f'max_sim_dial{i}'] = tkdial.Dial(self.frames[f'type{i}'], radius=8, text='', color_gradient=('white', 'blue'),
                                                        unit_length=5, unit_width=7, command=funcs[f'max_sim{i}'])
            self.inputs[f'max_sim_dial{i}'].grid(row=2, pady=2)

            self.inputs[f'gravity_dial{i}'] = tkdial.Dial(self.frames[f'type{i}'], radius=8, text='', color_gradient=('pink', 'blue'),
                                                     unit_length=5, unit_width=7, command=funcs[f'gravity{i}'], start=-100)
            self.inputs[f'gravity_dial{i}'].grid(row=2, column=1, pady=2)
            self.inputs[f'confidence_dial{i}'] = tkdial.Dial(self.frames[f'type{i}'], radius=8, text='', color_gradient=('white', 'blue'),
                                                        unit_length=5, unit_width=7, command=funcs[f'confidence{i}'])
            self.inputs[f'confidence_dial{i}'].grid(row=2, column=2, pady=2)
            self.inputs[f'resistance_dial{i}'] = tkdial.Dial(self.frames[f'type{i}'], radius=8, text='', color_gradient=('white', 'blue'),
                                                        unit_length=5, unit_width=7, command=funcs[f'resistance{i}'])
            self.inputs[f'resistance_dial{i}'].grid(row=2, column=3, pady=2)

            self._place_input_entry(f'max_sim{i}', f'type{i}', row=3, sticky='ew')
            self._place_input_entry(f'gravity{i}', f'type{i}', row=3, col=1, sticky='ew')
            self._place_input_entry(f'confidence{i}', f'type{i}', row=3, col=2, sticky='ew')
            self._place_input_entry(f'resistance{i}', f'type{i}', row=3, col=3, sticky='ew')

            self.vars[f'max_sim{i}'].set(1.)
            self.inputs[f'max_sim_dial{i}'].set(100)
            self.vars[f'gravity{i}'].set(0.)
            self.inputs[f'gravity_dial{i}'].set(0)
            self.vars[f'confidence{i}'].set(1.)
            self.inputs[f'confidence_dial{i}'].set(100)
            self.vars[f'resistance{i}'].set(0.)
            self.inputs[f'resistance_dial{i}'].set(0)
            self.vars[f'percent_type{i}'].set(1.)

            if self.parent is not None:
                for label in ['max_sim', 'gravity', 'confidence', 'resistance']:
                    self.inputs[f'{label}_dial{i}'].set(self.parent.inputs[f'{label}_dial{i}'].get())
                    self.vars[f'{label}{i}'].set(self.parent.vars[f'{label}{i}'].get())

            self._place_input_label(f'percent_type{i}', f'type{i}', 'Percent:', row=4)
            self._place_input_scale(f'percent_type{i}', f'type{i}', 0, 1, .01, row=4, col=1, columnspan=2, length=75)
            self._place_input_entry(f'percent_type{i}', f'type{i}', row=4, col=3, sticky='ew')

            self.vars[f'percent_type{i}'].set(0.)

        self.inputs['gravity1'].bind("<FocusOut>", self.set_gravitydial_1)
        self.inputs['gravity2'].bind("<FocusOut>", self.set_gravitydial_2)
        self.inputs['gravity3'].bind("<FocusOut>", self.set_gravitydial_3)
        self.inputs['max_sim1'].bind("<FocusOut>", self.set_maxsimdial_1)
        self.inputs['max_sim2'].bind("<FocusOut>", self.set_maxsimdial_2)
        self.inputs['max_sim3'].bind("<FocusOut>", self.set_maxsimdial_3)
        self.inputs['confidence1'].bind("<FocusOut>", self.set_confidencedial_1)
        self.inputs['confidence2'].bind("<FocusOut>", self.set_confidencedial_2)
        self.inputs['confidence3'].bind("<FocusOut>", self.set_confidencedial_3)
        self.inputs['resistance1'].bind("<FocusOut>", self.set_resistancedial_1)
        self.inputs['resistance2'].bind("<FocusOut>", self.set_resistancedial_2)
        self.inputs['resistance3'].bind("<FocusOut>", self.set_resistancedial_3)

        self.set_trace('percent_type1', self.typeperc_callback)
        self.set_trace('percent_type2', self.typeperc_callback)
        self.set_trace('percent_type3', self.typeperc_callback)
        self.set_trace('typename1', self.typeperc_callback)
        self.set_trace('typename2', self.typeperc_callback)
        self.set_trace('typename3', self.typeperc_callback)

        self.vars['typename1'].set('default')
        self.vars['max_sim1'].set(1.)
        self.inputs['max_sim_dial1'].set(100)
        self.vars['gravity1'].set(1.)
        self.inputs['gravity_dial1'].set(100)
        self.vars['confidence1'].set(1.)
        self.inputs['confidence_dial1'].set(100)
        self.vars['resistance1'].set(0.)
        self.inputs['resistance_dial1'].set(0)
        self.vars['percent_type1'].set(1.)

    def _populate_output_tab(self):
        '''

        :return:
        '''
        self._place_labelframe('metrics', self.notebook['output'], 'Data Collection')

        self._place_input_checkbutton('collect_degree', 'metrics', row=0, col=0, sticky='w', text='Degree')
        self._place_input_checkbutton('collect_betweenness', 'metrics', row=1, col=0, sticky='w', text='Betweenness')
        self._place_input_checkbutton('collect_closeness', 'metrics', row=2, col=0, sticky='w', text='Closeness')
        self._place_input_checkbutton('collect_clustering', 'metrics', row=3, col=0, sticky='w', text='Clustering')
        self._place_input_checkbutton('collect_diffspace', 'metrics', row=4, col=0, sticky='w', text='Diffusion Space')
        self._place_input_checkbutton('collect_avgdiffspace', 'metrics', row=5, col=0, sticky='w', text='Averaged Diffusion Space')

    def check_transmission_probs(self, *args):
        '''

        :param args:
        :return:
        '''
        for i in range(1, self.vars['numtransitions'].get() + 1):
            try:
                if self.vars[f't_prob{i}'].get() > 1:
                    self.inputs[f't_prob{i}'].configure(bg=ERRCOLOR)
                else:
                    if self.inputs[f't_prob{i}'].cget('bg') == ERRCOLOR:
                        self.reset_bgcolor([f't_prob{i}'])
            except:
                self.inputs[f't_prob{i}'].configure(bg=ERRCOLOR)

    def category_update_callback(self, *args):
        '''

        :param args:
        :return:
        '''
        num = self.vars['numtransitions'].get()
        old = []
        oldnames = []
        for i in range(9):
            if self.vars[f'catname{i+1}'].get() != '':
                try:
                    old.append((self.vars[f'catname{i+1}'].get(), self.vars[f'catperc{i+1}'].get(), i+1))
                except:
                    old.append((self.vars[f'catname{i + 1}'].get(), 0., i + 1))
                oldnames.append(self.vars[f'catname{i + 1}'].get())
        newnames = set()
        for i in range(1, num + 1):
            fromname = self.vars[f't_from{i}'].get()
            toname = self.vars[f't_to{i}'].get()
            contname = self.vars[f't_cont{i}'].get()
            newnames.add(fromname)
            newnames.add(toname)
            if xor(fromname == '', toname == ''):
                self.inputs[f't_from{i}'].configure(bg=ERRCOLOR)
                self.inputs[f't_to{i}'].configure(bg=ERRCOLOR)
            else:
                if self.inputs[f't_from{i}'].cget('bg') == ERRCOLOR or self.inputs[f't_to{i}'].cget('bg') == ERRCOLOR:
                    self.reset_bgcolor([f't_from{i}', f't_to{i}'])
            if self.vars[f't_cond{i}'].get() == 'contact' and contname == '':
                self.inputs[f't_cont{i}'].configure(bg=ERRCOLOR)
            else:
                if self.inputs[f't_cont{i}'].cget('bg') == ERRCOLOR:
                    self.reset_bgcolor([f't_cont{i}'])
            if contname != '':
                self.vars[f't_cond{i}'].set('contact')
            newnames.add(contname)
        if '' in newnames: newnames.remove('')
        newnames = list(newnames)
        new = []
        for name, val, idx in old:
            if name not in newnames:
                self.vars[f'catname{i}'].set('')
                self.vars[f'catperc{i}'].set(0.)
                continue
            newnames.remove(name)
            new.append((name, val))
        for name in newnames:
            new.append((name, 0.))
        for i in range(len(new)):
            name, val = new[i]
            self.vars[f'catname{i+1}'].set(name)
            self.vars[f'catperc{i+1}'].set(val)
            self.labels[f'catname{i+1}'].grid(row=(i // 3) + 1, column=2 * (i % 3))
            self.inputs[f'catperc{i+1}'].grid(row=(i // 3) + 1, column=2 * (i % 3) + 1)
        for i in range(len(new), 9):
            self.labels[f'catname{i+1}'].grid_forget()
            self.inputs[f'catperc{i+1}'].grid_forget()

        self.num_categories = len(new)

        self.trace_catname()

    def trace_catname(self, *args):
        '''

        :param args:
        :return:
        '''
        names = [self.vars[f'catname{i}'].get() for i in range(1, self.num_categories + 1) if self.vars[f'catname{i}'].get() != '']
        percs = []
        for i, _ in enumerate(names):
            try:
                percs.append(self.vars[f'catperc{i+1}'].get())
            except:
                percs.append(0.)
        total = sum(percs)
        if total != 1.:
            for i, _ in enumerate(names):
                self.inputs[f'catperc{i+1}'].configure(bg=ERRCOLOR)
        else:
            for i, _ in enumerate(names):
                self.reset_bgcolor([f'catperc{i+1}'])

    def _place_labelframe(self, tag, parent, text):
        '''

        :param tag:
        :param parent:
        :param text:
        :return:
        '''
        self.frames[tag] = tk.LabelFrame(parent, text=text, padx=5, pady=3)
        self.frames[tag].pack(fill=tk.BOTH, padx=5)

    def _place_input_label(self, tag, framename, text, row=0, col=0, sticky='e', columnspan=1, var=None):
        '''

        :param tag:
        :param framename:
        :param text:
        :param row:
        :param col:
        :param sticky:
        :param columnspan:
        :param var:
        :return:
        '''
        self.labels[tag] = tk.Label(self.frames[framename], text=text, padx=2, textvariable=var)
        self.labels[tag].grid(row=row, column=col, padx=2, sticky=sticky, columnspan=columnspan)

    def _place_input_entry(self, tag, framename, width=5, row=0, col=0, columnspan=1, sticky='w'):
        '''

        :param tag:
        :param framename:
        :param width:
        :param row:
        :param col:
        :param columnspan:
        :param sticky:
        :return:
        '''
        self.inputs[tag] = tk.Entry(self.frames[framename], textvariable=self.vars[tag], width=width)
        self.inputs[tag].grid(row=row, column=col, columnspan=columnspan, padx=2, sticky=sticky)

    def _place_input_checkbutton(self, tag, framename, row=0, col=0, sticky='w', text=None, columnspan=1,
                                 command=None):
        '''

        :param tag:
        :param framename:
        :param row:
        :param col:
        :param sticky:
        :param text:
        :param columnspan:
        :param command:
        :return:
        '''
        self.inputs[tag] = tk.Checkbutton(self.frames[framename], variable=self.vars[tag], text=text, padx=2,
                                          command=command)
        self.inputs[tag].grid(row=row, column=col, padx=2, sticky=sticky, columnspan=columnspan)

    def _place_input_optionmenu(self, tag, framename, firstoption, vals, row=0, col=0, columnspan=1, sticky='w',
                                command=None):
        '''

        :param tag:
        :param framename:
        :param firstoption:
        :param vals:
        :param row:
        :param col:
        :param columnspan:
        :param sticky:
        :param command:
        :return:
        '''
        self.inputs[tag] = ttk.OptionMenu(self.frames[framename], self.vars[tag], firstoption, *vals, command=command)
        self.inputs[tag].grid(row=row, column=col, padx=2, columnspan=columnspan, sticky=sticky)

    def _place_input_scale(self, tag, framename, lo, hi, res, length=100, showvalue=False, row=0, col=0,
                           columnspan=1, sticky='ew', command=None, orientation='horizontal'):
        '''

        :param tag:
        :param framename:
        :param lo:
        :param hi:
        :param res:
        :param length:
        :param showvalue:
        :param row:
        :param col:
        :param columnspan:
        :param sticky:
        :param command:
        :param orientation:
        :return:
        '''
        self.inputs[tag] = tk.Scale(self.frames[framename], length=length, variable=self.vars[tag], label=None,
                                    resolution=res, orient=orientation, from_=lo, to=hi, showvalue=showvalue,
                                    command=command)
        self.inputs[tag].grid(row=row, column=col, columnspan=columnspan, padx=5, sticky=sticky)

    def update_status(self, msg, color='black'):
        '''

        :param msg:
        :param color:
        :return:
        '''
        self.labels['status'].configure(text=msg, bg=color)

    def directed_callback(self):
        '''

        :return:
        '''
        if not self.vars['directed'].get():
            self.vars['symmetric'].set(True)
            self.disable_vars('symmetric')
        else:
            self.enable_vars('symmetric')

    def typeperc_callback(self, *args):
        '''

        :param args:
        :return:
        '''
        idxs = [i for i in range(1, 4) if self.vars[f'typename{i}'].get() != '']
        try:
            percs = [self.vars[f'percent_type{i}'].get() for i in idxs]
            if abs(sum(percs)- 1) > .0000001:
                for i in idxs:
                    self.inputs[f'percent_type{i}'].configure(bg=ERRCOLOR)
            else:
                for i in idxs:
                    if self.inputs[f'percent_type{i}'].cget('bg') == ERRCOLOR:
                        self.reset_bgcolor([f'percent_type{i}'])
        except:
            for i in idxs:
                self.inputs[f'percent_type{i}'].configure(bg=ERRCOLOR)

    def n_callback(self, *args):
        '''

        :param args:
        :return:
        '''
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
        '''

        :param args:
        :return:
        '''
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
                self.tooltips['weight_min'].update(TOOLTIP['weight_min']['error'], ERRCOLOR)
                self.tooltips['weight_max'].update(TOOLTIP['weight_max']['error'], ERRCOLOR)
            else:
                for tag in ['weight_min', 'weight_max']:
                    if tag in self.problems:
                        self.problems.remove(tag)
                self.reset_bgcolor(['weight_min', 'weight_max'])
                self.tooltips['weight_min'].update(TOOLTIP['weight_min']['normal'], NRMCOLOR)
                self.tooltips['weight_max'].update(TOOLTIP['weight_max']['normal'], NRMCOLOR)

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
                self.tooltips['weight_min'].update(TOOLTIP['weight_min']['error'], ERRCOLOR)
                self.tooltips['weight_max'].update(TOOLTIP['weight_max']['error'], ERRCOLOR)
                self.tooltips['weight_mean'].update(TOOLTIP['weight_mean']['error'], ERRCOLOR)

            else:
                for tag in ['weight_min', 'weight_max', 'weight_mean']:
                    if tag in self.problems:
                        self.problems.remove(tag)
                self.reset_bgcolor(['weight_min', 'weight_max', 'weight_mean'])
                self.tooltips['weight_mean'].update(TOOLTIP['weight_mean']['normal'], NRMCOLOR)
                self.tooltips['weight_max'].update(TOOLTIP['weight_max']['normal'], NRMCOLOR)
                self.tooltips['weight_min'].update(TOOLTIP['weight_min']['normal'], NRMCOLOR)

    def weight_stdev_callback(self, *args):
        '''

        :param args:
        :return:
        '''
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
            self.tooltips['weight_stdev'].update(TOOLTIP['weight_stdev']['warn'], WRNCOLOR)
        else:
            if 'weight_stdev' in self.problems:
                self.problems.remove('weight_stdev')
                self.reset_bgcolor(['weight_stdev'])
                self.tooltips['weight_stdev'].update(TOOLTIP['weight_stdev']['normal'], NRMCOLOR)

    def weight_dist_callback(self, *args):
        '''

        :param args:
        :return:
        '''
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
        '''

        :param tags:
        :param firstcall:
        :return:
        '''
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
        '''

        :return:
        '''
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
        '''

        :param event:
        :return:
        '''
        top = self.vars['topology'].get()

    def disable_vars(self, *vars):
        '''

        :param vars:
        :return:
        '''
        for var in vars:
            self.inputs[var].configure(state='disabled')

    def enable_vars(self, *vars):
        '''

        :param vars:
        :return:
        '''
        for var in vars:
            self.inputs[var].configure(state='normal')

    def invoke_callbacks(self):
        '''

        :return:
        '''
        self.weight_minmaxmean_callback()
        self.weight_stdev_callback()
        self.weight_dist_callback()
        self.n_callback()
        self.directed_callback()
        self.set_dataplot_entries()
        self.update_model_callback()
        self.set_transmission_entries(None)
        self.category_update_callback()

    def set_trace(self, tag, callback):
        '''

        :param tag:
        :param callback:
        :return:
        '''
        self.vars[tag].trace('w', callback)

    def update_model_callback(self, *args):
        '''

        :param args:
        :return:
        '''
        val = self.vars['dimensions'].get()
        if val == 'categorical':
            self.frames['diffusion'].pack_forget()
            self.frames['transmission_msg'].pack(fill=tk.BOTH, padx=5)
            self.frames['transmission_wait'].pack_forget()
            self.frames['transmission'].pack(fill=tk.BOTH, padx=5)
            self.frames['category_distribution'].pack(fill=tk.BOTH, padx=5)
            self.vars['update_method'].set('transmission')
        else:
            self.frames['transmission_msg'].pack_forget()
            self.frames['diffusion'].pack(fill=tk.BOTH, padx=5)
            self.frames['transmission_wait'].pack(fill=tk.BOTH, padx=5)
            self.frames['transmission'].pack_forget()
            self.frames['category_distribution'].pack_forget()

    def set_dataplot_entries(self):
        '''

        :return:
        '''
        if 'fig' not in self.plot:
            return
        nsubplots = self.vars['numplots'].get()
        for i in range(1, nsubplots):
            self.labels[f'plot{i}data'].grid(row=i, column=0)
            self.inputs[f'plot{i}data'].grid(row=i, column=1, columnspan=3, sticky='ew')
            self.buttons[f'plot{i}color'].grid(row=i, column=4, pady=2, sticky='e')
        for i in range(nsubplots, 7):
            self.labels[f'plot{i}data'].grid_forget()
            self.inputs[f'plot{i}data'].grid_forget()
            self.buttons[f'plot{i}color'].grid_forget()

    def set_transmission_entries(self, event):
        '''

        :param event:
        :return:
        '''
        if 'fig' not in self.plot:
            return
        nrules = self.vars['numtransitions'].get()
        for i in range(1, nrules + 1):
            self.inputs[f't_from{i}'].grid(row=i + 1, column=0)
            self.inputs[f't_to{i}'].grid(row=i + 1, column=1)
            self.inputs[f't_cond{i}'].grid(row=i + 1, column=2)
            self.inputs[f't_cont{i}'].grid(row=i + 1, column=3)
            self.inputs[f't_prob{i}'].grid(row=i + 1, column=4)
        for i in range(nrules + 1, 12):
            self.inputs[f't_from{i}'].grid_forget()
            self.inputs[f't_to{i}'].grid_forget()
            self.inputs[f't_cond{i}'].grid_forget()
            self.inputs[f't_cont{i}'].grid_forget()
            self.inputs[f't_prob{i}'].grid_forget()

        self.category_update_callback()

    def set_tooltip(self, tag):
        '''

        :param tag:
        :return:
        '''
        self.tooltips[tag] = ToolTip(self.inputs[tag], TOOLTIP[tag]['normal'])

    def construct(self):
        '''

        :return:
        '''
        if self.graph is not None:
            self.update_status('Graph already exists.', ERRCOLOR)
            return
        for i in self.inputs:
            if self.inputs[i].cget('state') == 'normal' and self.inputs[i].cget('bg') == ERRCOLOR:
                print('Please correct parameter errors.')
                return
        vals = self.get_vals_for_construct()
        self.graph = SocialNetwork(**vals)
        self.create_plot()
        self.update_status('Graph constructed', OKCOLOR)
        # self.graph.prop()

    def get_positions(self):
        '''

        :return:
        '''
        if self.graph is None:
            return
        layout = self.vars['layout'].get()
        pos = None
        if 'pos' in self.plotobjects['ax0']:
            pos = self.plotobjects['ax0']['pos']
            if self.vars['staticpos'].get():
                return pos
        if layout == 'spring':
            return networkx.spring_layout(self.graph.instance, pos=pos)
        elif layout == 'circle':
            return networkx.circular_layout(self.graph.instance)
        elif layout == 'spiral':
            return networkx.spiral_layout(self.graph.instance)
        elif layout == 'shell':
            return networkx.shell_layout(self.graph.instance)
        elif layout == 'random':
            return networkx.random_layout(self.graph.instance)

    def create_plot(self):
        '''

        :return:
        '''
        if self.graph is None:
            return
        if 'ax0' not in self.plotobjects:
            self.plotobjects['ax0'] = {}
        elif self.plotobjects['ax0'] is None:
            self.plotobjects['ax0'] = {}
        if 'pos' not in self.plotobjects['ax0']:
            self.plotobjects['ax0']['pos'] = self.get_positions()
        elif self.plotobjects['ax0']['pos'] is None:
            self.plotobjects['ax0']['pos'] = self.get_positions()
        pos = self.plotobjects['ax0']['pos']
        if self.graph.prop('selfloops'):
            self.plotobjects['ax0']['selflooppos'] = {i: (self.plotobjects['ax0']['pos'][i][0], self.plotobjects['ax0']['pos'][i][1] + .02)
                                                      for i in self.plotobjects['ax0']['pos']}
        self.plotobjects['ax0']['lines'] = {}
        alpha = self.vars['edgealpha'].get()
        sizes = self.get_node_sizes()

        self.add_edges(self.graph.edges)

        if self.graph.prop('selfloops'):
            news = sizes * 1.25
            self.plotobjects['ax0']['selfloops'] = self.plot['axes']['ax0'].scatter(*np.array(list(self.plotobjects['ax0']['selflooppos'].values())).T,
                                                                             s=news,
                                                                             facecolors='none', edgecolors='k',
                                                                             alpha=alpha, zorder=0)

        self.plotobjects['ax0']['nodes'] = self.plot['axes']['ax0'].scatter(*np.array(list(pos.values())).T,
                                                                     zorder=1, s=sizes)
        self.plotobjects['ax0']['nodelabels'] = {}
        labels = self.get_node_labels()
        for node in self.graph.nodes:
            self.plotobjects['ax0']['nodelabels'][node] = self.plot['axes']['ax0'].annotate(labels[node],
                                                                                     (pos[node][0],
                                                                                      pos[node][1]),
                                                                                      zorder=2)

        self.resize_nodes(None)
        self.realpha_nodes(None)
        self.recolor_nodes(None)
        self.realpha_edges(None)

        self.plot['axes']['ax0'].set_xlim([-1.1, 1.1])
        self.plot['axes']['ax0'].set_ylim([-1.1, 1.1])
        self.plot['canvas'].draw_idle()

    def check_update_subplots(self, event):
        '''

        :param event:
        :return:
        '''
        if 'axmetrics' not in self.data:
            self.data['axmetrics'] = {}
        for i in range(1, 7):
            if f'ax{i}' not in self.plot['axes']:
                continue

            if f'plot{i}data' not in self.data['axmetrics']:
                metric = self.vars[f'plot{i}data'].get()
                varnames = {'density': 'collect_density',
                            'betweenness': 'collect_betweenness',
                            'closeness': 'collect_closeness',
                            'clustering': 'collect_clustering',
                            'degree': 'collect_degree',
                            'diff. space': 'collect_diffspace',
                            'diff. avg.': 'collect_avgdiffspace'}
                if metric != '-':
                    self.data['axmetrics'][f'plot{i}data'] = metric
                    self.vars[varnames[metric]].set(True)
                continue
            if self.vars[f'plot{i}data'].get() != self.data['axmetrics'][f'plot{i}data']:
                self.data['axmetrics'][f'plot{i}data'] = self.vars[f'plot{i}data'].get()
                self.clear_subplot(i)
                self.update_subplot_data(i)

    def clear_subplot(self, i):
        '''

        :param i:
        :return:
        '''
        if f'ax{i}' in self.plot['axes'] and f'ax{i}' in self.plotobjects:
            if self.plotobjects[f'ax{i}'] is None:
                return
            for line in self.plotobjects[f'ax{i}']:
                try:
                    self.plot['axes'][f'ax{i}'].lines.remove(self.plotobjects[f'ax{i}'][line])
                except:
                    self.plot['axes'][f'ax{i}'].lines.remove(line)
            self.plotobjects[f'ax{i}'] = None
            self.plot['axes'][f'ax{i}'].clear()
            self.plot['axes'][f'ax{i}'].set_xticks([])
            self.plot['axes'][f'ax{i}'].set_yticks([])
            self.plot['canvas'].draw_idle()

    def clear(self):
        '''

        :return:
        '''
        self.drawing = False
        self.buttons['play'].configure(text='Play')
        del self.graph
        self.graph = None
        self.data = {}
        self.stepnum = 0
        for i in range(1, 7):
            self.clear_subplot(i)

        self._init_plot(None)

        self.update_status('Graph and data plots cleared.', OKCOLOR)

    def get_node_sizes(self):
        '''

        :return:
        '''
        if self.graph is None:
            return

        metric = self.vars['sizenodesby'].get()
        rawsizes = np.full(self.graph.prop('n'), self.vars['nodesize'].get())
        if metric == '-':
            return rawsizes
        elif metric == 'betweenness':
            btwn = networkx.betweenness_centrality(self.graph).values()
            return np.array([(a * b)**1.2 + 100 for a, b in zip(rawsizes, btwn)])
        elif metric == 'closeness':
            clsn = networkx.closeness_centrality(self.graph).values()
            return np.array([(a * b)**1.2 + 100 for a, b in zip(rawsizes, clsn)])
        elif metric == 'clustering':
            clst = networkx.clustering(self.graph).values()
            return np.array([(a * b)**1.2 + 100 for a, b in zip(rawsizes, clst)])
        elif metric == 'degree':
            dgr = networkx.degree_centrality(self.graph).values()
            return np.array([(a * b)**1.2 + 100 for a, b in zip(rawsizes, dgr)])

    def get_node_labels(self):
        '''

        :return:
        '''
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
            # return {node: str(node) + str(self.graph.prop('diffusion_space')[node]) for node in self.graph.nodes}
            return {node: str(self.graph.prop('diffusion_space')[node])[1:-1] for node in self.graph.nodes}

    def get_node_colors(self):
        '''

        :return:
        '''
        if self.graph is None:
            return
        metric = self.vars['colornodesby'].get()
        if metric == '-':
            return {node: 'b' for node in self.graph}
        elif metric == 'type':
            return {node: self.graph.prop('agent_models')[self.graph.prop('types')[node]]['color'] for node in self.graph}
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
        elif metric == 'diff. space':
            if self.graph.prop('dimensions') != 'categorical':
                dif = self.graph.prop('diffusion_space')
                return {node: COLORS((dif[node][0] + 1) / 2) for node in self.graph}
            else:
                if not self.graph._has_property('category_colors'):
                    cats = list(self.graph.prop('category_dist').keys())
                    self.graph.prop(category_colors={cat: catcolors[color] for color, cat in enumerate(cats)})
                c = self.graph.prop('category_colors')
                return {node: c[self.graph.prop('diffusion_space')[node][0]] for node in self.graph}

    def relabel_nodes(self, event):
        '''

        :param event:
        :return:
        '''
        if self.graph is None:
            return
        labels = self.get_node_labels()
        for node in self.plotobjects['ax0']['nodelabels']:
            self.plotobjects['ax0']['nodelabels'][node].set_text(labels[node])
        self.plot['canvas'].draw_idle()

    def resize_nodes(self, event):
        '''

        :param event:
        :return:
        '''
        if self.graph is None:
            return
        s = self.get_node_sizes()
        if self.graph.prop('selfloops'):
            news = s * 1.25
            self.plotobjects['ax0']['selfloops'].set_sizes(news)
            # self.plotobjects['ax0']['selfloops'].set_sizes(s)
        self.plotobjects['ax0']['nodes'].set_sizes(s)
        self.plot['canvas'].draw_idle()

    def realpha_nodes(self, event):
        '''

        :param event:
        :return:
        '''
        if self.graph is None:
            return
        alpha = self.vars['nodealpha'].get()
        self.plotobjects['ax0']['nodes'].set_alpha(.1 + (alpha * .9))
        self.plot['canvas'].draw_idle()

    def recolor_nodes(self, event):
        '''

        :param event:
        :return:
        '''
        if self.graph is None:
            return
        self.plotobjects['ax0']['nodes'].set_color(self.get_node_colors().values())
        self.plot['canvas'].draw_idle()

    def reposition_nodes(self, event):
        '''

        :param event:
        :return:
        '''
        if self.graph is None:
            return
        self.plotobjects['ax0']['pos'] = self.get_positions()
        pos = np.array(list(self.plotobjects['ax0']['pos'].values())).T
        self.plotobjects['ax0']['nodes'].set_offsets(np.c_[pos[0], pos[1]])
        if self.graph.prop('selfloops'):
            self.plotobjects['ax0']['selflooppos'] = {i: (self.plotobjects['ax0']['pos'][i][0], self.plotobjects['ax0']['pos'][i][1] + .02)
                                               for i in self.plotobjects['ax0']['pos']}
            selflooppos = np.array(list(self.plotobjects['ax0']['selflooppos'].values())).T
            self.plotobjects['ax0']['selfloops'].set_offsets(np.c_[selflooppos[0], selflooppos[1]])
        for node in self.plotobjects['ax0']['nodelabels']:
            self.plotobjects['ax0']['nodelabels'][node].set_position((pos[0][node], pos[1][node]))
        self.realpha_nodes(None)
        self.realpha_edges(None)
        self.reposition_edges()

    def realpha_edges(self, event):
        '''

        :param event:
        :return:
        '''
        if self.graph is None:
            return
        alpha = self.vars['edgealpha'].get()
        metric = self.vars['alphaedgesby'].get()
        if metric == '-':
            w = {e: 1 for e in self.plotobjects['ax0']['lines']}
        elif metric == 'weight' and self.graph.prop('weight_dist') != '-':
            w = self.graph.get_weights()
        for line in self.plotobjects['ax0']['lines']:
            self.plotobjects['ax0']['lines'][line].set_alpha(.1 + (alpha * w[line] * .9))
        if self.graph.prop('selfloops'):
            self.plotobjects['ax0']['selfloops'].set_alpha(.1 + (alpha * w[line] * .9))
        self.plot['canvas'].draw_idle()

    def get_edge_angles(self, numedges):
        '''

        :param numedges:
        :return:
        '''
        if numedges == 1:
            return [0.]
        return np.linspace(-.3, .3, numedges)

    def reposition_edges(self):
        '''

        :return:
        '''
        if self.graph is None:
            return
        pos = np.array(list(self.plotobjects['ax0']['pos'].values())).T
        alpha = self.vars['edgealpha'].get()
        lines = self.plotobjects['ax0']['lines'].values()
        for line in self.plotobjects['ax0']['lines'].keys():
            if self.graph.isgraph():
                self.plotobjects['ax0']['lines'][line].set_xdata([pos[0][line[0]], pos[0][line[1]]])
                self.plotobjects['ax0']['lines'][line].set_ydata([pos[1][line[0]], pos[1][line[1]]])
            elif self.graph.isdigraph() or self.graph.ismultigraph() or self.graph.ismultidigraph():
                start = (pos[0][line[0]], pos[1][line[0]])
                end = (pos[0][line[1]], pos[1][line[1]])
                self.plotobjects['ax0']['lines'][line].set_positions(start, end)
            self.plotobjects['ax0']['lines'][line].set_alpha(alpha)


    def update_layout_handler(self, event):
        '''

        :param event:
        :return:
        '''
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
        if rmv is None:
            return
        for e in rmv:
            if self.graph.isgraph():
                line = self.plotobjects['ax0']['lines'][e]
                # print(self.plot['axes']['ax0'].lines)
                # print(matplotlib._get_version())
                # print(self.plot['axes']['ax0'].lines._axes)
                # print(self.plot['axes']['ax0'].lines._axes._children)

                self.plot['axes']['ax0'].lines._axes._children.remove(line)
                # print(self.plot['axes']['ax0'].lines._axes._children)

                # self.plot['axes']['ax0'].lines.remove(line)

                del self.plotobjects['ax0']['lines'][e]
            elif self.graph.isdigraph():
                line = self.plotobjects['ax0']['lines'][e]
                self.plot['axes']['ax0'].patches.remove(line)
                del self.plotobjects['ax0']['lines'][e]
            elif self.graph.ismultigraph():
                if e[2] == None:
                    lines = [self.plotobjects['ax0']['lines'][key] for key in self.plotobjects['ax0']['lines'] if
                             key[0] == e[0] and key[1] == e[1]]
                else:
                    lines = [self.plotobjects['ax0']['lines'][e]]
                    for line in lines:
                        self.plot['axes']['ax0'].patches.remove(line)
                    del self.plotobjects['ax0']['lines'][e]
                    self.reangle_edges_between(e[0], e[1])
            elif self.graph.ismultidigraph():
                if e[2] == None:
                    lines = {key: self.plotobjects['ax0']['lines'][key] for key in self.plotobjects['ax0']['lines'] if
                             key[0] == e[0] and key[1] == e[1]}
                    for line in lines:
                        self.plot['axes']['ax0'].patches.remove(lines[line])
                        del self.plotobjects['ax0']['lines'][line]
                else:
                    lines = [self.plotobjects['ax0']['lines'][e]]
                    for line in lines:
                        self.plot['axes']['ax0'].patches.remove(line)
                    del self.plotobjects['ax0']['lines'][e]
                self.reangle_edges_between(e[0], e[1])

    def add_edges(self, add):
        '''

        :param add:
        :return:
        '''
        pos = self.plotobjects['ax0']['pos']
        alpha = self.vars['edgealpha'].get()
        if add is None:
            return
        if self.graph.isgraph():
            for e in add:
                if e[0] == e[1]:
                    continue
                x, y = [pos[e[0]][0], pos[e[1]][0]], [pos[e[0]][1], pos[e[1]][1]]
                self.plotobjects['ax0']['lines'][e], = self.plot['axes']['ax0'].plot(x, y, 'k', alpha=alpha, zorder=0)
        elif self.graph.isdigraph():
            for e in add:
                if e[0] == e[1]:
                    continue
                style = 'simple, head_length=8, head_width=4'
                start, end = (pos[e[0]][0], pos[e[0]][1]), (pos[e[1]][0], pos[e[1]][1])
                self.plotobjects['ax0']['lines'][e] = matplotlib.patches.FancyArrowPatch(start, end, arrowstyle=style)
                self.plot['axes']['ax0'].add_patch(self.plotobjects['ax0']['lines'][e])

        elif self.graph.ismultigraph():
            style = 'simple, tail_width=0.5, head_width=0'
            from_nodes = set([i[0] for i in add])
            for node in from_nodes:
                dests = set([i[1] for i in add if i[0] == node])
                for dest in dests:
                    start, end = (pos[node][0], pos[node][1]), (pos[dest][0], pos[dest][1])
                    myedges = [e for e in add if e[0] == node and e[1] == dest]
                    for e in myedges:
                        self.plotobjects['ax0']['lines'][e] = matplotlib.patches.FancyArrowPatch(start, end, arrowstyle=style)
                        self.plot['axes']['ax0'].add_patch(self.plotobjects['ax0']['lines'][e])
                    self.reangle_edges_between(node, dest)
        elif self.graph.ismultidigraph():
            style = 'simple, head_length=8, head_width=4'
            from_nodes = set([i[0] for i in add])
            for node in from_nodes:
                dests = set([i[1] for i in add if i[0] == node])
                for dest in dests:
                    start, end = (pos[node][0], pos[node][1]), (pos[dest][0], pos[dest][1])
                    myedges = [e for e in add if e[0] == node and e[1] == dest]
                    existing = [key for key in self.plotobjects['ax0']['lines'] if (key[0] == node and key[1] == dest) or
                                (key[1] == node and key[0] == dest)]
                    num = len(myedges) + len(existing)
                    angles = self.get_edge_angles(num)
                    for key, angle in zip(existing, angles[:len(existing)]):
                        if key[0] == node and key[1] == dest:
                            myangle = angle
                        elif key[1] == node and key[0] == dest:
                            myangle = -angle
                        self.plotobjects['ax0']['lines'][key].set(connectionstyle=f'arc3,rad={myangle}')
                    for e, angle in zip(myedges, angles[len(existing):]):
                        if e[0] == node and e[1] == dest:
                            myangle = angle
                        elif e[1] == node and e[0] == dest:
                            myangle = -angle
                        self.plotobjects['ax0']['lines'][e] = matplotlib.patches.FancyArrowPatch(start, end,
                                                                                                 arrowstyle=style,
                                                                                                 connectionstyle=f'arc3,rad={myangle}')
                        self.plot['axes']['ax0'].add_patch(self.plotobjects['ax0']['lines'][e])

    def reangle_edges_between(self, u, v):
        '''

        :param u:
        :param v:
        :return:
        '''
        edges = []
        if self.graph.ismultigraph():
            edges = [key for key in self.plotobjects['ax0']['lines'] if key[0] == u and key[1] == v]
        elif self.graph.ismultidigraph():
            edges = [key for key in self.plotobjects['ax0']['lines'] if ((key[0] == u and key[1] == v) or
                                                                         (key[0] == v and key[1] == u))]
        num = len(edges)
        angles = self.get_edge_angles(num)
        for e, angle in zip(edges, angles):
            self.plotobjects['ax0']['lines'][e].set(connectionstyle=f'arc3,rad={angle}')

    def add_edge_from_panel(self):
        '''
        addedgefrom
        addedgeto
        addedgelabel
        :return:
        '''
        if self.graph is None:
            self.update_status('Graph does not exist.', ERRCOLOR)
            return
        fromnode = self.vars['addedgefrom'].get()
        tonode = self.vars['addedgeto'].get()
        label = self.vars['addedgelabel'].get()
        if fromnode not in self.graph.nodes:
            self.update_status('Source node not in graph.', ERRCOLOR)
            return
        if tonode not in self.graph.nodes:
            self.update_status('Destination node not in graph.', ERRCOLOR)
            return
        if self.graph.isgraph() or self.graph.ismultigraph():
            if fromnode == tonode:
                return
            if fromnode > tonode:
                temp = fromnode
                fromnode = tonode
                tonode = temp
        if self.graph.isgraph() or self.graph.isdigraph():
            if (fromnode, tonode) in self.graph.edges:
                self.update_status('Edge already exists.', ERRCOLOR)
                return
        elif self.graph.ismultigraph() or self.graph.ismultidigraph():
            if label == '':
                label = None
            if label is not None:
                if (fromnode, tonode, label) in self.graph.edges:
                    self.update_status('Edge already exists.', ERRCOLOR)
                    return
        edges = self.graph.connect(fromnode, tonode, label)
        self.update_status(f'Connected nodes {fromnode} and {tonode}.', OKCOLOR)
        self.add_edges(edges)
        self.reposition_nodes(None)
        self.resize_nodes(None)
        self.recolor_nodes(None)
        self.relabel_nodes(None)
        self.plot['canvas'].draw_idle()

    def remove_edge_from_panel(self):
        '''

        :return:
        '''
        if self.graph is None:
            self.update_status('Graph does not exist.', ERRCOLOR)
            return
        fromnode = self.vars['deledgefrom'].get()
        tonode = self.vars['deledgeto'].get()
        label = self.vars['deledgelabel'].get()
        if fromnode not in self.graph.nodes:
            self.update_status('Source node not in graph.', ERRCOLOR)
            return
        if tonode not in self.graph.nodes:
            self.update_status('Destination node not in graph.', ERRCOLOR)
            return
        if self.graph.isgraph() or self.graph.ismultigraph():
            if fromnode == tonode:
                return
            if fromnode > tonode:
                temp = fromnode
                fromnode = tonode
                tonode = temp
        if self.graph.isgraph() or self.graph.isdigraph():
            if (fromnode, tonode) not in self.graph.edges:
                self.update_status('Edge does not exist.', ERRCOLOR)
                return
        elif self.graph.ismultigraph() or self.graph.ismultidigraph():
            if tonode not in self.graph[fromnode]:
                self.update_status('Nodes are not connected.', ERRCOLOR)
                return
        if label == '':
            label = None

        edges = self.graph.disconnect(fromnode, tonode, label)
        self.remove_edges(edges)
        self.update_status(f'Removed edge between {fromnode} and {tonode}.', OKCOLOR)
        self.reposition_nodes(None)
        self.resize_nodes(None)
        self.recolor_nodes(None)
        self.relabel_nodes(None)
        self.plot['canvas'].draw_idle()

    def step(self):
        '''

        :return:
        '''
        if self.graph is None:
            self.update_status('Graph does not exist.', ERRCOLOR)
            return

        if self.stepnum == 0:
            self.collect_data()

        self.stepnum += 1
        self.update_status(f'Step: {self.stepnum}', 'SystemButtonFace')

        self.collect_data()
        for i in range(1, 7):
            self.update_subplot_data(i)
        rmv, add = self.graph.step()
        self.remove_edges(rmv)
        self.add_edges(add)

        self.reposition_nodes(None)
        self.resize_nodes(None)
        self.recolor_nodes(None)
        self.relabel_nodes(None)

        self.plot['canvas'].draw_idle()

    def collect_data(self):
        '''

        :return:
        '''
        names = [f'plot{i}data' for i in range(1, 7)]
        self.data['axmetrics'] = {i: self.vars[i].get() for i in names if self.vars[i].get() != '-'}
        self.data['collecting'] = set([self.data['axmetrics'][i] for i in self.data['axmetrics']])
        for metric in self.data['collecting']:
            if metric not in self.data:
                if metric in ['density']:
                    self.data[metric] = []
                else:
                    self.data[metric] = {}
            if self.data[metric] == None:
                if metric in ['density']:
                    self.data[metric] = []
                else:
                    self.data[metric] = {}
            if metric == 'density':
                self.data['density'].append(nx.density(self.graph))
            elif metric == 'betweenness':
                data = nx.betweenness_centrality(self.graph)
                for key in data:
                    if key not in self.data[metric]:
                        self.data[metric][key] = [data[key]]
                    else:
                        self.data[metric][key].append(data[key])
            elif metric == 'closeness':
                data = nx.closeness_centrality(self.graph)
                for key in data:
                    if key not in self.data[metric]:
                        self.data[metric][key] = [data[key]]
                    else:
                        self.data[metric][key].append(data[key])
            elif metric == 'clustering':
                data = nx.clustering(self.graph)
                for key in data:
                    if key not in self.data[metric]:
                        self.data[metric][key] = [data[key]]
                    else:
                        self.data[metric][key].append(data[key])
            elif metric == 'degree':
                data = nx.degree_centrality(self.graph)
                for key in data:
                    if key not in self.data[metric]:
                        self.data[metric][key] = [data[key]]
                    else:
                        self.data[metric][key].append(data[key])
            elif metric == 'diff. space':
                pass
            elif metric == 'diff. avg.':
                pass

    def update_subplot_data(self, i):
        '''

        :param i:
        :return:
        '''
        if self.graph is None:
            return

        if 'axmetrics' not in self.data:
            return
        if f'plot{i}data' not in self.data['axmetrics']:
            return

        if f'ax{i}' not in self.plot['axes']:
            return
        if f'ax{i}' not in self.plotobjects:
            self.plotobjects[f'ax{i}'] = None
        if self.plotobjects[f'ax{i}'] is None:
            if self.data['axmetrics'][f'plot{i}data'] == 'density':
                self.plotobjects[f'ax{i}'] = None
            else:
                self.plotobjects[f'ax{i}'] = {}
        if self.data['axmetrics'][f'plot{i}data'] == 'density':
            data = self.data['density']
            numobs = len(data) - 1
            if self.plotobjects[f'ax{i}'] is None:
                color = self.vars[f'plot{i}color'].get()
                self.plotobjects[f'ax{i}'], = [self.plot['axes'][f'ax{i}'].plot(range(self.stepnum - numobs, self.stepnum + 1),
                                                                                data, color, alpha=.5)]
                self.plot['axes'][f'ax{i}'].set_ylim([0, 1])
            else:
                self.plotobjects[f'ax{i}'][0].set_xdata(range(self.stepnum - numobs, self.stepnum + 1))
                self.plotobjects[f'ax{i}'][0].set_ydata(data)
                self.plot['axes'][f'ax{i}'].set_xlim([0, self.stepnum])
                self.plot['axes'][f'ax{i}'].set_xlabel('Density')
        elif self.data['axmetrics'][f'plot{i}data'] in ['betweenness', 'closeness', 'degree', 'clustering']:
            if self.data['axmetrics'][f'plot{i}data'] in self.data:
                data = self.data[self.data['axmetrics'][f'plot{i}data']]
            else:
                data = None
            if data is not None:
                if self.plotobjects[f'ax{i}'] in [None, {}]:
                    if self.vars['colornodesby'].get() == 'type':
                        types = self.graph.prop('types')
                        models = self.graph.prop('agent_models')
                        colors = {key: models[types[key]]['color'] for key in data}
                    else:
                        colors = {key: self.vars[f'plot{i}color'].get() for key in data}
                    for key in data:
                        numobs = len(data[key]) - 1
                        self.plotobjects[f'ax{i}'][key], = self.plot['axes'][f'ax{i}'].plot(range(self.stepnum - numobs, self.stepnum + 1),
                                                                                            data[key], colors[key], alpha=.5)
                    self.plot['axes'][f'ax{i}'].set_ylim([0, 1])
                else:
                    for key in data:
                        numobs = len(data[key]) - 1
                        self.plotobjects[f'ax{i}'][key].set_xdata(range(self.stepnum - numobs, self.stepnum + 1))
                        self.plotobjects[f'ax{i}'][key].set_ydata(data[key])
                        self.plot['axes'][f'ax{i}'].set_xlim([0, self.stepnum])
                        self.plot['axes'][f'ax{i}'].set_xlabel(self.data['axmetrics'][f'plot{i}data'].capitalize())
        self.plot['canvas'].draw_idle()

    def animate(self):
        '''

        :return:
        '''
        if self.drawing:
            self.step()
            # Speed goes 0 to 5
            speed = self.vars['speed'].get()
            wait = 1000 - (175 * speed)
            if self.parent is not None:
                self.anim_id = self.root.after(wait, self.parent.animate)
            else:
                self.anim_id = self.root.after(wait, self.animate)

    def play(self):
        '''

        :return:
        '''
        if self.graph is None:
            return
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
                self.parent.animate()
            else:
                self.animate()
            # animate

    def get_vals_for_construct(self):
        '''

        :return:
        '''
        types = [i for i in range(1, 4) if self.vars[f'typename{i}'].get() != '']

        type_dist = {}
        models = {}
        for i in types:
            name = self.vars[f'typename{i}'].get()
            model = {}
            type_dist[self.vars[f'typename{i}'].get()] = self.vars[f'percent_type{i}'].get()
            grav = self.vars[f'gravity{i}'].get()
            if grav < 0:
                model['conformity'] = 'rebelling'
            else:
                model['conformity'] = 'conforming'
            model['gravity'] = grav
            model['max_sim'] = self.vars[f'max_sim{i}'].get()
            if model['max_sim'] > .5:
                model['homophily'] = 'homophilic'
            elif model['max_sim'] < .5:
                model['homophily'] = 'heterophilic'
            else:
                model['homophily'] = 'mesophilic'
            model['resistance'] = self.vars[f'resistance{i}'].get()
            model['confidence'] = self.vars[f'confidence{i}'].get()
            model['color'] = self.vars[f'typecolor{i}'].get()
            models[name] = model

        # Get transmission model if needed
        category_dist = {}
        transmission_probs = {}
        if self.vars['dimensions'].get() == 'categorical':
            for i in range(1, self.num_categories + 1):
                name = self.vars[f'catname{i}'].get()
                category_dist[name] = self.vars[f'catperc{i}'].get()
                transmission_probs[name] = {}
                for t in range(1, self.vars['numtransitions'].get() + 1):
                    if self.vars[f't_from{t}'].get() != name:
                        continue
                    if self.vars[f't_cond{t}'].get() == 'auto':
                        if 'auto' not in transmission_probs[name]:
                            transmission_probs[name]['auto'] = {}
                        toname = self.vars[f't_to{t}'].get()
                        prob = self.vars[f't_prob{t}'].get()
                        transmission_probs[name]['auto'][toname] = prob
                    elif self.vars[f't_cond{t}'].get() == 'contact':
                        if 'contact' not in transmission_probs[name]:
                            transmission_probs[name]['contact'] = {}
                        toname = self.vars[f't_to{t}'].get()
                        prob = self.vars[f't_prob{t}'].get()
                        cont = self.vars[f't_cont{t}'].get()
                        if cont not in transmission_probs[name]['contact']:
                            transmission_probs[name]['contact'][cont] = {}
                        transmission_probs[name]['contact'][cont] = (toname, prob)

        d = {}
        keys = ['n', 'directed', 'symmetric', 'multiedge', 'selfloops', 'normalize', 'topology', 'saturation',
                'weight_dist', 'weight_min', 'weight_mean', 'weight_max', 'weight_stdev', 'weight_const',
                'dimensions', 'num_dimensions', 'visibility', 'p_connect', 'p_disconnect', 'p_update',
                'update_method', 'distance', 'num_connections', 'num_nodes_connect', 'num_disconnections',
                'num_nodes_disconnect', 'num_nodes_update', 'thresh_connect', 'thresh_disconnect']
        for key in keys:
            d[key] = self.vars[key].get()
        if d['dimensions'] == 'categorical':
            d['update_method'] == 'transmission'
        if d['dimensions'] == 'continnuous':
            d['distance'] == 'euclidean'
        d['type_dist'] = type_dist
        d['agent_models'] = models
        d['category_dist'] = category_dist
        d['transmission_probs'] = transmission_probs

        return d

    def choose_color_plot1(self):
        color = colorchooser.askcolor()[1]
        self.buttons[f'plot1color'].configure(bg=color)
        self.vars[f'plot1color'].set(color)

    def choose_color_plot2(self):
        color = colorchooser.askcolor()[1]
        self.buttons[f'plot2color'].configure(bg=color)
        self.vars[f'plot2color'].set(color)

    def choose_color_plot3(self):
        color = colorchooser.askcolor()[1]
        self.buttons[f'plot3color'].configure(bg=color)
        self.vars[f'plot3color'].set(color)

    def choose_color_plot4(self):
        color = colorchooser.askcolor()[1]
        self.buttons[f'plot4color'].configure(bg=color)
        self.vars[f'plot4color'].set(color)

    def choose_color_plot5(self):
        color = colorchooser.askcolor()[1]
        self.buttons[f'plot5color'].configure(bg=color)
        self.vars[f'plot5color'].set(color)

    def choose_color_plot6(self):
        color = colorchooser.askcolor()[1]
        self.buttons[f'plot6color'].configure(bg=color)
        self.vars[f'plot6color'].set(color)

    def choose_color_type1(self):
        color = colorchooser.askcolor()[1]
        self.buttons[f'typecolor1'].configure(bg=color)
        self.vars[f'typecolor1'].set(color)

    def choose_color_type2(self):
        color = colorchooser.askcolor()[1]
        self.buttons[f'typecolor2'].configure(bg=color)
        self.vars[f'typecolor2'].set(color)

    def choose_color_type3(self):
        color = colorchooser.askcolor()[1]
        self.buttons[f'typecolor3'].configure(bg=color)
        self.vars[f'typecolor3'].set(color)

    def set_gravity_1(self):
        self.vars['gravity1'].set(self.inputs['gravity_dial1'].get() / 100)

    def set_gravity_2(self):
        self.vars['gravity2'].set(self.inputs['gravity_dial2'].get() / 100)

    def set_gravity_3(self):
        self.vars['gravity3'].set(self.inputs['gravity_dial3'].get() / 100)

    def set_gravitydial_1(self, event):
        val = self.bound_val('gravity3', -1, 1)
        self.inputs['gravity_dial1'].set(val * 100)

    def set_gravitydial_2(self, event):
        val = self.bound_val('gravity3', -1, 1)
        self.inputs['gravity_dial2'].set(val * 100)

    def set_gravitydial_3(self, event):
        val = self.bound_val('gravity3', -1, 1)
        self.inputs['gravity_dial3'].set(val * 100)

    def set_maxsimdial_1(self, event):
        val = self.bound_val('max_sim1', 0, 1)
        self.inputs['max_sim_dial1'].set(val * 100)

    def set_maxsimdial_2(self, event):
        val = self.bound_val('max_sim2', 0, 1)
        self.inputs['max_sim_dial2'].set(val * 100)

    def set_maxsimdial_3(self, event):
        val = self.bound_val('max_sim3', 0, 1)
        self.inputs['max_sim_dial3'].set(val * 100)

    def set_confidencedial_1(self, event):
        val = self.bound_val('confidence1', 0, 1)
        self.inputs['confidence_dial1'].set(val * 100)

    def set_confidencedial_2(self, event):
        val = self.bound_val('confidence2', 0, 1)
        self.inputs['confidence_dial2'].set(val * 100)

    def set_confidencedial_3(self, event):
        val = self.bound_val('confidence3', 0, 1)
        self.inputs['confidence_dial3'].set(val * 100)

    def set_resistancedial_1(self, event):
        val = self.bound_val('resistance1', 0, 1)
        self.inputs['resistance_dial1'].set(val * 100)

    def set_resistancedial_2(self, event):
        val = self.bound_val('resistance2', 0, 1)
        self.inputs['resistance_dial2'].set(val * 100)

    def set_resistancedial_3(self, event):
        val = self.bound_val('resistance3', 0, 1)
        self.inputs['resistance_dial3'].set(val * 100)

    def bound_val(self, tag, lo, hi):
        try:
            val = self.vars[tag].get()
            if val < lo: val = lo
            if val > hi: val = hi
        except:
            val = 0
        return val

    def set_maxsim_1(self):
        self.vars['max_sim1'].set(self.inputs['max_sim_dial1'].get() / 100)

    def set_maxsim_2(self):
        self.vars['max_sim2'].set(self.inputs['max_sim_dial2'].get() / 100)

    def set_maxsim_3(self):
        self.vars['max_sim3'].set(self.inputs['max_sim_dial3'].get() / 100)

    def set_confidence_1(self):
        self.vars['confidence1'].set(self.inputs['confidence_dial1'].get() / 100)

    def set_confidence_2(self):
        self.vars['confidence2'].set(self.inputs['confidence_dial2'].get() / 100)

    def set_confidence_3(self):
        self.vars['confidence3'].set(self.inputs['confidence_dial3'].get() / 100)

    def set_resistance_1(self):
        self.vars['resistance1'].set(self.inputs['resistance_dial1'].get() / 100)

    def set_resistance_2(self):
        self.vars['resistance2'].set(self.inputs['resistance_dial2'].get() / 100)

    def set_resistance_3(self):
        self.vars['resistance3'].set(self.inputs['resistance_dial3'].get() / 100)