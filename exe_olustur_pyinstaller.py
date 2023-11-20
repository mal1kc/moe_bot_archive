from distutils.dir_util import copy_tree

import PyInstaller.__main__


def main():
    PyInstaller.__main__.run(["moe_bot_program.spec"])

    copy_tree("./coordinates/", "./dist/coordinates/")


if __name__ == "__main__":
    main()
