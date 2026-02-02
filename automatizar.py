# -*- coding: utf-8 -*-
"""Script para automatizar pronósticos"""

# 1. Ejecutar tu modelo SARIMA
!python modelo_sarima.py

# 2. Mover las gráficas a una carpeta específica
import shutil
import os
from datetime import datetime

# Crear carpeta con fecha actual
fecha = datetime.now().strftime('%Y-%m-%d_%H')
carpeta_destino = f'/content/pronosticos_{fecha}'
os.makedirs(carpeta_destino, exist_ok=True)

# Mover archivos PNG
for archivo in os.listdir('/content'):
    if archivo.endswith('.png') and 'pronostico' in archivo:
        shutil.move(f'/content/{archivo}', f'{carpeta_destino}/{archivo}')

print(f"Gráficas guardadas en: {carpeta_destino}")
