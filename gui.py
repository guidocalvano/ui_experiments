import numpy as np

import signals
from app import App
from scene import BaseRegion

import asyncio


class SimpleRegion:
    def __init__(self, parent: BaseRegion, box: np.array):
        self.parent = parent

        if self.parent is not None and hasattr(self.parent, "children"):
            self.parent.children.append(self)

        self.box = box

        self.color = (np.random.random([3]) * 255).astype(np.uint8)

        self.click = signals.Input()

    def is_inside(self, point: np.array) -> bool:
        relative_point = point @ np.linalg.inv(self.box.get_state())
        print(point)
        print(relative_point)
        if np.all(np.floor(relative_point[:2]) == 0):
            return True

        return False

    def draw(self, screen):

        def do_draw(screen, box):
            print("DO DRAW")
            bounds = np.array([[0, 0, 1], [1, 1, 1]]) @ box
            screen[bounds[0, 1]: bounds[1, 1], bounds[0, 0]:bounds[1, 0], :] = (np.random.random([3]) * 255).astype(np.uint8)[np.newaxis, np.newaxis, :]

            print(bounds[1, 1], bounds[1, 0])

            print(screen.shape)

        self.screen_update = signals.Calculation(do_draw, [screen, self.box])

        self.screen_output = signals.Output(lambda v: print("screen output"), self.screen_update)

        self.screen_output.get_state()
        # bounds = np.array([[0, 0, 1], [1,1, 1]]) @ self.box.get_state()


    def pick(self, point):

        if self.is_inside(point):
            return self

        return None


class ComplexRegion(SimpleRegion):
    def __init__(self, parent: BaseRegion, box: np.array):
        super().__init__(parent, box)

        self.children = []

    def pick(self, point):

        if not self.is_inside(point):
            return None

        for child in self.children:

            result = child.pick(point @ np.linalg.inv(self.box.get_state()))
            if result is not None:
                return result

        return self


class GUI(BaseRegion):
    def __init__(self):
        self.app = App(resizable=True)

        self.click = signals.Input()

        self.width = signals.Input()
        self.height = signals.Input()

        self.width.set_state(self.app.width)
        self.height.set_state(self.app.height)

        self.screen_array = signals.Calculation(lambda height, width: np.zeros([height, width, 3], dtype=np.uint8), [self.height, self.width])


        @self.app.event
        def on_mouse_press(x, y, button, modifiers):
            self.click.set_state({"x": x, "y": y, "button": button, "modifiers": modifiers})

        @self.app.event
        def on_resize(width, height):
            self.width.set_state(width)
            self.height.set_state(height)
            print("SET WIDTH HEIGHT {width}, {height}".format(width=width, height=height))

        window_box = signals.Calculation(lambda width, height:
                                       np.array([
                                                 [height, 0, 0],
                                                 [0, width, 0], [0, 0, 1]
        ]), [self.height, self.width])

        self.root = ComplexRegion(self, window_box)

        self.root.draw(self.screen_array)

        # child = SimpleRegion(self.root, np.array([[.5, 0, 0],[0, 1, 0], [0,0,1]]))

        # signals.Output(lambda state: print(f"Clicked child {state}"), child.click)

        signals.Output(lambda state: print(f"Clicked root {state}"), self.root.click)

        self.output = signals.Output(lambda state: self.root.pick(np.array([state["x"], state["y"], 1] )).click.set_state(state), self.click)

        asyncio.run(self.app.start())


if __name__ == "__main__":
    GUI()