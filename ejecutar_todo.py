# ejecutar_todo.py
import os
import time

print("=" * 50)
print("EJECUTANDO PROCESO COMPLETO")
print("=" * 50)

# Paso 1: Ejecutar el modelo SARIMA
print("\n📊 Paso 1: Generando pronósticos SARIMA...")
os.system("python modelo_sarima.py")
time.sleep(2)

# Paso 2: Subir a GitHub
print("\n🚀 Paso 2: Subiendo a GitHub...")
os.system("python auto_git.py")

print("\n" + "=" * 50)
print("¡PROCESO COMPLETADO! ✅")
print("=" * 50)
print("\nTu dashboard está actualizado en:")
print("👉 https://majito0703.github.io/measure_data_logger/")
