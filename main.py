import pyglet


def main():
    window = pyglet.window.Window()

    # window.switch_to()


    @window.event
    def on_draw():
        window.clear()

        for y in range(40):
            for x in range(100):
                label = pyglet.text.Label('H',
                                          font_name='Times New Roman',
                                          font_size=10,
                                          x=x * 10, y=y * 10,
                                          anchor_x='center', anchor_y='center')

                label.draw()


    # @window.event
    # def on_draw():
    #     window.clear()
    #     label.draw()
    #     print('.')
    # window.switch_to()
    pyglet.app.run()
    # input()
    pass


if __name__ == '__main__':
    main()