import discord
from discord import app_commands
from discord.ui import View, Button
from discord.ext import commands
import asyncio
import random
import os
from datetime import datetime

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True
intents.guilds = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        try:
            await self.tree.sync()
            print("✅ Comandos slash sincronizados.")
        except Exception as e:
            print(f"⚠️ Error al sincronizar: {e}")

bot = MyBot()

# Categorías de comandos (puedes agregar más después)
CATEGORIES = {
    "antinuke": [
        {"name": "/antinuke enable", "desc": "Activa la protección anti-nuke", "usage": "/antinuke enable"},
        {"name": "/antinuke disable", "desc": "Desactiva la protección anti-nuke", "usage": "/antinuke disable"},
    ],
    "moderacion": [
        {"name": "/ban", "desc": "Banea a un usuario", "usage": "/ban @usuario"},
        {"name": "/kick", "desc": "Expulsa a un usuario", "usage": "/kick @usuario"},
        {"name": "/clear", "desc": "Borra mensajes", "usage": "/clear 50"},
    ],
    "roleplay": [
        {"name": "/rp hug", "desc": "Abraza a alguien", "usage": "/rp hug @usuario"},
        {"name": "/rp kiss", "desc": "Besa a alguien", "usage": "/rp kiss @usuario"},
    ],
    "generales": [
        {"name": "/ping", "desc": "Muestra la latencia", "usage": "/ping"},
        {"name": "/serverinfo", "desc": "Información del servidor", "usage": "/serverinfo"},
    ],
    "anime": [
        {"name": "/waifu", "desc": "Waifu aleatoria", "usage": "/waifu"},
    ],
    "sorteos": [
        {"name": "/giveaway start", "desc": "Inicia un sorteo", "usage": "/giveaway start premio: Premio"},
    ],
    "encuestas": [
        {"name": "/poll create", "desc": "Crea una encuesta", "usage": "/poll create pregunta: Pregunta"},
    ]
}

# Vista de paginación
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

# Vista de categorías
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

# Comandos
@bot.tree.command(name="help", description="Menú de ayuda con botones y páginas")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Ayuda del Bot", description="Selecciona una categoría abajo.", color=0x00ff88)
    await interaction.response.send_message(embed=embed, view=CategoryView(), ephemeral=True)

@bot.tree.command(name="ping", description="Prueba el bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! `{round(bot.latency * 1000)} ms`")

# Evento cuando el bot se enciende
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))

# Inicio del bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ No se encontró DISCORD_TOKEN. Agrégalo en Railway.")
        exit(1)
    print("🚀 Iniciando el bot...")
    bot.run(token)
