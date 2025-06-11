class Signal:

    def __init__(self):
        self.state = None
        self.observers = []
        self.is_initialized = False

        self.is_outdated = True

    def set_outdated(self):
        if self.is_outdated: return

        self.is_outdated = True

        [observer.set_outdated() for observer in self.observers]

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def _set_state(self, state):
        # underscore to mark as private. This indicates that only input signals should be used to set state
        self.state = state
        self.is_outdated = False
        # self.is_initialized = True
        self.propagate_initialized(True)
        [observer.set_outdated() for observer in self.observers]

    def propagate_initialized(self, is_initialized):
        old_is_initialized = self.is_initialized

        self.is_initialized = is_initialized

        if old_is_initialized == is_initialized:
            return

        [observer.propagate_initialized(self.is_initialized) for observer in self.observers]


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

    def propagate_initialized(self, new_is_initialized):

        if not new_is_initialized:
            self.is_initialized = new_is_initialized
            [observer.propagate_initialized(self.is_initialized) for observer in self.observers]

        # new_is_initialized is true and calculation was already is_initialized so nothing changes
        if self.is_initialized:
            return

        # we are trying to switch on is_initialized, but we need to check if the inputs warrent this
        # suppose true
        for input in self.inputs:
            if not input.is_initialized:
                return

        self.is_initialized = new_is_initialized

        [observer.propagate_initialized(self.is_initialized) for observer in self.observers]



class SignalInput(Calculation):
    def __init__(self, initial_signal=None):
        if initial_signal is None:
            initial_signal = Input()

        super().__init__(lambda x: x, [initial_signal])

        if initial_signal is None:
            self.propagate_initialized(False)
            return

        self.propagate_initialized(initial_signal.is_initialized)

    def set_input(self, signal):
        [input.remove_observer(self) for input in self.inputs]
        signal.add_observer(self)

        self.inputs = [signal]

        self.propagate_initialized(signal.is_initialized)
        self.set_outdated()

class Output(Calculation):

    def __init__(self, effect=lambda state: None, signal=None):
        super().__init__(effect, [signal])
        # to not defer initialisation call get_state immediately.
        # self.get_state()
        if signal.is_initialized:
            self.get_state()

    def propagate_initialized(self, new_is_initialized):
        if not self.is_initialized and new_is_initialized:
            self.get_state()



    def set_outdated(self):
        super().set_outdated()
        self.get_state()
        # self.state = self.inputs[0].get_state()
        #
        #
        # # self.is_outdated = False
        # #
        # self.calculation(self.state)




class SignalList(Signal):
    def __init__(self, list):
        super().__init__()

        [signal.add_observer(self) for signal in list]


    def append(self, signal):
        signal.add_observer(self)
        self.state.append(signal)

        self.set_outdated()

    def remove(self, signal):
        self.state.remove(signal)

        self.set_outdated()


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


    # test deferred initialization
    ladida = []

    inp2 = Input()

    outp2 = Output(lambda state: ladida.append(state), inp2)

    assert len(ladida) == 0

    inp2.set_state(6)
    assert ladida[0] == 6

    # SIGNAL INPUT
    tralala = []

    # test empty initialization
    si = SignalInput()

    outp3 = Output(lambda state: tralala.append(state), si)

    assert len(tralala) == 0
    assert si.is_initialized == False

    # test initialization with input that is not initialized
    inp3 = Input()

    si.set_input(inp3)
    assert len(tralala) == 0
    # test then initializing
    inp3.set_state(7)

    assert inp3.is_initialized == True
    assert si.is_initialized == True
    assert outp3.is_initialized == True

    assert tralala[0] == 7

    # test get state
    c = Calculation(lambda val: val + 2, [si])

    assert len(tralala) == 1
    assert c.state == None

    assert c.get_state() == 9

    # test attaching output to not initialized signal input
    # test attaching output to initialized signal input
    # test swapping initialized input with not initialized input


if __name__ == '__main__':
    test()