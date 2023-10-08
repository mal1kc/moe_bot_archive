from moe_bot.temel_siniflar import Diller, DilEnum
from moe_bot import arayuz

# def print_window_size(event):
#     print("Window size: {}x{}".format(event.width, event.height))


def print_sys_module_names():
    import sys

    for name, module in sys.modules.items():
        print(name)


if __name__ == "__main__":
    Diller(DilEnum.TR)
    ana_pencere = arayuz.MainGui(title="moe bot")
    # ana_pencere.change_page(arayuz.GUIPagesEnum.LOGIN)
    ana_pencere.root.resizable(True, True)
    # ana_pencere.root.bind("<Configure>", print_window_size)
    ana_pencere.mainloop()
    print(ana_pencere.interaction_variables)
