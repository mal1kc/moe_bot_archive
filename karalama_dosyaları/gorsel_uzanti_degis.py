from PIL import Image
import sys


def main():
    argv1 = sys.argv[1]
    if argv1.endswith(".png"):
        Image.open(argv1).save(argv1.replace(".png", ".jpg"))
    elif argv1.endswith(".jpg"):
        Image.open(argv1).save(argv1.replace(".jpg", ".png"))


if __name__ == "__main__":
    main()
