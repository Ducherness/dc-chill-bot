import os
import time
import config
import modules.classes

from config import Config
from discord.ext import commands
from colorama import Back, Fore, Style, init
init()

class ChillBot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kwargs['config'] = Config()

        self.config = config.Config()

    async def load_cogs(self):
            await self.tree.sync()

            current_time = (
                Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S") + Fore.BLUE + " CUR" + Back.RESET + Fore.WHITE + Style.BRIGHT
            )
            cogs_directory = "cogs"
            exclude_directory = os.path.join("cogs", "default", "modules")

            if not os.path.exists(cogs_directory):
                print(current_time + Fore.RED + f" Directory '{cogs_directory}' does not exist!")
                return

            try:
                self.initial_extensions = []
                for root, _, files in os.walk(cogs_directory):
                    if exclude_directory in root:
                        continue
                    for file in files:
                        if file.endswith('.py'):
                            relative_path = os.path.relpath(os.path.join(root, file), cogs_directory)
                            module_path = relative_path.replace(os.path.sep, ".").replace(".py", "")
                            self.initial_extensions.append(f"cogs.{module_path}")

                if not self.initial_extensions:
                    print(current_time + Fore.RED + " No .py files found in the 'cogs' directory!")
                    return

                print(current_time + Fore.CYAN + " Found cog modules:", self.initial_extensions)

                for extension in self.initial_extensions:
                    try:
                        await self.load_extension(extension)
                        print(current_time + Fore.YELLOW + f" {extension} — has been successfully loaded!")
                    except Exception as e:
                        print(current_time + Fore.RED + f" Error loading {extension}:\n — {type(e).__name__}: {e}")

            except Exception as e:
                print(current_time + Fore.RED + f" Error while accessing 'cogs' directory: {e}")
                
    async def setup_hook(self):
        await self.load_cogs()