"""
Script de Prueba y Demostración del Sistema de Biblioteca
Ejecutar para probar todas las funcionalidades sin interfaz gráfica

Uso: python test_biblioteca.py
"""

from biblioteca import Biblioteca
from tads import EstadoLibro, EstadoPrestamo
from datetime import datetime


def linea_separadora(titulo=""):
    """Imprime una línea separadora con título opcional"""
    if titulo:
        print(f"\n{'=' * 60}")
        print(f"  {titulo}")
        print(f"{'=' * 60}\n")
    else:
        print("-" * 60)


def prueba_registrar_libros(bib):
    """Prueba registro de libros"""
    linea_separadora("PRUEBA 1: Registro de Libros")
    
    libros = [
        ("L001", "Cien Años de Soledad", "Gabriel García Márquez", 1967, "Ficción", 1),
        ("L002", "Don Quijote", "Miguel de Cervantes", 1605, "Clásico", 1),
        ("L003", "1984", "George Orwell", 1949, "Distopía", 1),
        ("L004", "Orgullo y Prejuicio", "Jane Austen", 1813, "Romance", 1),
        ("L005", "Python Avanzado", "David Beazley", 2013, "Técnico", 1),
    ]
    
    print("Registrando 5 libros...\n")
    for codigo, titulo, autor, anio, categoria, stock in libros:
        exito, mensaje = bib.registrar_libro(codigo, titulo, autor, anio, categoria, stock)
        print(f"  {codigo}: {titulo}")
        print(f"           Autor: {autor} ({anio}) - {categoria} - Stock: {stock}")
        print(f"           ✓ {mensaje}\n")


def prueba_registrar_usuarios(bib):
    """Prueba registro de usuarios"""
    linea_separadora("PRUEBA 2: Registro de Usuarios")
    
    usuarios = [
        ("U001", "Juan Pérez", "juan@email.com", "50255001"),
        ("U002", "María García", "maria@email.com", "50255002"),
        ("U003", "Carlos López", "carlos@email.com", "50255003"),
        ("U004", "Ana Martínez", "ana@email.com", "50255004"),
    ]
    
    print("Registrando 4 usuarios...\n")
    for id_usuario, nombre, email, telefono in usuarios:
        exito, mensaje = bib.registrar_usuario(id_usuario, nombre, email, telefono)
        print(f"  {id_usuario}: {nombre}")
        print(f"           Email: {email}")
        print(f"           ✓ {mensaje}\n")


def prueba_busquedas(bib):
    """Prueba búsquedas eficientes"""
    linea_separadora("PRUEBA 3: Búsquedas (Análisis de Complejidad)")
    
    print("Búsqueda por Código - O(log n):")
    libro = bib.buscar_por_codigo("L002")
    if libro:
        print(f"  ✓ Encontrado: {libro.titulo} por {libro.autor}")
    
    print("\nBúsqueda por Título - O(log n):")
    libro = bib.buscar_por_titulo("1984")
    if libro:
        print(f"  ✓ Encontrado: {libro.titulo} ({libro.anio_publicacion})")
    
    print("\nBúsqueda por Autor - O(log n):")
    libro = bib.buscar_por_autor("George Orwell")
    if libro:
        print(f"  ✓ Encontrado: {libro.titulo}")
    
    print("\nBúsqueda por Categoría - O(n):")
    libros = bib.buscar_por_categoria("Clásico")
    print(f"  ✓ Encontrados {len(libros)} libros de categoría 'Clásico':")
    for libro in libros:
        print(f"     - {libro.titulo} ({libro.autor})")
    
    print("\nBúsqueda Similar - O(n):")
    libros = bib.buscar_similares("Orwell")
    print(f"  ✓ Encontrados {len(libros)} libros con 'Orwell':")
    for libro in libros:
        print(f"     - {libro.titulo}")
    
    print("\nBúsqueda por Rango - O(log n + k):")
    libros = bib.buscar_por_rango_codigo("L001", "L003")
    print(f"  ✓ Encontrados {len(libros)} libros entre L001 y L003:")
    for libro in libros:
        print(f"     - {libro.codigo}: {libro.titulo}")


