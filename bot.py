import os
import requests
import threading
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import database as db

load_dotenv()

TOKEN = os.getenv(8869290353:AAHlGsgSui4Eib6geib2BBITOjMGfszSRMU)
RPAY_API_KEY = os.getenv(sk_live_bbd5a355cd37c0efd9eaacee6b7637c491a30bdc4a6d921f)
PUBLIC_URL = os.getenv(http://localhost:3000)
CHAT_VIP_PADRAO = os.getenv(-1004389165942)
CHAT_SUPER_VIP = os.getenv(-1003444530644)

db.init_db()
app = Flask(__name__)

def criar_pix_rpay(user_id, valor, produto):
    url = "https://api.rpay.com/v1/charge"
    headers = {"Authorization": f"Bearer {RPAY_API_KEY}"}
    payload = {
        "amount": valor,
        "external_id": f"{user_id}_{produto}",
        "callback_url": f"{PUBLIC_URL}/webhook/rpay",
        "description": f"Acesso VIP - {produto}"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Erro na API RPay: {e}")
        return {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗓️ Plano Mensal - R$ 14,90", callback_data="pay_mensal")],
        [InlineKeyboardButton("♾️ Plano Vitalício - R$ 29,90", callback_data="pay_vitalicio")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 **Seja bem-vindo(a) ao Nosso Canal VIP!**\n\n"
        "Escolha abaixo o seu plano para liberar o acesso instantâneo:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "pay_mensal":
        dados_pix = criar_pix_rpay(user_id, 14.90, "mensal")
        copia_cola = dados_pix.get("pix_code", "CHAVE_PIX_EXEMPLO")
        await query.message.reply_text(
            f"🔑 **PIX Gerado (Plano Mensal - R$ 14,90)**\n\n"
            f"Copie o código abaixo para pagar no seu banco:\n\n`{copia_cola}`\n\n"
            f"⚡ Assim que o pagamento for confirmado, seu link será enviado automaticamente aqui!",
            parse_mode="Markdown"
        )

    elif query.data == "pay_vitalicio":
        dados_pix = criar_pix_rpay(user_id, 29.90, "vitalicio")
        copia_cola = dados_pix.get("pix_code", "CHAVE_PIX_EXEMPLO")
        await query.message.reply_text(
            f"🔑 **PIX Gerado (Plano Vitalício - R$ 29,90)**\n\n"
            f"Copie o código abaixo para pagar no seu banco:\n\n`{copia_cola}`\n\n"
            f"⚡ Assim que o pagamento for confirmado, seu link será enviado automaticamente aqui!",
            parse_mode="Markdown"
        )

    elif query.data == "pay_upsell":
        dados_pix = criar_pix_rpay(user_id, 39.90, "upsell_super_vip")
        copia_cola = dados_pix.get("pix_code", "CHAVE_PIX_EXEMPLO")
        await query.message.reply_text(
            f"🚀 **PIX Super VIP (R$ 39,90 - Oferta Exclusiva)**\n\n"
            f"Copie o código abaixo para migrar seu acesso:\n\n`{copia_cola}`",
            parse_mode="Markdown"
        )

@app.route('/webhook/rpay', methods=['POST'])
def rpay_webhook():
    data = request.json
    if data and data.get("status") == "PAID":
        external_id = data.get("external_id")
        user_id_str, produto = external_id.split("_", 1)
        user_id = int(user_id_str)
        bot_url = f"https://api.telegram.org/bot{TOKEN}"

        if produto in ["mensal", "vitalicio"]:
            db.registrar_pagamento(user_id, produto)

            res_link = requests.post(f"{bot_url}/createChatInviteLink", json={
                "chat_id": CHAT_VIP_PADRAO,
                "member_limit": 1
            }).json()
            invite_link = res_link.get("result", {}).get("invite_link", "")

            # Mensagem 1: Libera Acesso Imediato
            requests.post(f"{bot_url}/sendMessage", json={
                "chat_id": user_id,
                "text": f"✅ **Pagamento Confirmado!**\n\nSeu acesso ao Grupo VIP já está liberado. Clique no link individual abaixo para entrar:\n\n🔗 {invite_link}",
                "parse_mode": "Markdown"
            })

            # Mensagem 2: Oferta de Upsell
            requests.post(f"{bot_url}/sendMessage", json={
                "chat_id": user_id,
                "text": (
                    "🔥 **ESPERA! OPORTUNIDADE ÚNICA E EXCLUSIVA!**\n\n"
                    "Já que você é um novo membro, liberamos **agora** uma vaga com desconto para o nosso **Grupo Super VIP Premium**.\n\n"
                    "🔹 Conteúdos inéditos diários\n"
                    "🔹 Suporte estendido e networking exclusivo\n\n"
                    "⏳ *Esta oferta só está disponível nesta tela e expira em breve.*\n\n"
                    "De ~R$ 97,00~ por apenas **R$ 39,90 (Acesso Vitalício)**!"
                ),
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "🚀 QUERO O SUPER VIP POR R$ 39,90", "callback_data": "pay_upsell"}]
                    ]
                },
                "parse_mode": "Markdown"
            })

        elif produto == "upsell_super_vip":
            db.ativar_super_vip(user_id)

            res_link = requests.post(f"{bot_url}/createChatInviteLink", json={
                "chat_id": CHAT_SUPER_VIP,
                "member_limit": 1
            }).json()
            invite_link = res_link.get("result", {}).get("invite_link", "")

            requests.post(f"{bot_url}/sendMessage", json={
                "chat_id": user_id,
                "text": f"🎉 **PARABÉNS! Você agora é membro SUPER VIP!**\n\nAqui está o seu link de acesso exclusivo:\n\n🔗 {invite_link}",
                "parse_mode": "Markdown"
            })

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(button_click))
    
    threading.Thread(target=telegram_app.run_polling, kwargs={"drop_pending_updates": True}).start()
    app.run(host="0.0.0.0", port=5000)
