# GUI Class

from helpers import DISTS
from SocialNetwork import PROPDEFAULTS, PROPSELECT, SocialNetwork

import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

class GUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Social Network Evolution Engine")

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
                     'weight_dist': tk.StringVar()}

        self._init_panel_frames()
        self._init_plot()
        self._init_notebook()

        self.labels['status'] = tk.Label(self.frames['status'], text="All good right now.")
        self.labels['status'].grid(sticky='ew')

        self.root.mainloop()

    def _init_panel_frames(self):
        self.frames['window'] = tk.Frame(self.root, padx=5, pady=5)
        self.frames['window'].grid(padx=5, pady=5, sticky='news')

        self.frames['notebook'] = tk.LabelFrame(self.frames['window'], text='Control', padx=5, pady=5)
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
        self.plot['ax'] = self.plot['fig'].add_subplot()
        self.plot['canvas'] = FigureCanvasTkAgg(self.plot['fig'], master=self.frames['plot'])
        self.plot['canvas'].draw()
        self.plot['toolbar'] = NavigationToolbar2Tk(self.plot['canvas'], self.frames['plot'])
        self.plot['toolbar'].update()
        self.plot['canvas'].get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.plot['ax'].set_xticks([])
        self.plot['ax'].set_yticks([])

    def _init_notebook(self):

        style = ttk.Style(self.root)
        style.configure('lefttab.TNotebook', tabposition='wn', tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", padding=[3, 3], font=('Courier', '8'))

        self.notebook['notebook'] = ttk.Notebook(self.frames['notebook'], style='lefttab.TNotebook')

        self.notebook['parameters'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['animation'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['evolution'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['edit'] = ttk.Frame(self.notebook['notebook'])
        self.notebook['other'] = ttk.Frame(self.notebook['notebook'])

        self.notebook['notebook'].add(self.notebook['parameters'], text='PRM')
        self.notebook['notebook'].add(self.notebook['animation'], text='ANI')
        self.notebook['notebook'].add(self.notebook['evolution'], text='EVO')
        self.notebook['notebook'].add(self.notebook['edit'], text='EDT')
        self.notebook['notebook'].add(self.notebook['other'], text='OTH')

        self.notebook['notebook'].grid(padx=5, pady=5, sticky=tk.N + tk.E + tk.S + tk.W)

        self._populate_parameters_tab()
        self._populate_animation_tab()
        self._populate_evolution_tab()
        self._populate_edit_tab()

    def _populate_parameters_tab(self):

        self._place_labelframe('graph_structure', self.notebook['parameters'], 'Graph Structure')

        self._place_input_label('n', 'graph_structure', 'Nodes: ')
        self._place_input_entry('n', 'graph_structure', col=1)

        self._place_input_label('symmetric', 'graph_structure', 'Symmetric: ', row=1)
        self._place_input_checkbutton('symmetric', 'graph_structure', row=1, col=1)

        self._place_input_label('directed', 'graph_structure', 'Directed: ', row=2)
        self._place_input_checkbutton('directed', 'graph_structure', row=2, col=1)

        self._place_input_label('selfloops', 'graph_structure', 'Self loops: ', row=1, col=2)
        self._place_input_checkbutton('selfloops', 'graph_structure', row=1, col=3)

        self._place_input_label('multiedge', 'graph_structure', 'Multiedges: ', row=2, col=2)
        self._place_input_checkbutton('multiedge', 'graph_structure', row=2, col=3)

        self._place_labelframe('topology', self.notebook['parameters'], 'Topology')

        self._place_input_label('topology', 'topology', 'Topology: ')
        self._place_input_optionmenu('topology', 'topology', '-', PROPSELECT['topology'], col=1, columnspan=3)

        self._place_input_label('saturation', 'topology', 'Saturation: ', row=1)
        self._place_input_entry('saturation', 'topology', row=1, col=1)

        self._place_labelframe('edge_weights', self.notebook['parameters'], 'Weights')

        self._place_input_label('weight_dist', 'edge_weights', 'Weights: ')
        self._place_input_optionmenu('weight_dist', 'edge_weights', '-', DISTS, col=1, columnspan=3)

        self._place_input_label('weight_min', 'edge_weights', 'Minimum: ', row=1)
        self._place_input_entry('weight_min', 'edge_weights', row=1, col=1)

        self._place_input_label('weight_max', 'edge_weights', 'Maximum: ', row=1, col=2)
        self._place_input_entry('weight_max', 'edge_weights', row=1, col=3)

        self._place_input_label('weight_mean', 'edge_weights', 'Mean: ', row=2)
        self._place_input_entry('weight_mean', 'edge_weights', row=2, col=1)

        self._place_input_label('weight_stdev', 'edge_weights', 'Stdev: ', row=2, col=2)
        self._place_input_entry('weight_stdev', 'edge_weights', row=2, col=3)

        self._place_input_label('weight_const', 'edge_weights', 'Constant: ', row=3)
        self._place_input_entry('weight_const', 'edge_weights', row=3, col=1)

        self._place_input_label('normalize', 'edge_weights', 'Normalize: ', row=3, col=2)
        self._place_input_checkbutton('normalize', 'edge_weights', row=3, col=3)

        self._place_labelframe('construct', self.notebook['parameters'], '')
        self.buttons['construct'] = tk.Button(self.frames['construct'], text='Construct')
        self.buttons['construct'].pack(fill=tk.BOTH)
        self.buttons['clear'] = tk.Button(self.frames['construct'], text='Clear')
        self.buttons['clear'].pack(fill=tk.BOTH)

    def _populate_animation_tab(self):
        self._place_labelframe('animation', self.notebook['animation'], 'Animation')

        self._place_input_label('staticpos', 'animation', 'Fixed pos: ')
        self._place_input_checkbutton('staticpos', 'animation', col=1)

        self._place_labelframe('animation', self.notebook['animation'], 'Features')

        self._place_input_label('anentry', 'animation', 'holdplace: ')
        self._place_input_entry('anentry', 'animation', col=1)

    def _populate_evolution_tab(self):
        pass

    def _populate_edit_tab(self):
        pass

    def _place_labelframe(self, tag, parent, text):
        self.frames[tag] = tk.LabelFrame(parent, text=text, padx=5, pady=3)
        self.frames[tag].pack(fill=tk.BOTH, padx=5)

    def _place_input_label(self, tag, framename, text, row=0, col=0):
        self.labels[tag] = tk.Label(self.frames[framename], text=text, padx=2)
        self.labels[tag].grid(row=row, column=col, padx=2, sticky=tk.E)

    def _place_input_entry(self, tag, framename, width=5, row=0, col=0, columnspan=1):
        self.inputs[tag] = tk.Entry(self.frames[framename], width=width)
        self.inputs[tag].grid(row=row, column=col, columnspan=columnspan, padx=2, sticky=tk.W)

    def _place_input_checkbutton(self, tag, framename, row=0, col=0):
        self.inputs[tag] = tk.Checkbutton(self.frames[framename], variable=self.vars[tag], padx=2)
        self.inputs[tag].grid(row=row, column=col, padx=2)

    def _place_input_optionmenu(self, tag, framename, firstoption, vals, row=0, col=0, columnspan=1):
        self.inputs[tag] = ttk.OptionMenu(self.frames[framename], self.vars[tag], firstoption, *vals)
        self.inputs[tag].grid(row=row, column=col, padx=2, columnspan=columnspan, sticky=tk.W)

# 1 fish bone
# 3 raccoon skin
# 1 rat skin
# 1 rabbit skin