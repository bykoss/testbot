import discord
from discord import app_commands
from discord.ui import View, Button
from discord.ext import commands
import asyncio
import random
from datetime import datetime, timedelta
import json  # Para guardar sorteos simples (puedes mejorar con SQLite después)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True
intents.guilds = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot {self.user} iniciado y comandos sincronizados.")

bot = MyBot()

# ==================== DICCIONARIO DE COMANDOS (versión mejorada) ====================
CATEGORIES = {
    "antinuke": [
        {"name": "/antinuke enable", "desc": "Activa la protección anti-nuke", "usage": "/antinuke enable"},
        {"name": "/antinuke disable", "desc": "Desactiva la protección anti-nuke", "usage": "/antinuke disable"},
        {"name": "/antinuke set-log", "desc": "Establece canal de logs", "usage": "/antinuke set-log #canal"},
        {"name": "/antinuke whitelist add", "desc": "Añade usuario a whitelist", "usage": "/antinuke whitelist add @usuario"},
        {"name": "/antinuke whitelist remove", "desc": "Quita usuario de whitelist", "usage": "/antinuke whitelist remove @usuario"},
        # Agrega aquí más comandos anti-nuke (hasta ~50)
    ],
    "moderacion": [
        {"name": "/ban", "desc": "Banea a un usuario", "usage": "/ban @usuario razón: texto"},
        {"name": "/kick", "desc": "Expulsa a un usuario", "usage": "/kick @usuario razón"},
        {"name": "/mute", "desc": "Silencia temporalmente", "usage": "/mute @usuario tiempo: 30m"},
        {"name": "/clear", "desc": "Borra mensajes", "usage": "/clear cantidad: 50"},
        {"name": "/slowmode", "desc": "Establece modo lento", "usage": "/slowmode segundos: 10"},
        # Agrega más aquí
    ],
    "roleplay": [
        {"name": "/rp hug", "desc": "Abrazas a alguien", "usage": "/rp hug @usuario"},
        {"name": "/rp kiss", "desc": "Besas a alguien", "usage": "/rp kiss @usuario"},
        {"name": "/rp pat", "desc": "Acaricias la cabeza", "usage": "/rp pat @usuario"},
        {"name": "/rp slap", "desc": "Bofetada juguetona", "usage": "/rp slap @usuario"},
        # Agrega aquí los ~100+ comandos roleplay
    ],
    "generales": [
        {"name": "/ping", "desc": "Latencia del bot", "usage": "/ping"},
        {"name": "/serverinfo", "desc": "Info del servidor", "usage": "/serverinfo"},
        {"name": "/userinfo", "desc": "Info de usuario", "usage": "/userinfo @usuario"},
    ],
    "anime": [
        {"name": "/waifu", "desc": "Waifu random", "usage": "/waifu"},
        {"name": "/neko", "desc": "Imagen de neko", "usage": "/neko"},
    ],
    "sorteos": [
        {"name": "/giveaway start", "desc": "Inicia sorteo con botones", "usage": "/giveaway start premio: Premio tiempo: 1h"},
    ],
    "encuestas": [
        {"name": "/poll create", "desc": "Crea encuesta con botones", "usage": "/poll create pregunta: ¿Qué prefieres?"},
    ]
}

# ==================== VISTAS CON BOTONES (VERSIÓN ESTABLE) ====================
class CommandPageView(View):
    def __init__(self, commands_list: list, category: str):
        super().__init__(timeout=600)
        self.commands_list = commands_list
        self.category = category
        self.page = 0
        self.per_page = 8

    def get_embed(self):
        embed = discord.Embed(
            title=f"📋 {self.category.upper()} - Comandos",
            color=0x00ff88,
            timestamp=datetime.now()
        )
        start = self.page * self.per_page
        end = start + self.per_page
        page_cmds = self.commands_list[start:end]

        for cmd in page_cmds:
            embed.add_field(
                name=cmd["name"],
                value=f"{cmd['desc']}\n**Uso:** `{cmd['usage']}`",
                inline=False
            )

        total_pages = (len(self.commands_list) + self.per_page - 1) // self.per_page
        embed.set_footer(text=f"Página {self.page + 1} de {total_pages} • Total: {len(self.commands_list)} comandos")
        return embed

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="➡️ Siguiente", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        total_pages = (len(self.commands_list) + self.per_page - 1) // self.per_page
        if self.page < total_pages - 1:
            self.page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="❌ Cerrar", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()

class CategorySelectView(View):
    def __init__(self):
        super().__init__(timeout=600)
        for cat in CATEGORIES:
            btn = Button(label=cat.capitalize(), style=discord.ButtonStyle.blurple)
            btn.callback = self.create_callback(cat)
            self.add_item(btn)

    def create_callback(self, category: str):
        async def callback(interaction: discord.Interaction):
            cmds = CATEGORIES[category]
            if not cmds:
                await interaction.response.send_message("Esta categoría está vacía por ahora.", ephemeral=True)
                return
            view = CommandPageView(cmds, category)
            await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)
        return callback

