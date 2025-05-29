class Signal:

    def __init__(self):
        self.state = None
        self.observers = []

        self.is_outdated = True

    def set_observers_outdated(self):
        if self.is_outdated: return

        self.is_outdated = True

        [observer.set_observers_outdated() for observer in self.observers]

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def _set_state(self, state):
        # underscore to mark as private. This indicates that only input signals should be used to set state
        self.state = state
        self.is_outdated = False

        [observer.set_observers_outdated() for observer in self.observers]

    def get_state(self):
        raise Exception("State cannot be retrieved without defining how")

class Input(Signal):

    def __init__(self):
        super().__init__()

        # not setting state here allows the input signal to be passed like a promise


    def set_state(self, state):
        self._set_state(state)

    def get_state(self):
        return self.state


class Calculation(Signal):

    def __init__(self, calculation, inputs):
        super().__init__()
        self.calculation = calculation

        self.inputs = inputs

        [input.add_observer(self) for input in self.inputs]

    def get_state(self):
        if not self.is_outdated:
            return self.state

        state_list = [input.get_state() for input in self.inputs]

        self._set_state(self.calculation(*state_list))

        return self.state

class SignalList(Signal):
    def __init__(self, list):
        super().__init__()

        [signal.add_observer(self) for signal in list]


    def append(self, signal):
        signal.add_observer(self)
        self.state.append(signal)

        self.set_observers_outdated()

    def remove(self, signal):
        self.state.remove(signal)

        self.set_observers_outdated()


class Output(Calculation):

    def __init__(self, effect=lambda state: None, signal=None):
        super().__init__(effect, [signal])

        self.in_update = False
        self.is_outdated = False
        # self._set_state(signal.get_state())
        #
        # self.calculation(self.state)


    def set_observers_outdated(self):
        # super().set_observers_outdated()
        if self.in_update:
            return
        self.in_update = True
        self.state = self.inputs[0].get_state()

        self.in_update = False

        # self.is_outdated = False
        #
        self.calculation(self.state)


def test():
    inp = Input()

    calc = Calculation(lambda val: "calc on " + str(val), [inp])

    assert calc.get_state() == "calc on " + str(None)

    assert inp.get_state() is None

    inp.set_state(3)

    assert calc.state == "calc on " + str(None)

    assert calc.get_state() == "calc on " + str(3)

    assert inp.get_state() == 3

    inp.set_state(4)

    assert calc.get_state() == "calc on " + str(4)

    bla = []

    outp = Output(lambda state: bla.append(state), calc)

    assert bla[0] ==  "calc on " + str(4)

    inp.set_state(5)

    assert bla[1] == "calc on " + str(5)
    assert calc.state == "calc on " + str(5)



if __name__ == '__main__':
    test()