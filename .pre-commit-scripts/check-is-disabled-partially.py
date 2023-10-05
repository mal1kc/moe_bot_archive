import os

files_to_check = {"./moe_bot/hatalar.py": [32, 40]}


def main():
    disabled_lines = []

    for fpath, lines_to_check in files_to_check.items():
        if not os.path.exists(fpath):
            print(f"{fpath} dosyası bulunamadı.")

            exit(1)

        with open(fpath, "r", encoding="utf-8") as f:
            print(f"{fpath} dosyası bulundu. Kontrol ediliyor. satırlar {lines_to_check[0]}-{lines_to_check[1]}")
            fline = f.readlines()
            for _line in range(lines_to_check[0], lines_to_check[1]):
                if "#" in fline[_line]:
                    disabled_lines.append(_line)
        if disabled_lines == list(range(lines_to_check[0], lines_to_check[1])):
            print(f"{fpath} dosyasındaki {disabled_lines} satırlarının hepsi yorum satırı.")
            exit(1)

    exit(0)


if __name__ == "__main__":
    main()
