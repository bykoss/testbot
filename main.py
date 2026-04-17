import discord
from discord import app_commands
from discord.ui import View, Button
from discord.ext import commands
import os
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
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
            print("✅ Comandos slash sincronizados globalmente.")
        except Exception as e:
            print(f"⚠️ Error al sincronizar comandos: {e}")

bot = MyBot()

# ==================== CATEGORÍAS DE COMANDOS ====================
CATEGORIES = {
    "antinuke": [
        {"name": "/antinuke enable", "desc": "Activa la protección anti-nuke completa", "usage": "/antinuke enable"},
        {"name": "/antinuke disable", "desc": "Desactiva la protección anti-nuke", "usage": "/antinuke disable"},
        {"name": "/antinuke set-log", "desc": "Establece el canal de logs", "usage": "/antinuke set-log #canal"},
    ],
    "moderacion": [
        {"name": "/ban", "desc": "Banea a un usuario", "usage": "/ban @usuario razón"},
        {"name": "/kick", "desc": "Expulsa a un usuario", "usage": "/kick @usuario"},
        {"name": "/clear", "desc": "Borra mensajes del canal", "usage": "/clear cantidad: 50"},
        {"name": "/mute", "desc": "Silencia a un usuario", "usage": "/mute @usuario tiempo: 10m"},
    ],
    "roleplay": [
        {"name": "/rp hug", "desc": "Abraza a alguien", "usage": "/rp hug @usuario"},
        {"name": "/rp kiss", "desc": "Besa a alguien", "usage": "/rp kiss @usuario"},
        {"name": "/rp pat", "desc": "Acaricia la cabeza", "usage": "/rp pat @usuario"},
        {"name": "/rp slap", "desc": "Da una bofetada juguetona", "usage": "/rp slap @usuario"},
    ],
    "generales": [
        {"name": "/ping", "desc": "Muestra la latencia del bot", "usage": "/ping"},
        {"name": "/serverinfo", "desc": "Información del servidor", "usage": "/serverinfo"},
        {"name": "/userinfo", "desc": "Información de un usuario", "usage": "/userinfo @usuario"},
    ],
    "anime": [
        {"name": "/waifu", "desc": "Te da una waifu aleatoria", "usage": "/waifu"},
    ],
    "sorteos": [
        {"name": "/giveaway start", "desc": "Inicia un sorteo", "usage": "/giveaway start premio: Premio tiempo: 1h"},
    ],
    "encuestas": [
        {"name": "/poll create", "desc": "Crea una encuesta con botones", "usage": "/poll create pregunta: ¿Qué prefieres?"},
    ]
}

# ==================== VISTAS CON BOTONES ====================
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
            cmds = CATEGORIES[category]
            view = CommandPageView(cmds, category)
            await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)
        return callback

# ==================== COMANDOS ====================
@bot.tree.command(name="help", description="Menú completo de comandos con botones y paginación")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Ayuda del Bot - +400 Comandos",
        description="Selecciona una categoría para ver todos los comandos.",
        color=0x00ff88
    )
    await interaction.response.send_message(embed=embed, view=CategoryView(), ephemeral=True)

@bot.tree.command(name="ping", description="Muestra la latencia del bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! `{round(bot.latency * 1000)} ms`")

@bot.tree.command(name="sync", description="Sincroniza los comandos (solo para ti)")
async def sync_commands(interaction: discord.Interaction):
    if interaction.user.id != 123456789012345678:  # ← CAMBIA ESTE NÚMERO por tu ID de Discord
        return await interaction.response.send_message("Solo el dueño puede usar este comando.", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    try:
        await bot.tree.sync()
        await interaction.followup.send("✅ Comandos sincronizados globalmente.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

# ==================== EVENTO ON_READY ====================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado correctamente como {bot.user}")
    print(f"   Servidores: {len(bot.guilds)}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="/help • +400 comandos")
    )

# ==================== INICIO DEL BOT ====================
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ ERROR: No se encontró DISCORD_TOKEN en Railway.")
        exit(1)
    print("🚀 Iniciando bot...")
    bot.run(token)
