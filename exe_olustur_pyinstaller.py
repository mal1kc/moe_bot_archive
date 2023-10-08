import PyInstaller.__main__
from distutils.dir_util import copy_tree


def main():
    PyInstaller.__main__.run(["moe_bot_program.py"])

    copy_tree("./coordinates/", "./dist/coordinates/")


if __name__ == "__main__":
    main()
