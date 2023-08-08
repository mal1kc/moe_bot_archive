"""
process objeleri paylaşması
"""


from multiprocessing import Process


class Hello:
    def __init__(self, name: str | None) -> None:
        if name:
            self.name = name
        else:
            self.name = "unicorns"
        # if name is None:
        #     global name
        #     self.name = name

    def say_hello(self) -> None:
        print(f"Hello {self.name}")

    def __repr__(self) -> str:
        return f"Hello({self.name!r})"


class Hi:
    def __init__(self, thing) -> None:
        self.thing = thing

    def say_hi(self) -> None:
        print(f"Hi {self.thing}")

    def __repr__(self) -> str:
        return f"Hi({self.thing!r})"

    def __str__(self) -> str:
        return f"Hi {self.thing!s}"


class Yeller:
    def __init__(self, sayclass: object = None) -> None:
        global hello
        if sayclass is None:
            self.what_the_yell = hello
        else:
            self.what_the_yell = sayclass

    def yell(self) -> None:
        print(str(self.what_the_yell).upper())


class HelloProcess(Process):
    """
    process sınıfı kalıtımı
    """

    def __init__(self, name: str) -> None:
        super().__init__()
        global hello
        hello = Hello("ss")
        self.hi = Hi(name)
        self.yeller = Yeller()

    def run(self) -> None:
        self.yeller.yell()


def main() -> None:
    hp = HelloProcess("universe")
    hp.start()
    hp.join()


if __name__ == "__main__":
    main()
