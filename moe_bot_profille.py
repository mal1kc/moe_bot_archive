import profile


def programi_baslat():
    from moe_bot import main as moe_bot_main

    moe_bot_main()


if __name__ == "__main__":
    profile.run("programi_baslat()", "moe_bot_profile.report")
