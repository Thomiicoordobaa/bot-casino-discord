import discord
from discord.ext import commands
import random
import json
import os
from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

FICHAS_FILE = "fichas.json"

# Servidor web para mantener el bot activo
app = Flask('')

@app.route('/')
def home():
    return "El bot está activo"

def mantener_online():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# Funciones para guardar/cargar fichas
def cargar_fichas():
    if os.path.exists(FICHAS_FILE):
        with open(FICHAS_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_fichas():
    with open(FICHAS_FILE, "w") as f:
        json.dump(fichas, f)

fichas = cargar_fichas()

# Ver fichas
@bot.command()
async def ver_fichas(ctx, miembro: discord.Member = None):
    miembro = miembro or ctx.author
    total = fichas.get(str(miembro.id), 0)
    await ctx.send(f"{miembro.mention} tiene {total} fichas.")

# Apostar en slot
@bot.command()
async def apostar_slot(ctx, cantidad: int):
    user_id = str(ctx.author.id)

    if cantidad <= 0:
        await ctx.send("La cantidad debe ser mayor a 0.")
        return

    if fichas.get(user_id, 0) < cantidad:
        await ctx.send("No tenés suficientes fichas.")
        return

    fichas[user_id] -= cantidad

    simbolos = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
    resultado = [random.choice(simbolos) for _ in range(3)]
    await ctx.send(f"Resultado: {' '.join(resultado)}")

    if resultado.count(resultado[0]) == 3:
        premio = cantidad * 5
        fichas[user_id] += premio
        await ctx.send(f"¡Jackpot! Ganaste {premio} fichas.")
    elif resultado[0] == resultado[1] or resultado[1] == resultado[2] or resultado[0] == resultado[2]:
        premio = cantidad * 2
        fichas[user_id] += premio
        await ctx.send(f"¡Ganaste {premio} fichas!")
    else:
        await ctx.send("Perdiste...")

    guardar_fichas()

# Apostar en ruleta rusa
@bot.command()
async def apostar_ruleta(ctx, cantidad: int):
    user_id = str(ctx.author.id)

    if cantidad <= 0:
        await ctx.send("La cantidad debe ser mayor a 0.")
        return

    if fichas.get(user_id, 0) < cantidad:
        await ctx.send("No tenés suficientes fichas.")
        return

    fichas[user_id] -= cantidad
    bala = random.randint(1, 6)

    if bala == 1:
        await ctx.send("¡Bang! Perdiste tus fichas.")
    else:
        premio = cantidad * 2
        fichas[user_id] += premio
        await ctx.send(f"¡Suerte! Ganaste {premio} fichas.")

    guardar_fichas()

# Transferir fichas entre usuarios
@bot.command()
async def transferir_fichas(ctx, destino: discord.Member, cantidad: int):
    origen_id = str(ctx.author.id)
    destino_id = str(destino.id)

    if cantidad <= 0:
        await ctx.send("La cantidad debe ser mayor a 0.")
        return

    if fichas.get(origen_id, 0) < cantidad:
        await ctx.send("No tenés suficientes fichas para transferir.")
        return

    fichas[origen_id] -= cantidad
    fichas[destino_id] = fichas.get(destino_id, 0) + cantidad
    guardar_fichas()

    await ctx.send(f"{ctx.author.mention} transfirió {cantidad} fichas a {destino.mention}.")

# Crear fichas (solo admins)
@bot.command()
@commands.has_permissions(administrator=True)
async def crear_fichas(ctx, miembro: discord.Member, cantidad: int):
    if cantidad <= 0:
        await ctx.send("La cantidad debe ser mayor a 0.")
        return

    user_id = str(miembro.id)
    fichas[user_id] = fichas.get(user_id, 0) + cantidad
    guardar_fichas()

    await ctx.send(f"Se han creado {cantidad} fichas para {miembro.mention}. Ahora tiene {fichas[user_id]} fichas.")

# Evento de conexión del bot
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

# Iniciar servidor web y bot
mantener_online()
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
