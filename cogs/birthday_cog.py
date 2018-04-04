import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import db.db_adapter as database
from datetime import datetime, timedelta

from db.birthday import Birthday


class BirthdayCommands:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Today starts as yesterday to make the loop run the first time
        self.today = (datetime.today() - timedelta(days=1)).date()
        self.bot.loop.create_task(self.birthday_loop())

    today = None

    @commands.command(pass_context=True)
    async def birthday_add(self, ctx: Context, day, month, year=-1):
        """<Day Mont [Year]> Adds your birthday."""
        member: discord.Member = ctx.message.author
        # Just in case don't add bots to the database
        if member.bot:
            return
        database.create_birthday(user_id=member.id, day=day, month=month, year=year)
        await self.bot.say('Birthday added')

    @commands.command(pass_context=True)
    async def birthday_update(self, ctx: Context, day, month, year=-1):
        """<Day Mont [Year]> Update your birthday."""
        member: discord.Member = ctx.message.author
        database.update_birthday(user_id=member.id, day=day, month=month, year=year)
        await self.bot.say('Birthday updated')

    @commands.command(pass_context=True)
    async def birthday_delete(self, ctx: Context):
        """Delete your birthday."""
        member: discord.Member = ctx.message.author
        birthday = Birthday(user_id=member.id)
        database.delete_birthday(birthday)
        await self.bot.say('Birthday deleted')

    @commands.command(pass_context=True)
    async def birthday(self, ctx: Context, member: discord.Member = None):
        """<[Member]> Show a member's birthday. Displays your birthday by default."""
        if member is None:
            member = ctx.message.author
        birthday: Birthday = database.get_birthday_one(user_id=member.id)
        if birthday is None:
            message = f'\n{member.display_name}: no registered.'
        else:
            message = f'\n{member.display_name}\'s birthday is on {birthday.printable_date()}.'
        await self.bot.say(message)

    @commands.command(pass_context=True)
    async def birthday_all(self, ctx: Context, show=None):
        """[show not registered?] Show everyone's birthday"""
        message = 'Birthdays:'
        for member in ctx.message.server.members:
            if member.bot:
                # Ignore bots
                continue
            birthday = database.get_birthday_one(user_id=member.id)
            if birthday is None:
                if show is not None:
                    message += f'\n{member.display_name}: no registered.'
            else:
                message += f'\n{member.display_name}\'s birthday is on {birthday.printable_date()}.'
        await self.bot.say(message)

    @commands.command(pass_context=True)
    async def birthday_today(self, ctx: Context):
        """Show today's birthday"""
        birthdays = birthdays_today_server(ctx.message.server)
        if len(birthdays) == 0:
            message = "No birthdays today."
        else:
            jump = ''
            message = '@here\n'
            for bd in birthdays:
                member = discord.utils.get(ctx.message.server.members, id=bd.user_id)
                message = f'{jump} It\'s {member.mention}\' birthday!'
                jump = '\n'
        await self.bot.say(message)

    async def birthday_loop(self):
        while not self.bot.is_closed:
            await asyncio.sleep(3600)
            if datetime.today().date() != self.today:
                # When day changes
                self.today = datetime.today().date()
                for server in self.bot.servers:
                    birthdays = birthdays_today_server(server)
                    if len(birthdays) != 0:
                        for channel in server.channels:
                            if channel.permissions_for(server.me).send_messages \
                                    and channel.type is discord.ChannelType.text:
                                jump = ''
                                message = '@everyone\n'
                                for bd in birthdays:
                                    member = discord.utils.get(server.members, id=bd.user_id)
                                    message = f'{jump} It\'s {member.mention}\' birthday!'
                                    jump = '\n'
                                await self.bot.send_message(channel, message)
                                break


def birthdays_today_server(server):
    birthdays = []
    today = datetime.today().date()
    for member in server.members:
        if member.bot:
            # Ignore bots
            continue
        birthday = database.get_birthday_one(user_id=member.id)
        if birthday is not None:
            if today.day == birthday.day and today.month == birthday.month:
                birthdays.append(birthday)
    return birthdays


def setup(bot: commands.Bot):
    bot.add_cog(BirthdayCommands(bot))
