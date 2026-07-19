"""
Tipos Abstractos de Datos para el Sistema de Gestión de Biblioteca
Define las estructuras básicas: Libro, Usuario y Préstamo
"""

from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod


def _parse_datetime(valor, formato='%Y-%m-%d'):
    """Convierte texto guardado en JSON a datetime."""
    if not valor or valor == 'Pendiente':
        return None
    return datetime.strptime(valor, formato)


class EntidadBiblioteca(ABC):
    """
    Clase abstracta base para todos los TADs del sistema (Libro, Usuario,
    Prestamo, Accion). Obliga a que cada entidad sepa convertirse a
    diccionario y reconstruirse desde uno, que es lo único que
    Biblioteca necesita para guardar/cargar el JSON.
    """

    @abstractmethod
    def to_dict(self):
        """Convierte la entidad a diccionario (para guardar en JSON)"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(cls, datos):
        """Reconstruye la entidad desde un diccionario (leído del JSON)"""
        raise NotImplementedError


class EstadoLibro(Enum):
    """Estados posibles de un libro en la biblioteca"""
    DISPONIBLE = "Disponible"
    PRESTADO = "Prestado"
    RESERVADO = "Reservado"


class EstadoPrestamo(Enum):
    """Estados posibles de un préstamo"""
    ACTIVO = "Activo"
    DEVUELTO = "Devuelto"
    RETRASADO = "Retrasado"


class EstadoUsuario(Enum):
    """Estados posibles de un usuario"""
    ACTIVO = "Activo"
    MOROSO = "Moroso"


class Libro(EntidadBiblioteca):
    """
    TAD Libro: Representa un libro en la biblioteca
    
    Atributos:
        codigo: Identificador único del libro
        titulo: Nombre del libro
        autor: Autor del libro
        anio_publicacion: Año de publicación
        categoria: Categoría del libro
        estado: EstadoLibro (Disponible, Prestado, Reservado)
        cantidad_prestamos: Contador de cuántas veces fue prestado
    """
    
    def __init__(self, codigo, titulo, autor, anio_publicacion, categoria, stock=1):
        self.codigo = codigo
        self.titulo = titulo
        self.autor = autor
        self.anio_publicacion = anio_publicacion
        self.categoria = categoria
        self.stock = stock
        self.estado = EstadoLibro.DISPONIBLE if stock > 0 else EstadoLibro.PRESTADO
        self.cantidad_prestamos = 0
    
    def actualizar_estado(self):
        """Sincroniza el estado del libro según el stock disponible."""
        self.estado = EstadoLibro.DISPONIBLE if self.stock > 0 else EstadoLibro.PRESTADO
    
    def __repr__(self):
        return (f"Libro(codigo={self.codigo}, titulo='{self.titulo}', "
                f"stock={self.stock}, estado={self.estado.value})")
    
    def __str__(self):
        return (f"ID: {self.codigo} | Título: {self.titulo} | "
                f"Autor: {self.autor} | Año: {self.anio_publicacion} | "
                f"Categoría: {self.categoria} | Stock: {self.stock} | Estado: {self.estado.value}")
    
    def __eq__(self, otro):
        """Compara libros por código"""
        if isinstance(otro, Libro):
            return self.codigo == otro.codigo
        return False
    
    def __lt__(self, otro):
        """Para comparación en árboles (por código)"""
        return self.codigo < otro.codigo
    
    def to_dict(self):
        """Convierte el libro a diccionario"""
        return {
            'codigo': self.codigo,
            'titulo': self.titulo,
            'autor': self.autor,
            'anio_publicacion': self.anio_publicacion,
            'categoria': self.categoria,
            'stock': self.stock,
            'estado': self.estado.value,
            'cantidad_prestamos': self.cantidad_prestamos
        }

    @classmethod
    def from_dict(cls, datos):
        """Reconstruye un libro desde un diccionario JSON."""
        estado_guardado = datos.get('estado', EstadoLibro.DISPONIBLE.value)
        # Compatibilidad con datos antiguos que no guardaban 'stock':
        # se infiere un stock razonable a partir del estado guardado.
        stock_por_defecto = 1 if estado_guardado == EstadoLibro.DISPONIBLE.value else 0
        libro = cls(
            datos['codigo'],
            datos['titulo'],
            datos['autor'],
            datos['anio_publicacion'],
            datos['categoria'],
            datos.get('stock', stock_por_defecto)
        )
        libro.estado = EstadoLibro(estado_guardado)
        libro.cantidad_prestamos = datos.get('cantidad_prestamos', 0)
        return libro


class Usuario(EntidadBiblioteca):
    """
    TAD Usuario: Representa un usuario de la biblioteca
    
    Atributos:
        id_usuario: Identificador único del usuario
        nombre: Nombre del usuario
        email: Email del usuario
        telefono: Teléfono de contacto
        fecha_registro: Fecha de registro en la biblioteca
        libros_activos: Lista de códigos de libros que tiene prestados
    """
    
    def __init__(self, id_usuario, nombre, email, telefono):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.fecha_registro = datetime.now()
        self.libros_activos = []
        self.estado = EstadoUsuario.ACTIVO
    
    def __repr__(self):
        return (f"Usuario(id={self.id_usuario}, nombre='{self.nombre}', "
                f"libros_activos={len(self.libros_activos)})")
    
    def __str__(self):
        return (f"ID: {self.id_usuario} | Nombre: {self.nombre} | "
                f"Email: {self.email} | Teléfono: {self.telefono} | "
                f"Libros Activos: {len(self.libros_activos)} | "
                f"Estado: {self.estado.value}")

    def es_moroso(self):
        """Indica si el usuario está marcado como moroso"""
        return self.estado == EstadoUsuario.MOROSO

    def marcar_moroso(self):
        """Marca al usuario como moroso"""
        self.estado = EstadoUsuario.MOROSO

    def marcar_activo(self):
        """Marca al usuario como activo (al día)"""
        self.estado = EstadoUsuario.ACTIVO
    
    def agregar_libro(self, codigo_libro):
        """Agrega un libro a la lista de libros activos"""
        if codigo_libro not in self.libros_activos:
            self.libros_activos.append(codigo_libro)
    
    def devolver_libro(self, codigo_libro):
        """Remueve un libro de la lista de libros activos"""
        if codigo_libro in self.libros_activos:
            self.libros_activos.remove(codigo_libro)
    
    def tiene_libro(self, codigo_libro):
        """Verifica si el usuario tiene un libro específico"""
        return codigo_libro in self.libros_activos
    
    def to_dict(self):
        """Convierte el usuario a diccionario"""
        return {
            'id_usuario': self.id_usuario,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d'),
            'libros_activos': list(self.libros_activos),
            'estado': self.estado.value
        }

    @classmethod
    def from_dict(cls, datos):
        """Reconstruye un usuario desde un diccionario JSON."""
        usuario = cls(
            datos['id_usuario'],
            datos['nombre'],
            datos['email'],
            datos['telefono']
        )
        usuario.fecha_registro = _parse_datetime(datos.get('fecha_registro')) or datetime.now()
        libros_activos = datos.get('libros_activos', [])
        usuario.libros_activos = libros_activos if isinstance(libros_activos, list) else []
        usuario.estado = EstadoUsuario(datos.get('estado', EstadoUsuario.ACTIVO.value))
        return usuario


class Prestamo(EntidadBiblioteca):
    """
    TAD Préstamo: Representa un préstamo de un libro
    
    Atributos:
        id_prestamo: Identificador único del préstamo
        codigo_libro: Código del libro prestado
        id_usuario: ID del usuario que toma el préstamo
        fecha_prestamo: Fecha del préstamo
        fecha_devolucion_esperada: Fecha esperada de devolución (30 días)
        fecha_devolucion_real: Fecha real de devolución (None si activo)
        estado: EstadoPrestamo
    """
    
    contador = 0  # Contador de clase para IDs automáticos
    DIAS_PRESTAMO = 30  # Duración estándar de un préstamo
    
    def __init__(self, codigo_libro, id_usuario):
        Prestamo.contador += 1
        self.id_prestamo = Prestamo.contador
        self.codigo_libro = codigo_libro
        self.id_usuario = id_usuario
        self.fecha_prestamo = datetime.now()
        self.fecha_devolucion_esperada = self.fecha_prestamo + timedelta(days=self.DIAS_PRESTAMO)
        self.fecha_devolucion_real = None
        self.estado = EstadoPrestamo.ACTIVO
    
    def __repr__(self):
        return (f"Prestamo(id={self.id_prestamo}, libro={self.codigo_libro}, "
                f"usuario={self.id_usuario}, estado={self.estado.value})")
    
    def __str__(self):
        estado_str = f"Devuelto el {self.fecha_devolucion_real.strftime('%Y-%m-%d')}" \
            if self.fecha_devolucion_real else f"Vence: {self.fecha_devolucion_esperada.strftime('%Y-%m-%d')}"
        return (f"Préstamo #{self.id_prestamo} | Libro: {self.codigo_libro} | "
                f"Usuario: {self.id_usuario} | {estado_str} | "
                f"Estado: {self.estado.value}")
    
    def devolver(self):
        """Registra la devolución del libro"""
        self.fecha_devolucion_real = datetime.now()
        if self.fecha_devolucion_real > self.fecha_devolucion_esperada:
            self.estado = EstadoPrestamo.RETRASADO
        else:
            self.estado = EstadoPrestamo.DEVUELTO
    
    def esta_retrasado(self):
        """Verifica si el préstamo está retrasado (sin devolver)"""
        if self.estado == EstadoPrestamo.ACTIVO:
            return datetime.now() > self.fecha_devolucion_esperada
        return self.estado == EstadoPrestamo.RETRASADO
    
    def dias_restantes(self):
        """Calcula los días restantes para la devolución"""
        if self.estado != EstadoPrestamo.ACTIVO:
            return 0
        dias = (self.fecha_devolucion_esperada - datetime.now()).days
        return max(0, dias)
    
    def to_dict(self):
        """Convierte el préstamo a diccionario"""
        return {
            'id_prestamo': self.id_prestamo,
            'codigo_libro': self.codigo_libro,
            'id_usuario': self.id_usuario,
            'fecha_prestamo': self.fecha_prestamo.strftime('%Y-%m-%d'),
            'fecha_devolucion_esperada': self.fecha_devolucion_esperada.strftime('%Y-%m-%d'),
            'fecha_devolucion_real': self.fecha_devolucion_real.strftime('%Y-%m-%d') if self.fecha_devolucion_real else 'Pendiente',
            'estado': self.estado.value
        }

    @classmethod
    def from_dict(cls, datos):
        """Reconstruye un prestamo desde un diccionario JSON."""
        prestamo = cls.__new__(cls)
        prestamo.id_prestamo = int(datos['id_prestamo'])
        prestamo.codigo_libro = datos['codigo_libro']
        prestamo.id_usuario = datos['id_usuario']
        prestamo.fecha_prestamo = _parse_datetime(datos.get('fecha_prestamo')) or datetime.now()
        prestamo.fecha_devolucion_esperada = (
            _parse_datetime(datos.get('fecha_devolucion_esperada'))
            or prestamo.fecha_prestamo + timedelta(days=cls.DIAS_PRESTAMO)
        )
        prestamo.fecha_devolucion_real = _parse_datetime(datos.get('fecha_devolucion_real'))
        prestamo.estado = EstadoPrestamo(datos.get('estado', EstadoPrestamo.ACTIVO.value))
        Prestamo.contador = max(Prestamo.contador, prestamo.id_prestamo)
        return prestamo


class Accion(EntidadBiblioteca):
    """
    TAD Acción: Representa una acción realizada en el sistema
    Utilizado en el historial y pila de operaciones
    
    Atributos:
        tipo: Tipo de acción (Préstamo, Devolución, Registro, etc.)
        descripcion: Descripción detallada de la acción
        timestamp: Fecha y hora de la acción
        datos: Diccionario con datos adicionales
    """
    
    def __init__(self, tipo, descripcion, datos=None):
        self.tipo = tipo
        self.descripcion = descripcion
        self.timestamp = datetime.now()
        self.datos = datos or {}
    
    def __repr__(self):
        return (f"Accion(tipo='{self.tipo}', timestamp={self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
    
    def __str__(self):
        return (f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.tipo}: {self.descripcion}")
    
    def to_dict(self):
        """Convierte la acción a diccionario"""
        return {
            'tipo': self.tipo,
            'descripcion': self.descripcion,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'datos': self.datos
        }

    @classmethod
    def from_dict(cls, datos):
        """Reconstruye una accion desde un diccionario JSON."""
        accion = cls.__new__(cls)
        accion.tipo = datos['tipo']
        accion.descripcion = datos['descripcion']
        accion.timestamp = _parse_datetime(datos.get('timestamp'), '%Y-%m-%d %H:%M:%S') or datetime.now()
        accion.datos = datos.get('datos', {})
        return accion