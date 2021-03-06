from helpers.question_parser import QuestionParser
from helpers.reply_composer import ReplyComposer
from algo.algo_selector import AlgoSelector


class AlgoRunner:

    def __init__(self, brain):
        self.brain = brain
        self.input_nodes = []
        self.stack = []
        self.active_algorithm = None
        self.current_tick = 0
        self.verbose = False
        for algo in self.brain.algo_container.algorithms:
            algo.callback = self.algorithm_callback


    def init(self, input):
        question_parser = QuestionParser(self.brain.onto_container, input)
        self.input_nodes = question_parser.get_initial_nodes()

        self.brain.working_memory.context = question_parser.get_context_entry()

        algo_selector = AlgoSelector()
        algo_name = algo_selector.get_algo(input)
        self.active_algorithm = self.brain.algo_container.get_algo_by_name(algo_name)


    def run(self, input):
        self.init(input)
        self.run_loop()

        reply_composer = ReplyComposer(brain=self.brain)
        return reply_composer.reply_as_string()


    def run_loop(self):
        self.current_tick = 1
        self.stack.append(self.active_algorithm)
        self.active_algorithm.start(self.current_tick)

        while not self.brain.algo_container.is_finished() and self.current_tick <= 60:
            self.update_state()
            if self.verbose:
                print(self.brain.algo_container.active_algorithm, self.brain.onto_container)
                print(self.brain.working_memory)


    def update_state(self):
        self.brain.current_tick = self.current_tick
        self.active_algorithm.update(self.current_tick)
        self.current_tick += 1


    def algorithm_callback(self, switching_to):
        self.active_algorithm = self.brain.algo_container.get_algo_by_name(switching_to)
        self.stack.append(self.active_algorithm)
        self.active_algorithm.start(self.current_tick)


    def reset_state(self, algorithm):
        for node in self.brain.onto_container.nodes:
            node.potential = 0
        self.fire_initial()
        algorithm.init_onto_nodes()

