from moe_bot import arayuz
from moe_bot.temel_siniflar import DilEnum, Diller

# def print_window_size(event):
#     print("Window size: {}x{}".format(event.width, event.height))


def print_sys_module_names():
    import sys

    for name, module in sys.modules.items():
        print(name)


if __name__ == "__main__":
    Diller(DilEnum.TR)
    ana_pencere = arayuz.MainGui(title="moe bot")
    ana_pencere.change_page(arayuz.GUIPagesEnum.MOE_GATHERER)
    ana_pencere.interaction_variables["server"] = None
    ana_pencere.root.resizable(True, True)
    # ana_pencere.root.bind("<Configure>", print_window_size)
    ana_pencere.mainloop()

#          uyari1
# resource  lvls    sefer_Sys
# |         |       resim
# |         |       btn basla
# |         |
# |         |       btn_cik
# hpsi      hpsi
#           uyari2
