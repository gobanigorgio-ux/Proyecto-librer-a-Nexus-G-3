"""
Sistema de Gestión de Biblioteca
Integra todas las estructuras de datos para gestionar libros, usuarios y préstamos
"""

import json
import os
import re
from datetime import datetime
from tads import Libro, Usuario, Prestamo, Accion, EstadoLibro, EstadoPrestamo, EstadoUsuario
from estructuras import Pila, Cola, ListaEnlazada, ArbolBinarioBusqueda


def _validar_telefono(telefono):
    """Un teléfono válido debe tener exactamente 8 dígitos numéricos."""
    tel = str(telefono).strip()
    return tel.isdigit() and len(tel) == 8


def _validar_email(email):
    """Un email válido debe tener la forma usuario@dominio.algo (ej: @gmail.com)."""
    em = str(email).strip().lower()
    patron = r'^[^@\s]+@[^@\s]+\.[a-z]{2,}$'
    return re.match(patron, em) is not None


class Biblioteca:
    """
    Sistema principal de gestión de biblioteca
    
    Estructuras utilizadas:
    - Diccionario: para acceso O(1) a libros y usuarios
    - ArbolBST: para búsqueda eficiente por código, título y autor
    - Cola: para lista de espera de préstamos
    - Pila: para historial de operaciones
    """
    
    def __init__(self, archivo_datos=None, cargar_datos=True):
        self.archivo_datos = archivo_datos or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "datos_biblioteca.json"
        )
        self._cargando = False
        self._inicializar_estructuras()
        if cargar_datos:
            self.cargar_desde_json()

    def _inicializar_estructuras(self):
        # Almacenamiento principal
        self.libros = {}  # {codigo: Libro}
        self.usuarios = {}  # {id_usuario: Usuario}
        self.prestamos = {}  # {id_prestamo: Prestamo}
        self.catalogo_enlazado = ListaEnlazada()
        
        # Índices con árboles BST para búsqueda eficiente
        self.indice_libros_codigo = ArbolBinarioBusqueda(lambda x: x.codigo)
        self.indice_libros_titulo = ArbolBinarioBusqueda(lambda x: x.titulo.lower())
        self.indice_libros_autor = ArbolBinarioBusqueda(lambda x: x.autor.lower())
        
        # Colas de espera para libros (por código de libro)
        self.colas_espera = {}  # {codigo_libro: Cola}
        
        # Historial de operaciones
        self.historial = Pila()
        
        # Estadísticas
        self.contador_prestamos = {}  # {codigo_libro: cantidad}

    def _reconstruir_indices(self):
        """Reconstruye lista enlazada e indices BST desde los libros cargados."""
        self.catalogo_enlazado = ListaEnlazada()
        self.indice_libros_codigo = ArbolBinarioBusqueda(lambda x: x.codigo)
        self.indice_libros_titulo = ArbolBinarioBusqueda(lambda x: x.titulo.lower())
        self.indice_libros_autor = ArbolBinarioBusqueda(lambda x: x.autor.lower())
        for libro in self.libros.values():
            self.catalogo_enlazado.insertar_final(libro)
            self.indice_libros_codigo.insertar(libro)
            self.indice_libros_titulo.insertar(libro)
            self.indice_libros_autor.insertar(libro)

    def hay_datos_guardados(self):
        """Indica si existe un archivo JSON persistente con informacion."""
        return os.path.exists(self.archivo_datos) and os.path.getsize(self.archivo_datos) > 0

    def guardar_en_json(self):
        """Guarda todo el estado del sistema en un archivo JSON."""
        if self._cargando:
            return
        datos = {
            'libros': [libro.to_dict() for libro in self.libros.values()],
            'usuarios': [usuario.to_dict() for usuario in self.usuarios.values()],
            'prestamos': [prestamo.to_dict() for prestamo in self.prestamos.values()],
            'colas_espera': {
                codigo: list(cola)
                for codigo, cola in self.colas_espera.items()
            },
            'historial': [accion.to_dict() for accion in self.historial],
            'contador_prestamos': self.contador_prestamos
        }
        with open(self.archivo_datos, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)

    def cargar_desde_json(self):
        """Carga el estado del sistema desde el archivo JSON si existe."""
        if not self.hay_datos_guardados():
            return False
        self._cargando = True
        try:
            with open(self.archivo_datos, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)

            Prestamo.contador = 0
            self._inicializar_estructuras()
            self.libros = {
                libro.codigo: libro
                for libro in (Libro.from_dict(item) for item in datos.get('libros', []))
            }
            self.usuarios = {
                usuario.id_usuario: usuario
                for usuario in (Usuario.from_dict(item) for item in datos.get('usuarios', []))
            }
            self.prestamos = {
                prestamo.id_prestamo: prestamo
                for prestamo in (Prestamo.from_dict(item) for item in datos.get('prestamos', []))
            }
            self.colas_espera = {}
            for codigo, usuarios in datos.get('colas_espera', {}).items():
                cola = Cola()
                for id_usuario in usuarios:
                    cola.enqueue(id_usuario)
                self.colas_espera[codigo] = cola

            self.historial = Pila()
            for accion in reversed(datos.get('historial', [])):
                self.historial.push(Accion.from_dict(accion))

            self.contador_prestamos = datos.get('contador_prestamos', {})
            for codigo, libro in self.libros.items():
                self.contador_prestamos.setdefault(codigo, libro.cantidad_prestamos)

            self._reconstruir_indices()
            return True
        except (OSError, json.JSONDecodeError, KeyError, ValueError) as error:
            print(f"No se pudo cargar el archivo de datos: {error}")
            self._inicializar_estructuras()
            return False
        finally:
            self._cargando = False
    
    # ==================== GESTIÓN DE LIBROS ====================
    
    def registrar_libro(self, codigo, titulo, autor, anio_publicacion, categoria, stock=1):
        """Registra un nuevo libro en la biblioteca"""
        if codigo in self.libros:
            return False, "El libro ya existe"
        
        libro = Libro(codigo, titulo, autor, anio_publicacion, categoria, stock)
        self.libros[codigo] = libro
        self.catalogo_enlazado.insertar_final(libro)
        
        # Insertar en índices
        self.indice_libros_codigo.insertar(libro)
        self.indice_libros_titulo.insertar(libro)
        self.indice_libros_autor.insertar(libro)
        
        # Inicializar contador
        self.contador_prestamos[codigo] = 0
        
        # Registrar acción
        accion = Accion("REGISTRO_LIBRO", f"Libro registrado: {titulo}", 
                       {'codigo': codigo, 'titulo': titulo})
        self.historial.push(accion)
        
        self.guardar_en_json()
        return True, "Libro registrado exitosamente"
    
    def obtener_libro(self, codigo):
        """Obtiene un libro por código"""
        return self.libros.get(codigo)
    
    def eliminar_libro(self, codigo):
        """Elimina un libro del sistema"""
        if codigo not in self.libros:
            return False, "El libro no existe"
        
        libro = self.libros[codigo]
        del self.libros[codigo]
        self.catalogo_enlazado.eliminar(libro)
        
        # Eliminar de índices
        self.indice_libros_codigo.eliminar(libro.codigo)
        self.indice_libros_titulo.eliminar(libro.titulo.lower())
        self.indice_libros_autor.eliminar(libro.autor.lower())
        self.contador_prestamos.pop(codigo, None)
        self.colas_espera.pop(codigo, None)
        
        # Registrar acción
        accion = Accion("ELIMINACION_LIBRO", f"Libro eliminado: {libro.titulo}",
                       {'codigo': codigo})
        self.historial.push(accion)
        
        self.guardar_en_json()
        return True, "Libro eliminado exitosamente"
    
    def listar_libros(self):
        """Retorna todos los libros"""
        return list(self.catalogo_enlazado)

    def recorrer_catalogo_enlazado(self):
        """Recorre la lista enlazada usada como catalogo dinamico."""
        return list(self.catalogo_enlazado)
    
    # ==================== BÚSQUEDA DE LIBROS ====================
    
    def buscar_por_codigo(self, codigo):
        """Búsqueda por código - O(log n)"""
        return self.indice_libros_codigo.buscar(codigo)
    
    def buscar_por_titulo(self, titulo):
        """Búsqueda por título - O(log n)"""
        return self.indice_libros_titulo.buscar(titulo.lower())
    
    def buscar_por_autor(self, autor):
        """Búsqueda exacta por autor"""
        return self.indice_libros_autor.buscar(autor.lower())
    
    def buscar_por_rango_codigo(self, codigo_min, codigo_max):
        """Búsqueda de libros en rango de códigos"""
        return self.indice_libros_codigo.buscar_rango(codigo_min, codigo_max)
    
    def buscar_similares(self, termino):
        """Busca libros con título o autor que contengan el término"""
        resultados = []
        termino_lower = termino.lower()
        
        for libro in self.libros.values():
            if (termino_lower in libro.titulo.lower() or 
                termino_lower in libro.autor.lower()):
                resultados.append(libro)
        
        return resultados
    
    def buscar_por_categoria(self, categoria):
        """Busca libros por categoría"""
        return [libro for libro in self.libros.values() 
                if libro.categoria == categoria]
    
    def obtener_libros_disponibles(self):
        """Obtiene todos los libros disponibles"""
        return [libro for libro in self.libros.values() 
                if libro.estado == EstadoLibro.DISPONIBLE]
    
    # ==================== GESTIÓN DE USUARIOS ====================
    
    def registrar_usuario(self, id_usuario, nombre, email, telefono):
        """Registra un nuevo usuario en la biblioteca"""
        if id_usuario in self.usuarios:
            return False, "El usuario ya existe"

        if not _validar_telefono(telefono):
            return False, "El teléfono debe tener exactamente 8 dígitos"

        if not _validar_email(email):
            return False, "El email debe incluir un dominio válido (ejemplo: usuario@gmail.com)"

        usuario = Usuario(id_usuario, nombre, email, telefono)
        self.usuarios[id_usuario] = usuario
        
        # Registrar acción
        accion = Accion("REGISTRO_USUARIO", f"Usuario registrado: {nombre}",
                       {'id_usuario': id_usuario, 'nombre': nombre})
        self.historial.push(accion)
        
        self.guardar_en_json()
        return True, "Usuario registrado exitosamente"
    
    def obtener_usuario(self, id_usuario):
        """Obtiene un usuario por ID"""
        return self.usuarios.get(id_usuario)
    
    def listar_usuarios(self):
        """Retorna todos los usuarios"""
        return list(self.usuarios.values())

    def eliminar_usuario(self, id_usuario):
        """Elimina un usuario del sistema (si no tiene libros activos o préstamos activos)."""
        usuario = self.obtener_usuario(id_usuario)
        if usuario is None:
            return False, "El usuario no existe"

        # No permitir eliminar si el usuario tiene préstamos activos o libros activos
        prestamos_activos = self.obtener_prestamos_activos(id_usuario)
        if prestamos_activos:
            return False, "No se puede eliminar: el usuario tiene préstamos activos"

        if getattr(usuario, "libros_activos", None):
            if len(usuario.libros_activos) > 0:
                return False, "No se puede eliminar: el usuario tiene libros activos"

        # Eliminar al usuario
        del self.usuarios[id_usuario]

        # Registrar acción e historial
        accion = Accion(
            "ELIMINACION_USUARIO",
            f"Usuario eliminado: {usuario.nombre}",
            {'id_usuario': id_usuario, 'nombre': usuario.nombre},
        )
        self.historial.push(accion)
        self.guardar_en_json()
        return True, "Usuario eliminado exitosamente"

    # ==================== ESTADO MOROSO ====================

    def actualizar_estado_moroso(self, id_usuario):
        """
        Revisa los préstamos activos de un usuario y actualiza su estado:
        - MOROSO si tiene al menos un préstamo retrasado (no devuelto a tiempo)
        - ACTIVO en caso contrario
        """
        usuario = self.obtener_usuario(id_usuario)
        if usuario is None:
            return

        tiene_retraso = any(
            prestamo.esta_retrasado()
            for prestamo in self.obtener_prestamos_activos(id_usuario)
        )

        nuevo_estado = EstadoUsuario.MOROSO if tiene_retraso else EstadoUsuario.ACTIVO
        if usuario.estado != nuevo_estado:
            usuario.estado = nuevo_estado
            accion = Accion(
                "CAMBIO_ESTADO_USUARIO",
                f"Usuario {usuario.nombre} marcado como {nuevo_estado.value}",
                {'id_usuario': id_usuario, 'estado': nuevo_estado.value}
            )
            self.historial.push(accion)

    def actualizar_morosos(self):
        """Recorre todos los usuarios y actualiza su estado moroso/activo."""
        for id_usuario in list(self.usuarios.keys()):
            self.actualizar_estado_moroso(id_usuario)
        self.guardar_en_json()

    def obtener_usuarios_morosos(self):
        """Retorna la lista de usuarios actualmente marcados como morosos"""
        return [u for u in self.usuarios.values() if u.es_moroso()]

    
    # ==================== GESTIÓN DE PRÉSTAMOS ====================
    
    def realizar_prestamo(self, codigo_libro, id_usuario):
        """
        Realiza un préstamo de un libro.
        Si hay stock disponible, se presta de inmediato.
        Si el stock es 0, el usuario se agrega automáticamente a la
        cola de espera del libro (FIFO: el primero en llegar es el
        primero en recibir el libro cuando se libere una copia).
        """
        # Validaciones
        libro = self.obtener_libro(codigo_libro)
        usuario = self.obtener_usuario(id_usuario)
        
        if not libro:
            return False, "Libro no encontrado"
        if not usuario:
            return False, "Usuario no encontrado"

        # Verifica si el usuario tiene préstamos retrasados antes de prestar
        self.actualizar_estado_moroso(id_usuario)
        if usuario.es_moroso():
            return False, (f"'{usuario.nombre}' está marcado como MOROSO "
                          f"(tiene préstamos retrasados sin devolver) y no puede "
                          f"realizar nuevos préstamos hasta regularizar su situación")

        if usuario.tiene_libro(codigo_libro):
            return False, f"El usuario ya tiene prestado '{libro.titulo}'"
        
        # Sin stock disponible: se encola automáticamente (FIFO)
        if libro.stock <= 0:
            if codigo_libro not in self.colas_espera:
                self.colas_espera[codigo_libro] = Cola()
            cola = self.colas_espera[codigo_libro]
            if id_usuario in list(cola):
                posicion = list(cola).index(id_usuario) + 1
                return False, f"El usuario ya está en la lista de espera (posición {posicion})"
            
            cola.enqueue(id_usuario)
            
            accion = Accion("USUARIO_EN_ESPERA",
                           f"Usuario {usuario.nombre} en espera de '{libro.titulo}' (sin stock)",
                           {'codigo_libro': codigo_libro, 'id_usuario': id_usuario})
            self.historial.push(accion)
            
            self.guardar_en_json()
            return True, (f"Sin stock disponible de '{libro.titulo}'. "
                          f"'{usuario.nombre}' fue agregado a la lista de espera "
                          f"(posición {cola.tamano()}).")
        
        # Hay stock: se presta de inmediato
        prestamo = Prestamo(codigo_libro, id_usuario)
        self.prestamos[prestamo.id_prestamo] = prestamo
        
        # Actualizar estados
        libro.stock -= 1
        libro.actualizar_estado()
        libro.cantidad_prestamos += 1
        self.contador_prestamos[codigo_libro] += 1
        usuario.agregar_libro(codigo_libro)
        
        # Registrar acción
        accion = Accion("PRESTAMO", 
                       f"Préstamo de '{libro.titulo}' a {usuario.nombre}",
                       {'id_prestamo': prestamo.id_prestamo, 
                        'codigo_libro': codigo_libro,
                        'id_usuario': id_usuario})
        self.historial.push(accion)
        
        self.guardar_en_json()
        return True, f"Préstamo #{prestamo.id_prestamo} realizado exitosamente"
    
    def devolver_libro(self, id_prestamo):
        """Registra la devolución de un libro"""
        prestamo = self.prestamos.get(id_prestamo)
        if not prestamo:
            return False, "Préstamo no encontrado"
        
        if prestamo.estado != EstadoPrestamo.ACTIVO:
            return False, f"El préstamo ya fue devuelto"
        
        # Procesar devolución
        prestamo.devolver()
        libro = self.obtener_libro(prestamo.codigo_libro)
        usuario = self.obtener_usuario(prestamo.id_usuario)
        
        # Actualizar estado del libro y del usuario
        usuario.devolver_libro(prestamo.codigo_libro)
        libro.stock += 1

        # Reevaluar si el usuario sigue teniendo préstamos retrasados
        self.actualizar_estado_moroso(prestamo.id_usuario)
        
        # Registrar acción de devolución
        estado = "a tiempo" if prestamo.estado == EstadoPrestamo.DEVUELTO else "retrasado"
        accion = Accion("DEVOLUCION", 
                       f"Devolución de '{libro.titulo}' ({estado})",
                       {'id_prestamo': id_prestamo,
                        'codigo_libro': prestamo.codigo_libro,
                        'estado': prestamo.estado.value})
        self.historial.push(accion)
        
        mensaje = f"Devolución registrada ({estado})"
        
        # Si hay alguien en la cola de espera (FIFO), se le presta
        # automáticamente el libro que acaba de quedar libre.
        if (prestamo.codigo_libro in self.colas_espera and 
            not self.colas_espera[prestamo.codigo_libro].esta_vacia()):
            
            siguiente_id = self.colas_espera[prestamo.codigo_libro].dequeue()
            siguiente_usuario = self.obtener_usuario(siguiente_id)
            
            if siguiente_usuario is not None:
                nuevo_prestamo = Prestamo(prestamo.codigo_libro, siguiente_id)
                self.prestamos[nuevo_prestamo.id_prestamo] = nuevo_prestamo
                
                libro.stock -= 1
                libro.cantidad_prestamos += 1
                self.contador_prestamos[prestamo.codigo_libro] += 1
                siguiente_usuario.agregar_libro(prestamo.codigo_libro)
                
                accion_asignacion = Accion(
                    "PRESTAMO_AUTOMATICO",
                    f"Libro '{libro.titulo}' asignado automáticamente a "
                    f"{siguiente_usuario.nombre} (primero en la lista de espera)",
                    {'id_prestamo': nuevo_prestamo.id_prestamo,
                     'codigo_libro': prestamo.codigo_libro,
                     'id_usuario': siguiente_id})
                self.historial.push(accion_asignacion)
                
                mensaje += (f". '{libro.titulo}' se asignó automáticamente a "
                           f"'{siguiente_usuario.nombre}', quien era el primero "
                           f"en la lista de espera (préstamo #{nuevo_prestamo.id_prestamo}).")
        
        libro.actualizar_estado()
        self.guardar_en_json()
        return True, mensaje
    
    def obtener_prestamo(self, id_prestamo):
        """Obtiene un préstamo por ID"""
        return self.prestamos.get(id_prestamo)
    
    def obtener_prestamos_activos(self, id_usuario=None):
        """Obtiene préstamos activos de un usuario o todos"""
        prestamos = []
        for prestamo in self.prestamos.values():
            if prestamo.estado == EstadoPrestamo.ACTIVO:
                if id_usuario is None or prestamo.id_usuario == id_usuario:
                    prestamos.append(prestamo)
        return prestamos
    
    def obtener_prestamos_retrasados(self):
        """Obtiene todos los préstamos retrasados"""
        retrasados = []
        for prestamo in self.prestamos.values():
            if prestamo.esta_retrasado():
                retrasados.append(prestamo)
        return retrasados
    
    # ==================== GESTIÓN DE LISTA DE ESPERA ====================
    
    def agregar_a_espera(self, codigo_libro, id_usuario):
        """Agrega un usuario a la cola de espera de un libro"""
        libro = self.obtener_libro(codigo_libro)
        usuario = self.obtener_usuario(id_usuario)
        
        if not libro:
            return False, "Libro no encontrado"
        if not usuario:
            return False, "Usuario no encontrado"
        if libro.stock > 0:
            return False, "El libro está disponible"
        
        # Crear cola si no existe
        if codigo_libro not in self.colas_espera:
            self.colas_espera[codigo_libro] = Cola()
        
        self.colas_espera[codigo_libro].enqueue(id_usuario)
        
        # Registrar acción
        accion = Accion("USUARIO_EN_ESPERA",
                       f"Usuario {usuario.nombre} en espera de '{libro.titulo}'",
                       {'codigo_libro': codigo_libro, 'id_usuario': id_usuario})
        self.historial.push(accion)
        
        self.guardar_en_json()
        return True, f"Usuario agregado a lista de espera (posición {self.colas_espera[codigo_libro].tamano()})"
    
    def obtener_cola_espera(self, codigo_libro):
        """Obtiene la cola de espera de un libro"""
        if codigo_libro in self.colas_espera:
            return list(self.colas_espera[codigo_libro])
        return []
    
    # ==================== HISTORIAL Y ANÁLISIS ====================
    
    def obtener_historial(self, cantidad=10):
        """Obtiene las últimas N acciones del historial"""
        resultado = []
        temp = []
        
        # Extraer de la pila sin modificarla
        while not self.historial.esta_vacia():
            accion = self.historial.pop()
            temp.append(accion)
            if len(resultado) < cantidad:
                resultado.append(accion)
        
        # Restaurar la pila
        for accion in temp:
            self.historial.push(accion)
        
        return resultado
    
    def obtener_libros_mas_prestados(self, cantidad=10):
        """Obtiene los libros más prestados"""
        libros_sorted = sorted(
            [(codigo, count) for codigo, count in self.contador_prestamos.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        resultado = []
        for codigo, count in libros_sorted[:cantidad]:
            libro = self.obtener_libro(codigo)
            if libro:
                resultado.append((libro, count))
        
        return resultado
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas generales del sistema"""
        prestamos_activos = self.obtener_prestamos_activos()
        prestamos_retrasados = self.obtener_prestamos_retrasados()
        
        return {
            'total_libros': len(self.libros),
            'total_usuarios': len(self.usuarios),
            'libros_disponibles': len(self.obtener_libros_disponibles()),
            'libros_prestados': len([l for l in self.libros.values() 
                                     if l.estado == EstadoLibro.PRESTADO]),
            'prestamos_activos': len(prestamos_activos),
            'prestamos_retrasados': len(prestamos_retrasados),
            'total_prestamos_historicos': len(self.prestamos),
            'usuarios_morosos': len(self.obtener_usuarios_morosos())
        }
    
    # ==================== RECOMENDACIONES ====================
    
    def recomendar_libros(self, id_usuario, cantidad=5):
        """Recomienda libros basado en el historial de préstamos"""
        usuario = self.obtener_usuario(id_usuario)
        if not usuario:
            return []
        
        # Encontrar categorías de libros que ha prestado
        categorias_usuario = set()
        for codigo in usuario.libros_activos:
            libro = self.obtener_libro(codigo)
            if libro:
                categorias_usuario.add(libro.categoria)
        
        # Buscar libros similares no prestados
        recomendaciones = []
        for libro in self.obtener_libros_disponibles():
            if libro.codigo not in usuario.libros_activos:
                if libro.categoria in categorias_usuario:
                    recomendaciones.append(libro)
        
        return recomendaciones[:cantidad]
    
    # ==================== ANÁLISIS DE COMPLEJIDAD ====================
    
    def obtener_analisis_complejidad(self):
        """Retorna análisis de complejidad de las operaciones principales"""
        return {
            'registrar_libro': {
                'promedio': 'O(log n)',
                'peor_caso': 'O(n)',
                'descripcion': 'O(log n) por inserción en árbol + O(1) en diccionario'
            },
            'buscar_por_codigo': {
                'promedio': 'O(log n)',
                'peor_caso': 'O(n)',
                'descripcion': 'Búsqueda en árbol BST'
            },
            'buscar_por_titulo': {
                'promedio': 'O(log n)',
                'peor_caso': 'O(n)',
                'descripcion': 'Búsqueda en árbol BST indexado'
            },
            'realizar_prestamo': {
                'promedio': 'O(1)',
                'peor_caso': 'O(1)',
                'descripcion': 'Operación en diccionario'
            },
            'devolver_libro': {
                'promedio': 'O(1)',
                'peor_caso': 'O(n)',
                'descripcion': 'O(1) en diccionario + O(n) si hay cola de espera'
            },
            'obtener_historial': {
                'promedio': 'O(n)',
                'peor_caso': 'O(n)',
                'descripcion': 'Recorrido de pila'
            },
            'recorrer_catalogo_enlazado': {
                'promedio': 'O(n)',
                'peor_caso': 'O(n)',
                'descripcion': 'Recorrido secuencial de la lista enlazada de libros'
            },
            'comparar_busqueda_secuencial_vs_arbol': {
                'promedio': 'Lista O(n) vs arbol O(log n)',
                'peor_caso': 'Lista O(n) vs arbol O(n)',
                'descripcion': 'Compara el catalogo enlazado contra el indice BST por codigo'
            }
        }

    def comparar_busqueda_secuencial_vs_arbol(self, codigo):
        """Compara pasos de busqueda en lista enlazada contra busqueda en arbol."""
        pasos_lista = 0
        encontrado_lista = None
        for libro in self.catalogo_enlazado:
            pasos_lista += 1
            if libro.codigo == codigo:
                encontrado_lista = libro
                break

        pasos_arbol = 0
        nodo = self.indice_libros_codigo.raiz
        while nodo:
            pasos_arbol += 1
            clave_nodo = self.indice_libros_codigo.clave_comparacion(nodo.dato)
            if codigo == clave_nodo:
                break
            nodo = nodo.izquierda if codigo < clave_nodo else nodo.derecha

        return {
            'codigo': codigo,
            'encontrado': encontrado_lista is not None,
            'pasos_lista': pasos_lista,
            'pasos_arbol': pasos_arbol,
            'conclusion': 'El arbol reduce comparaciones cuando esta equilibrado.'
        }
    
    def __str__(self):
        stats = self.obtener_estadisticas()
        return (f"Biblioteca(libros={stats['total_libros']}, "
                f"usuarios={stats['total_usuarios']}, "
                f"prestamos_activos={stats['prestamos_activos']})")