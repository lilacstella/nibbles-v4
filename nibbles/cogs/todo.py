import discord
from discord.ext import commands
from tinydb import TinyDB, Query

from nibbles.config import todo_json


class Menu(discord.ui.Select):
    def __init__(self, task_list):
        super().__init__(placeholder="What to check off?", custom_id="todo_check")
        self.response = None
        if len(task_list) == 0:
            self.add_option(label="You have finished everything!", default=True)
            self.disabled = True
        for task in task_list:
            self.add_option(label=task, default=False)

    async def callback(self, interaction: discord.Interaction):
        with TinyDB(todo_json) as db:
            todo_list = db.search(Query().user == interaction.user.id)
            if len(todo_list) != 0:
                todo_list = todo_list[0].get('todo')
            new_list = todo_list
            new_list.remove(self.values[0])

            db.update({'user': interaction.user.id, 'todo': new_list}, Query().user == interaction.user.id)

        embed, task_list = todo_embed(interaction.user.id, interaction.user.name)
        await interaction.response.edit_message(
            content=f"{self.values[0]} has been checked off!",
            embed=embed,
            view=MenuView(task_list)
        )


class MenuView(discord.ui.View):
    def __init__(self, task_list, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(Menu(task_list))


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

        return embed, todo


class Todo(commands.GroupCog, group_name="todo"):

    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name='ls', description='interact with your to-do list!')
    async def todo(self, interaction: discord.Interaction):
        embed, task_list = todo_embed(interaction.user.id, interaction.user.display_name)

        if embed is not None:
            await interaction.response.send_message(embed=embed, view=MenuView(task_list))
        else:
            await interaction.response.send_message(
                content=f"{interaction.user.display_name} does not have a to-do list yet!"
            )

    @discord.app_commands.command(
        name="add",
        description='add an item to your to-do list!'
    )
    @discord.app_commands.describe(
        item="what would you like to add to your todo list"
    )
    async def todo_add(self, interaction: discord.Interaction, item: str):
        with TinyDB(todo_json) as db:
            todo = db.search(Query().user == interaction.user.id)
            if len(todo) != 0:
                new_list = todo[0].get('todo')
                if item in new_list:
                    await interaction.response.send_message("You already have this task in your list!")
                    return
                new_list.append(item)
                db.update({'user': interaction.user.id, 'todo': new_list}, Query().user == interaction.user.id)
            else:
                db.insert({'user': interaction.user.id, 'todo': [item]})
        name = interaction.user.display_name
        embed, task_list = todo_embed(interaction.user.id, name)

        await interaction.response.send_message(
            content='Added to your to-do list!',
            embed=embed,
            view=MenuView(task_list)
        )


async def setup(client):
    await client.add_cog(Todo(client))
