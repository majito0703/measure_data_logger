# -*- coding: utf-8 -*-
"""MODELO SARIMA para ejecución en GitHub Actions"""

import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo para GitHub Actions
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.dates as mdates
import json
import os
import base64
import requests
from datetime import timedelta
import sys

# Configurar para evitar advertencias
warnings.filterwarnings("ignore")

# Configurar Matplotlib para GitHub Actions
matplotlib.rcParams["figure.max_open_warning"] = 0
plt.rcParams["xtick.major.pad"] = 10
plt.rcParams["ytick.major.pad"] = 10

print("=" * 60)
print("🚀 INICIANDO MODELO SARIMA EN GITHUB ACTIONS")
print("=" * 60)

# ======================================================
# 1. LECTURA DE DATOS DESDE GOOGLE SHEETS
# ======================================================
def cargar_datos_google_sheets():
    """
    Carga datos desde Google Sheets usando credenciales de GitHub Secrets
    """
    try:
        sheet_id = "1x1FeUolFWlR07tgrc6F4cgeUhJYV7uQ5yuRTBHO8jWI"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

        
        print(f"📥 Descargando datos desde Google Sheets...")
        df_full = pd.read_csv(url)
        
        # Tomar solo los últimos 1,100 datos
        df0 = df_full.tail(600)
        
        print(f"✅ Datos cargados exitosamente")
        print(f"   Total de filas originales: {len(df_full)}")
        print(f"   Filas procesadas (últimos 1,100): {len(df0)}")
        
        return df0
        
    except Exception as e:
        print(f"❌ Error cargando datos de Google Sheets: {e}")
        print("⚠️  Intentando cargar datos de respaldo...")
        
        # Intentar cargar datos locales como respaldo
        try:
            if os.path.exists("datos_respaldo.csv"):
                df_full = pd.read_csv("datos_respaldo.csv")
                df0 = df_full.tail(1100)
                print(f"✅ Datos de respaldo cargados ({len(df0)} filas)")
                return df0
        except Exception as e2:
            print(f"❌ Error con datos de respaldo: {e2}")
        
        # Crear datos de ejemplo si todo falla
        print("⚠️  Generando datos de ejemplo...")
        fechas = pd.date_range(end=pd.Timestamp.now(), periods=1100, freq='H')
        datos = {
            'Date': [d.strftime('%d/%m/%Y %H:%M:%S') for d in fechas],
            'Temperature': np.random.normal(25, 5, 1100),
            'Humidity': np.random.normal(60, 15, 1100),
            'PM 2.5(µg/m³)': np.random.normal(20, 10, 1100),
            'PM 10 (µg/m³)': np.random.normal(35, 15, 1100),
            'Radiacion Solar (W/m)': np.random.normal(300, 100, 1100)
        }
        df0 = pd.DataFrame(datos)
        print(f"✅ Datos de ejemplo generados ({len(df0)} filas)")
        return df0

# ======================================================
# 2. FUNCIONES AUXILIARES PARA PROCESAMIENTO DE DATOS
# ======================================================
def parse_datetime_index(df, format="%d/%m/%Y %H:%M:%S"):
    """Convierte la columna de fecha a índice datetime"""
    df_copy = df.copy()
    
    # Renombrar columnas
    df_copy.rename(
        columns={
            "Date": "date",
            "PM 1.0 (µg/m³)": "PM 1",
            "PM 2.5(µg/m³)": "PM 2.5",
            "PM 10 (µg/m³)": "PM 10",
            "Radiacion Solar (W/m)": "Radiacion Solar",
        },
        inplace=True,
    )
    
    # Convertir tipos de datos
    df_copy["Temperature"] = pd.to_numeric(df_copy["Temperature"], errors="coerce")
    df_copy["Humidity"] = pd.to_numeric(df_copy["Humidity"], errors="coerce")
    df_copy["PM 2.5"] = pd.to_numeric(df_copy["PM 2.5"], errors="coerce")
    df_copy["PM 10"] = pd.to_numeric(df_copy["PM 10"], errors="coerce")
    df_copy["Radiacion Solar"] = pd.to_numeric(df_copy["Radiacion Solar"], errors="coerce")
    
    # Convertir fecha a datetime y establecer como índice
    df_copy["date"] = pd.to_datetime(df_copy["date"], format=format, errors="coerce")
    df_copy.set_index("date", inplace=True)
    
    # Eliminar filas con fechas inválidas
    df_copy = df_copy[df_copy.index.notnull()]
    
    return df_copy

