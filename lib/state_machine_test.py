from unittest import TestCase, main
from lib.state_machine import StateMachine


class StateMachineTest(TestCase):
    def test_next(self):
        transitions = {
            "1": "1.3",
            "1.3": "1.6",
            "1.6": "2",
            "2": "2.3",
            "2.3": "2.6",
            "2.6": "1"
        }
        machine = StateMachine(transitions, "1", False)
        steps = 0
        for x in ["1", "1.3", "1.6", "2", "2.3", "2.6"]:
            self.assertEqual(
                machine.step,
                x
            )
            self.assertEqual(
                machine.steps,
                steps
            )
            steps = steps + 1
            machine.next()


if __name__ == '__main__':
    main()
