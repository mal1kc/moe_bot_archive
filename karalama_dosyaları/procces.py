from multiprocessing import Process


class P(Process):
    def __init__(self):
        super(P, self).__init__()

    def run(self):
        print("hello")
        self.aa()

    def __del__(self):
        # print('del')
        ...

    def aa(self):
        print("aa")


if __name__ == "__main__":
    p = P()
    p.start()
    p.join()