# ==================== COMANDO HELP PRINCIPAL ====================
@bot.tree.command(name="help", description="Menú de ayuda con botones y paginación")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Ayuda del Bot - +400 Comandos",
        description="Selecciona una categoría abajo.\nTodo funciona con embeds, botones y paginación.",
        color=0x00ff88
    )
    embed.add_field(name="Categorías disponibles", value=", ".join(c.capitalize() for c in CATEGORIES.keys()), inline=False)
    embed.set_footer(text="Toca un botón → explora los comandos con Anterior/Siguiente")

    view = CategorySelectView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ==================== COMANDOS FUNCIONALES DE EJEMPLO ====================
@bot.tree.command(name="ping", description="Muestra la latencia del bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! `{latency}ms`")

@bot.tree.command(name="giveaway_start", description="Inicia un sorteo con botones")
@app_commands.describe(premio="Qué se sortea", duracion="Ejemplo: 30m, 1h, 2h", ganadores="Número de ganadores (default 1)")
async def giveaway_start(interaction: discord.Interaction, premio: str, duracion: str, ganadores: int = 1):
    try:
        # Parse simple de duración (mejorable)
        if duracion.endswith("m"):
            seconds = int(duracion[:-1]) * 60
        elif duracion.endswith("h"):
            seconds = int(duracion[:-1]) * 3600
        else:
            seconds = 3600

        embed = discord.Embed(
            title="🎉 ¡SORTEO ACTIVO!",
            description=f"**Premio:** {premio}\n**Ganadores:** {ganadores}\n**Tiempo restante:** {duracion}",
            color=0xff0000
        )
        embed.set_footer(text=f"Iniciado por {interaction.user}")

        view = View(timeout=None)
        participants = []

        async def join_callback(i: discord.Interaction):
            if i.user.id not in participants:
                participants.append(i.user.id)
                await i.response.send_message("✅ ¡Participando!", ephemeral=True)
            else:
                await i.response.send_message("Ya estás participando.", ephemeral=True)

        join_btn = Button(label="¡Participar!", style=discord.ButtonStyle.green, emoji="🎟️")
        join_btn.callback = join_callback
        view.add_item(join_btn)

        await interaction.response.send_message(embed=embed, view=view)
        message = await interaction.original_response()

        await asyncio.sleep(seconds)

        if participants:
            winners = random.sample(participants, min(ganadores, len(participants)))
            winner_mentions = " ".join(f"<@{w}>" for w in winners)
            await interaction.channel.send(f"🎊 **¡Sorteo terminado!**\n**Ganador(es):** {winner_mentions}\n**Premio:** {premio}")
        else:
            await interaction.channel.send("El sorteo terminó sin participantes.")

    except Exception as e:
        await interaction.response.send_message(f"Error al crear sorteo: {str(e)}", ephemeral=True)

@bot.tree.command(name="poll_create", description="Crea una encuesta simple con botones")
@app_commands.describe(pregunta="La pregunta de la encuesta", opcion1="Primera opción", opcion2="Segunda opción")
async def poll_create(interaction: discord.Interaction, pregunta: str, opcion1: str, opcion2: str):
    embed = discord.Embed(title="📊 Encuesta", description=pregunta, color=0x00ffff)
    embed.add_field(name="Opciones", value=f"1️⃣ {opcion1}\n2️⃣ {opcion2}", inline=False)

    view = View(timeout=None)
    votes = {opcion1: 0, opcion2: 0}

    async def vote1(i: discord.Interaction):
        votes[opcion1] += 1
        await i.response.send_message(f"Votaste por **{opcion1}**", ephemeral=True)

    async def vote2(i: discord.Interaction):
        votes[opcion2] += 1
        await i.response.send_message(f"Votaste por **{opcion2}**", ephemeral=True)

    btn1 = Button(label=opcion1[:80], style=discord.ButtonStyle.blue)
    btn2 = Button(label=opcion2[:80], style=discord.ButtonStyle.blue)
    btn1.callback = vote1
    btn2.callback = vote2

    view.add_item(btn1)
    view.add_item(btn2)

    await interaction.response.send_message(embed=embed, view=view)

# ==================== EVENTOS BÁSICOS ====================
@bot.event
async def on_ready():
    print(f"✅ {bot.user} está en línea y listo.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help | +400 comandos"))

@bot.event
async def on_guild_channel_delete(channel):
    print(f"🚨 Canal eliminado: {channel.name} - Anti-nuke debería revisar esto (implementa lógica completa aquí)")

# ==================== INICIO ====================
if __name__ == "__main__":
    TOKEN = "TU_TOKEN_AQUÍ"  # ← Reemplaza con tu token real
    bot.run(TOKEN)
