# GUI Class

import tkinter as tk
import tkinter.ttk as ttk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

from SocialNetwork import SocialNetwork

class GUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Social Network Evolution Engine")

        self.windowframe = tk.Frame(self.root, padx=5, pady=5)
        self.windowframe.grid(padx=5, pady=5)

        self.notebook = ttk.Notebook(self.windowframe)

        self.graphtab = ttk.Frame(self.notebook)
        self.paramtab = ttk.Frame(self.notebook)
        self.simultab = ttk.Frame(self.notebook)
        self.othertab = ttk.Frame(self.notebook)

        self.notebook.add(self.graphtab, text='Visualization')
        self.notebook.add(self.paramtab, text='Parameters')
        self.notebook.add(self.simultab, text='Simulation')
        self.notebook.add(self.othertab, text='Other')

        self.notebook.grid()

        self.plotframe = tk.LabelFrame(self.graphtab, padx=5, pady=5, text="Network Visualization", bg="White")
        self.plotframe.grid(padx=5, pady=5)

        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plotframe)  # A tk.DrawingArea.
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plotframe)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.root.mainloop()