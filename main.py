import os
import re
import json
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import server_info

#for client decorator
client = commands.Bot(command_prefix='?')


def get_auth():
    #get tokens and auth for the bot
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    guild = os.getenv('DISCORD_GUILD')
    return token, guild


def get_len_file(file_name):
    return os.path.getsize(f'data\\{file_name}')


@client.event
async def on_guild_join(guild):
    guild_path = f'data\\{guild.name}-{guild.id}.json'
    print(guild_path)
    print(os.path.exists(guild_path))
    if not os.path.exists(guild_path):
        with open(guild_path, "w") as f:
            pass
    else:
        json.load(open(guild_path))


@client.event
async def on_guild_remove(guild):
    print("REMOVED")


@client.command(name='delete')
async def admin_delete_trigger(ctx):
    # delete an entry (key) trigger and (value) response from the dictionary
    file_name = f'{ctx.guild.name}-{ctx.guild.id}.json'
    if get_len_file(file_name) > 0:
        trigger_response = load_triggers_file(file_name)
    else:
        trigger_response = {}
    current_user = ctx.author
    await ctx.send(
        f'{current_user}: Enter the trigger\'s name to delete it\'s entry:')
    trigger = await client.wait_for('message',
                                    check=lambda m: m.author == current_user)
    trigger = trigger.content.lower().strip()
    if trigger in trigger_response.keys():
        response = trigger_response[trigger]
        del trigger_response[trigger]
        update_trigger_file(trigger_response, file_name)
        await ctx.send(
            f'{current_user}: "Trigger {trigger}" with response "{response}" was deleted with success'
        )
    else:
        await ctx.send(f'{current_user}: {trigger} does not exist!')


@client.command(name='add')
async def admin_add_trigger(ctx):
    # admin to add a trigger, response to the (key) trigger and (value) response dictionary
    current_user = ctx.author
    file_name = f'{ctx.guild.name}-{ctx.guild.id}.json'
    if get_len_file(file_name) > 0:
        trigger_response = load_triggers_file(file_name)
    else:
        trigger_response = {}
    await ctx.send(f'{current_user}: Please add a new trigger:')

    trigger = await client.wait_for('message',
                                    check=lambda m: m.author == current_user)
    trigger = trigger.content.lower().strip()

    if trigger in trigger_response.keys():
        await ctx.send(
            f'{current_user}: The trigger: "{trigger}" already exists!')
        return
    else:
        await ctx.send(f'{current_user}: Now add a response to the trigger:')
        response = await client.wait_for(
            'message', check=lambda m: m.author == current_user)
        response = response.content.lower().strip()
        await ctx.send(
            f'{current_user} Trigger: "{trigger}" with response: "{response}" added with success!!'
        )
        trigger_response[trigger] = response
        update_trigger_file(trigger_response, file_name)


@client.event
async def on_message(message):
    # get user message and send him a response based on the dict: trigger_key - response_value
    file_name = f'{message.guild.name}-{message.guild.id}.json'

    if get_len_file(file_name) > 0:
        trigger_response = load_triggers_file(file_name)
    else:
        trigger_response = {}
    current_user = message.author
    msg = message.content.lower().strip()
    trigger = get_clean_trigger_from(msg, trigger_response)

    if message.author == client.user:
        return

    if is_user_trigger_valid(
            msg, trigger_response) or msg in trigger_response.keys():
        await message.channel.send(trigger_response[trigger])

    elif message.content == 'raise-exception':
        raise discord.DiscordException
    await client.process_commands(message)


@client.event
async def on_member_join(member):
    # greet people when they join the server
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!')


@client.event
async def on_ready():
    print("READY")


# check guild members and server name
# guild = discord.utils.get(client.guilds, name=GUILD)
# print(f'{client.user} is connected to the following guild:\n'
#       f'{guild.name}(id: {guild.id})')

# members = '\n - '.join([member.name for member in guild.members])
# print(f'Guild Members:\n - {members}')


def load_triggers_file(trigger_file):
    #load the trigger.txt file in json format and return as a
    #dictionary that stores the key: trigger with value: response
    trigger_path = f"data\\{trigger_file}"
    return json.load(open(trigger_path))


def is_user_trigger_valid(user_msg, dic):
    # check if the trigger is valid
    trigger = get_clean_trigger_from(user_msg, dic)
    return trigger in dic


def get_clean_trigger_from(user_msg, dic):
    # get regex pattern to match everything before and after the trigger
    # and return the clean trigger
    lst = re.findall(r"(?=(" + '|'.join(dic) + r"))", user_msg)
    result = ''.join(lst)
    return result


def update_trigger_file(dic, trigger_file):
    # rewrite the file when deleting
    trigger_path = f"data\\{trigger_file}"
    json.dump(dic,
              open(trigger_path, 'w'),
              sort_keys=True,
              indent=4,
              separators=(',', ': '))


@client.command(name="server")
async def get_server_info(ctx):
    # display server info
    await server_info.server_info(ctx)


if __name__ == "__main__":

    TOKEN, GUILD = get_auth()

    client.run(TOKEN)
