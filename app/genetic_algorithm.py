"""
    Stata should include
        Generations
        Average Fitness %

    Process
        SETUP
            Initialize a population of N elements, each with random DNA
        DRAW
            Selection: Evaluate Fitness for each element of population
            Reproduction:
                - pick two parents with probability according to relative fitness
                - crossover create child by combining the dna of these two parents
                - mutation mutate the children dna based on given probability
                - add new child to population
            Replace old population with new population
"""
import math
import random


class PopulationOrder:

    def __init__(self, source: list, do_shuffle=True):
        self.data = source[:]
        if do_shuffle is True:
            random.shuffle(self.data)
        self.fitness_score = 0
        self.fitness_score_percent = None
        self.total_distance = 0

    def __eq__(self, other):
        return self.data == other.data

    def __hash__(self):
        return hash(repr(self.data))

    def __gt__(self, other):
        """     Python Implementation for the .order() function      """
        return self.fitness_score_percent > other.fitness_score_percent

    def __len__(self):
        """     Custom Length implementation    """
        return len(self.data)

    def create_copy(self):
        """     Custom Copy Population Order Implementation     """
        return PopulationOrder(source=self.data.copy(), do_shuffle=False)

    def set_fitness_score(self, unique_paths: set, minimizing_factor: float):
        self.total_distance = 0
        first = None
        previous = None
        for index in range(len(self.data)):
            if first is None:
                first = previous = self.data[index]
                continue
            self.total_distance += self.get_relative_distance(*self.data[index], *previous)
            previous = self.data[index]
        # self.total_distance += self.get_relative_distance(*previous, *first)
        self.fitness_score = self.get_fitness_score(total_distance=self.total_distance, is_new=self not in unique_paths, minimizing_factor=minimizing_factor)

    def set_fitness_score_percent(self, total: float):
        self.fitness_score_percent = self.fitness_score / total

    @staticmethod
    def get_relative_distance(x1, y1, x2, y2):
        # -- Calculate Distance between two points -- #
        return abs(
            math.sqrt(
                (x2 - x1) ** 2 +
                (y2 - y1) ** 2
            )
        )

    @staticmethod
    def get_fitness_score(total_distance: float, is_new: bool, minimizing_factor: float):
        # -- MINIMIZATION -- #
        # -- We want to minimize distance
        # -- If we divide one by the distance, then
        # -- lower distances will have a higher fitness
        # -- score.
        if is_new is True:
            return 1 / (total_distance * minimizing_factor)
        else:
            return 1 / total_distance


