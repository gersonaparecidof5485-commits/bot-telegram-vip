import sqlite3
from datetime import datetime, timedelta

DB_NAME = "bot_vip.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assinantes (
            user_id INTEGER PRIMARY KEY,
            plano TEXT,
            status TEXT,
            data_pagamento TEXT,
            data_vencimento TEXT,
            is_super_vip INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def registrar_pagamento(user_id, plano):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    agora = datetime.now()
    vencimento = None
    if plano == "mensal":
        vencimento = (agora + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO assinantes (user_id, plano, status, data_pagamento, data_vencimento, is_super_vip)
        VALUES (?, ?, 'ativo', ?, ?, 0)
        ON CONFLICT(user_id) DO UPDATE SET
            plano=excluded.plano,
            status='ativo',
            data_pagamento=excluded.data_pagamento,
            data_vencimento=excluded.data_vencimento
    ''', (user_id, plano, agora.strftime("%Y-%m-%d %H:%M:%S"), vencimento))
    
    conn.commit()
    conn.close()

def ativar_super_vip(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE assinantes SET is_super_vip = 1 WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()

def obter_expirados():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        SELECT user_id FROM assinantes 
        WHERE plano = 'mensal' AND status = 'ativo' AND data_vencimento <= ?
    ''', (agora,))
    expirados = cursor.fetchall()
    conn.close()
    return [u[0] for u in expirados]

def marcar_expirado(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE assinantes SET status = 'expirado' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
