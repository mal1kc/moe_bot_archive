from moe_bot.kaynakislem import Varsayilanlar


def test_singleton_is_always_same():
    assert Varsayilanlar() is Varsayilanlar()

    class Dummy:
        pass

    assert Varsayilanlar() is not Dummy()