def plot_time_series(df, variable, units="", time_unit="Day"):
    """Función simplificada para graficar series de tiempo"""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df.index, df[variable], linewidth=1)
    ax.set_title(f"{variable} {units}")
    ax.set_xlabel(f"Tiempo ({time_unit})")
    ax.set_ylabel(f"{variable} {units}")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig

# ======================================================
# 3. OPTIMIZADOR SARIMA
# ======================================================
def buscar_mejor_modelo(series):
    """Busca el mejor modelo SARIMA para una serie temporal"""
    p = d = q = [0, 1]
    P = D = Q = [0, 1]
    m = 12  # estacionalidad de 12 horas
    
    mejor_aic = float("inf")
    mejor_modelo = None
    mejor_orden = None
    mejor_orden_season = None
    mejores_parametros = None
    mejor_summary = None

    for pi in p:
        for di in d:
            for qi in q:
                for Pi in P:
                    for Di in D:
                        for Qi in Q:
                            orden = (pi, di, qi)
                            orden_seas = (Pi, Di, Qi, m)

                            try:
                                modelo = SARIMAX(
                                    series,
                                    order=orden,
                                    seasonal_order=orden_seas,
                                    enforce_stationarity=False,
                                    enforce_invertibility=False,
                                ).fit(disp=False, maxiter=200)

                                if modelo.aic < mejor_aic:
                                    mejor_aic = modelo.aic
                                    mejor_modelo = modelo
                                    mejor_orden = orden
                                    mejor_orden_season = orden_seas
                                    mejores_parametros = modelo.params
                                    mejor_summary = modelo.summary()

                            except Exception as e:
                                continue

    return (
        mejor_modelo,
        mejor_orden,
        mejor_orden_season,
        mejor_aic,
        mejores_parametros,
        mejor_summary,
    )

# ======================================================
# 4. FUNCIONES PARA ECUACIÓN Y PARÁMETROS
# ======================================================
def obtener_ecuacion_sarima(modelo, orden, orden_seas):
    """Genera la ecuación matemática del modelo SARIMA"""
    p, d, q = orden
    P, D, Q, m = orden_seas

    params = modelo.params

    parte_ar = ""
    parte_ma = ""
    parte_sar = ""
    parte_sma = ""

    # Coeficientes AR (no estacional)
    for i in range(1, p + 1):
        if f"ar.L{i}" in params:
            coef = params[f"ar.L{i}"]
            parte_ar += f" + {coef:.4f}·y_t-{i}"

    # Coeficientes MA (no estacional)
    for i in range(1, q + 1):
        if f"ma.L{i}" in params:
            coef = params[f"ma.L{i}"]
            parte_ma += f" + {coef:.4f}·ε_t-{i}"

    # Coeficientes SAR (estacional)
    for i in range(1, P + 1):
        if f"ar.S.L{m*i}" in params:
            coef = params[f"ar.S.L{m*i}"]
            parte_sar += f" + {coef:.4f}·y_t-{m*i}"

    # Coeficientes SMA (estacional)
    for i in range(1, Q + 1):
        if f"ma.S.L{m*i}" in params:
            coef = params[f"ma.S.L{m*i}"]
            parte_sma += f" + {coef:.4f}·ε_t-{m*i}"

    # Constante
    constante = ""
    if "intercept" in params:
        constante = f"{params['intercept']:.4f} + "
    elif "const" in params:
        constante = f"{params['const']:.4f} + "

    # Construir ecuación
    if d == 0 and D == 0:
        ecuacion = f"y_t = {constante}"
    else:
        ecuacion = "Δ^d Δ_s^D y_t = "
        if constante.strip():
            ecuacion = f"Δ^d Δ_s^D y_t = {constante}"

    # Agregar partes
    if parte_ar:
        ecuacion += parte_ar[3:] if ecuacion.endswith("= ") else parte_ar
    if parte_ma:
        ecuacion += parte_ma
    if parte_sar:
        ecuacion += parte_sar
    if parte_sma:
        ecuacion += parte_sma

    if parte_ar or parte_ma or parte_sar or parte_sma:
        ecuacion += " + ε_t"
    else:
        ecuacion += "ε_t"

    return ecuacion

