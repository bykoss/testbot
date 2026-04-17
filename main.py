import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
intents = discord.Intents.default()
intents.message_content = True   # Necesario para leer comandos con prefijo
intents.members = True
intents.moderation = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ==================== CATEGORÍAS DE COMANDOS ====================
CATEGORIES = {
    "antinuke": [
        {"name": "!antinuke enable", "desc": "Activa la protección anti-nuke", "usage": "!antinuke enable"},
        {"name": "!antinuke disable", "desc": "Desactiva la protección anti-nuke", "usage": "!antinuke disable"},
    ],
    "moderacion": [
        {"name": "!ban", "desc": "Banea a un usuario", "usage": "!ban @usuario razón"},
        {"name": "!kick", "desc": "Expulsa a un usuario", "usage": "!kick @usuario"},
        {"name": "!clear", "desc": "Borra mensajes", "usage": "!clear 50"},
    ],
    "roleplay": [
        {"name": "!rp hug", "desc": "Abraza a alguien", "usage": "!rp hug @usuario"},
        {"name": "!rp kiss", "desc": "Besa a alguien", "usage": "!rp kiss @usuario"},
        {"name": "!rp pat", "desc": "Acaricia la cabeza", "usage": "!rp pat @usuario"},
    ],
    "generales": [
        {"name": "!ping", "desc": "Muestra latencia del bot", "usage": "!ping"},
        {"name": "!serverinfo", "desc": "Información del servidor", "usage": "!serverinfo"},
    ],
    "anime": [
        {"name": "!waifu", "desc": "Waifu aleatoria", "usage": "!waifu"},
    ],
    "sorteos": [
        {"name": "!giveaway", "desc": "Inicia un sorteo", "usage": "!giveaway premio: Premio"},
    ],
    "encuestas": [
        {"name": "!poll", "desc": "Crea una encuesta", "usage": "!poll pregunta: ¿Qué prefieres?"},
    ]
}

# ==================== VISTAS CON BOTONES Y PAGINACIÓN ====================
class CommandPageView(View):
    def __init__(self, cmd_list, category):
        super().__init__(timeout=600)
        self.cmd_list = cmd_list
        self.category = category
        self.page = 0
        self.per_page = 8

    def get_embed(self):
        embed = discord.Embed(title=f"📋 {self.category.upper()} - Comandos", color=0x00ff88)
        start = self.page * self.per_page
        end = start + self.per_page
        for cmd in self.cmd_list[start:end]:
            embed.add_field(name=cmd["name"], value=f"{cmd['desc']}\n**Uso:** `{cmd['usage']}`", inline=False)
        total = (len(self.cmd_list) + self.per_page - 1) // self.per_page
        embed.set_footer(text=f"Página {self.page + 1}/{total} • Usa !help para volver")
        return embed

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="➡️ Siguiente", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: Button):
        total = (len(self.cmd_list) + self.per_page - 1) // self.per_page
        if self.page < total - 1:
            self.page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="❌ Cerrar", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()

class CategoryView(View):
    def __init__(self):
        super().__init__(timeout=600)
        for cat in CATEGORIES:
            btn = Button(label=cat.capitalize(), style=discord.ButtonStyle.blurple)
            btn.callback = self.make_callback(cat)
            self.add_item(btn)

    def make_callback(self, category):
        async def callback(interaction: discord.Interaction):
            cmds = CATEGORIES[category]
            view = CommandPageView(cmds, category)
            await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)
        return callback

# ==================== COMANDO !HELP ====================
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🤖 Menú de Ayuda del Bot",
        description="Selecciona una categoría con los botones de abajo.\nTodo con paginación y uso completo.",
        color=0x00ff88
    )
    embed.set_footer(text="¡Haz clic en los botones! • Desarrollado para ti")
    
    view = CategoryView()
    await ctx.send(embed=embed, view=view)

# ==================== COMANDO !PING ====================
@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! `{latency} ms`")

# ==================== EVENTO ON_READY ====================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print(f"   Servidores: {len(bot.guilds)}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="!help • +400 comandos")
    )

# ==================== INICIO DEL BOT (Railway) ====================
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ ERROR: No se encontró la variable DISCORD_TOKEN en Railway.")
        exit(1)
    
    print("🚀 Iniciando el bot con prefijo ! ...")
    bot.run(token)
