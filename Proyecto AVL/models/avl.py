# avl.py
import json

class NodoAVL:
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
    def __init__(self):
        self.raiz = None
        self.rotation_callback = None  # Callback para rotaciones
        self.json_file = None # Archivo JSON para guardar la información
        self.rotations_performed = [] # Lista de rotaciones realizadas
        
    def set_json_file(self, file_path):
        self.json_file = file_path

    def set_rotation_callback(self, callback):
        """
        Establece la función de callback que se llamará cuando se realice una rotación.
        La función de callback debe aceptar tres parámetros:
            - tipo_rotacion: "rotacion_derecha" o "rotacion_izquierda"
            - clave_nodo_y: la clave del nodo y
            - clave_nodo_x: la clave del nodo x
        """
        self.rotation_callback = callback

    def obtener_altura(self, nodo):
        if not nodo:
            return 0
        return nodo.altura

    def obtener_balance(self, nodo):
        if not nodo:
            return 0
        return self.obtener_altura(nodo.izquierda) - self.obtener_altura(nodo.derecha)

    def rotacion_derecha(self, y):
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
        if self.buscar(clave)[0]:
            raise ValueError(f"La clave {clave} ya existe en el árbol.")
        self.raiz = self._insertar(self.raiz, clave, nombre, cantidad, precio, categoria)
        self._actualizar_json()

    def _insertar(self, nodo, clave, nombre, cantidad, precio, categoria):
        # Inserción estándar en BST
        if not nodo:
            return NodoAVL(clave, nombre, cantidad, precio, categoria)
        elif clave < nodo.clave:
            nodo.izquierda = self._insertar(nodo.izquierda, clave, nombre, cantidad, precio, categoria)
        elif clave > nodo.clave:
            nodo.derecha = self._insertar(nodo.derecha, clave, nombre, cantidad, precio, categoria)
        else:
            # Actualizar información si la clave ya existe
            nodo.nombre = nombre
            nodo.cantidad = cantidad
            nodo.precio = precio
            nodo.categoria = categoria
            return nodo

        # Actualizar la altura del ancestro nodo
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
        def _actualizar_recursivo(nodo):
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
        current = nodo
        while current.izquierda:
            current = current.izquierda
        return current

    def eliminar(self, clave):
        self.rotations_performed = [] # Limpiar lista de rotaciones
        self.raiz = self._eliminar(self.raiz, clave)
        self._actualizar_json()
        return self.rotations_performed # Retornar lista de rotaciones realizadas

    def _eliminar(self, nodo, clave):
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
        return self._buscar(self.raiz, clave, [])

    def _buscar(self, nodo, clave, camino):
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
        elementos = []
        self._in_order_traversal(self.raiz, elementos)
        return elementos

    def _in_order_traversal(self, nodo, elementos):
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
        if archivo_json:
            self.json_file = archivo_json
        if not self.json_file:
            raise ValueError("No se ha especificado un archivo JSON")
        datos = self.in_order_traversal()
        with open(self.json_file, 'w') as file:
            json.dump(datos, file, indent=2)

    def _actualizar_json(self):
        if self.json_file:
            self.guardar_en_json()
            
    def buscar_por_rango_precios(self, precio_min, precio_max):
        resultados = []
        camino_busqueda = []
        self._buscar_por_rango_precios(self.raiz, precio_min, precio_max, resultados, camino_busqueda)
        return resultados, camino_busqueda

    def _buscar_por_rango_precios(self, nodo, precio_min, precio_max, resultados, camino_busqueda):
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
        if categoria not in ["Hogar", "Cocina", "Electrodomesticos", "Deportes"]:
            raise ValueError("Categoría no válida. Debe ser: Hogar, Cocina, Electrodomesticos o Deportes")
        
        resultados = []
        camino_busqueda = []
        self._buscar_por_categoria_recursivo(self.raiz, categoria, resultados, camino_busqueda)
        return sorted(resultados, key=lambda x: x['clave']), camino_busqueda

    def _buscar_por_categoria_recursivo(self, nodo, categoria, resultados, camino_busqueda):
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
        resultados = []
        camino_busqueda = []
        self._busqueda_combinada_recursiva(self.raiz, precio_min, precio_max, categoria, resultados, camino_busqueda)
        return sorted(resultados, key=lambda x: x['clave']), camino_busqueda

    def _busqueda_combinada_recursiva(self, nodo, precio_min, precio_max, categoria, resultados, camino_busqueda):
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
        productos_sin_stock = []
        self._verificar_stock_recursivo(self.raiz, productos_sin_stock)
        return productos_sin_stock

    def _verificar_stock_recursivo(self, nodo, productos_sin_stock):
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
