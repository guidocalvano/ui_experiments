import asyncio
import threading
import numpy as np

import pyglet
from pyglet.gl import GLubyte

import signals
import time


class App(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def start(self):

        # loop = asyncio.get_event_loop()
        # loop.create_task(self.flicker_rect())

        while(True):
            self.dispatch_events()
            # self.clear()
            await asyncio.sleep(0.02)


    async def flicker_rect(self):
        screen_array = np.zeros([self.height, self.width, 3], dtype=np.uint8)


        while True:
            screen_array[100:200, 20:30, :] = (np.random.random([3]) * 255).astype(np.uint8)

            self.render(screen_array)

            await asyncio.sleep(.1)

    def on_resize(self, width, height):
        print(f'The window was resized to {width},{height}')
        # self.screen_array.set_state(np.zeros([height, width, 3], dtype=np.uint8))

    def on_mouse_motion(self, x, y, button, modifiers):
        pass

    # def on_mouse_press(self, x, y, button, modifiers):
    #     self.click.set_state({"x": x, "y": y, "button": button, "modifiers": modifiers})

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def render(self, screen_array):
        t = time.time()
        # swap_xy = np.ascontiguousarray(np.transpose(self.screen_array, [1, 0, 2]))
        #
        # pitch = self.screen_array.shape[0] * self.screen_array.shape[2]
        # image = pyglet.image.ImageData(
        #     self.screen_array.shape[0],
        #     self.screen_array.shape[1],
        #     "RGB",
        #     swap_xy.ctypes.data,
        #     pitch=pitch
        # )

        pitch = screen_array.shape[1] * screen_array.shape[2]
        image = pyglet.image.ImageData(
            screen_array.shape[1],
            screen_array.shape[0],
            "RGB",
            screen_array.ctypes.data,
            pitch=pitch
        )

        image.blit(0, 0)
        self.flip()

        # print(time.time()-t)

# def array_to_image_data(a):
#     return (GLubyte * a.size)( *np.reshape(np.transpose(a, [1, 0, 2]), [-1] ))

if __name__ == "__main__":

    async def process():
        app = App(None)
        a = app.start()
        b = app.flicker_rect()

        loop = asyncio.get_event_loop()
        loop.create_task(a)
        loop.create_task(b)

        await a
    asyncio.run(process())