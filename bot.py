import json
import sys
import traceback
from discord.ext import commands

with open("settings.json", encoding="utf-8") as config:
    config = json.load(config)

description = config["description"]
prefixes = config["prefixes"]
bot_token = config["token"]
modules = config["cogs"]

bot = commands.Bot(command_prefix=commands.when_mentioned_or(*prefixes), description=description)


@bot.event
async def on_ready():
    print('bot name: ' + bot.user.name)
    print('bot id: ' + bot.user.id)
    print('Loading cogs...')
    if __name__ == '__main__':
        modules_loaded = 0
        for module in modules:
            try:
                bot.load_extension(module)
                print('\t' + module)
                modules_loaded += 1
            except Exception as details:
                traceback.print_exc()
                print(f'Error loading the extension {module}', file=sys.stderr)
                print(details)

        print(str(modules_loaded) + '/' + str(modules.__len__()) + ' modules loaded')
        print('Systems 100%')
    print('------')


if __name__ == "__main__":
    bot.run(bot_token)
