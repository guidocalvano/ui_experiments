from dataclasses import dataclass
import numpy as np

class BaseRegion:
    pass


@dataclass
class Region(BaseRegion):

    parent: BaseRegion

    def set_parent(self, parent: BaseRegion):
        self.parent = parent

    def pick(self, position):
        if np.any(position > self.bounding_box[1, :]):
            return None

        if np.any(position < self.bounding_box[0, :]):
            return None

        yield self

    def render(self, screen):
        pass

    def sub_screen(self, screen):
        return screen[self.bounding_box[0, 0]:self.bounding_box[1, 0],
                      self.bounding_box[0, 1]:self.bounding_box[1 , 1], :]

    def paint(self, sub_screen):
        pass

class ComplexRegion(Region):

    def __init__(self):

        self.children = []

    def pick(self, position):

        inside = next(super().pick(position))
        if inside is None:
            return

        for  child in self.children:
            yield from child.pick(position)

        yield inside

        return

    def render(self, screen):

        sub_screen = self.sub_screen(screen)

        self.paint(sub_screen)

        for child in self.children:
            child.render(sub_screen)


class SimpleRegion(Region):

    pass



class SubRegion(SimpleRegion):

    to_child: np.array
    to_world: np.array

    child: Region

    def set_parent(self, parent):
        self.parent = parent
        ancestor = parent
        while ancestor is not None and not isinstance(ancestor, SubRegion):
            ancestor = ancestor.parent

        if ancestor is None:
            self.to_world = np.eye(3)
            return

        #@TODO check coordinate systems here
        self.to_world = np.linalg.inv(np.linalg.inv(ancestor.to_world) @ self.to_child)


    def pick(self, position):
        transformed_position = position @ self.transform

        if not np.all(np.floor(transformed_position) == 0):
            return

        yield self.child

    def _sub_screen(self, screen):
        bounding_box = np.array([[0, 0, 1],[1, 1, 1]]) @ np.linalg.inv(self.transform)

        return screen[bounding_box[0, 0]:bounding_box[1, 0], bounding_box[0, 1]: bounding_box[1, ], :]

    def render(self, screen):
        self.child.render(self.sub_screen(screen))
