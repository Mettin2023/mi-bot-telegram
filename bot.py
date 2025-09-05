import logging
import random
import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

# Configura tus tokens
TELEGRAM_TOKEN = "8237917484:AAHfYb0ggeAU7tnvLQ-o8VWOQBwu3E7BEy0"
OPENAI_API_KEY = "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"

# Inicializar cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Archivo para guardar datos
DATA_FILE = "usuarios.json"

# Cargar datos si existen
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        usuarios = json.load(f)
else:
    usuarios = {}

# Listas
frases = [
    "La calle no espera, pero vos tampoco te quedes quieto 🔥",
    "Si nadie cree en vos, no importa. Usted crea en usted mismo 💪",
    "La vida golpea, pero usted golpea más duro, ¿oyó? 👊",
    "No hay excusas, solo resultados. ¡Pilas pues! 🚀"
]

tips = [
    "Aprenda algo nuevo hoy, así sea pequeño. Cada día suma.",
    "No se compare, compare su progreso con el de ayer.",
    "Levántese temprano, la calle premia al que se mueve.",
    "Controle la mente, porque ella controla el resto."
]

realidades = [
    "Si no se mueve, nadie va a mover el mundo por usted.",
    "En la calle nadie regala nada, todo se gana.",
    "Si no arriesga, se queda en el mismo lugar toda la vida.",
    "La única persona que lo puede salvar es usted mismo."
]

retos = [
    "Haz 30 flexiones sin parar, porque usted no se rinde 💪🔥",
    "Levántese 1 hora más temprano y escriba 3 metas para hoy ✍️",
    "Ahorre $5.000 hoy, así empieza la riqueza 💰",
    "Dedique 30 minutos a aprender algo nuevo 📚",
    "Llame a alguien y hable positivo, contagie energía 🔥",
    "Camine 3 km hoy, mueva esas piernas 🏃",
    "Escriba 5 cosas por las que está agradecido 🙌"
]

# Guardar datos
def guardar_datos():
    with open(DATA_FILE, "w") as f:
        json.dump(usuarios, f)

# Calcular nivel
def calcular_nivel(puntos):
    return puntos // 50 + 1

# Actualizar puntos
def agregar_puntos(user_id, puntos, nombre):
    user_id = str(user_id)
    if user_id not in usuarios:
        usuarios[user_id] = {"puntos": 0, "nombre": nombre, "racha": 0, "ultimo_dia": ""}
    usuarios[user_id]["puntos"] += puntos
    guardar_datos()

# Comandos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 ¿Qué hubo, mi pana? Usa /motivame /reto /cumplido /nivel /ranking /racha /frase /tip /realidad /plan")

async def motivame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pilas pues, que la calle no perdona, pero usted tampoco se rinde, ¿oyó? 💪🔥")

async def reto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Reto del día: " + random.choice(retos))

async def cumplido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    nombre = update.message.from_user.first_name
    hoy = datetime.now().strftime("%Y-%m-%d")

    if user_id not in usuarios:
        usuarios[user_id] = {"puntos": 0, "nombre": nombre, "racha": 0, "ultimo_dia": ""}

    ultimo = usuarios[user_id]["ultimo_dia"]

    # Calcular racha
    if ultimo == hoy:
        bonus = 0
    else:
        if ultimo == "":
            usuarios[user_id]["racha"] = 1
        else:
            dia_anterior = datetime.strptime(ultimo, "%Y-%m-%d")
            if (datetime.now() - dia_anterior).days == 1:
                usuarios[user_id]["racha"] += 1
            else:
                usuarios[user_id]["racha"] = 1

    usuarios[user_id]["ultimo_dia"] = hoy

    # Calcular puntos extra por racha
    racha = usuarios[user_id]["racha"]
    bonus = min(10 + (racha - 1) * 5, 50)

    usuarios[user_id]["puntos"] += bonus
    guardar_datos()

    await update.message.reply_text(
        f"🔥 Bien hecho, {nombre}. Racha: {racha} días. Ganaste +{bonus} puntos. Total: {usuarios[user_id]['puntos']} pts."
    )

async def nivel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    puntos = usuarios.get(user_id, {}).get("puntos", 0)
    nivel = calcular_nivel(puntos)
    await update.message.reply_text(f"📊 Puntos: {puntos} | Nivel: {nivel}")

async def racha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    racha = usuarios.get(user_id, {}).get("racha", 0)
    await update.message.reply_text(f"🔥 Tu racha actual es de {racha} días seguidos. ¡Sigue así, mi pana!")

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ranking_lista = sorted(usuarios.items(), key=lambda x: x[1]["puntos"], reverse=True)
    mensaje = "🏆 *Ranking Global*\n\n"
    top = ranking_lista[:5]
    for i, (uid, data) in enumerate(top, start=1):
        mensaje += f"{i}. {data['nombre']} - {data['puntos']} pts (Nivel {calcular_nivel(data['puntos'])})\n"
    user_id = str(update.message.from_user.id)
    if user_id not in [u[0] for u in top]:
        posicion = [u[0] for u in ranking_lista].index(user_id) + 1
        mensaje += f"\nTu posición: {posicion} con {usuarios[user_id]['puntos']} pts"
    await update.message.reply_text(mensaje, parse_mode="Markdown")

async def frase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(frases))

async def tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(tips))

async def realidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(realidades))

async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Plan de hoy: 1) Levántese con actitud 💪 2) Haga ejercicio 🏋️ 3) Aprenda algo nuevo 📚 4) Trabaje en su meta 🔥")

# Respuesta IA
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Habla como un coach callejero motivador, directo y realista."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=100
    )
    respuesta = response.choices[0].message.content
    await update.message.reply_text(respuesta)

# Inicializar bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("motivame", motivame))
app.add_handler(CommandHandler("reto", reto))
app.add_handler(CommandHandler("cumplido", cumplido))
app.add_handler(CommandHandler("nivel", nivel))
app.add_handler(CommandHandler("racha", racha))
app.add_handler(CommandHandler("ranking", ranking))
app.add_handler(CommandHandler("frase", frase))
app.add_handler(CommandHandler("tip", tip))
app.add_handler(CommandHandler("realidad", realidad))
app.add_handler(CommandHandler("plan", plan))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

print("✅ Bot con Racha Diaria + Ranking + Progreso andando...")
app.run_polling()