def prueba_prestamos(bib):
    """Prueba sistema de préstamos"""
    linea_separadora("PRUEBA 4: Préstamos y Devoluciones")
    
    print("Realizando 3 préstamos...\n")
    prestamos_realizados = []
    
    prestamos_datos = [
        ("L001", "U001"),
        ("L002", "U002"),
        ("L003", "U003"),
    ]
    
    for codigo_libro, id_usuario in prestamos_datos:
        libro = bib.obtener_libro(codigo_libro)
        usuario = bib.obtener_usuario(id_usuario)
        
        exito, mensaje = bib.realizar_prestamo(codigo_libro, id_usuario)
        print(f"  Préstamo: {libro.titulo} → {usuario.nombre}")
        print(f"  {mensaje}")
        
        if exito:
            prestamo = bib.obtener_prestamos_activos(id_usuario)[0]
            prestamos_realizados.append(prestamo.id_prestamo)
            print(f"  Vencimiento: {prestamo.fecha_devolucion_esperada.strftime('%Y-%m-%d')}\n")
    
    print("\nDevolviendo libros...\n")
    for id_prestamo in prestamos_realizados[:2]:
        prestamo = bib.obtener_prestamo(id_prestamo)
        libro = bib.obtener_libro(prestamo.codigo_libro)
        
        exito, mensaje = bib.devolver_libro(id_prestamo)
        print(f"  Devolución: {libro.titulo}")
        print(f"  {mensaje}\n")


def prueba_lista_espera(bib):
    """Prueba lista de espera"""
    linea_separadora("PRUEBA 5: Lista de Espera (Cola - FIFO)")
    
    # Buscar un libro prestado
    prestamos_activos = bib.obtener_prestamos_activos()
    if prestamos_activos:
        prestamo = prestamos_activos[0]
        codigo_libro = prestamo.codigo_libro
        
        print(f"Agregando usuarios a lista de espera para: {bib.obtener_libro(codigo_libro).titulo}\n")
        
        usuarios_espera = ["U002", "U004"]
        for id_usuario in usuarios_espera:
            usuario = bib.obtener_usuario(id_usuario)
            exito, mensaje = bib.agregar_a_espera(codigo_libro, id_usuario)
            if exito:
                print(f"  {usuario.nombre}: {mensaje}")
            else:
                print(f"  {usuario.nombre}: Error - {mensaje}")
        
        print("\nCola de espera actual (FIFO):")
        cola = bib.obtener_cola_espera(codigo_libro)
        for i, id_usuario in enumerate(cola, 1):
            usuario = bib.obtener_usuario(id_usuario)
            print(f"  {i}. {usuario.nombre} (ID: {id_usuario})")


def prueba_historial(bib):
    """Prueba historial de operaciones con Pila"""
    linea_separadora("PRUEBA 6: Historial de Operaciones (Pila - LIFO)")
    
    print("Últimas 10 operaciones realizadas:\n")
    historial = bib.obtener_historial(10)
    
    for i, accion in enumerate(historial, 1):
        print(f"  {i}. [{accion.timestamp.strftime('%H:%M:%S')}] {accion.tipo}")
        print(f"     {accion.descripcion}")
        print()


def prueba_estadisticas(bib):
    """Prueba estadísticas del sistema"""
    linea_separadora("PRUEBA 7: Estadísticas del Sistema")
    
    stats = bib.obtener_estadisticas()
    
    print("Resumen General:")
    print(f"  Total de Libros: {stats['total_libros']}")
    print(f"  Usuarios Registrados: {stats['total_usuarios']}")
    print(f"  Libros Disponibles: {stats['libros_disponibles']}")
    print(f"  Libros Prestados: {stats['libros_prestados']}")
    print(f"  Préstamos Activos: {stats['prestamos_activos']}")
    print(f"  Préstamos Retrasados: {stats['prestamos_retrasados']}")
    print(f"  Total de Préstamos (histórico): {stats['total_prestamos_historicos']}")
    print(f"  Usuarios Morosos: {stats['usuarios_morosos']}")
    
    print("\n\nLibros Más Prestados:")
    libros_top = bib.obtener_libros_mas_prestados(5)
    for i, (libro, cantidad) in enumerate(libros_top, 1):
        print(f"  {i}. {libro.titulo} - {cantidad} préstamos")


def prueba_analisis_complejidad(bib):
    """Muestra análisis de complejidad"""
    linea_separadora("PRUEBA 8: Análisis de Complejidad Temporal")
    
    analisis = bib.obtener_analisis_complejidad()
    
    for operacion, info in analisis.items():
        print(f"\n{operacion.upper()}")
        print(f"  Caso Promedio: {info['promedio']}")
        print(f"  Peor Caso: {info['peor_caso']}")
        print(f"  Descripción: {info['descripcion']}")


