import tkinter as tk
from app.genetic_algorithm import RouteOptimizationGeneticAlgorithm
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


class AppGUI:
    # -- Instantiate tkinter object -- #
    window = tk.Tk()

    # -- Title -- #
    title = 'Genetic Algorithm - Application'

    # -- Options Frame Settings -- #
    population_count = tk.StringVar()
    mutation_rate_percent = tk.StringVar()
    generations = tk.StringVar()
    average_fitness = tk.StringVar()
    best_fitness = tk.StringVar()
    best_generation = tk.StringVar()
    best_distance = tk.StringVar()
    minimizing_factor = tk.StringVar()

    # -- Canvas -- #
    tile_width = 90
    tile_height = 90
    tile_border = 3
    grid_rows = 3
    grid_columns = 3
    canvas_id = None

    # -- Routes -- #
    genetic_algorithm = RouteOptimizationGeneticAlgorithm()
    routes = list()
    route_connections = list()

    # -- Start/Stop Global -- #
    is_genetic_algorithm_running = False

    # -- Graphs -- #
    graphs = dict()
    graphs_data = dict()

    def __init__(self):
        # -- Add Title -- #
        self.window.title(self.title)

        # -- Initialize Options Frame -- #
        self.init_options_frame()

        # -- Initialize Canvas Frame -- #
        self.init_canvas_frame()

        # -- Init Graphing options -- #
        self.init_graphs()

        # -- Start Window -- #
        self.window.mainloop()

    def init_options_frame(self):

        """     These are configuration options      """

        self.set_options_frame_defaults()

        frame_label = tk.LabelFrame(self.window, text="Options")
        frame_label.pack(side='left', anchor=tk.N, expand="yes")
        frame = tk.Frame(frame_label, width=200, height=400)
        frame.pack(fill='both', padx=10, pady=5, expand=True)
        row_count = 0

        # -- Input -- #
        row_count += 1
        tk.Label(frame, text="Population (Count)").grid(row=row_count, column=0, sticky=tk.W)
        tk.Entry(frame, textvariable=self.population_count, justify=tk.RIGHT).grid(row=row_count, column=2)
        row_count += 1
        tk.Label(frame, text="Mutation Rate (%)").grid(row=row_count, column=0, sticky=tk.W)
        tk.Entry(frame, textvariable=self.mutation_rate_percent, justify=tk.RIGHT).grid(row=row_count, column=2)
        row_count += 1
        tk.Label(frame, text="Minimize Seen by (factor)").grid(row=row_count, column=0, sticky=tk.W)
        tk.Entry(frame, textvariable=self.minimizing_factor, justify=tk.RIGHT).grid(row=row_count, column=2)

        # -- SPACE -- #
        row_count += 2
        tk.Label(frame, text=None).grid(row=row_count, column=1)

        # -- Output -- #
        row_count += 1
        tk.Label(frame, text="Generations:").grid(row=row_count, column=0, sticky=tk.W)
        tk.Label(frame, textvariable=self.generations, font="Helvetica 8 bold", justify=tk.RIGHT).grid(row=row_count, column=2, sticky=tk.E)
        row_count += 1
        tk.Label(frame, text="Best Generation:").grid(row=row_count, column=0, sticky=tk.W)
        tk.Label(frame, textvariable=self.best_generation, font="Helvetica 8 bold", justify=tk.RIGHT).grid(row=row_count, column=2, sticky=tk.E)
        row_count += 1
        tk.Label(frame, text="Best Fitness Score:").grid(row=row_count, column=0, sticky=tk.W)
        tk.Label(frame, textvariable=self.best_fitness, font="Helvetica 8 bold", justify=tk.RIGHT).grid(row=row_count, column=2, sticky=tk.E)
        row_count += 1
        tk.Label(frame, text="Best Distance (pixels):").grid(row=row_count, column=0, sticky=tk.W)
        tk.Label(frame, textvariable=self.best_distance, font="Helvetica 8 bold", justify=tk.RIGHT).grid(row=row_count, column=2, sticky=tk.E)
        row_count += 1
        tk.Label(frame, text="Average Fitness Score:").grid(row=row_count, column=0, sticky=tk.W)
        tk.Label(frame, textvariable=self.average_fitness, font="Helvetica 8 bold", justify=tk.RIGHT).grid(row=row_count, column=2, sticky=tk.E)

        # -- SPACE -- #
        row_count += 2
        tk.Label(frame, text=None).grid(row=row_count, column=1)

        # -- Buttons -- #
        row_count += 1
        tk.Button(frame, text="Start (All)", command=self.start_endless).grid(row=row_count, column=0, sticky=tk.W)
        tk.Button(frame, text="Start (Threshold)", command=self.start_with_threshold).grid(row=row_count, column=1, sticky=tk.W)
        tk.Button(frame, text="Stop", command=self.stop).grid(row=row_count, column=2, sticky=tk.E)
        tk.Button(frame, text="Reset", command=self.reset).grid(row=row_count, column=3, sticky=tk.E)

    def set_options_frame_defaults(self):
        """     Sets defaults for Options Frame     """
        self.population_count.set('50')
        self.mutation_rate_percent.set('1')
        self.generations.set('-')
        self.average_fitness.set('-')
        self.best_fitness.set('-')
        self.best_generation.set('-')
        self.best_distance.set('-')
        self.minimizing_factor.set('1')

    def init_canvas_frame(self):
        frame_label = tk.LabelFrame(self.window, text="Routes MAP")
        frame_label.pack(side='left', anchor=tk.N, expand="yes")
        frame = tk.Frame(frame_label, width=400, height=400)
        frame.pack(fill='both', padx=10, pady=5, expand=True)
        self.canvas_id = tk.Canvas(frame, bg="powder blue")
        self.canvas_id.bind('<ButtonPress-1>', self.add_route)
        self.canvas_id.pack()

    def init_graphs(self):
        frame_label = tk.LabelFrame(self.window, text="Graph 1")
        frame_label.pack(side='left', anchor=tk.N, expand="yes")
        frame = tk.Frame(frame_label, width=400, height=400)
        frame.pack(fill='both', padx=10, pady=5, expand=True)
        self.graphs['graph1'] = frame

        frame_label = tk.LabelFrame(self.window, text="Graph 2")
        frame_label.pack(side='left', anchor=tk.N, expand="yes")
        frame = tk.Frame(frame_label, width=400, height=400)
        frame.pack(fill='both', padx=10, pady=5, expand=True)
        self.graphs['graph2'] = frame

    def update_graph_1(self):
        frame = self.graphs['graph1']
        x, y = list(), list()
        for i in self.graphs_data['graph1']:
            _x, _y = i
            x.append(_x)
            y.append(_y)

        for widget in frame.winfo_children():
            widget.destroy()
        fig = Figure(figsize=(7, 6), dpi=75)
        fig.suptitle('Total Distance by Generation', fontsize=20)
        plot1 = fig.add_subplot(111)
        plot1.plot(
            x,  # X
            y  # Y
        )
        plot1.set_ylabel("Total Distance", fontsize=14)
        plot1.set_xlabel("Generation", fontsize=14)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        canvas.get_tk_widget().pack()

    def update_graph_2(self):
        frame = self.graphs['graph2']
        x_global_best, x_local_best, y = list(), list(), list()
        for i in self.graphs_data.get('graph2', list()):
            _y, _x_local_best, _x_global_best = i
            x_local_best.append(_x_local_best)
            x_global_best.append(_x_global_best)
            y.append(_y)

        for widget in frame.winfo_children():
            widget.destroy()
        fig = Figure(figsize=(7, 6), dpi=75)
        fig.suptitle('OverallBest/CurrentBest Fitness by Generation', fontsize=20)
        plot1 = fig.add_subplot(111)
        plot1.plot(
            y,
            x_global_best,
            color='r',
        )
        plot1.plot(
            y,
            x_local_best,
            color='g',
        )
        plot1.set_ylabel("Fitness", fontsize=14)
        plot1.set_xlabel("Generation", fontsize=14)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        canvas.get_tk_widget().pack()

    def start_endless(self):
        self.start(with_threshold=False)

    def start_with_threshold(self):
        self.start(with_threshold=True)

    def start(self, with_threshold: bool):

        self.genetic_algorithm = RouteOptimizationGeneticAlgorithm()
        self.graphs_data = dict()

        self.is_genetic_algorithm_running = True
        self.genetic_algorithm.init(
            available_coordinates=self.routes,
            population_size=int(self.population_count.get()),
            mutation_rate=float(self.mutation_rate_percent.get()) / 100,  # Convert % to Decimal
            minimizing_factor=float(self.minimizing_factor.get()),
        )

        while self.is_genetic_algorithm_running is True:

            # -- Check for Threshold condition (100) -- #
            if with_threshold is True:
                if self.genetic_algorithm.generation - self.genetic_algorithm.best_generation >= 100:
                    break

            # -- Next Generation -- #
            self.genetic_algorithm.set_next_generation()

            # -- Function to create  connections -- #
            connections = list()
            start = None
            last = None
            for i in self.genetic_algorithm.best_population_order.data:
                if start is None:
                    start = last = i
                    continue
                connections.append((*i, *last))
                last = i
            # connections.append((*last, *start))

            self.average_fitness.set(f'{round(self.genetic_algorithm.average_fitness * 100, ndigits=2)}')
            self.best_fitness.set(f'{round(self.genetic_algorithm.best_population_order.fitness_score * 100, ndigits=2)}')
            self.best_generation.set(f'{self.genetic_algorithm.best_generation}')
            self.best_distance.set(f'{round(self.genetic_algorithm.best_population_order.total_distance, ndigits=2)}')
            self.generations.set(f'{self.genetic_algorithm.generation}')
            d = self.graphs_data.get('graph1', list())
            d.append((self.genetic_algorithm.generation, round(self.genetic_algorithm.best_population_order.total_distance, ndigits=2)))
            self.graphs_data['graph1'] = d

            d = self.graphs_data.get('graph2', list())
            d.append((self.genetic_algorithm.generation, self.genetic_algorithm.best_population_order.fitness_score, self.genetic_algorithm.current_best_population_order.fitness_score))
            self.graphs_data['graph2'] = d

            # -- Clear previous connections from route map -- #
            self.clear_connections()

            # -- Add new connections to route map -- #
            for conn in connections:
                self.add_route_connection(*conn)

            # -- Sleep so that GUI is interactive -- #
            self.__waiting__(msec=50)

        self.update_graph_1()
        self.update_graph_2()

    def stop(self):
        self.is_genetic_algorithm_running = False
        # -- Update Graphs -- #
        self.update_graph_1()
        self.update_graph_2()

    def reset(self):
        self.set_options_frame_defaults()
        self.routes = list()
        self.canvas_id.delete('all')
        self.is_genetic_algorithm_running = False
        self.graphs_data = dict()

    def add_route(self, event):
        ratio = 3
        x1, y1 = (event.x - ratio), (event.y - ratio)
        x2, y2 = (event.x + ratio), (event.y + ratio)
        self.canvas_id.create_oval(x1, y1, x2, y2, fill='black')
        center = self.find_center_oval(x1, y1, x2, y2)
        self.routes.append(center)

    def add_route_connection(self, x1, y1, x2, y2):
        line_id = self.canvas_id.create_line(x1, y1, x2, y2, fill="black", tags=f"{x1},{y1},{x2},{y2}")
        self.route_connections.append(line_id)

    def clear_connections(self):
        while self.route_connections:
            line_id = self.route_connections.pop(0)
            self.canvas_id.delete(line_id)

    @staticmethod
    def find_center_oval(x1, y1, x2, y2) -> tuple:
        """     Returns x,y location of center of Oval      """
        return int((x1 + x2)/2), int((y1+y2)/2)

    def __waiting__(self, msec: int):

        """     Sleep Function for Tkiner   """

        var = tk.IntVar()
        self.window.after(msec, var.set, 1)
        self.window.wait_variable(var)
