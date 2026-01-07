import duckdb
import pandas as pd

# Conectar DuckDB en memoria (simula el data warehouse local)
con = duckdb.connect(database=':memory:')

# --- Staging y limpieza ---
# Limpiar emails y normalizar fechas para poder unir datos luego
print("--- 1. Creando capa de staging y limpieza ---")

# Normalizar CRM: dejar el email en minúsculas y sin espacios
con.execute("""
    CREATE OR REPLACE TABLE stg_crm AS
    SELECT 
        SubscriberKey as user_id,
        TRIM(LOWER(Email)) as email_clean,
        Registration_Date,
        DNI
    FROM read_csv_auto('CRM_Users.csv')
""")

# Normalizar transacciones: unificar formatos de fecha a TIMESTAMP
con.execute("""
    CREATE OR REPLACE TABLE stg_pos AS
    SELECT 
        Transaction_ID,
        Customer_ID,
        Total_Amount,
        Channel,
        CAST(Date_Time AS TIMESTAMP) as txn_date
    FROM read_csv_auto('POS_Transactions.csv')
""")

# Normalizar web: convertir timestamps en micros a fechas
con.execute("""
    CREATE OR REPLACE TABLE stg_web AS
    SELECT 
        user_pseudo_id as cookie_id,
        user_id as logged_in_user_id,
        TRIM(LOWER(captured_email)) as web_email,
        event_name,
        to_timestamp(event_timestamp / 1000000) as event_date
    FROM read_csv_auto('Web_Tracking.csv')
""")

# --- Resolución de identidad ---
# Unir datos web y pos a nivel usuario; si falta user_id, usar email
print("--- 2. Ejecutando resolución de identidad ---")

con.execute("""
    CREATE OR REPLACE TABLE dim_customers_resolved AS
    SELECT 
        c.user_id,
        c.email_clean,
        c.Registration_Date,
        COUNT(DISTINCT w.cookie_id) as known_cookies,
        COUNT(CASE WHEN w.event_name = 'page_view' THEN 1 END) as total_page_views,
        COUNT(CASE WHEN w.event_name = 'add_to_cart' THEN 1 END) as total_add_to_cart,
        MAX(w.event_date) as last_web_interaction
    FROM stg_crm c
    LEFT JOIN stg_web w 
        ON c.user_id = w.logged_in_user_id 
        OR c.email_clean = w.web_email
    GROUP BY 1, 2, 3
""")

# --- Generar tabla maestra (features) ---
# Calcular RFM y otras métricas en SQL y guardar como CSV
print("--- 3. Generando tabla maestra de features ---")

df_master = con.execute("""
    WITH rfm_calc AS (
        SELECT 
            c.user_id,
            DATE_DIFF('day', MAX(p.txn_date), CURRENT_DATE) as days_since_last_purchase,
            COUNT(DISTINCT p.Transaction_ID) as total_transactions,
            SUM(p.Total_Amount) as total_spend,
            AVG(p.Total_Amount) as avg_ticket_value,
            COUNT(CASE WHEN p.Channel = 'Web' THEN 1 END) * 1.0 / NULLIF(COUNT(*),0) as web_purchase_ratio
        FROM stg_crm c
        JOIN stg_pos p ON c.user_id = p.Customer_ID
        GROUP BY c.user_id
    )
    SELECT 
        base.user_id,
        base.email_clean,
        COALESCE(rfm.days_since_last_purchase, 999) as recency_days,
        COALESCE(rfm.total_transactions, 0) as frequency,
        COALESCE(rfm.total_spend, 0) as monetary,
        COALESCE(rfm.avg_ticket_value, 0) as avg_ticket,
        base.total_page_views,
        base.total_add_to_cart,
        CASE 
            WHEN base.total_add_to_cart > 0 AND (rfm.days_since_last_purchase > 7 OR rfm.days_since_last_purchase IS NULL) 
            THEN 1 ELSE 0 
        END as is_cart_abandoner
    FROM dim_customers_resolved base
    LEFT JOIN rfm_calc rfm ON base.user_id = rfm.user_id
""").fetchdf()

print(f"Master table: {len(df_master)} filas.")
print(df_master.head(5).to_markdown(index=False))

# Guardar CSV para la capa de ML
df_master.to_csv('Master_Features.csv', index=False)
