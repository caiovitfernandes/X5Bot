import discord
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Conectado a: {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!start'):
        voice_channel = message.author.voice.channel
        if not voice_channel:
            await message.channel.send("Você não está em um canal de voz.")
            return

        members = voice_channel.members
        if not members:
            await message.channel.send("Não há nenhum jogador na sala de voz.")
            return

        team_1_channel = discord.utils.get(message.guild.voice_channels, name='Equipe 1')
        team_2_channel = discord.utils.get(message.guild.voice_channels, name='Equipe 2')

        random.shuffle(members)
        team_1 = members[:len(members)//2]
        team_2 = members[len(members)//2:]

        confirm_message = await message.channel.send(f'Separar os jogadores em equipes 1 e 2?\nEquipe 1: {", ".join([member.name for member in team_1])}\nEquipe 2: {", ".join([member.name for member in team_2])}')
        await confirm_message.add_reaction("✅")
        await confirm_message.add_reaction("❌")

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await confirm_message.delete()
            await message.channel.send("Tempo esgotado para confirmação.")
            return

        if str(reaction.emoji) == "✅":
            for team_1_member in team_1:
                await team_1_member.move_to(team_1_channel)
            for team_2_member in team_2:
                await team_2_member.move_to(team_2_channel)
            await message.channel.send("Jogadores separados em equipes.")
        else:
            await message.channel.send("Separação de jogadores cancelada.")

    elif message.content.startswith("!end"):
        voice_channel_team_1 = discord.utils.get(message.guild.voice_channels, name='Equipe 1')
        voice_channel_team_2 = discord.utils.get(message.guild.voice_channels, name='Equipe 2')
        voice_channel_out = discord.utils.get(message.guild.voice_channels, name='-De fora- Inhouse')

        members_team_1 = voice_channel_team_1.members
        members_team_2 = voice_channel_team_2.members

        confirm_message = await message.channel.send(f'Qual equipe venceu o jogo?\nEquipe 1: 🔵\nEquipe 2: 🔴')
        await confirm_message.add_reaction("🔵")
        await confirm_message.add_reaction("🔴")

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) in ["🔵", "🔴"]

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await confirm_message.delete()
            await message.channel.send("Tempo esgotado para confirmação.")
            return

        if str(reaction.emoji) == "🔵":
            for member in members_team_1:
                await member.move_to(voice_channel_out)
            for member in members_team_2:
                await member.move_to(voice_channel_out)
            await message.channel.send("Equipe 1 venceu o jogo.")
        elif str(reaction.emoji) == "🔴":
            for member in members_team_2:
                await member.move_to(voice_channel_out)
            for member in members_team_1:
                await member.move_to(voice_channel_out)
            await message.channel.send("Equipe 2 venceu o jogo.")

client.run('MTA3MTU0MzYxNjk2MDQ4MzM2OQ.G2CJTn.LMNPIgmvlcpNvFyYZfnX3xbI3H1Q7kPA-leIIs')
