import tr as lang_tr


def main() -> None:
    lang_tr_dict = lang_tr.to_dict()
    print("{", end="")
    for head_k in lang_tr_dict.keys():
        if isinstance(lang_tr_dict[head_k], str):
            print(f"'{head_k}': None")
        elif isinstance(lang_tr_dict[head_k], dict):
            print(f"'{head_k}'", end=": {\n")
            for k in lang_tr_dict[head_k].keys():
                print(f"'{k}': None,")
        print(",", end="")
    print("}")


if __name__ == "__main__":
    main()
