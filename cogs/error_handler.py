import sys
import traceback
import logging

from discord.ext import commands
import discord


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        if hasattr(ctx.command, 'on_error'):  # ローカルのハンドリングがあるコマンドは除く
            return

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.CheckFailure):

            await ctx.send(f'you have no permission to execute {ctx.command}.')
            return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                print("couldn't send direct message")

        elif isinstance(error, commands.BadArgument):
            return await ctx.send("無効な引数です")

        elif isinstance(error, commands.CommandInvokeError):
            error = getattr(error, 'original', error)
            print(
                'Ignoring exception in command {}:'.format(
                    ctx.command),
                file=sys.stderr)
            traceback.print_exception(
                type(error),
                error,
                error.__traceback__,
                file=sys.stderr)
            error_content = f'error content: {error}\nmessage_content: {ctx.message.content}\nmessage_author : {ctx.message.author}\n{ctx.message.jump_url}'

            logging.error(error_content, exc_info=True)
            # 設定を変えてwarnまで出るようにするべし:ここで本番

    @commands.command(name='repeat', aliases=['mimic', 'copy'])
    async def do_repeat(self, ctx, *, inp: str):
        await ctx.send(inp)

    @do_repeat.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'inp':
                await ctx.send("You forgot to give me input to repeat!")


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
