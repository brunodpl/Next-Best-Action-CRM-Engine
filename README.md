# Retail Pulse – NBA Engine
### *Next Best Action & CRM Automation Simulator*

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-DuckDB-yellow?logo=duckdb&logoColor=white)
![Data Engineering](https://img.shields.io/badge/Data-Engineering-orange)
![CRM](https://img.shields.io/badge/CRM-Marketing_Automation-blue)

## 📌 ¿Qué problema resuelve esto?

En retail, los datos están desperdigados en mil sistemas que no se hablan entre sí: el CRM de Salesforce tiene una versión del cliente, el ERP de tienda tiene otra, y Google Analytics solo ve cookies anónimas. El resultado es que mandas campañas genéricas que saturan al cliente y tiras el presupuesto de marketing.

Este proyecto simula cómo unificar esos datos rotos y convertirlos en acciones concretas: qué cliente contactar, por qué canal y con qué mensaje. Es lo que realmente se hace en consultoría de CRM Marketing Automation.

## 🚀 Impacto Real en Negocio

Si esto se implementa en una empresa de retail mediana (tipo Inditex, Mango, El Corte Inglés):

*   **Reducción de saturación:** Se dejan de mandar emails genéricos a todos. Solo contactas a quien tiene alta propensión y no está saturado. Eso mejora el engagement (open rate, click rate).
*   **Optimización de presupuesto:** No regalas descuentos a quien ya iba a comprar. Eso se traduce en más margen.
*   **Aumento de conversión:** Identificas "cart abandoners" con alta intención y les mandas el empujón final (SMS, email con urgencia). En retail, eso puede subir conversión un 15-20%.
*   **Vista única del cliente:** El CMO puede ver al cliente de forma unificada (web + tienda + CRM). Eso mejora la toma de decisiones estratégicas.

> **Caso de uso concreto:** Imagina que detectas 500 clientes que añadieron al carrito un abrigo de invierno, no compraron, y tienen historial de compra alta. Les mandas un email con "Últimas unidades - Tu talla se agota". Eso en retail funciona brutalmente bien.

---

## 🛠️ Flujo del Proyecto

### 1. Generación de Datos Realistas (`gen_raw_data.py`)
Creo 3 archivos CSV que simulan fuentes de datos reales con toda su "suciedad":

*   **`CRM_Users.csv` (Salesforce Sim):** Emails con mayúsculas random, espacios basura, DNIs duplicados, campos NULL. El caos típico de un CRM mal mantenido.
*   **`POS_Transactions.csv` (ERP/SAP Sim):** Transacciones de tienda física y web. Fechas en formatos diferentes (UTC vs local), devoluciones con importes negativos, compras sin identificar (Foreign Keys nulas).
*   **`Web_Tracking.csv` (GA4 Sim):** Logs de navegación. Millones de eventos (`page_view`, `add_to_cart`, `purchase`) con timestamps en microsegundos Unix. El puzzle de *identity resolution* (User_ID vs Cookie vs Email).

> *Por qué esto es importante: En mi FP hicimos bases de datos "limpias" de laboratorio. Aquí demuestro que sé trabajar con datos rotos, que es lo que hay en producción.*

### 2. Data Engineering con SQL (`data_engineering.py`)
Aquí está el trabajo duro. Uso **DuckDB** (motor SQL en Python) para transformar ese caos en una vista única del cliente (*Single Customer View*). Lo hago en 3 capas:

*   **Capa 1: Staging & Cleaning:** Normalizo emails, arreglo el desastre de fechas (parseo UTC e ISO 8601) y convierto timestamps.
*   **Capa 2: Identity Resolution:** Unifico al mismo usuario que navega en web con el que compra en tienda.
    *   *Estrategia:* Si tengo su ID lo cruzo directo, si no busco por email normalizado. Esto es lo que diferencia un Data Analyst junior de uno senior.
*   **Capa 3: Feature Engineering:**
    *   Calculo métricas RFM (*Recency, Frequency, Monetary*) directamente en SQL.
    *   Agrego features de comportamiento: ratio de abandono de carrito, preferencia web vs tienda, ticket medio.
    *   Genero la tabla `Master_Features.csv` lista para el modelo.

> *Por qué SQL y no Python: Porque para 500k filas SQL es 10x más rápido que Pandas. En consultoría te piden eficiencia, no solo que funcione.*

### 3. Scoring & Next Best Action (`next_best_action.ipynb`)
*(Fase diseñada, pendiente de implementación completa)*

1.  Cargar `Master_Features.csv` y entrenar un modelo de propensión de compra (**XGBoost** o **LightGBM**).
2.  Aplicar una capa de reglas de negocio encima del modelo:
    *   **Anti-saturación:** Si abrió un email hace menos de 2 días → ⛔ NO contactar.
    *   **Urgencia por stock:** Si propensión > 0.8 y stock bajo → ⚡ SMS urgente.
    *   **Eficiencia de margen:** Si propensión > 0.9 → 💰 NO mandar descuento (ya va a comprar).

> *Esto es clave: El modelo ML predice probabilidad, pero las reglas deciden la acción. Así funciona en real.*

### 4. Reverse ETL - Output Final (`toload.ipynb`)
El objetivo final es generar dos archivos listos para activación:

*   📄 **`DE_Target_Audience.csv`:** La audiencia lista para importar en Salesforce Marketing Cloud. Columnas: `SubscriberKey`, `Email`, `NBA_Code` (Next Best Action), `Dynamic_Subject_Line_ID`.
*   🛠️ **`Trigger_Log.json`:** Un log técnico para auditoría. Simula mentalidad de Data Engineer (trazabilidad).

---

## 💻 Stack Técnico

*   **Lenguajes:** Python (Pandas), SQL (Avanzado).
*   **Motor de Datos:** DuckDB (Simula la potencia de Snowflake/BigQuery en local).
*   **Machine Learning:** scikit-learn/XGBoost (Planned).
*   **Simulación de Entorno:** Salesforce CRM, SAP ERP, Google Analytics 4, Salesforce Marketing Cloud.

## ⭐ Por qué este proyecto me diferencia

1.  **Realismo:** La mayoría de portfolios hacen Kaggle con datos limpios. Aquí simulo el caos real de una empresa.
2.  **End-to-End:** Demuestro que entiendo el flujo completo, desde la ingesta de datos sucios hasta la activación de campañas.
3.  **SQL Avanzado:** Uso CTEs, Window Functions y lógica de Identity Resolution. No dependo solo de Pandas.
4.  **Mentalidad de Consultor:** No solo hago el modelo, diseño las reglas de negocio que maximizan el ROI.

***

**Autor:** Bruno
**Ubicación:** A Coruña, España
**Especialidad:** Python, SQL (DuckDB/PostgreSQL), Data Engineering, CRM Automation
