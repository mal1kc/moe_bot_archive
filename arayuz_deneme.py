import moe_bot.arayuz as arayuz


def print_window_size(event):
    print("Window size: {}x{}".format(event.width, event.height))


if __name__ == "__main__":
    ana_pencere = arayuz.MainGui(title="moe bot")
    ana_pencere.change_page(arayuz.GUIPagesEnum.MOE_GATHERER)
    ana_pencere.root.resizable(True, True)
    ana_pencere.root.bind("<Configure>", print_window_size)
    ana_pencere.mainloop()

#          uyari1
# resource  lvls    sefer_Sys
# |         |       resim
# |         |       btn basla
# |         |
# |         |       btn_cik
# hpsi      hpsi
#           uyari2