def mostrar_parametros_tabla(modelo, orden, orden_seas, aic):
    """Muestra los parámetros en formato de tabla"""
    params = modelo.params
    p, d, q = orden
    P, D, Q, m = orden_seas

    print("\n" + "=" * 60)
    print("PARÁMETROS DEL MODELO SARIMA")
    print("=" * 60)

    parametros_lista = []

    # Parámetros AR
    for i in range(1, p + 1):
        key = f"ar.L{i}"
        if key in params:
            parametros_lista.append((f"φ_{i}", params[key], modelo.bse.get(key, "N/A")))

    # Parámetros MA
    for i in range(1, q + 1):
        key = f"ma.L{i}"
        if key in params:
            parametros_lista.append((f"θ_{i}", params[key], modelo.bse.get(key, "N/A")))

    # Parámetros SAR
    for i in range(1, P + 1):
        key = f"ar.S.L{m*i}"
        if key in params:
            parametros_lista.append((f"Φ_{i}", params[key], modelo.bse.get(key, "N/A")))

    # Parámetros SMA
    for i in range(1, Q + 1):
        key = f"ma.S.L{m*i}"
        if key in params:
            parametros_lista.append((f"Θ_{i}", params[key], modelo.bse.get(key, "N/A")))

    # Constante
    if "intercept" in params:
        parametros_lista.append(
            ("intercept", params["intercept"], modelo.bse.get("intercept", "N/A"))
        )
    elif "const" in params:
        parametros_lista.append(
            ("const", params["const"], modelo.bse.get("const", "N/A"))
        )

    # Mostrar tabla
    print(f"\nOrden: SARIMA{orden}{orden_seas}")
    print(f"AIC: {aic:.2f}")
    print("\n" + "-" * 60)
    print(f"{'Parámetro':<15} {'Valor':<15} {'Error estándar':<15}")
    print("-" * 60)

    for nombre, valor, error in parametros_lista:
        if isinstance(error, (int, float)):
            print(f"{nombre:<15} {valor:<15.4f} {error:<15.4f}")
        else:
            print(f"{nombre:<15} {valor:<15.4f} {str(error):<15}")

    print("-" * 60)

# ======================================================
# 5. FUNCIÓN PARA EXPORTAR PRONÓSTICOS A JSON
# ======================================================
def exportar_pronosticos_json(modelo, serie, pasos=72, var_name=""):
    """Exporta pronósticos a formato JSON para el dashboard"""
    pred = modelo.get_forecast(steps=pasos)
    media = pred.predicted_mean
    conf_80 = pred.conf_int(alpha=0.20)
    conf_95 = pred.conf_int(alpha=0.05)

    # Limitar historial a las últimas 700 observaciones
    historico = []
    for fecha, valor in serie.tail(700).items():
        historico.append(
            {
                "fecha": fecha.strftime("%Y-%m-%d %H:%M:%S"),
                "valor": float(valor) if not pd.isna(valor) else None,
            }
        )

    pronosticos = []
    for i in range(len(media)):
        fecha_str = media.index[i].strftime("%Y-%m-%d %H:%M:%S")
        pronosticos.append(
            {
                "fecha": fecha_str,
                "pronostico": float(media.iloc[i]),
                "confianza_80_min": float(conf_80.iloc[i, 0]),
                "confianza_80_max": float(conf_80.iloc[i, 1]),
                "confianza_95_min": float(conf_95.iloc[i, 0]),
                "confianza_95_max": float(conf_95.iloc[i, 1]),
            }
        )

    # Definir límites permitidos
    limites = {
        "Temperature": None,
        "Humidity": None,
        "PM 2.5": 37,
        "PM 10": 75,
        "Radiacion Solar": None,
    }

    datos_json = {
        "variable": var_name,
        "fecha_generacion": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modelo": f"SARIMA{modelo.specification.order}{modelo.specification.seasonal_order}",
        "aic": float(modelo.aic),
        "observaciones_historicas": len(serie),
        "horas_pronostico": pasos,
        "limite_permitido": limites.get(var_name),
        "historico": historico,
        "pronosticos": pronosticos,
    }

    return datos_json

