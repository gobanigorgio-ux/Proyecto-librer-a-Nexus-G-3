"""
Estructuras de Datos: Pila, Cola, Lista Enlazada y Árbol Binario de Búsqueda
Con análisis de complejidad temporal
"""
from collections import deque
from abc import ABC, abstractmethod


class EstructuraDatos(ABC):
    """
    Clase abstracta base para las estructuras de datos del sistema
    (Pila, Cola, ListaEnlazada, ArbolBinarioBusqueda). Unifica la
    interfaz común: saber si está vacía, cuántos elementos tiene,
    vaciarse y poder recorrerse con un for.
    """

    @abstractmethod
    def esta_vacia(self):
        """Verifica si la estructura está vacía"""
        raise NotImplementedError

    @abstractmethod
    def tamano(self):
        """Retorna la cantidad de elementos almacenados"""
        raise NotImplementedError

    @abstractmethod
    def vaciar(self):
        """Elimina todos los elementos de la estructura"""
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        """Permite recorrer la estructura con un for"""
        raise NotImplementedError


# ==================== PILA (STACK) ====================
class Pila(EstructuraDatos):
    """
    Estructura de datos LIFO (Last In, First Out)
    Utilizada para: Historial de operaciones y deshacer acciones
    
    Complejidad:
    - push(): O(1)
    - pop(): O(1)
    - peek(): O(1)
    """
    
    def __init__(self):
        self.elementos = []
    
    def push(self, elemento):
        """Agrega un elemento a la pila"""
        self.elementos.append(elemento)
    
    def pop(self):
        """Remueve y retorna el elemento superior"""
        if not self.esta_vacia():
            return self.elementos.pop()
        return None
    
    def peek(self):
        """Retorna el elemento superior sin removerlo"""
        if not self.esta_vacia():
            return self.elementos[-1]
        return None
    
    def esta_vacia(self):
        """Verifica si la pila está vacía"""
        return len(self.elementos) == 0
    
    def tamano(self):
        """Retorna el tamaño de la pila"""
        return len(self.elementos)
    
    def vaciar(self):
        """Limpia la pila"""
        self.elementos.clear()
    
    def __iter__(self):
        """Permite iterar la pila desde el tope"""
        for i in range(len(self.elementos) - 1, -1, -1):
            yield self.elementos[i]
    
    def __str__(self):
        return f"Pila({self.elementos})"


# ==================== COLA (QUEUE) ====================
class Cola(EstructuraDatos):
    """
    Estructura de datos FIFO (First In, First Out)
    Utilizada para: Lista de espera de préstamos
    
    Complejidad:
    - enqueue(): O(1)
    - dequeue(): O(1)
    - peek(): O(1)
    """
    
    def __init__(self):
        self.elementos = deque()
    
    def enqueue(self, elemento):
        """Agrega un elemento al final de la cola"""
        self.elementos.append(elemento)
    
    def dequeue(self):
        """Remueve y retorna el primer elemento de la cola"""
        if not self.esta_vacia():
            return self.elementos.popleft()
        return None
    
    def peek(self):
        """Retorna el primer elemento sin removerlo"""
        if not self.esta_vacia():
            return self.elementos[0]
        return None
    
    def esta_vacia(self):
        """Verifica si la cola está vacía"""
        return len(self.elementos) == 0
    
    def tamano(self):
        """Retorna el tamaño de la cola"""
        return len(self.elementos)
    
    def vaciar(self):
        """Limpia la cola"""
        self.elementos.clear()
    
    def __iter__(self):
        """Permite iterar la cola"""
        return iter(self.elementos)
    
    def __str__(self):
        return f"Cola({list(self.elementos)})"


# ==================== NODO DE LISTA ENLAZADA ====================
class NodoLista:
    """Nodo para la lista enlazada"""
    
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


