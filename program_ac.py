import multiprocessing

multiprocessing.freeze_support()


def _bilgi_yazdir():
    print("\r")
    print("s: Bot başlat.\nd : Bot durdur. (Ekran taramasi bittikten sonra duracaktir)")


# class _Popen(multiprocessing.forking.Popen):
#     def __init__(self, *args, **kw):
#         if hasattr(sys, "frozen"):
#             # We have to set original _MEIPASS2 value from sys._MEIPASS
#             # to get --onefile mode working.
#             os.putenv("_MEIPASS2", sys._MEIPASS)  # type: ignore
#         try:
#             super(_Popen, self).__init__(*args, **kw)
#         finally:
#             if hasattr(sys, "frozen"):
#                 # On some platforms (e.g. AIX) 'os.unsetenv()' is not
#                 # available. In those cases we cannot delete the variable
#                 # but only set it to the empty string. The bootloader
#                 # can handle this case.
#                 if hasattr(os, "unsetenv"):
#                     os.unsetenv("_MEIPASS2")
#                 else:
#                     os.putenv("_MEIPASS2", "")


# class Process(multiprocessing.Process):
#     _Popen = _Popen


def main():
    app = uygulama_olustur()
    app.mainloop()


if __name__ == "__main__":
    from moe_gatherer import uygulama_olustur

    main()
