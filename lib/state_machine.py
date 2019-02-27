from termcolor import colored


class StateMachine:
    def __init__(self, state_transitions, current_step, log = True):
        self.transitions = state_transitions
        self.step = current_step
        self.steps = 0
        self.log = log

    def next(self):
        self.steps += 1
        if self.log:
            print(
                colored("transition from {} to {} step".format(self.step, self.transitions[self.step]), "magenta")
            )
        self.step = self.transitions[self.step]