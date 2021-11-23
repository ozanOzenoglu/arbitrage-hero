from queue import Queue, Empty
from threading import Thread

class SafeWriter:
    def __init__(self, *args):
        self.filewriter = open(*args)
        self.queue = Queue()
        self.finished = False
        Thread(name = "SafeWriter", target=self.internal_writer).start()

    def write(self, data):
        self.queue.put(data)

    def internal_writer(self):
        while not self.finished:
            try:
                data = self.queue.get(True, 1)
            except Empty:
                continue
            self.queue.task_done()
            self.filewriter.write(data)

    def close(self):
        self.queue.join()
        self.finished = True
        self.filewriter.close()

#use it like ordinary open like this:
#w = SafeWriter("filename", "w")
#w.write("can be used among multiple threads")
#w.close() #it is really important to close or the programm would not end


from time import sleep

