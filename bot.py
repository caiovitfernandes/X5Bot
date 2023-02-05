import discord
import random
import json

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

def create_user_file():
    users = {}
    with open('users.json', 'w') as f:
        json.dump(users, f)

def calculate_winrate(usuarios):
    for user in usuarios:
        vitorias = usuarios[user]["vitorias"]
        derrotas = usuarios[user]["derrotas"]
        total = vitorias + derrotas
        if total == 0:
            winrate = 0
        else:
            winrate = (vitorias / (vitorias + derrotas)) * 100
        usuarios[user]["winrate"] = winrate

    with open("users.json", "w") as file:
        json.dump(usuarios, file, indent=4)
        file.close()

def add_user(user_id, username):
    with open('users.json', 'r') as f:
        users = json.load(f)
    if user_id not in users:
        users[username] = {"vitorias": 0, "derrotas": 0, "winrate": 0}
        with open('users.json', 'w') as f:
            json.dump(users, f)


def classificar():
    with open("users.json", "r") as file:
        users = json.load(file)

    # Ordena os usuários pelo winrate (com vitórias como critério de desempate)
    sorted_users = sorted(users.items(), key=lambda x: (-x[1]["vitorias"], x[1]["winrate"]))

    with open("users.json", "w") as file:
        json.dump(dict(sorted_users), file, indent=4)

@client.event
async def on_ready():
    print(f'Conectado a: {client.user}')
    try:
        with open('users.json', 'r') as f:
            json.load(f)
    except FileNotFoundError:
        create_user_file()
        for member in client.get_all_members():
            add_user(str(member.id), member.name)
    

@client.event
async def on_member_join(member):
    add_user(str(member.id), member.name)

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

            with open("users.json", "r") as file:
                usuarios = json.load(file)

            for member in members_team_1:
                if member.name in usuarios:
                    usuarios[member.name]["vitorias"] += 1
                else:
                    usuarios[member.name] = {"vitorias": 1, "derrotas": 0}

            for member in members_team_2:
                if member.name in usuarios:
                    usuarios[member.name]["derrotas"] += 1
                else:
                    usuarios[member.name] = {"vitorias": 0, "derrotas": 1}

            with open("users.json", "w") as file:
                json.dump(usuarios, file)
            
            calculate_winrate(usuarios)

        elif str(reaction.emoji) == "🔴":
            for member in members_team_2:
                await member.move_to(voice_channel_out)
            for member in members_team_1:
                await member.move_to(voice_channel_out)
            await message.channel.send("Equipe 2 venceu o jogo.")

            with open("users.json", "r") as file:
                usuarios = json.load(file)

            for member in members_team_2:
                if member.name in usuarios:
                    usuarios[member.name]["vitorias"] += 1
                else:
                    usuarios[member.name] = {"vitorias": 1, "derrotas": 0}

            for member in members_team_1:
                if member.name in usuarios:
                    usuarios[member.name]["derrotas"] += 1
                else:
                    usuarios[member.name] = {"vitorias": 0, "derrotas": 1}

            with open("users.json", "w") as file:
                json.dump(usuarios, file)
                file.close()
    
            calculate_winrate(usuarios)
        classificar()

        
        

client.run('MTA3MTU0MzYxNjk2MDQ4MzM2OQ.G2CJTn.LMNPIgmvlcpNvFyYZfnX3xbI3H1Q7kPA-leIIs')
