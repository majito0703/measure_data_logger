# auto_git.py - VERSIÓN SUPER SIMPLE
import os
import subprocess

print("🚀 Subiendo pronósticos a GitHub...")

# 1. Agregar archivos a Git
subprocess.run(["git", "add", "pronosticos/"])

# 2. Hacer commit
subprocess.run(["git", "commit", "-m", "Actualización automática de pronósticos"])

# 3. Subir a GitHub
subprocess.run(["git", "push"])

print("✅ ¡Todo subido a GitHub!")
print("🌐 Tu dashboard se actualizará en:")
print("   https://majito0703.github.io/measure_data_logger/")
