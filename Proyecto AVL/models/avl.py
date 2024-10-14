# avl.py
import json

class NodoAVL:
    """
        Inicializa un nodo del árbol AVL.
        
        Parámetros:
            clave (int): La clave del nodo.
            cantidad (int): La cantidad de productos en el nodo.
            precio (float): El precio del producto en el nodo.
            categoria (str): La categoría del producto en el nodo.
            altura (int): La altura del nodo en el árbol.
            izquierda (NodoAVL): Referencia al nodo hijo izquierdo.
            derecha (NodoAVL): Referencia al nodo hijo derecho.S
    """
    def __init__(self, clave, nombre, cantidad, precio, categoria):
        self.clave = clave
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.categoria = categoria
        self.altura = 1
        self.izquierda = None
        self.derecha = None 


class AVLTree:
    """
    Clase que representa un árbol AVL.

    Atributos:
        raiz (NodoAVL): La raíz del árbol AVL.
        rotation_callback (función): Callback para notificar rotaciones.
        json_file (str): Ruta del archivo JSON para guardar la información.
        rotations_performed (list): Lista de rotaciones realizadas.
    """
    
    def __init__(self):
        """
        Inicializa un árbol AVL vacío.
        """
        self.raiz = None
        self.rotation_callback = None  # Callback para rotaciones
        self.json_file = None # Archivo JSON para guardar la información
        self.rotations_performed = [] # Lista de rotaciones realizadas
        
        
    def set_json_file(self, file_path):
        """
        Establece la ruta del archivo JSON para guardar la información.

        Parámetros:
            file_path (str): La ruta del archivo JSON.
        """
        self.json_file = file_path


    def set_rotation_callback(self, callback):
        """
        Establece el callback para notificar rotaciones.

        Parámetros:
            callback (función): La función de callback para rotaciones.
        """
        self.rotation_callback = callback


    def obtener_altura(self, nodo):
        """
        Obtiene la altura de un nodo.

        Parámetros:
            nodo (NodoAVL): El nodo del cual obtener la altura.

        Retorna:
            int: La altura del nodo, o 0 si el nodo es None.
        """
        if not nodo:
            return 0
        return nodo.altura


    def obtener_balance(self, nodo):
        """
        Obtiene el factor de balance de un nodo.

        Parámetros:
            nodo (NodoAVL): El nodo del cual obtener el factor de balance.

        Retorna:
            int: El factor de balance del nodo, o 0 si el nodo es None.
        """
        if not nodo:
            return 0
        return self.obtener_altura(nodo.izquierda) - self.obtener_altura(nodo.derecha)


    def rotacion_derecha(self, y):
        """
    Realiza una rotación a la derecha en el subárbol con raíz en y.
    
    Parámetros:
        y (NodoAVL): La raíz del subárbol a rotar.
    
    Retorna:
        NodoAVL: La nueva raíz del subárbol después de la rotación.
    
    Funcionamiento:
        1. Se guarda el hijo izquierdo de y en x.
        2. Se guarda el hijo derecho de x en T2.
        3. Si hay un callback de rotación definido, se notifica la rotación.
        4. Se realiza la rotación:
            - El hijo derecho de x se convierte en y.
            - El hijo izquierdo de y se convierte en T2.
        5. Se actualizan las alturas de y y x.
        6. Se retorna x como la nueva raíz del subárbol.
        """
        x = y.izquierda
        T2 = x.derecha

        # Notificar la rotación
        if self.rotation_callback:
            self.rotation_callback("rotacion_derecha", y.clave, x.clave)

        # Realizar rotación
        x.derecha = y
        y.izquierda = T2

        # Actualizar alturas
        y.altura = 1 + max(self.obtener_altura(y.izquierda),
                           self.obtener_altura(y.derecha))
        x.altura = 1 + max(self.obtener_altura(x.izquierda),
                           self.obtener_altura(x.derecha))
        return x


    def rotacion_izquierda(self, x):
        """
    Realiza una rotación a la izquierda en el subárbol con raíz en x.
    
    Parámetros:
        x (NodoAVL): La raíz del subárbol a rotar.
    
    Retorna:
        NodoAVL: La nueva raíz del subárbol después de la rotación.
    
    Funcionamiento:
        1. Se guarda el hijo derecho de x en y.
        2. Se guarda el hijo izquierdo de y en T2.
        3. Si hay un callback de rotación definido, se notifica la rotación.
        4. Se realiza la rotación:
            - El hijo izquierdo de y se convierte en x.
            - El hijo derecho de x se convierte en T2.
        5. Se actualizan las alturas de x y y.
        6. Se retorna y como la nueva raíz del subárbol.
        """
        y = x.derecha
        T2 = y.izquierda

        # Notificar la rotación
        if self.rotation_callback:
            self.rotation_callback("rotacion_izquierda", x.clave, y.clave)

        # Realizar rotación
        y.izquierda = x
        x.derecha = T2

        # Actualizar alturas
        x.altura = 1 + max(self.obtener_altura(x.izquierda),
                           self.obtener_altura(x.derecha))
        y.altura = 1 + max(self.obtener_altura(y.izquierda),
                           self.obtener_altura(y.derecha))
        return y


    def insertar(self, clave, nombre, cantidad, precio, categoria):
        """
        Inserta un nuevo nodo en el subárbol con raíz en nodo.
        
        Esta función verifica si la clave ya existe en el árbol. Si no existe, 
        llama a la función _insertar para agregar el nuevo nodo y luego actualiza 
        la representación del árbol en un archivo JSON.
        
        :param nodo: Nodo raíz del subárbol.
        :param clave: Clave única del nodo.
        :param nombre: Nombre asociado al nodo.
        :param cantidad: Cantidad asociada al nodo.
        :param precio: Precio asociado al nodo.
        :param categoria: Categoría asociada al nodo.
        :return: Nueva raíz del subárbol.
        """
        # Verifica si la clave ya existe en el árbol
        if self.buscar(clave)[0]:
            # Si la clave ya existe, lanza una excepción
            raise ValueError(f"La clave {clave} ya existe en el árbol.")
        # Inserta el nuevo nodo en el árbol
        self.raiz = self._insertar(self.raiz, clave, nombre, cantidad, precio, categoria)
        # Actualiza la representación del árbol en un archivo JSON
        self._actualizar_json()


    def _insertar(self, nodo, clave, nombre, cantidad, precio, categoria):
        """
        Inserta un nuevo nodo en el subárbol con raíz en nodo.

        Esta función realiza la inserción estándar en un árbol binario de búsqueda (BST).
        Luego, actualiza la altura del nodo ancestro y verifica si el subárbol se ha 
        desbalanceado. Si es así, realiza las rotaciones necesarias para balancear el árbol.

        :param nodo: Nodo raíz del subárbol.
        :param clave: Clave única del nodo.
        :param nombre: Nombre asociado al nodo.
        :param cantidad: Cantidad asociada al nodo.
        :param precio: Precio asociado al nodo.
        :param categoria: Categoría asociada al nodo.
        :return: Nueva raíz del subárbol.
        """
        
        # Inserción estándar en BST
        if not nodo:
            # Si el nodo es None, crea un nuevo nodo y lo retorna
            return NodoAVL(clave, nombre, cantidad, precio, categoria)
        elif clave < nodo.clave:
            # Si el nodo es None, crea un nuevo nodo y lo retorna
            nodo.izquierda = self._insertar(nodo.izquierda, clave, nombre, cantidad, precio, categoria)
        elif clave > nodo.clave:
            # Si la clave es mayor que la clave del nodo actual, inserta en el subárbol derecho
            nodo.derecha = self._insertar(nodo.derecha, clave, nombre, cantidad, precio, categoria)
        else:
            # Si la clave ya existe, actualiza la información del nodo
            nodo.nombre = nombre
            nodo.cantidad = cantidad
            nodo.precio = precio
            nodo.categoria = categoria
            return nodo

        # Actualiza la altura del nodo ancestro
        nodo.altura = 1 + max(self.obtener_altura(nodo.izquierda),
                              self.obtener_altura(nodo.derecha))

        # Obtener el factor de balance
        balance = self.obtener_balance(nodo)

        # Balancear el árbol
        # Caso Izquierda Izquierda
        if balance > 1 and clave < nodo.izquierda.clave:
            return self.rotacion_derecha(nodo)

        # Caso Derecha Derecha
        if balance < -1 and clave > nodo.derecha.clave:
            return self.rotacion_izquierda(nodo)

        # Caso Izquierda Derecha
        if balance > 1 and clave > nodo.izquierda.clave:
            nodo.izquierda = self.rotacion_izquierda(nodo.izquierda)
            return self.rotacion_derecha(nodo)

        # Caso Derecha Izquierda
        if balance < -1 and clave < nodo.derecha.clave:
            nodo.derecha = self.rotacion_derecha(nodo.derecha)
            return self.rotacion_izquierda(nodo)

        return nodo


    def actualizar_producto(self, clave, nueva_cantidad=None, nuevo_precio=None):
        """
        Actualiza la cantidad y/o precio de un producto en el árbol AVL.

        :param clave: Clave del producto a actualizar.
        :param nueva_cantidad: Nueva cantidad del producto (opcional).
        :param nuevo_precio: Nuevo precio del producto (opcional).
        """
        
        def _actualizar_recursivo(nodo):
            """
            Función recursiva para buscar y actualizar el producto en el árbol.

            :param nodo: Nodo actual en el recorrido del árbol.
            :return: True si se actualizó el producto, None si no se encontró.
            """
            if not nodo:
                return None
            
            if clave == nodo.clave:
                if nueva_cantidad is not None:
                    nodo.cantidad = nueva_cantidad
                if nuevo_precio is not None:
                    nodo.precio = nuevo_precio
                return True
            elif clave < nodo.clave:
                return _actualizar_recursivo(nodo.izquierda)
            else:
                return _actualizar_recursivo(nodo.derecha)

        resultado = _actualizar_recursivo(self.raiz)
        if resultado:
            self._actualizar_json()
        return resultado


    def min_valor_nodo(self, nodo):
        """
        Encuentra el nodo con el valor mínimo en un subárbol.

        :param nodo: Nodo raíz del subárbol.
        :return: Nodo con el valor mínimo.
        """
        current = nodo
        while current.izquierda:
            current = current.izquierda
        return current


    def eliminar(self, clave):
        """
        Elimina un nodo con la clave dada del árbol AVL y actualiza el archivo JSON.

        :param clave: Clave del nodo a eliminar.
        :return: Lista de rotaciones realizadas durante la eliminación.
        """
        self.rotations_performed = [] # Limpiar lista de rotaciones
        self.raiz = self._eliminar(self.raiz, clave)
        self._actualizar_json()
        return self.rotations_performed # Retornar lista de rotaciones realizadas

    def _eliminar(self, nodo, clave):
        """
        Función recursiva para eliminar un nodo del árbol AVL.

        :param nodo: Nodo actual en el recorrido del árbol.
        :param clave: Clave del nodo a eliminar.
        :return: Nodo raíz del subárbol modificado.
        """
        if not nodo:
            return nodo

        if clave < nodo.clave:
            nodo.izquierda = self._eliminar(nodo.izquierda, clave)
        elif clave > nodo.clave:
            nodo.derecha = self._eliminar(nodo.derecha, clave)
        else:
            if not nodo.izquierda:
                return nodo.derecha
            elif not nodo.derecha:
                return nodo.izquierda

            temp = self.min_valor_nodo(nodo.derecha)
            nodo.clave = temp.clave
            nodo.nombre = temp.nombre
            nodo.cantidad = temp.cantidad
            nodo.precio = temp.precio
            nodo.categoria = temp.categoria
            nodo.derecha = self._eliminar(nodo.derecha, temp.clave)

        if not nodo:
            return nodo

        nodo.altura = 1 + max(self.obtener_altura(nodo.izquierda),
                              self.obtener_altura(nodo.derecha))

        balance = self.obtener_balance(nodo)

        # Caso Izquierda Izquierda
        if balance > 1 and self.obtener_balance(nodo.izquierda) >= 0:
            self.rotations_performed.append(f"Rotación Derecha en nodo {nodo.clave}")
            return self.rotacion_derecha(nodo)

        # Caso Izquierda Derecha
        if balance > 1 and self.obtener_balance(nodo.izquierda) < 0:
            self.rotations_performed.append(f"Rotación Izquierda en nodo {nodo.izquierda.clave}")
            self.rotations_performed.append(f"Rotación Derecha en nodo {nodo.clave}")
            nodo.izquierda = self.rotacion_izquierda(nodo.izquierda)
            return self.rotacion_derecha(nodo)

        # Caso Derecha Derecha
        if balance < -1 and self.obtener_balance(nodo.derecha) <= 0:
            self.rotations_performed.append(f"Rotación Izquierda en nodo {nodo.clave}")
            return self.rotacion_izquierda(nodo)

        # Caso Derecha Izquierda
        if balance < -1 and self.obtener_balance(nodo.derecha) > 0:
            self.rotations_performed.append(f"Rotación Derecha en nodo {nodo.derecha.clave}")
            self.rotations_performed.append(f"Rotación Izquierda en nodo {nodo.clave}")
            nodo.derecha = self.rotacion_derecha(nodo.derecha)
            return self.rotacion_izquierda(nodo)

        return nodo


    def buscar(self, clave):
        """
        Busca un nodo con la clave dada en el árbol AVL.

        :param clave: Clave del nodo a buscar.
        :return: Diccionario con los datos del nodo encontrado y el camino recorrido.
        """
        return self._buscar(self.raiz, clave, [])


    def _buscar(self, nodo, clave, camino):
        """
        Función recursiva para buscar un nodo en el árbol AVL.

        :param nodo: Nodo actual en el recorrido del árbol.
        :param clave: Clave del nodo a buscar.
        :param camino: Lista que almacena el camino recorrido.
        :return: Diccionario con los datos del nodo encontrado y el camino recorrido.
        """
        if not nodo:
            return None, camino
        
        camino.append(nodo.clave)
        
        if clave == nodo.clave:
            return {
                "clave": nodo.clave,
                "nombre": nodo.nombre,
                "cantidad": nodo.cantidad,
                "precio": nodo.precio,
                "categoria": nodo.categoria
            }, camino
        elif clave < nodo.clave:
            return self._buscar(nodo.izquierda, clave, camino)
        else:
            return self._buscar(nodo.derecha, clave, camino)


    def in_order_traversal(self):
        """
        Realiza un recorrido in-order del árbol AVL.

        :return: Lista de diccionarios con los datos de los nodos en orden.
        """
        elementos = []
        self._in_order_traversal(self.raiz, elementos)
        return elementos


    def _in_order_traversal(self, nodo, elementos):
        """
        Función recursiva para realizar un recorrido in-order del árbol AVL.

        :param nodo: Nodo actual en el recorrido del árbol.
        :param elementos: Lista que almacena los datos de los nodos en orden.
        """
        if nodo:
            self._in_order_traversal(nodo.izquierda, elementos)
            elementos.append({
                "clave": nodo.clave,
                "nombre": nodo.nombre,
                "cantidad": nodo.cantidad,
                "precio": nodo.precio,
                "categoria": nodo.categoria
            })
            self._in_order_traversal(nodo.derecha, elementos)
            
            
            
    def cargar_desde_json(self, archivo_json):
        """
        Carga los datos del árbol AVL desde un archivo JSON.

        :param archivo_json: Ruta del archivo JSON.
        """
        with open(archivo_json, 'r') as file:
            datos = json.load(file)
        for producto in datos:
            self.insertar(
                producto['clave'],
                producto['nombre'],
                producto['cantidad'],
                producto['precio'],
                producto['categoria']
            )


    def guardar_en_json(self, archivo_json=None):
        """
        Guarda los datos del árbol AVL en un archivo JSON.

        :param archivo_json: Ruta del archivo JSON (opcional).
        """
        if archivo_json:
            self.json_file = archivo_json
        if not self.json_file:
            raise ValueError("No se ha especificado un archivo JSON")
        datos = self.in_order_traversal()
        with open(self.json_file, 'w') as file:
            json.dump(datos, file, indent=2)


    def _actualizar_json(self):
        """
        Actualiza el archivo JSON con los datos actuales del árbol AVL.
        """
        if self.json_file:
            self.guardar_en_json()
            
            
    def buscar_por_rango_precios(self, precio_min, precio_max):
        """
        Busca productos en el árbol AVL cuyo precio esté dentro de un rango dado.

        :param precio_min: Precio mínimo.
        :param precio_max: Precio máximo.
        :return: Lista de productos encontrados y el camino recorrido.
        """
        resultados = []
        camino_busqueda = []
        self._buscar_por_rango_precios(self.raiz, precio_min, precio_max, resultados, camino_busqueda)
        return resultados, camino_busqueda


    def _buscar_por_rango_precios(self, nodo, precio_min, precio_max, resultados, camino_busqueda):
        """
        Función recursiva para buscar productos por rango de precios en el árbol AVL.

        :param nodo: Nodo actual en el recorrido del árbol.
        :param precio_min: Precio mínimo.
        :param precio_max: Precio máximo.
        :param resultados: Lista que almacena los productos encontrados.
        :param camino_busqueda: Lista que almacena el camino recorrido.
        """
        if not nodo:
            return
        
        camino_busqueda.append(nodo.clave)
        
        if precio_min <= nodo.precio <= precio_max:
            resultados.append({
                "clave": nodo.clave,
                "nombre": nodo.nombre,
                "cantidad": nodo.cantidad,
                "precio": nodo.precio,
                "categoria": nodo.categoria
            })
        
        if precio_min < nodo.precio:
            self._buscar_por_rango_precios(nodo.izquierda, precio_min, precio_max, resultados, camino_busqueda)
        
        if precio_max > nodo.precio:
            self._buscar_por_rango_precios(nodo.derecha, precio_min, precio_max, resultados, camino_busqueda)
            
            
    def buscar_por_categoria(self, categoria):
        """
        Busca productos en el árbol AVL por categoría.

        :param categoria: Categoría del producto.
        :return: Lista de productos encontrados y el camino recorrido.
        """
        if categoria not in ["Hogar", "Cocina", "Electrodomesticos", "Deportes"]:
            raise ValueError("Categoría no válida. Debe ser: Hogar, Cocina, Electrodomesticos o Deportes")
        
        resultados = []
        camino_busqueda = []
        self._buscar_por_categoria_recursivo(self.raiz, categoria, resultados, camino_busqueda)
        return sorted(resultados, key=lambda x: x['clave']), camino_busqueda


    def _buscar_por_categoria_recursivo(self, nodo, categoria, resultados, camino_busqueda):
        """
        Función recursiva para buscar productos por categoría en el árbol AVL.

        :param nodo: Nodo actual en el recorrido del árbol.
        :param categoria: Categoría del producto.
        :param resultados: Lista que almacena los productos encontrados.
        :param camino_busqueda: Lista que almacena el camino recorrido.
        """
        if not nodo:
            return
        
        camino_busqueda.append(nodo.clave)
        
        self._buscar_por_categoria_recursivo(nodo.izquierda, categoria, resultados, camino_busqueda)
        
        if nodo.categoria == categoria:
            resultados.append({
                "clave": nodo.clave,
                "nombre": nodo.nombre,
                "cantidad": nodo.cantidad,
                "precio": nodo.precio,
                "categoria": nodo.categoria
            })
        
        self._buscar_por_categoria_recursivo(nodo.derecha, categoria, resultados, camino_busqueda)
        
        
        
    def busqueda_combinada(self, precio_min=None, precio_max=None, categoria=None):
        """
        Realiza una búsqueda combinada por precio y categoría en el árbol AVL.

        :param precio_min: Precio mínimo (opcional).
        :param precio_max: Precio máximo (opcional).
        :param categoria: Categoría del producto (opcional).
        :return: Lista de productos encontrados y el camino recorrido.
        """
        resultados = []
        camino_busqueda = []
        self._busqueda_combinada_recursiva(self.raiz, precio_min, precio_max, categoria, resultados, camino_busqueda)
        return sorted(resultados, key=lambda x: x['clave']), camino_busqueda


    def _busqueda_combinada_recursiva(self, nodo, precio_min, precio_max, categoria, resultados, camino_busqueda):
        """
        Función recursiva para realizar una búsqueda combinada por precio y categoría en el árbol AVL.

        :param nodo: Nodo actual en el recorrido del árbol.
        :param precio_min: Precio mínimo (opcional).
        :param precio_max: Precio máximo (opcional).
        :param categoria: Categoría del producto (opcional).
        :param resultados: Lista que almacena los productos encontrados.
        :param camino_busqueda: Lista que almacena el camino recorrido.
        """
        if not nodo:
            return
        
        camino_busqueda.append(nodo.clave)
        
        
        # Decidir si continuar la búsqueda en el subárbol izquierdo
        if precio_min is None or nodo.precio >= precio_min:
            self._busqueda_combinada_recursiva(nodo.izquierda, precio_min, precio_max, categoria, resultados, camino_busqueda)
        
        # Verificar si el nodo actual cumple con los criterios
        cumple_criterios = True
        if precio_min is not None and nodo.precio < precio_min:
            cumple_criterios = False
        if precio_max is not None and nodo.precio > precio_max:
            cumple_criterios = False
        if categoria is not None and nodo.categoria != categoria:
            cumple_criterios = False
        
        if cumple_criterios:
            resultados.append({
                "clave": nodo.clave,
                "nombre": nodo.nombre,
                "cantidad": nodo.cantidad,
                "precio": nodo.precio,
                "categoria": nodo.categoria
            })
        
        # Decidir si continuar la búsqueda en el subárbol derecho
        if precio_max is None or nodo.precio <= precio_max:
            self._busqueda_combinada_recursiva(nodo.derecha, precio_min, precio_max, categoria, resultados, camino_busqueda)
            
            
    def verificar_stock(self):
        """
        Verifica los productos que están sin stock en el árbol AVL.

        :return: Lista de productos sin stock.
        """
        productos_sin_stock = []
        self._verificar_stock_recursivo(self.raiz, productos_sin_stock)
        return productos_sin_stock


    def _verificar_stock_recursivo(self, nodo, productos_sin_stock):
        """
        Función recursiva para verificar los productos sin stock en el árbol AVL.

        :param nodo: Nodo actual en el recorrido del árbol.
        :param productos_sin_stock: Lista que almacena los productos sin stock.
        """
        if not nodo:
            return
        
        self._verificar_stock_recursivo(nodo.izquierda, productos_sin_stock)
        
        if nodo.cantidad == 0:
            productos_sin_stock.append({
                "clave": nodo.clave,
                "nombre": nodo.nombre,
                "cantidad": nodo.cantidad,
                "precio": nodo.precio,
                "categoria": nodo.categoria
            })
        
        self._verificar_stock_recursivo(nodo.derecha, productos_sin_stock)