import os
import requests
from dotenv import load_dotenv
import database as db

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_VIP_PADRAO = os.getenv("CHAT_ID_VIP_PADRAO")

def remover_membros_expirados():
    expirados = db.obter_expirados()
    bot_url = f"https://api.telegram.org/bot{TOKEN}"

    for user_id in expirados:
        try:
            requests.post(f"{bot_url}/banChatMember", json={"chat_id": CHAT_VIP_PADRAO, "user_id": user_id})
            requests.post(f"{bot_url}/unbanChatMember", json={"chat_id": CHAT_VIP_PADRAO, "user_id": user_id})
            
            requests.post(f"{bot_url}/sendMessage", json={
                "chat_id": user_id,
                "text": "⚠️ **Sua assinatura de 30 dias venceu.**\n\nPara renovar seu acesso ao Grupo VIP por R$ 14,90, envie o comando /start para o bot."
            })
            
            db.marcar_expirado(user_id)
            print(f"Usuário {user_id} removido por vencimento.")
        except Exception as e:
            print(f"Erro ao remover {user_id}: {e}")

if __name__ == "__main__":
    remover_membros_expirados()
