import asyncio
from threading import Thread, Lock

class Thing:

    def __init__(self):
        self.init_lock = Lock()
        self.init_lock.acquire()

        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError as e:
            self.loop = asyncio.new_event_loop()

        self.lock = Lock()

        register_thread_safe_cell_execution()

        self.init_lock.release()

    def async_thread_safe

    async def cell_execution_loop(self):

        # Lock so you can release in the loop
        self.lock.acquire()
        while True:
            self.lock.release()  # let the notebook cell thread execute
            self.lock.acquire()  # and immediately lock again

            await asyncio.sleep(0)  # Let the event loop execute a scheduled task


    def asyncio_in_thread(init_lock):
        global notebook_loops
        global notebook_locks

        init_loop(init_lock)

        loop = get_event_loop()
        loop.run_until_complete(cell_execution_loop(notebook_locks[notebook_hash()]))

thread = Thread(target=asyncio_in_thread, args=(init_lock,)).start()