# ==================== LISTA ENLAZADA ====================
class ListaEnlazada(EstructuraDatos):
    """
    Lista dinámica basada en nodos enlazados
    Utilizada para: Gestión de colecciones dinámicas
    
    Complejidad:
    - insertar_inicio(): O(1)
    - insertar_final(): O(n)
    - eliminar(): O(n)
    - buscar(): O(n)
    - recorrer(): O(n)
    """
    
    def __init__(self):
        self.cabeza = None
        self._tamano = 0
    
    def insertar_inicio(self, dato):
        """Inserta un elemento al inicio"""
        nuevo_nodo = NodoLista(dato)
        nuevo_nodo.siguiente = self.cabeza
        self.cabeza = nuevo_nodo
        self._tamano += 1
    
    def insertar_final(self, dato):
        """Inserta un elemento al final"""
        nuevo_nodo = NodoLista(dato)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self._tamano += 1
    
    def eliminar(self, dato):
        """Elimina la primera ocurrencia de un dato"""
        if self.cabeza is None:
            return False
        
        if self.cabeza.dato == dato:
            self.cabeza = self.cabeza.siguiente
            self._tamano -= 1
            return True
        
        actual = self.cabeza
        while actual.siguiente:
            if actual.siguiente.dato == dato:
                actual.siguiente = actual.siguiente.siguiente
                self._tamano -= 1
                return True
            actual = actual.siguiente
        
        return False
    
    def buscar(self, dato):
        """Busca un dato en la lista"""
        actual = self.cabeza
        while actual:
            if actual.dato == dato:
                return True
            actual = actual.siguiente
        return False
    
    def obtener_por_indice(self, indice):
        """Obtiene un elemento por su índice"""
        if indice < 0 or indice >= self._tamano:
            return None
        
        actual = self.cabeza
        for _ in range(indice):
            actual = actual.siguiente
        return actual.dato
    
    def tamano(self):
        """Retorna el tamaño de la lista"""
        return self._tamano
    
    def esta_vacia(self):
        """Verifica si la lista está vacía"""
        return self.cabeza is None
    
    def vaciar(self):
        """Limpia la lista"""
        self.cabeza = None
        self._tamano = 0
    
    def __iter__(self):
        """Permite iterar la lista"""
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente
    
    def __str__(self):
        elementos = list(self)
        return f"ListaEnlazada({elementos})"


# ==================== NODO DE ÁRBOL BINARIO ====================
class NodoArbol:
    """Nodo para el árbol binario de búsqueda"""
    
    def __init__(self, dato):
        self.dato = dato
        self.izquierda = None
        self.derecha = None
        self.altura = 1


