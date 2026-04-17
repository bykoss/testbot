import discord
from discord.ext import commands
from discord.ui import View, Button
import os

# ==================== CONFIGURACIÓN ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ==================== CATEGORÍAS ====================
CATEGORIES = {
    "antinuke": [
        {"name": "!antinuke enable", "desc": "Activa protección anti-nuke", "usage": "!antinuke enable"},
        {"name": "!antinuke disable", "desc": "Desactiva anti-nuke", "usage": "!antinuke disable"},
    ],
    "moderacion": [
        {"name": "!ban", "desc": "Banea usuario", "usage": "!ban @usuario"},
        {"name": "!kick", "desc": "Expulsa usuario", "usage": "!kick @usuario"},
        {"name": "!clear", "desc": "Borra mensajes", "usage": "!clear 50"},
    ],
    "roleplay": [
        {"name": "!rp hug", "desc": "Abraza a alguien", "usage": "!rp hug @usuario"},
        {"name": "!rp kiss", "desc": "Besa a alguien", "usage": "!rp kiss @usuario"},
    ],
    "generales": [
        {"name": "!ping", "desc": "Latencia del bot", "usage": "!ping"},
        {"name": "!serverinfo", "desc": "Info del servidor", "usage": "!serverinfo"},
    ],
    "anime": [
        {"name": "!waifu", "desc": "Waifu random", "usage": "!waifu"},
    ],
    "sorteos": [
        {"name": "!giveaway", "desc": "Inicia sorteo", "usage": "!giveaway premio: Premio"},
    ],
    "encuestas": [
        {"name": "!poll", "desc": "Crea encuesta", "usage": "!poll pregunta: Pregunta"},
    ]
}

# ==================== VISTAS ====================
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
        embed.set_footer(text=f"Página {self.page + 1}/{total}")
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
            view = CommandPageView(CATEGORIES[category], category)
            await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)
        return callback

# ==================== COMANDOS ====================
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🤖 Menú de Ayuda",
        description="Selecciona una categoría con los botones:",
        color=0x00ff88
    )
    view = CategoryView()
    await ctx.send(embed=embed, view=view)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)} ms`")

# ==================== ON_READY ====================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado correctamente como {bot.user}")
    print(f"   Servidores: {len(bot.guilds)}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="!help")
    )

# ==================== INICIO ====================
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ No se encontró DISCORD_TOKEN en Railway")
        exit(1)
    print("🚀 Iniciando bot...")
    bot.run(token)