# ======================================================
# 6. FUNCIÓN PARA SUBIR A GITHUB
# ======================================================
def subir_a_github(nombre_archivo, contenido_json, token):
    """Sube archivos al repositorio de GitHub"""
    if not token or token == "":
        print(f"  ⚠️  No hay token de GitHub, guardando solo localmente")
        return False
    
    url = f"https://api.github.com/repos/majito0703/measure_data_logger/contents/pronosticos/{nombre_archivo}"
    
    contenido_str = json.dumps(contenido_json, indent=2, ensure_ascii=False)
    contenido_base64 = base64.b64encode(contenido_str.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Intentar obtener SHA si el archivo ya existe
    sha = None
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            sha = response.json().get("sha")
    except:
        pass
    
    data = {
        "message": f"🤖 Actualización automática: {nombre_archivo}",
        "content": contenido_base64,
        "branch": "main",
    }
    
    if sha:
        data["sha"] = sha
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=30)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"  ❌ Error {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  ❌ Error de conexión: {e}")
        return False

# ======================================================
# 7. FUNCIÓN PRINCIPAL
# ======================================================
def main():
    """Función principal del script"""
    print("\n📊 PROCESANDO DATOS...")
    
    # 1. Cargar datos
    df0 = cargar_datos_google_sheets()
    
    # 2. Procesar fechas
    df1 = parse_datetime_index(df0, format="%d/%m/%Y %H:%M:%S")
    df1 = df1.resample("1H").mean()
    
    # 3. Imputar valores faltantes
    df2 = df1.copy()
    vars_to_impute = ["Temperature", "Humidity", "PM 10", "PM 2.5", "Radiacion Solar"]
    
    for var in vars_to_impute:
        means = df2.groupby(df2.index.time)[var].transform("mean")
        df2[var] = df2[var].fillna(means)
    
    # 4. Eliminar últimos 2 días para evitar datos incompletos
    df3 = df2.copy()
    last_dates = df3.index.normalize().unique()[-2:]
    df3 = df3[~df3.index.normalize().isin(last_dates)]
    df3 = df3.drop(columns=["PM 1"], errors='ignore')
    
    # 5. Resample a datos por hora
    df_hourly = df3.resample("H").mean().dropna()
    
    variables = ["Temperature", "Humidity", "PM 2.5", "PM 10", "Radiacion Solar"]
    
    # 6. Optimizar modelos SARIMA para cada variable
    print("\n🔍 OPTIMIZANDO MODELOS SARIMA...")
    resultados = {}
    
    for var in variables:
        print(f"\n{'='*60}")
        print(f"Variable: {var}")
        print(f"{'='*60}")
        
        serie = df_hourly[var]
        
        modelo, orden, orden_s, aic, parametros, summary = buscar_mejor_modelo(serie)
        
        print(f"Mejor modelo: SARIMA{orden}{orden_s}")
        print(f"AIC = {aic:.2f}")
        
        # Mostrar ecuación
        ecuacion = obtener_ecuacion_sarima(modelo, orden, orden_s)
        print(f"\nEcuación matemática:\n{ecuacion}")
        
        # Mostrar parámetros
        mostrar_parametros_tabla(modelo, orden, orden_s, aic)
        
        # Guardar resultados
        resultados[var] = modelo
        
        print(f"✅ Modelo para {var} optimizado exitosamente")
    
    # 7. Crear carpeta para pronósticos
    os.makedirs("pronosticos", exist_ok=True)
    
    # 8. Obtener token de GitHub (de variable de entorno)
    token_github = os.environ.get("GH_TOKEN", "")
    if not token_github:
        print("\n⚠️  ADVERTENCIA: No se encontró GH_TOKEN en variables de entorno")
        print("   Los archivos se guardarán solo localmente")
    
    # 9. Exportar pronósticos a JSON
    print(f"\n{'='*60}")
    print("EXPORTANDO PRONÓSTICOS A JSON")
    print(f"{'='*60}")
    
    # Nombres de archivos
    nombres = {
        "Temperature": "pronostico_Temperature.json",
        "Humidity": "pronostico_Humidity.json",
        "PM 2.5": "pronostico_PM_2_5.json",
        "PM 10": "pronostico_PM_10.json",
        "Radiacion Solar": "pronostico_radiacion.json",
    }
    
    archivos_subidos = []
    
    for var in variables:
        print(f"\n📊 {var}:")
        
        # Generar JSON
        datos = exportar_pronosticos_json(
            modelo=resultados[var], 
            serie=df_hourly[var], 
            pasos=72, 
            var_name=var
        )
        
        # Nombre del archivo
        nombre_archivo = nombres.get(
            var, f"pronostico_{var.replace(' ', '_').replace('.', '_')}.json"
        )
        
        # Guardar localmente
        ruta_local = f"pronosticos/{nombre_archivo}"
        with open(ruta_local, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Guardado localmente: {ruta_local}")
        
        # Subir a GitHub
        if token_github:
            if subir_a_github(nombre_archivo, datos, token_github):
                archivos_subidos.append(nombre_archivo)
                print(f"  ✅ Subido a GitHub")
            else:
                print(f"  ❌ Error al subir a GitHub")
        
        # Información básica
        print(f"  📅 Pronóstico: {datos['pronosticos'][0]['fecha']} → {datos['pronosticos'][-1]['fecha']}")
    
    # 10. Crear y subir archivo índice
    print(f"\n📁 CREANDO ARCHIVO ÍNDICE...")
    
    index_data = {
        "variables": variables,
        "ultima_actualizacion": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "archivos": {
            var: nombres.get(
                var, f"pronostico_{var.replace(' ', '_').replace('.', '_')}.json"
            )
            for var in variables
        },
        "total_archivos": len(variables),
    }
    
    # Guardar índice localmente
    with open("pronosticos/index.json", "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    print("✓ index.json creado localmente")
    
    # Subir índice a GitHub
    if token_github:
        if subir_a_github("index.json", index_data, token_github):
            archivos_subidos.append("index.json")
            print("✅ Índice subido a GitHub")
    
    # 11. Resumen final
    print(f"\n{'='*60}")
    print("RESUMEN FINAL")
    print(f"{'='*60}")
    
    print(f"\n📁 Archivos generados en carpeta 'pronosticos/':")
    for var in variables:
        nombre = nombres.get(
            var, f"pronostico_{var.replace(' ', '_').replace('.', '_')}.json"
        )
        print(f"  • {nombre}")
    
    if archivos_subidos:
        print(f"\n✅ Subidos a GitHub ({len(archivos_subidos)} archivos)")
    else:
        print(f"\n⚠️  Los archivos NO se subieron a GitHub")
        print(f"   (Solo guardados localmente)")
    
    print(f"\n📊 Variables procesadas: {len(variables)}")
    print(f"⏰ Hora de ejecución: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 Repositorio: https://github.com/majito0703/measure_data_logger")
    print(f"{'='*60}")
    
    return 0

# ======================================================
# 8. EJECUCIÓN PRINCIPAL
# ======================================================
if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
