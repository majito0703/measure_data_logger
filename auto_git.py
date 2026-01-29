# auto_git.py
import os
import subprocess
from datetime import datetime

def subir_a_github():
    """Esta función sube los archivos a GitHub automáticamente"""
    
    print("🚀 Iniciando subida a GitHub...")
    
    # Paso 1: Verificar si estamos en un repositorio git
    if not os.path.exists(".git"):
        print("❌ No es un repositorio git. Configurando...")
        subprocess.run(["git", "init"])
        subprocess.run(["git", "branch", "-M", "main"])
        subprocess.run(["git", "remote", "add", "origin", 
                       "https://github.com/majito0703/measure_data_logger.git"])
    
    # Paso 2: Mover archivos JSON a la carpeta correcta
    if os.path.exists("pronosticos_json"):
        # Crear carpeta 'pronosticos' si no existe
        if not os.path.exists("pronosticos"):
            os.makedirs("pronosticos")
        
        # Copiar todos los archivos JSON
        for archivo in os.listdir("pronosticos_json"):
            if archivo.endswith(".json"):
                origen = f"pronosticos_json/{archivo}"
                destino = f"pronosticos/{archivo}"
                
                # Copiar archivo
                with open(origen, 'r', encoding='utf-8') as f_origen:
                    contenido = f_origen.read()
                
                with open(destino, 'w', encoding='utf-8') as f_destino:
                    f_destino.write(contenido)
                
                print(f"📄 Copiado: {archivo}")
    
    # Paso 3: Hacer commit y push
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    mensaje = f"Actualización automática: {fecha_actual}"
    
    try:
        # Agregar todos los cambios
        subprocess.run(["git", "add", "."])
        
        # Hacer commit
        subprocess.run(["git", "commit", "-m", mensaje])
        
        # Subir a GitHub
        subprocess.run(["git", "push", "origin", "main"])
        
        print("✅ ¡Todo subido a GitHub exitosamente!")
        print(f"📅 Hora: {fecha_actual}")
        print("🔗 Tu dashboard: https://majito0703.github.io/measure_data_logger/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("⚠️  Intenta ejecutar estos comandos manualmente:")
        print("   git add .")
        print(f"   git commit -m '{mensaje}'")
        print("   git push origin main")

if __name__ == "__main__":
    subir_a_github()
