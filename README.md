# X5Bot
Olá! Eu sou o bot X5, eu fui criado para ajudar vocês a jogarem partidas personalizadas online de maneira justa e organizada. Comigo, vocês podem iniciar partidas, ver as estatísticas dos jogadores que estão na mesma sala e até mesmo ver a tabela de classificação do server.
![X5Bot](https://github.com/caiovitfernandes/X5Bot/blob/main/perf.png?raw=true)
## Como instalar e utilizar o X5Bot
### Pré-requisitos:
Antes de começarmos, você precisará ter os seguintes itens instalados em sua máquina:

* [Python](https://www.python.org/downloads/)
* Git (opcional, mas recomendado para clonar o repositório)
* Conta no Discord

### Passo 1: Clonar o repositório ou baixar o arquivo .zip
Se você instalou o Git em sua máquina, abra o terminal e navegue até o diretório onde deseja clonar o repositório. Digite o seguinte comando:
```$ git clone https://github.com/seu-username/seu-repositorio.git```
Caso contrário, você pode baixar o código como um arquivo zip no botão "Download ZIP" no GitHub.

### Passo 2: Instalar as bibliotecas necessárias do Python 
Abra o terminal do seu computador e, com o Python já instalado, digite os comandos:
```pip install discord```
```pip install json```
```pip install random```
```pip install asyncio```

### Passo 3: Criar o bot do Discord
Vá até a [página de desenvolvedores do Discord](https://discord.com/developers/) e faça login com sua conta do Discord. Clique no botão "Criar aplicativo" e dê um nome para o seu aplicativo.

Em seguida, vá para a aba "Bot" e clique no botão "Adicionar Bot". Seu bot será criado e você poderá obter o seu token clicando no botão "Clique aqui para revelar" ou "Reset Tokem". Abra a pasta do repositório clonado e cole o código no arquivo token.txt

### Passo 4: Convidar o bot para o servidor
Na página de desenvolvedores do Discord, vá para a aba "OAuth2", em "URL GeneratoR", e selecione a opção "bot" em "Scopes". Em seguida, nas permissões, marque a permissão de "Administrador" para o seu bot e copie o link gerado. Cole o link em seu navegador, selecione o servidor e autorize o bot a entrar.

### Passo 5: Rodando e testando o bot
Na pasta do repositório clonado, execute o arquivo "bot.bat". O bot deve carregar e em seguida exibir a mensagem "Conectado a: ID_DO_BOT".
Em seguida, verifique se no seu servidor do discord foi criado um agrupamento de canais chamado "X5Bot". Se sim, é possível que o bot já esteja funcionando.

## Comandos do Bot:
* !x5 : Inicia as partidas. Ao utilizar este comando, o bot verifica as estatísticas dos jogadores presentes na 🔀 Sala e balanceia os memos em dois times baseando-se no rank dos mesmos. Se gostarem do balanceamento, basta clicar em ✅ e os jogadores serão dividos em duas salas para realizarem a partida. Caso não gostem do balanceamento, é possível gerar dois times de maneira aleatória utilizando o botão 🔁. O botão ❌ cancela a execução da partida
* !gg : Encerra as partidas e move os jogadores para o Lobby. Ao encerrar a partida, o bot pergunta qual dos dois times saiu vitorioso. É importante marcar o time correto para que as estatísticas sejam atualizadas da maneira correta. É possível setar as estatísticas manualmente no arquivo ID_DO_SERVER.json (para quem clonou o repositório e está hosteando o bot)
* !rank : Exibe uma tabela de classificação que mostra apenas as estatísticas dos jogadores presentes na sala
* !top : Exibe a tabela de classificação com os 20 primeiros classificados do server (exibe apenas jogadores que já participaram de pelo menos uma partida)
* !eu : Exibe as estatísticas do jogador que enviou o comando
* !bo : Menciona todos os membros do servidor em uma mensagem chamando para jogar