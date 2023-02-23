import discord
import json
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

def get_server_id(ctx):
    return ctx.guild.id

def create_user_file(id):
    users = {}
    with open(f'{id}.json', 'w') as f:
        json.dump(users, f)

def calculate_winrate(usuarios, id):
    for user in usuarios:
        vitorias = usuarios[user]["vitorias"]
        derrotas = usuarios[user]["derrotas"]
        total = vitorias + derrotas
        if total == 0:
            winrate = 0
        else:
            winrate = (vitorias / (vitorias + derrotas)) * 100
        usuarios[user]["winrate"] = round(winrate, 1)

    with open(f"{id}.json", "w") as file:
        json.dump(usuarios, file, indent=4)
        

def add_user(user_id, username, id):
    with open(f'{id}.json', 'r') as f:
        users = json.load(f)
    if username not in users:
        users[username] = {"pontos": 0,"vitorias": 0, "derrotas": 0, "winrate": 0}
        with open(f'{id}.json', 'w') as f:
            json.dump(users, f)

def classificar(id):
    with open(f"{id}.json", "r") as file:
        users = json.load(file)

    # Ordena os usuários pelos pontos (com winrate como critério de desempate)
    sorted_users = sorted(users.items(), key=lambda x: (-x[1]["winrate"], -x[1]["pontos"]))

    with open(f"{id}", "w") as file:
        json.dump(dict(sorted_users), file, indent=4)

def tabela20(id):
    with open(f'{id}.json', 'r') as file:
        data = json.load(file)
    played = [(name, player) for name, player in data.items() if player["vitorias"] + player["derrotas"] > 0]
    sorted_users = sorted(played, key=lambda x: (-x[1]["pontos"], -x[1]["winrate"], -x[1]["vitorias"], x[1]["derrotas"]))
    return sorted_users[:20]

def balancear(members, id):
    with open(f"{id}.json", "r") as file:
        users = json.load(file)
    members = [member for member in members if str(member.name) in users]
    members = sorted(members, key=lambda x: (users[str(x.name)]["pontos"], users[str(x.name)]["winrate"], users[str(x.name)]["vitorias"], users[str(x.name)]["derrotas"]), reverse=True)
    half = len(members)//2
    team_1 = []
    team_2 = []
    geral = []
    pontos1 = 0
    pontos2 = 0
    for i in range(len(members)):
        if users[str(members[i].name)]["pontos"] > 0:
            if pontos1 != pontos2:
                if pontos1 > pontos2:
                    team_1.append(members[i])
                else:
                    team_2.append(members[i])
            else:
                if len(team_1) > len(team_2):
                    team_2.append(members[i])
                elif len(team_2) > len(team_1):
                    team_1.append(members[i]) 
                else:
                    team_1.append(members[i])
        else:
            if len(team_1) > len(team_2):
                team_2.append(members[i])
            elif len(team_2) > len(team_1):
                team_1.append(members[i]) 
            else:
                team_1.append(members[i])
    for i in range(len(members)):
        if i < len(team_1):
            geral.append(team_1[i])
        else:
            geral.append(team_2[i - len(team_1)])
    return geral

def get_server_id(ctx):
    return ctx.id

