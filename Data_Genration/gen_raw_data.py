import pandas as pd
import numpy as np
import random
import string
from datetime import datetime, timedelta

# Configuración del generador de datos
NUM_USERS = 500
NUM_TRANSACTIONS = 2000
NUM_WEB_LOGS = 5000
np.random.seed(42)

# Funciones auxiliares
def random_string(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_date(start_year=2024, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime.now()
    delta = end - start
    random_days = random.randrange(delta.days)
    return start + timedelta(days=random_days)

names_list = ["Juan Perez", "Maria Garcia", "Luis Rodriguez", "Ana Martinez", "Carlos Sanchez",
              "Laura Lopez", "Pedro Gomez", "Sofia Diaz", "Diego Fernandez", "Elena Ruiz"]
domains = ['gmail.com', 'hotmail.com', 'yahoo.es', 'outlook.com']

# --- Sección 1: CRM_Users.csv (simula Salesforce) ---
print("Generando CRM...")
crm_data = []
for _ in range(NUM_USERS):
    # IDs con prefijo '003' para simular Salesforce
    uid = f"003{random_string(15)}"
    name = random.choice(names_list)
    clean_email = f"{name.split()[0].lower()}.{name.split()[1].lower()}@{random.choice(domains)}"

    # Introducir ruido en los emails
    # Variar mayúsculas/minúsculas
    email = clean_email if random.random() > 0.3 else clean_email.upper()
    # Agregar espacios aleatorios
    if random.random() < 0.05:
        email = f" {email} "

    # DNI con algunos nulos
    dni = f"{random.randint(10000000, 99999999)}{random.choice(string.ascii_uppercase)}"
    if random.random() < 0.1:
        dni = None

    crm_data.append([uid, email, name.split()[0], name.split()[1], dni, random_date()])

df_crm = pd.DataFrame(crm_data, columns=['SubscriberKey', 'Email', 'FirstName', 'LastName', 'DNI', 'Registration_Date'])

# Agregar duplicados (mismo DNI, distinto ID) para probar casos reales
duplicates = df_crm.sample(10).copy()
duplicates['SubscriberKey'] = [f"003{random_string(15)}" for _ in range(10)]
df_crm = pd.concat([df_crm, duplicates], ignore_index=True)

# --- Sección 2: POS_Transactions.csv (simula ERP/SAP) ---
print("Generando POS...")
pos_data = []
crm_ids = df_crm['SubscriberKey'].tolist()

for _ in range(NUM_TRANSACTIONS):
    tid = f"TXN-{random.randint(100000, 999999)}"
    channel = random.choices(['Store', 'Web'], weights=[0.6, 0.4])[0]

    base_dt = random_date()
    # Generar fechas en distintos formatos
    if channel == 'Store':
        # Fecha local sin zona
        dt_str = base_dt.replace(hour=random.randint(10, 20)).strftime("%Y-%m-%d %H:%M:%S")
        store_id = random.choice(['MAD-001', 'BCN-002', 'COR-003'])
    else:
        # Fecha web en formato ISO UTC
        dt_str = base_dt.isoformat() + "Z"
        store_id = 'WEB-000'

    # Importes y devoluciones (valores negativos)
    amt = round(random.uniform(10, 200), 2)
    qty = random.randint(1, 5)
    if random.random() < 0.05:
        amt *= -1
        qty *= -1

    # Simular compras sin Customer_ID
    cid = random.choice(crm_ids) if random.random() > 0.3 else None

    pos_data.append([tid, dt_str, channel, store_id, f"SKU-{random.randint(1000,9999)}", qty, amt, cid])

df_pos = pd.DataFrame(pos_data, columns=['Transaction_ID', 'Date_Time', 'Channel', 'Store_ID', 'SKU', 'Quantity', 'Total_Amount', 'Customer_ID'])

# --- Sección 3: Web_Tracking.csv (simula GA4) ---
print("Generando Web Tracking...")
web_data = []
# Reusar cookies para simular sesiones repetidas
cookies = [f"ga_{random_string(10)}" for _ in range(300)]

for _ in range(NUM_WEB_LOGS):
    cookie = random.choice(cookies)
    event = random.choices(['page_view', 'add_to_cart', 'purchase'], weights=[0.7, 0.2, 0.1])[0]

    # Simular distintos tipos de identidad: user_id, cookie o email capturado
    uid = None
    email_cap = None

    if event == 'purchase' or random.random() < 0.1:
        user_row = df_crm.sample(1).iloc[0]
        uid = user_row['SubscriberKey']
        if isinstance(user_row['Email'], str):
            email_cap = user_row['Email'].lower().strip()

    # Timestamp en micros (estilo BigQuery/GA4)
    ts = int(datetime.now().timestamp() * 1e6) - random.randint(0, 1000000000)

    web_data.append([ts, event, cookie, uid, email_cap, f"https://shop.com/product/{random.randint(1,50)}"])

df_web = pd.DataFrame(web_data, columns=['event_timestamp', 'event_name', 'user_pseudo_id', 'user_id', 'captured_email', 'page_location'])

# Guardar archivos CSV generados
df_crm.to_csv('CRM_Users.csv', index=False)
df_pos.to_csv('POS_Transactions.csv', index=False)
df_web.to_csv('Web_Tracking.csv', index=False)

print("¡Archivos generados! Listos para la fase de data engineering.")
