import discord
from discord.ext import commands

from tinydb import TinyDB, Query

from nibbles.config import todo_json

class Box(discord.ui.Select):
    def __init__(self, task_list):
        super().__init__(placeholder="What to check off?", max_values=10, min_values=0, custom_id="todo_check")
        self.response = None
        for task in task_list:
            self.add_option(label=task, description="hi", default=False)

    async def next(self, interaction: discord.Interaction, menu: discord.ui.Select):
        print(menu)
        print(menu.values)
        menu.options = []
        embed, task_list = todo_embed(interaction.user.id, interaction.user.name)
        for task in task_list:
            menu.add_option(label=task, default=False)
        if embed is None:
            await interaction.response.defer()
            return
        await interaction.response.edit_message(embed=embed, view=self)

def todo_embed(uid, author_name):
    with TinyDB(todo_json) as db:
        todo = db.search(Query().user == uid)
        if len(todo) == 0:
            return None
        todo = todo[0].get('todo')
        desc = '\n'
        for index, task in enumerate(todo):
            desc += f'{index + 1}. {task}\n\n'
        title = f"{len(todo)} Tasks" if len(todo) > 0 else 'Congratulations, you finished your tasks!'
        embed = discord.Embed(title=title, colour=discord.Colour(0x24bdff), description=desc)

        embed.set_author(name=author_name)
        print(todo)
        return embed, Box(todo)


class Todo(commands.Cog):

    def __init__(self, client):
        self.client = client

    # @commands.hybrid_command(
    #     name="add",
    #     description='add an item to your to-do list!'
    # )
    # async def todo_add(self, ctx: commands.Context, *, item: str):
    #     with TinyDB(todo_json) as db:
    #         todo = db.search(Query().user == ctx.author.id)
    #         if len(todo) != 0:
    #             new_list = todo[0].get('todo')
    #             new_list.append(item)
    #             db.update({'user': ctx.author.id, 'todo': new_list}, Query().user == ctx.author.id)
    #         else:
    #             db.insert({'user': ctx.author.id, 'todo': [item]})
    #     name = ctx.author.display_name
    #
    #     await ctx.send(content='Added to your to-do list!', embed=todo_embed(ctx.author.id, name))

    @discord.app_commands.command(description='interact with your to-do list!')
    async def todo(self, interaction: discord.Interaction):
        user = interaction.user
        name = user.display_name
        embed, box = todo_embed(user.id, name)
        print(box.options)
        # if embed is not None:
        #     await interaction.response.send_message(content=f"{name}'s to-do list", embed=embed, view=box)
        # else:
        # await interaction.response.send_message(content=f"{name} does not have a to-do list yet!", view=box)
        await interaction.response.send_message(content=f"test", view=box)

    # @commands.command(description='check off a task from your to-do list\n.todo_check 3;.check 1',
    #                   aliases=['check', 'remove'])
    # async def todo_check(self, ctx, value: int):
    #     with TinyDB('./data/todo.json') as db:
    #         todo = db.search(Query().user == ctx.author.id)
    #         if len(todo) != 0:
    #             todo = todo[0].get('todo')
    #         else:
    #             await ctx.send('this user has not made a todo list yet')
    #             return
    #         new_list = todo
    #         if len(todo) >= value:
    #             removed = new_list.pop(value - 1)
    #         else:
    #             await ctx.send('such task does not exist :(')
    #             return
    #         db.update({'user': ctx.author.id, 'todo': new_list}, Query().user == ctx.author.id)
    #         name = ctx.author.display_name if not hasattr(ctx.author,
    #                                                       'nick') or ctx.author.nick is None else ctx.author.nick
    #         async for message in ctx.channel.history(limit=10):
    #             if message.author.bot and 'to-do' in message.content:
    #                 if len(message.embeds) > 0 and message.embeds[0].author.name == name:
    #                     await message.delete()
    #         await ctx.send(content=f'"{removed}" has been checked off!',
    #                        embed=todo_embed(ctx.author.id, name))


async def setup(client):
    await client.add_cog(Todo(client))
