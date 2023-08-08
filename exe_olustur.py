import PyInstaller.__main__
from distutils.dir_util import copy_tree


def main():
    PyInstaller.__main__.run(
        [
            "program_ac.spec",
        ]
    )

    copy_tree("./coordinates/", "./dist/coordinates/")


if __name__ == "__main__":
    main()