class RouteOptimizationGeneticAlgorithm:

    """
        Takes in a list of tuples (x,y coordinates) of routes
        on a 2 Dimensional space. Then using Genetic Algorithm
        (GA), the best path is efficiently chosen.
    """

    # -- Core -- #
    population_size: int
    population: list
    generation: int
    mutation_rate: float

    # -- STATS -- #
    best_population_order: PopulationOrder or None
    best_generation: int
    current_best_population_order: PopulationOrder or None
    average_fitness: float

    # -- Uniqueness -- #
    unique_paths: set
    unique_paths_max: int

    minimizing_factor: float

    def init(self, available_coordinates: list, population_size: int, mutation_rate: float, minimizing_factor: float) -> None:
        self.generation = 0
        # -- Inputs -- #
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        # -- Stats -- #
        self.average_fitness = 0
        self.best_population_order = None
        self.best_generation = 0
        self.current_best_population_order = None
        # -- Uniqueness -- #
        self.unique_paths = set()

        self.minimizing_factor = minimizing_factor

        # -- Initial Population -- #
        self.population = self.init_population(available_coordinates)

    # -------------------- #
    # -- INITIALIZATION -- #
    # -------------------- #

    def init_population(self, available_coordinates: list) -> list:
        """
            Takes available coordinates and generates a population
            of population_size with each element being in
            shuffled/random order initially.
        """
        population = list()
        for i in range(self.population_size):
            population_order = PopulationOrder(available_coordinates, do_shuffle=True)
            population_order.set_fitness_score(self.unique_paths, self.minimizing_factor)
            self.unique_paths.add(population_order)
            population.append(population_order)
        population = self.set_fitness_percentages(population)
        return population

    # ------------------------ #
    # -- Next Generation(s) -- #
    # ------------------------ #

    def set_next_generation(self) -> None:
        """
            Generates a next generation and then sets the
            fitness scores / percentages.
        """
        self.current_best_population_order = None
        new_population = self.generate_next()
        new_population = self.set_fitness_percentages(new_population)
        self.population = new_population

    def generate_next(self) -> list:
        """
            The next generation is set by the following processes:
                - Natural Selection (randomly select population using fitness percentages)
                - CrossOver the two populations returned from natural selection. This
                    process mixes the populations half/half (or relative if odd).
                - Mutation randomly swaps two items if a randomly generated float is lower
                    then the mutation rate.
        """

        # -- Up Generation Count -- #
        self.generation += 1
        # -- Iterate through population count to begin  -- #
        # -- evolution cycle.                           -- #
        new_population = list()
        for index in range(self.population_size):
            # -- CONTEXT: Population Order (PO) -- #
            # -- Natural Selection -- #
            po_a = self.natural_selection(self.population).create_copy()
            po_b = self.natural_selection(self.population).create_copy()
            # -- CrossOver -- #
            po = self.crossover_v2(po_a, po_b)
            # -- Mutation -- #
            po = self.mutation_v3(po)
            # -- Set fitness percentages -- #
            po.set_fitness_score(self.unique_paths, self.minimizing_factor)
            self.unique_paths.add(po)
            # -- Add to new population -- #
            new_population.append(po)
        return new_population

    @staticmethod
    def natural_selection(population: list) -> PopulationOrder:
        """
            Population list is sorted in ascending order of fitness score
            percentages. If the random_float falls under a given population
            orders percentage start/end, then it matched that population
            order.
        """
        # -- Random Float 0-1 to represent 0 - 100 % -- #
        random_float = random.uniform(0, 1)
        # -- CONTEXT: Population Order (PO) -- #
        fitness_start = 0
        for po in population:
            fitness_end = fitness_start + po.fitness_score_percent
            if fitness_start <= random_float <= fitness_end:
                return po
            fitness_start = fitness_end

    @staticmethod
    def crossover_v2(po_a: PopulationOrder, po_b: PopulationOrder) -> PopulationOrder:
        """
            Performs the following CrossOver method
                - Find the middle of the array
                - Combine the first half of the first population
                  and the second half of the second generation,
                  ensuring we maintain the uniqueness of
                  coordinates.
        """
        # -- CONTEXT: Population Order (PO) -- #
        # -- Find middle of list -- #
        mid_point = int(len(po_a)/2)
        # -- First half of First Population -- #
        new_data = po_a.data[:mid_point]
        # -- Second Half of Second Population -- #
        new_data += [
            i for i in po_b.data if i not in new_data
        ]
        # -- Set and Return -- #
        po_a.data = new_data
        return po_a

    def mutation_v3(self, po: PopulationOrder) -> PopulationOrder:
        """
            For the length of coordinates in a given population,
            perform the following operations:
                - Generate a random float 0-1
                - - if the number is lower then the mutation_rate,
                - - - then swap two random coordinates.
        """
        # -- CONTEXT: Population Order (PO) -- #
        # -- Perform this random probability swap a -- #
        # -- number of times equal to the number of -- #
        # -- coordinates.                           -- #
        for i in range(len(po)):
            # -- If random float is smaller then mutation rate provided -- #
            if random.uniform(0, 1) <= self.mutation_rate:
                # -- Generate random indexes to swap -- #
                index1 = random.randint(0, len(po) - 1)
                index2 = random.randint(0, len(po) - 1)
                # -- Traditional Swap method -- #
                tmp = po.data[index1]
                po.data[index1] = po.data[index2]
                po.data[index2] = tmp
        return po

    # ------------ #
    # -- SHARED -- #
    # ------------ #

    def set_fitness_percentages(self, population: list) -> list:
        """
            (1) Calculates the total Fitness of each order of coordinates
            (2) For each order of coordinates, set the fitness percent using the total fitness
            (3) Order population by Fitness Score
        """
        # -- Calculate total Fitness -- #
        total_fitness_score = sum(
            [population.fitness_score for population in population]
        )
        # -- CONTEXT: Population Order (PO) -- #
        # -- Set individual fitness percentage for this given population -- #
        for po in population:
            po.set_fitness_score_percent(total=total_fitness_score)
            # -- GLOBALS: Best Population by Fitness Score -- #
            if self.best_population_order is None:
                self.best_population_order = po
                self.best_generation = self.generation
            elif po.fitness_score > self.best_population_order.fitness_score:
                self.best_population_order = po
                self.best_generation = self.generation
            # -- GLOBALS: Best ["current"] Population by Fitness Score -- #
            if self.current_best_population_order is None or po.fitness_score > self.current_best_population_order.fitness_score:
                self.current_best_population_order = po
            # -- GLOBALS: Average Fitness -- #
            self.average_fitness = (self.average_fitness + po.fitness_score) / 2
        # -- Sort by fitness lower to highest -- #
        population.sort()
        return population
