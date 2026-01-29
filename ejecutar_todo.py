# ejecutar_todo.py
import os

print("🤖 EJECUTANDO PROCESO COMPLETO")
print("=" * 40)

print("\n1. 📊 Generando pronósticos SARIMA...")
os.system("python modelo_sarima.py")

print("\n2. 🚀 Subiendo a GitHub...")
os.system("python auto_git.py")

print("\n" + "=" * 40)
print("✅ ¡PROCESO COMPLETADO!")
print("=" * 40)
print("\n🌐 Tu dashboard está en:")
print("👉 https://majito0703.github.io/measure_data_logger/")
