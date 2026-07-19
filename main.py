"""
Sistema de Gestión de Biblioteca - Archivo Principal
Ejecutar este archivo para iniciar la aplicación con interfaz gráfica

Requisitos:
- Python 3.7+
- tkinter (incluido en la mayoría de distribuciones de Python)

Estructura del Proyecto:
- tads.py: Tipos Abstractos de Datos (Libro, Usuario, Préstamo, Acción)
- estructuras.py: Estructuras de Datos (Pila, Cola, Lista Enlazada, Árbol BST)
- biblioteca.py: Lógica principal del Sistema
- gui.py: Interfaz gráfica con tkinter
- main.py: Punto de entrada de la aplicación
"""

import sys
import os

# Asegurar que los módulos se puedan importar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import tkinter as tk
    from gui import InterfazBiblioteca
    
    def main():
        """Inicia la aplicación"""
        print("=" * 60)
        print("Sistema de Gestión de Biblioteca")
        print("=" * 60)
        print("\nIniciando interfaz gráfica...")
        print("Cargando datos de ejemplo...")
        
        ventana = tk.Tk()
        app = InterfazBiblioteca(ventana)
        
        print("\n✓ Interfaz cargada correctamente")
        print("✓ Datos de ejemplo cargados")
        print("\nVentana principal abierta...")
        print("-" * 60)
        
        ventana.mainloop()
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error de importación: {e}")
    print("\nAsegúrese de que todos los archivos estén en el mismo directorio:")
    print("  - tads.py")
    print("  - estructuras.py")
    print("  - biblioteca.py")
    print("  - gui.py")
    print("  - main.py")
    sys.exit(1)
except Exception as e:
    print(f"Error inesperado: {e}")
    sys.exit(1)