# ==================== ÁRBOL BINARIO DE BÚSQUEDA ====================
class ArbolBinarioBusqueda(EstructuraDatos):
    """
    Árbol Binario de Búsqueda (BST)
    Utilizado para: Indexar libros por código, título o autor
    
    Complejidad (caso promedio):
    - insertar(): O(log n)
    - buscar(): O(log n)
    - eliminar(): O(log n)
    - recorrer_inorden(): O(n)
    
    Complejidad (peor caso - árbol degenerado):
    - insertar(): O(n)
    - buscar(): O(n)
    - eliminar(): O(n)
    """
    
    def __init__(self, clave_comparacion=None):
        """
        Inicializa el árbol
        clave_comparacion: función para extraer la clave de comparación del dato
        """
        self.raiz = None
        self.clave_comparacion = clave_comparacion or (lambda x: x)
        self._tamano = 0
    
    def insertar(self, dato):
        """Inserta un dato en el árbol"""
        if self.raiz is None:
            self.raiz = NodoArbol(dato)
            self._tamano += 1
        else:
            self._insertar_recursivo(self.raiz, dato)
    
    def _insertar_recursivo(self, nodo, dato):
        """Función recursiva para insertar"""
        clave = self.clave_comparacion(dato)
        clave_nodo = self.clave_comparacion(nodo.dato)
        
        if clave < clave_nodo:
            if nodo.izquierda is None:
                nodo.izquierda = NodoArbol(dato)
                self._tamano += 1
            else:
                self._insertar_recursivo(nodo.izquierda, dato)
        elif clave > clave_nodo:
            if nodo.derecha is None:
                nodo.derecha = NodoArbol(dato)
                self._tamano += 1
            else:
                self._insertar_recursivo(nodo.derecha, dato)
    
    def buscar(self, clave):
        """Busca un dato por clave"""
        return self._buscar_recursivo(self.raiz, clave)
    
    def _buscar_recursivo(self, nodo, clave):
        """Función recursiva para buscar"""
        if nodo is None:
            return None
        
        clave_nodo = self.clave_comparacion(nodo.dato)
        
        if clave == clave_nodo:
            return nodo.dato
        elif clave < clave_nodo:
            return self._buscar_recursivo(nodo.izquierda, clave)
        else:
            return self._buscar_recursivo(nodo.derecha, clave)
    
    def buscar_rango(self, clave_min, clave_max):
        """Busca todos los elementos en un rango"""
        resultados = []
        self._buscar_rango_recursivo(self.raiz, clave_min, clave_max, resultados)
        return resultados
    
    def _buscar_rango_recursivo(self, nodo, clave_min, clave_max, resultados):
        """Busca en rango de forma recursiva"""
        if nodo is None:
            return
        
        clave_nodo = self.clave_comparacion(nodo.dato)
        
        if clave_min <= clave_nodo <= clave_max:
            resultados.append(nodo.dato)
        
        if clave_nodo > clave_min:
            self._buscar_rango_recursivo(nodo.izquierda, clave_min, clave_max, resultados)
        if clave_nodo < clave_max:
            self._buscar_rango_recursivo(nodo.derecha, clave_min, clave_max, resultados)
    
    def eliminar(self, clave):
        """Elimina un nodo por clave"""
        self.raiz, eliminado = self._eliminar_recursivo(self.raiz, clave)
        if eliminado:
            self._tamano -= 1
        return eliminado
    
    def _eliminar_recursivo(self, nodo, clave):
        """Función recursiva para eliminar"""
        if nodo is None:
            return None, False
        
        clave_nodo = self.clave_comparacion(nodo.dato)
        
        if clave < clave_nodo:
            nodo.izquierda, eliminado = self._eliminar_recursivo(nodo.izquierda, clave)
            return nodo, eliminado
        elif clave > clave_nodo:
            nodo.derecha, eliminado = self._eliminar_recursivo(nodo.derecha, clave)
            return nodo, eliminado
        else:
            # Nodo encontrado
            # Caso 1: Sin hijos
            if nodo.izquierda is None and nodo.derecha is None:
                return None, True
            
            # Caso 2: Un hijo
            if nodo.izquierda is None:
                return nodo.derecha, True
            if nodo.derecha is None:
                return nodo.izquierda, True
            
            # Caso 3: Dos hijos
            # Encontrar el mínimo en el subárbol derecho
            minimo = self._encontrar_minimo(nodo.derecha)
            nodo.dato = minimo
            nodo.derecha, _ = self._eliminar_recursivo(nodo.derecha, 
                                                       self.clave_comparacion(minimo))
            return nodo, True
    
    def _encontrar_minimo(self, nodo):
        """Encuentra el nodo con valor mínimo"""
        actual = nodo
        while actual.izquierda:
            actual = actual.izquierda
        return actual.dato
    
    def recorrer_inorden(self):
        """Recorrido inorden (izquierda-raíz-derecha)"""
        resultado = []
        self._recorrer_inorden_recursivo(self.raiz, resultado)
        return resultado
    
    def _recorrer_inorden_recursivo(self, nodo, resultado):
        """Recorrido inorden recursivo"""
        if nodo:
            self._recorrer_inorden_recursivo(nodo.izquierda, resultado)
            resultado.append(nodo.dato)
            self._recorrer_inorden_recursivo(nodo.derecha, resultado)
    
    def recorrer_preorden(self):
        """Recorrido preorden (raíz-izquierda-derecha)"""
        resultado = []
        self._recorrer_preorden_recursivo(self.raiz, resultado)
        return resultado
    
    def _recorrer_preorden_recursivo(self, nodo, resultado):
        """Recorrido preorden recursivo"""
        if nodo:
            resultado.append(nodo.dato)
            self._recorrer_preorden_recursivo(nodo.izquierda, resultado)
            self._recorrer_preorden_recursivo(nodo.derecha, resultado)
    
    def recorrer_postorden(self):
        """Recorrido postorden (izquierda-derecha-raíz)"""
        resultado = []
        self._recorrer_postorden_recursivo(self.raiz, resultado)
        return resultado
    
    def _recorrer_postorden_recursivo(self, nodo, resultado):
        """Recorrido postorden recursivo"""
        if nodo:
            self._recorrer_postorden_recursivo(nodo.izquierda, resultado)
            self._recorrer_postorden_recursivo(nodo.derecha, resultado)
            resultado.append(nodo.dato)
    
    def altura_arbol(self):
        """Calcula la altura del árbol"""
        return self._calcular_altura(self.raiz)
    
    def _calcular_altura(self, nodo):
        """Calcula la altura de forma recursiva"""
        if nodo is None:
            return 0
        return 1 + max(self._calcular_altura(nodo.izquierda),
                       self._calcular_altura(nodo.derecha))
    
    def tamano(self):
        """Retorna el número de nodos"""
        return self._tamano
    
    def esta_vacio(self):
        """Verifica si el árbol está vacío (alias de esta_vacia)"""
        return self.esta_vacia()

    def esta_vacia(self):
        """Verifica si el árbol está vacío"""
        return self.raiz is None
    
    def vaciar(self):
        """Limpia el árbol"""
        self.raiz = None
        self._tamano = 0

    def __iter__(self):
        """Permite recorrer el árbol con un for (recorrido inorden)"""
        return iter(self.recorrer_inorden())
    
    def obtener_hojas(self):
        """Obtiene todas las hojas del árbol"""
        hojas = []
        self._obtener_hojas_recursivo(self.raiz, hojas)
        return hojas
    
    def _obtener_hojas_recursivo(self, nodo, hojas):
        """Obtiene hojas de forma recursiva"""
        if nodo:
            if nodo.izquierda is None and nodo.derecha is None:
                hojas.append(nodo.dato)
            self._obtener_hojas_recursivo(nodo.izquierda, hojas)
            self._obtener_hojas_recursivo(nodo.derecha, hojas)
    
    def __str__(self):
