# GUI Class

from helpers import DISTS, METRICS
from SocialNetwork import PROPDEFAULTS, PROPSELECT, SocialNetwork

import functools
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

class GUI(tk.Toplevel):

    def __init__(self, root=None):

        if root is None:
            self.root = tk.Tk()
            self.root.title("Social Network Evolution Engine")
            self.poppedoff = False

        else:
            super().__init__(self, root)
            self.root = root
            self.poppedoff = True

        self.frames = {}
        self.inputs = {}
        self.labels = {}
        self.buttons = {}
        self.notebook = {}
        self.plot = {}
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

        self._init_panel_frames()
        self._init_plot()
        self._init_notebook()

        self.labels['status'] = tk.Label(self.frames['status'], text="All good right now.")
        self.labels['status'].grid(sticky='ew')

        self.root.mainloop()

    def _init_panel_frames(self):
        self.frames['window'] = tk.Frame(self.root, padx=5, pady=5)
        self.frames['window'].grid(padx=5, pady=5, sticky='news')

        self.frames['notebook'] = tk.LabelFrame(self.frames['window'], text='Control Panel', padx=5, pady=5)
        self.frames['notebook'].grid(row=0, column=0, padx=5, pady=5, sticky='news')

        self.frames['status'] = tk.LabelFrame(self.frames['window'], text='Status', padx=5, pady=5)
        self.frames['status'].grid(row=1, column=0, padx=5, pady=5, sticky='sew')

        self.frames['plot'] = tk.LabelFrame(self.frames['window'], text='Plot', padx=5, pady=5)
        self.frames['plot'].grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky='news')

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frames['window'].columnconfigure(1, weight=1)
        self.frames['window'].rowconfigure(0, weight=1)

    def _init_plot(self):
        self.plot['fig'] = Figure(figsize=(7, 5), dpi=100)
        # self.plot['ax'] = self.plot['fig'].add_subplot()
        self.plot['canvas'] = FigureCanvasTkAgg(self.plot['fig'], master=self.frames['plot'])
        self.plot['canvas'].draw()
        self.plot['toolbar'] = NavigationToolbar2Tk(self.plot['canvas'], self.frames['plot'])
        self.plot['toolbar'].update()
        self.plot['canvas'].get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # X = [(2, 3, (1, 3)), (2, 3, 4), (2, 3, 5), (2, 3, 6)]
        X = [(4, 3, (1, 9)), (4, 3, 10), (4, 3, 11), (4, 3, 12)]
        for nrows, ncols, plot_number in X:
            sub = self.plot['fig'].add_subplot(nrows, ncols, plot_number)
            sub.set_xticks([])
            sub.set_yticks([])

        self.plot['fig'].subplots_adjust(bottom=0.025, left=0.025, top=0.975, right=0.975, hspace=0.1, wspace=0.1)

    def _init_notebook(self):

        style = ttk.Style(self.root)
        style.configure('lefttab.TNotebook', tabposition='wn', tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", padding=[3, 3], font=('Courier', '8'))

        self.notebook['notebook'] = ttk.Notebook(self.frames['notebook'], style='lefttab.TNotebook')

        self.notebook['parameters'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['animation'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['evolution'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['edit'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['command'] = ttk.Frame(self.notebook['notebook'])

        self.notebook['notebook'].add(self.notebook['parameters'], text='PRM')
        self.notebook['notebook'].add(self.notebook['animation'], text='ANI')
        self.notebook['notebook'].add(self.notebook['evolution'], text='EVO')
        self.notebook['notebook'].add(self.notebook['edit'], text='EDT')
        self.notebook['notebook'].add(self.notebook['command'], text='CMD')

        self.notebook['notebook'].grid(padx=5, pady=5, sticky=tk.N + tk.E + tk.S + tk.W)

        self._populate_parameters_tab()
        self._populate_animation_tab()
        self._populate_evolution_tab()
        self._populate_edit_tab()

    def _populate_parameters_tab(self):

        self._place_labelframe('graph_structure', self.notebook['parameters'], 'Graph Structure')

        self._place_input_label('n', 'graph_structure', 'Nodes: ')
        self._place_input_entry('n', 'graph_structure', col=1)
        self.vars['n'].trace('w', self.n_callback)

        self._place_input_checkbutton('symmetric', 'graph_structure', text='Symmetric', row=1, columnspan=2)
        self._place_input_checkbutton('directed', 'graph_structure', text='Directed', row=2, columnspan=2,
                                      command=self.directed_callback)
        self._place_input_checkbutton('selfloops', 'graph_structure', text='Self loops', row=1, col=2, columnspan=2)
        self._place_input_checkbutton('multiedge', 'graph_structure', text='Multiedges', row=2, col=2, columnspan=2)

        self._place_labelframe('topology', self.notebook['parameters'], 'Topology')

        self._place_input_label('topology', 'topology', 'Topology: ')
        self._place_input_optionmenu('topology', 'topology', '-', PROPSELECT['topology'], col=1, columnspan=3,
                                     sticky='ew')

        self._place_input_label('saturation', 'topology', 'Saturation: ', row=1)
        self._place_input_entry('saturation', 'topology', row=1, col=1)

        self._place_labelframe('edge_weights', self.notebook['parameters'], 'Weights')

        self._place_input_label('weight_dist', 'edge_weights', 'Weights: ')
        self._place_input_optionmenu('weight_dist', 'edge_weights', '-', DISTS, col=1, columnspan=3, sticky='ew')

        self._place_input_label('weight_min', 'edge_weights', 'Minimum: ', row=1)
        self._place_input_entry('weight_min', 'edge_weights', row=1, col=1)
        self.vars['weight_min'].trace('w', self.weight_minmax_callback)
        self.vars['weight_max'].trace('w', self.weight_minmax_callback)

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

        self._place_labelframe('construct', self.notebook['parameters'], '')
        self.buttons['construct'] = tk.Button(self.frames['construct'], text='Construct')
        self.buttons['construct'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.buttons['clear'] = tk.Button(self.frames['construct'], text='Clear')
        self.buttons['clear'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.buttons['popoff'] = tk.Button(self.frames['construct'], text='Pop Off')
        self.buttons['popoff'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _populate_animation_tab(self):
        self._place_labelframe('animation', self.notebook['animation'], 'Animation')

        self._place_input_label('speed', 'animation', 'Speed: ', row=1, col=0)
        self._place_input_scale('speed', 'animation', 0, 5, 1, length=150, row=1, col=1, columnspan=3)

        self._place_input_label('layout', 'animation', 'Layout: ', row=0, col=0)
        self._place_input_optionmenu('layout', 'animation', 'spring', ['spring', 'circle','spiral','random','shell'],
                                     row=0, col=1, columnspan=2, sticky='ew')

        self._place_labelframe('nodes', self.notebook['animation'], 'Nodes')

        self._place_input_checkbutton('staticpos', 'nodes', row=0, col=0, sticky='w', text='Fixed pos.')
        self._place_input_label('size', 'nodes', 'Size: ', row=0, col=1)
        self._place_input_scale('size', 'nodes', 0, 1, .1, length=70, row=0, col=2)
        self._place_input_label('nodealpha', 'nodes', 'Alpha: ', row=1, col=1)
        self._place_input_scale('nodealpha', 'nodes', 0, 1, .1, length=70, row=1, col=2)

        self._place_input_label('sizenodesby', 'nodes', 'Size nodes: ', row=2, col=0)
        self._place_input_optionmenu('sizenodesby', 'nodes', '-', METRICS, row=2, col=1, columnspan=3, sticky='ew')
        self._place_input_label('colornodesby', 'nodes', 'Color nodes: ', row=3, col=0)
        self._place_input_optionmenu('colornodesby', 'nodes', '-', METRICS + ['type'], row=3, col=1, columnspan=3,
                                     sticky='ew')
        self._place_input_label('labelnodesby', 'nodes', 'Label nodes: ', row=4, col=0)
        self._place_input_optionmenu('labelnodesby', 'nodes', '-', METRICS + ['name', 'diff. space', 'type'], row=4,
                                     col=1, columnspan=3, sticky='ew')

        self._place_labelframe('edges', self.notebook['animation'], 'Edges')

        self._place_input_label('edgealpha', 'edges', 'Alpha: ', row=0, col=0)
        self._place_input_scale('edgealpha', 'edges', 0, 1, .01, length=80, row=0, col=1, columnspan=2)
        self._place_input_entry('edgealpha', 'edges', row=0, col=3)

        self._place_input_label('alphaedgesby', 'edges', 'Darken edges: ', row=1, col=0)
        self._place_input_optionmenu('alphaedgesby', 'edges', '-', ['-', 'betweenness', 'weight'], row=1, col=1,
                                     columnspan=3, sticky='ew')
        self._place_input_label('coloredgesby', 'edges', 'Color edges: ', row=2, col=0)
        self._place_input_optionmenu('coloredgesby', 'edges', '-', ['-', 'betweenness', 'weight', 'label'], row=2,
                                     col=1, columnspan=3, sticky='ew')
        self._place_input_label('labeledgesby', 'edges', 'Label edges: ', row=4, col=0)
        self._place_input_optionmenu('labeledgesby', 'edges', '-', ['-', 'betweenness', 'weight', 'label'], row=4,
                                     col=1, columnspan=3, sticky='ew')

        self._place_labelframe('dataplots', self.notebook['animation'], 'Data Plots')

        self._place_input_label('numplots', 'dataplots', '# Plots: ', row=0, col=0)
        self._place_input_scale('numplots', 'dataplots', 0, 4, 1, length=80, row=0, col=1, columnspan=3)
        self._place_input_label('plot1data', 'dataplots', 'Plot 1 Data: ', row=1, col=0)
        self._place_input_optionmenu('plot1data', 'dataplots', '-', METRICS, row=1, col=1, columnspan=3, sticky='ew')
        self._place_input_label('plot2data', 'dataplots', 'Plot 2 Data: ', row=2, col=0)
        self._place_input_optionmenu('plot2data', 'dataplots', '-', METRICS, row=2, col=1, columnspan=3, sticky='ew')
        self._place_input_label('plot3data', 'dataplots', 'Plot 3 Data: ', row=3, col=0)
        self._place_input_optionmenu('plot3data', 'dataplots', '-', METRICS, row=3, col=1, columnspan=3, sticky='ew')
        self._place_input_label('plot4data', 'dataplots', 'Plot 4 Data: ', row=4, col=0)
        self._place_input_optionmenu('plot4data', 'dataplots', '-', METRICS, row=4, col=1, columnspan=3, sticky='ew')

        self.labels['plot1data'].grid_forget()
        self.inputs['plot1data'].grid_forget()
        self.labels['plot2data'].grid_forget()
        self.inputs['plot2data'].grid_forget()
        self.labels['plot3data'].grid_forget()
        self.inputs['plot3data'].grid_forget()
        self.labels['plot4data'].grid_forget()
        self.inputs['plot4data'].grid_forget()

        self._place_labelframe('play', self.notebook['animation'], '')

        self.buttons['play'] = tk.Button(self.frames['play'], text='Play')
        self.buttons['play'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.buttons['step'] = tk.Button(self.frames['play'], text='Step')
        self.buttons['step'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.buttons['pause'] = tk.Button(self.frames['play'], text='Pause')
        self.buttons['pause'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _populate_evolution_tab(self):
        self._place_labelframe('evolution', self.notebook['evolution'], 'Evolution Parameters')

        self._place_input_label('num_dimensions', 'evolution', 'Dimensions: ')
        self._place_input_entry('num_dimensions', 'evolution', col=1)

        self._place_input_label('dimensions', 'evolution', 'Domain: ', row=1)
        self._place_input_optionmenu('dimensions', 'evolution', 'binary', ['binary', 'continuous'],
                                     row=1, col=1, columnspan=3)

        self._place_input_label('visibility', 'evolution', 'Visibility: ', row=2)
        self._place_input_optionmenu('visibility', 'evolution', 'visible', ['visible', 'hidden', 'random'],
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
        self._place_input_optionmenu('update_method', 'diffusion', '-', ['-', 'voter', 'majority', 'average',
                                                                         'transmission'],
                                     row=4, col=1, columnspan=3, sticky='ew')

        self._place_labelframe('reward', self.notebook['evolution'], 'Reward')

        self._place_input_label('max_reward', 'reward', 'Sim. Max.: ', row=0)
        self._place_input_scale('max_reward', 'reward', 0, 1, .5, row=0, col=1, columnspan=2, length=70)
        self._place_input_entry('max_reward', 'reward', row=0, col=3)
        self._place_input_label('distance', 'reward', 'Distance: ', row=1)
        self._place_input_optionmenu('distance', 'reward', 'hamming', ['hamming', 'euclidean', 'cosine'],
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

    def _place_input_entry(self, tag, framename, width=5, row=0, col=0, columnspan=1):
        self.inputs[tag] = tk.Entry(self.frames[framename], textvariable=self.vars[tag], width=width)
        self.inputs[tag].grid(row=row, column=col, columnspan=columnspan, padx=2, sticky=tk.W)

    def _place_input_checkbutton(self, tag, framename, row=0, col=0, sticky='w', text=None, columnspan=1,
                                 command=None):
        self.inputs[tag] = tk.Checkbutton(self.frames[framename], variable=self.vars[tag], text=text, padx=2,
                                          command=command)
        self.inputs[tag].grid(row=row, column=col, padx=2, sticky=sticky, columnspan=columnspan)

    def _place_input_optionmenu(self, tag, framename, firstoption, vals, row=0, col=0, columnspan=1, sticky='w'):
        self.inputs[tag] = ttk.OptionMenu(self.frames[framename], self.vars[tag], firstoption, *vals)
        self.inputs[tag].grid(row=row, column=col, padx=2, columnspan=columnspan, sticky=sticky)

    def _place_input_scale(self, tag, framename, lo, hi, res, length=100, showvalue=False, row=0, col=0,
                           columnspan=1):
        self.inputs[tag] = tk.Scale(self.frames[framename], length=length, variable=self.vars[tag], label=None,
                     resolution=res, orient='horizontal', from_=lo, to=hi, showvalue=showvalue)
        self.inputs[tag].grid(row=row, column=col, columnspan=columnspan, padx=5, sticky='ew')

    def directed_callback(self):
        if not self.vars['directed'].get():
            self.vars['symmetric'].set(True)
            self.inputs['symmetric'].configure(state='disabled')
        else:
            self.inputs['symmetric'].configure(state='normal')

    def n_callback(self, *args):
        try:
            n = self.vars['n'].get()
            if n < 0:
                self.inputs['n'].configure(bg='IndianRed1')
            elif self.inputs['n']['bg'] == 'IndianRed1':
                self.reset_bgcolor(['n'])
        except:
            self.inputs['n'].configure(bg='IndianRed1')

    def weight_minmax_callback(self, *args):
        wmin = self.vars['weight_min'].get()
        wmax = self.vars['weight_max'].get()
        if wmin >= wmax:
            self.inputs['weight_min'].configure(bg='IndianRed1')
            self.inputs['weight_max'].configure(bg='IndianRed1')
        else:
            self.reset_bgcolor(['weight_min', 'weight_max'])

    def reset_bgcolor(self, tags, firstcall=True):
        for tag in tags:
            if firstcall:
                self.inputs[tag].configure(bg='LightBlue1')
            else:
                self.inputs[tag].configure(bg='white')
        if firstcall:
            self.root.after(1000, lambda: self.reset_bgcolor(tags, firstcall=False))