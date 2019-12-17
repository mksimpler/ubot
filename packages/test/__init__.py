from tes_module import welcome


def start(bot):
    if bot.seen("menu/button_battle"):
        bot.tap("menu/button_battle")
        print("I'm done")

    welcome()
