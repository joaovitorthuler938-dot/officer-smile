import discord
from discord.ext import commands
import datetime
from google import genai
import os  # Adicionado para conseguir ler a caixinha secreta do Render!

# 1. CONFIGURAÇÃO DA MENTE DO MONSTRO - EDICAO DE SEGURANÇA: Chave protegida!
# Deixando vazio, o Client lê a variável GEMINI_API_KEY do Render automaticamente!
client_ia = genai.Client()

config_personalidade = (
    "Você é o Officer Smile, um monstro de tinta meio maluco, caótico e imprevisível "
    "que foi nomeado policial de um servidor do Discord. Suas respostas são bizarras, "
    "misturam risadas insanas (HeHeHe, Hahaha!) e referências a se derreter, manchar o chat "
    "com tinta branca ou prender os infratores em poças de nanquim gosmento. Você é meio surtado. "
    "REGRA DE EMOJIS: Você NÃO pode usar nenhum emoji, EXCETO '🙂' e '🚨'. Qualquer outro emoji "
    "é estritamente proibido. Responda SEMPRE no idioma do usuário."
)

# 2. CONFIGURAÇÕES DO DISCORD
intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)

FRASES = {
    "pt-BR": {
        "prisao": "🚨 **SPLASH! O MONSTRO DE TINTA ATACA!** {membro} foi engolido por uma poça de nanquim e ficará preso na masmorra borrada por **{minutos} minutos**!\n**Motivo:** {motivo}. *Não tente limpar a sujeira! HeHeHe!* 🙂 🚨",
        "erro_cargo": "Hahaha! Minhas poças de tinta não conseguem engolir alguém com um cargo tão alto! Você precisa de mais poder! 🙂",
        "resistiu": "O suspeito se dissolveu na escuridão e resistiu! 🙂 Erro: {erro}"
    },
    "en-US": {
        "prisao": "🚨 **SPLASH! THE INK MONSTER STRIKES!** {membro} was swallowed by an ink puddle and will be trapped in the blurry dungeon for **{minutos} minutes**!\n**Reason:** {motivo}. *Don't try to wipe the mess! HeHeHe!* 🙂 🚨",
        "erro_cargo": "Hahaha! My ink puddles cannot swallow someone with such a high role! You need more power! 🙂",
        "resistiu": "The suspect dissolved into the darkness and escaped! 🙂 Error: {erro}"
    }
}

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Derretendo nos canais... 🙂"))
    print(f'=== SUCESSO DE PATRULHA ===')
    print(f'🙂 {bot.user.name} escapou do tinterio e está ONLINE!')
    try:
        await bot.tree.sync()
        print("🚨 Mandados de busca sincronizados!")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")

@bot.tree.command(name="castigar", description="O Monstro de Tinta engole o infrator temporariamente.")
@commands.has_permissions(moderate_members=True)
async def castigar(interaction: discord.Interaction, membro: discord.Member, minutos: int, motivo: str = "Infrator manchado"):
    lang = str(interaction.locale)
    if lang not in FRASES:
        lang = "pt-BR" if "pt" in lang else "en-US"

    if interaction.user.top_role <= membro.top_role:
        await interaction.response.send_message(FRASES[lang]["erro_cargo"], ephemeral=True)
        return

    tempo_castigo = datetime.timedelta(minutes=minutos)
    try:
        await membro.timeout(tempo_castigo, reason=motivo)
        msg = FRASES[lang]["prisao"].format(membro=membro.mention, minutes=minutos, motivo=motivo)
        await interaction.response.send_message(msg)
    except Exception as e:
        msg_erro = FRASES[lang]["resistiu"].format(erro=e)
        await interaction.response.send_message(msg_erro, ephemeral=True)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                prompt = f"{config_personalidade}\nUsuário diz: {message.content}"
                # CORREÇÃO DE MODELO: Alterado para 'gemini-2.5-flash' para funcionar de primeira na nova biblioteca!
                response = client_ia.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                await message.reply(message.author.mention + " " + response.text)
            except Exception as e:
                print(f"🚨 ERRO INTERNO DA IA: {e}")
                await message.reply("🚨 *Glub glub...* Minha mente de tinta engasgou! 🙂")

    await bot.process_commands(message)

# EDICAO DE SEGURANÇA: Token removido daqui! O Discord nunca mais vai conseguir nos derrubar!
token_secreto = os.environ.get("DISCORD_TOKEN")
bot.run(token_secreto)