async def x5(members, message, team_1_channel, team_2_channel):
    team_1 = members[:len(members)//2]
    team_2 = members[len(members)//2:]

    confirm_message = await message.channel.send(f'Separar os jogadores em equipes 1 e 2?\nEquipe 1: {", ".join([member.name for member in team_1])}\nEquipe 2: {", ".join([member.name for member in team_2])}')
    await confirm_message.add_reaction("✅")
    await confirm_message.add_reaction("🔁")
    await confirm_message.add_reaction("❌")

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in ["✅", "❌", "🔁"]

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
    elif str(reaction.emoji) == "🔁":
        random.shuffle(members)
        await x5(members, message, team_1_channel, team_2_channel)
        return
    else:
        await message.channel.send("Separação de jogadores cancelada.")

async def get_member_by_username(guild: discord.Guild, username: str) -> discord.Member:
    # Use a função discord.utils.find() para procurar o membro pelo nome de usuário
    member = discord.utils.find(lambda m: m.name == username, guild.members)
    
    # Se o membro for encontrado, retorne o objeto Member correspondente
    if member is not None:
        return member
    
    # Se o membro não for encontrado, levante uma exceção
    raise ValueError(f"Member '{username}' not found in guild '{guild.name}'")

@client.event
async def on_ready():
    print(f'Conectado a: {client.user}')
    

@client.event
async def on_guild_join(guild):
    global id 
    id = get_server_id(guild)
    print(f"O bot acabou de entrar no servidor com id: {id}")
    try:
        with open(f'{id}.json', 'r') as f:
            json.load(f)
    except FileNotFoundError:
        create_user_file(id)
        for member in client.get_all_members():
            add_user(str(member.id), member.name, id)

    # Criando a categoria e os canais
    canais = ["🏰 Lobby", "🔀 Sala 1", "🔀 Sala 2", "🔀 Sala 3", "🔵 S1 Equipe 1", "🔴 S1 Equipe 2", "🔵 S2 Equipe 1", "🔴 S2 Equipe 2", "🔵 S3 Equipe 1", "🔴 S3 Equipe 2"]
    global catergoria 
    categoria = await guild.create_category(name="🤖 X5Bot")
    await guild.create_text_channel(name="💬 Comandos X5", category=categoria)
    for canal in canais:
        await guild.create_voice_channel(name=canal, category=categoria)
    ola = await discord.utils.get(guild.text_channels, name="💬-comandos-x5").send("Olá! Eu sou o bot X5, eu fui criado para ajudar vocês a jogarem partidas personalizadas online de maneira justa e organizada. Comigo, vocês podem iniciar partidas, ver as estatísticas dos jogadores que estão na mesma sala e até mesmo ver a tabela de classificação do server.\nPara começar a jogar, basta entrar em uma das Salas 🔀 digitar o comando \"!x5\". Eu vou balancear os jogadores da sala e separá-los em equipes 🔵🔴. Quando a partida terminar, vocês podem usar o comando \"!gg\" para que eu salve o resultado e atualize as estatísticas e mova os jogadores para o Lobby 🏰.\nSe quiserem ver as estatísticas de quem está na sala com você, basta usar o comando \"!rank\". E se quiserem ver a tabela de classificação do server, basta digitar \"!top\" que eu mostro pra vocês os 20 primeiros colocados. Para visualizar apenas as suas estatísticas, basta mandar o comando \"!eu\". Para chamar todo mundo para jogar, basta enviar o comando \"!bo\". Lembrem-se: para utilizar os comando !x5, !gg e !rank é necessário estar nas salas de voz.\nEu espero que vocês aproveitem as partidas com o meu auxílio e boa sorte a todos!")
    await ola.pin()


@client.event
async def on_member_join(member):
    print(f"O usuário {member.name} entrou no servidor")
    add_user(str(member.id), member.name, get_server_id(member.guild))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!x5'):
        try:
            voice_channel = message.author.voice.channel
        except:
            await message.channel.send("Você não está em um canal de voz. Entre em uma das 🔀 Salas.")
        members = voice_channel.members
        team_1_channel = ''
        team_2_channel = ''
        if voice_channel.name == "🔀 Sala 1":
            team_1_channel = discord.utils.get(message.guild.voice_channels, name='🔵 S1 Equipe 1')
            team_2_channel = discord.utils.get(message.guild.voice_channels, name='🔴 S1 Equipe 2')
        elif voice_channel.name == "🔀 Sala 2":
            team_1_channel = discord.utils.get(message.guild.voice_channels, name='🔵 S2 Equipe 1')
            team_2_channel = discord.utils.get(message.guild.voice_channels, name='🔴 S2 Equipe 2')
        elif voice_channel.name == "🔀 Sala 3":
            team_1_channel = discord.utils.get(message.guild.voice_channels, name='🔵 S3 Equipe 1')
            team_2_channel = discord.utils.get(message.guild.voice_channels, name='🔴 S3 Equipe 2')
        else:
            await message.channel.send("Você não está em uma das 🔀 Salas.")
            return
        
        members = balancear(members, get_server_id(message.guild))

        await x5(members, message, team_1_channel, team_2_channel)
    elif message.content.startswith("!gg"):
        try:
            voice_channel = message.author.voice.channel
        except:
            await message.channel.send("Você não está em uma sala de voz!")
            return
        members = voice_channel.members

        if voice_channel.name == "🔵 S1 Equipe 1" or voice_channel.name == "🔴 S1 Equipe 2":
            voice_channel_team_1 = discord.utils.get(message.guild.voice_channels, name='🔵 S1 Equipe 1')
            voice_channel_team_2 = discord.utils.get(message.guild.voice_channels, name='🔴 S1 Equipe 2')
        elif voice_channel.name == "🔵 S2 Equipe 1" or voice_channel.name == "🔴 S2 Equipe 2":
            voice_channel_team_1 = discord.utils.get(message.guild.voice_channels, name='🔵 S2 Equipe 1')
            voice_channel_team_2 = discord.utils.get(message.guild.voice_channels, name='🔴 S2 Equipe 2')
        elif voice_channel.name == "🔵 S3 Equipe 1" or voice_channel.name == "🔴 S3 Equipe 2":
            voice_channel_team_1 = discord.utils.get(message.guild.voice_channels, name='🔵 S3 Equipe 1')
            voice_channel_team_2 = discord.utils.get(message.guild.voice_channels, name='🔴 S3 Equipe 2')
        else:
            await message.channel.send("Você não está em uma sala de partida 🔵🔴")
            return
        voice_channel_out = discord.utils.get(message.guild.voice_channels, name='🏰 Lobby')
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

            with open(f"{get_server_id(message.guild)}.json", "r") as file:
                usuarios = json.load(file)

            for member in members_team_1:
                if member.name in usuarios:
                    usuarios[member.name]["vitorias"] += 1
                    usuarios[member.name]["pontos"] += 10
                else:
                    usuarios[member.name] = {"pontos": 10, "vitorias": 1, "derrotas": 0}

            for member in members_team_2:
                if member.name in usuarios:
                    usuarios[member.name]["derrotas"] += 1
                    if usuarios[member.name]["pontos"] > 7:
                        usuarios[member.name]["pontos"] -= 8
                    else:
                        usuarios[member.name]["pontos"] = 0
                else:
                    usuarios[member.name] = {"pontos": 0,"vitorias": 0, "derrotas": 1}

            with open(f"{get_server_id(message.guild)}.json", "w") as file:
                json.dump(usuarios, file)
            
            calculate_winrate(usuarios, get_server_id(message.guild))

        elif str(reaction.emoji) == "🔴":
            for member in members_team_2:
                await member.move_to(voice_channel_out)
            for member in members_team_1:
                await member.move_to(voice_channel_out)
            await message.channel.send("Equipe 2 venceu o jogo.")

            with open(f"{get_server_id(message.guild)}.json", "r") as file:
                usuarios = json.load(file)

            for member in members_team_2:
                if member.name in usuarios:
                    usuarios[member.name]["vitorias"] += 1
                    usuarios[member.name]["pontos"] += 10
                else:
                    usuarios[member.name] = {"pontos": 10, "vitorias": 1, "derrotas": 0}

            for member in members_team_1:
                if member.name in usuarios:
                    usuarios[member.name]["derrotas"] += 1
                    if usuarios[member.name]["pontos"] > 7:
                        usuarios[member.name]["pontos"] -= 8
                    else:
                        usuarios[member.name]["pontos"] = 0
                else:
                    usuarios[member.name] = {"pontos": 0,"vitorias": 0, "derrotas": 1}

            with open(f"{get_server_id(message.guild)}.json", "w") as file:
                json.dump(usuarios, file)
                file.close()
    
            calculate_winrate(usuarios, get_server_id(message.guild))
        classificar(get_server_id(message.guild))

    if message.content.startswith('!rank'):
        voice_channel = message.author.voice.channel
        if not voice_channel:
            await message.channel.send("Você não está em um canal de voz.")
            return

        members = voice_channel.members
        
        # Abrindo o arquivo users.json
        with open(f"{get_server_id(message.guild)}.json", "r") as f:
            users = json.load(f)

        # Encontrando todos os membros no canal de voz
        voice_channel = message.author.voice.channel
        voice_channel_members = voice_channel.members

        # Armazenando apenas os usuários com informações no arquivo
        relevant_users = {username: users[username] for username in users if username in [member.name for member in voice_channel_members]}

        # Ordenando os usuários pelo winrate, com vitórias como critério de desempate
        sorted_users = sorted(relevant_users.items(), key=lambda x: (-x[1]["pontos"], -x[1]["winrate"]))

        # Enviando a classificação no canal
        leaderboard = "Tabela de classificação da sala:\n"
        for i, (username, user_info) in enumerate(sorted_users):
            membro = await get_member_by_username(message.guild, username)
            leaderboard += f"{i + 1}.\t {membro.mention}:\t\t Pontos: \t{user_info['pontos']}\t\t Vitórias: \t{user_info['vitorias']}\t\t Derrotas: \t{user_info['derrotas']}\t\t Winrate: \t{user_info['winrate']}%\n"

        await message.channel.send(leaderboard)
    
    if message.content.startswith('!eu'):
        with open(f"{get_server_id(message.guild)}.json", "r") as f:
            users = json.load(f)

        # Obtendo o username do autor da mensagem
        username = str(message.author.name)

        # Verificando se o autor da mensagem tem informações no arquivo
        if username not in users:
            await message.channel.send(f"{username} não tem informações registradas.")
            return

        # Obtendo as informações do autor da mensagem
        user_info = users[username]

        # Montando a mensagem com as estatísticas do autor da mensagem
        leaderboard = f"Estatísticas de {message.author.mention}:\n"
        leaderboard += f"Pontos: \t{user_info['pontos']}\n"
        leaderboard += f"Vitórias: \t{user_info['vitorias']}\n"
        leaderboard += f"Derrotas: \t{user_info['derrotas']}\n"
        leaderboard += f"Winrate: \t{user_info['winrate']}%\n"

        # Enviando a mensagem com as estatísticas
        await message.channel.send(leaderboard)

    if message.content.startswith('!bo'):
        mensagem = f"{message.author.mention} Está te convidando: BORA X5? Conecte-se em uma das 🔀 Salas para jogar.\n\n\t\t@everyone"
        confirm_message = await message.channel.send(mensagem)
        await confirm_message.add_reaction("✅")
        await confirm_message.add_reaction("❌")

    if message.content.startswith('!top'):
        top = tabela20(get_server_id(message.guild))
        # Construir a tabela de classificação com os 20 primeiros colocados
        leaderboard = "Tabela do server:\n"
        for i, (username, user_data) in enumerate(top):
            membro = await get_member_by_username(message.guild, username)
            leaderboard += f"{i + 1}. {membro.mention}:\t\t Pontos: \t{user_data['pontos']}\t\t Vitórias: \t{user_data['vitorias']}\t\t Derrotas: \t{user_data['derrotas']}\t\t Winrate: \t{user_data['winrate']}%\n"

        # Enviar a tabela de classificação para o canal de chat
        await message.channel.send(leaderboard)
with open("token.txt", "r") as arquivo:
    token = arquivo.readline()
client.run(token)