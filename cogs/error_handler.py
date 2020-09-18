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
            return await ctx.send(f'このコマンドを実行する権限がありません:{ctx.author.mention}\n{error}')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                print("couldn't send direct message")

        elif isinstance(error, commands.BadArgument):
            return await ctx.send("無効な引数です")

        # elif isinstance(error, commands.MissingRequiredArgument):
        #     return await ctx.send("引数が足りません")

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(f'このコマンドを実行する権限がありません:{ctx.author.mention}\n{error}')

        else:
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


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