def prueba_estructuras_datos(bib):
    """Muestra información sobre las estructuras de datos utilizadas"""
    linea_separadora("PRUEBA 9: Información de Estructuras de Datos")
    
    print("Estructuras utilizadas en el sistema:\n")
    
    print("1. ÁRBOL BINARIO DE BÚSQUEDA (BST)")
    print("   Uso: Indexación de libros (código, título, autor)")
    print("   O(log n) para búsqueda en caso promedio")
    print(f"   - Libros indexados: {bib.indice_libros_codigo.tamano()}")
    print(f"   - Altura del árbol: {bib.indice_libros_codigo.altura_arbol()}")
    
    print("\n2. PILA (STACK)")
    print("   Uso: Historial de operaciones")
    print("   LIFO - Last In, First Out")
    print(f"   - Operaciones almacenadas: {bib.historial.tamano()}")
    
    print("\n3. COLA (QUEUE)")
    print("   Uso: Listas de espera para libros")
    print("   FIFO - First In, First Out")
    colas_activas = sum(1 for cola in bib.colas_espera.values() 
                        if not cola.esta_vacia())
    usuarios_en_espera = sum(cola.tamano() for cola in bib.colas_espera.values())
    print(f"   - Colas activas: {colas_activas}")
    print(f"   - Usuarios en espera: {usuarios_en_espera}")
    
    print("\n4. DICCIONARIO (Hash Table)")
    print("   Uso: Almacenamiento primario de libros y usuarios")
    print("   O(1) para búsqueda")
    print(f"   - Libros: {len(bib.libros)}")
    print(f"   - Usuarios: {len(bib.usuarios)}")
    print(f"   - Préstamos: {len(bib.prestamos)}")


def prueba_casos_uso_reales(bib):
    """Simula casos de uso reales"""
    linea_separadora("PRUEBA 10: Casos de Uso Reales")
    
    print("Escenario: Usuario buscando libros para leer\n")
    
    # Usuario busca libros de ficción
    print("1. Búsqueda de libros de Ficción:")
    libros_ficcion = bib.buscar_por_categoria("Ficción")
    print(f"   Encontrados: {len(libros_ficcion)}")
    for libro in libros_ficcion:
        disponibilidad = "✓ Disponible" if libro.estado == EstadoLibro.DISPONIBLE else "✗ No disponible"
        print(f"   - {libro.titulo} {disponibilidad}")
    
    # Usuario busca libros de un autor específico
    print("\n2. Búsqueda de libros de Cervantes:")
    libro = bib.buscar_por_autor("Miguel de Cervantes")
    if libro:
        print(f"   - {libro.titulo} ({libro.anio_publicacion})")
    
    # Sistema recomienda libros
    print("\n3. Recomendaciones personalizadas:")
    usuario = bib.obtener_usuario("U001")
    print(f"   Para: {usuario.nombre}")
    recomendaciones = bib.recomendar_libros("U001", 3)
    if recomendaciones:
        for libro in recomendaciones:
            print(f"   - {libro.titulo}")
    else:
        print("   - No hay recomendaciones disponibles")


def main():
    """Función principal"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  SISTEMA DE GESTIÓN DE BIBLIOTECA - PRUEBAS".center(58) + "║")
    print("║" + "  Demostración de Estructuras de Datos".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝\n")
    
    # Crear instancia de biblioteca
    bib = Biblioteca()
    
    # Ejecutar todas las pruebas
    try:
        prueba_registrar_libros(bib)
        prueba_registrar_usuarios(bib)
        prueba_busquedas(bib)
        prueba_prestamos(bib)
        prueba_lista_espera(bib)
        prueba_historial(bib)
        prueba_estadisticas(bib)
        prueba_analisis_complejidad(bib)
        prueba_estructuras_datos(bib)
        prueba_casos_uso_reales(bib)
        
        # Resumen final
        linea_separadora("RESUMEN FINAL")
        print("✓ Todas las pruebas completadas exitosamente\n")
        
        print("Características demostradas:")
        print("  ✓ Tipos Abstractos de Datos (TAD)")
        print("  ✓ Pila (Stack) para historial")
        print("  ✓ Cola (Queue) para listas de espera")
        print("  ✓ Árbol Binario de Búsqueda para indexación")
        print("  ✓ Búsquedas eficientes O(log n)")
        print("  ✓ Análisis de complejidad temporal")
        print("  ✓ Gestión completa de biblioteca")
        print("\n" + "=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()