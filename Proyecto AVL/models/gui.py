# gui.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem,
    QFileDialog, QFormLayout
)
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF, QTimer
from models.avl import AVLTree
from collections import deque

class AVLVisualizer(QGraphicsView):
    def __init__(self, avl_tree, parent=None):
        super().__init__(parent)
        self.avl_tree = avl_tree
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.node_radius = 20
        self.level_gap = 100
        self.horizontal_gap = 300
        self.setMinimumHeight(600)
        self.setMinimumWidth(800)
        
        # Configurar políticas de scroll
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Cola para almacenar los eventos de rotación
        self.rotation_events = deque()
        self.is_animating = False

        # Nodos a resaltar durante la rotación
        self.highlighted_nodes = set()

        # Timer para la animación
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_rotation_event)

    def add_rotation_event(self, event):
        """
        Agrega un evento de rotación a la cola de eventos.
        El evento es una tupla: (tipo_rotacion, clave_nodo_y, clave_nodo_x)
        """
        self.rotation_events.append(event)
        if not self.is_animating:
            self.is_animating = True
            self.timer.start(1000)  # 500 ms entre eventos

    def process_rotation_event(self):
        if self.rotation_events:
            event = self.rotation_events.popleft()
            tipo_rotacion, clave_y, clave_x = event
            print(f"Realizando {tipo_rotacion} en nodos y: {clave_y}, x: {clave_x}")
            
            # Resaltar los nodos involucrados
            self.highlighted_nodes = {clave_y, clave_x}
            self.draw_tree()

            # Esperar 500 ms antes de quitar el resaltado
            QTimer.singleShot(500, self.clear_highlight)
        else:
            self.timer.stop()
            self.is_animating = False

    def clear_highlight(self):
        self.highlighted_nodes = set()
        self.draw_tree()

    def draw_tree(self):
        self.scene.clear()
        if self.avl_tree.raiz:
            # Iniciar el dibujo con la raíz en el centro
            self._draw_node(self.avl_tree.raiz, 0, self.width() / 2, 0)
        # Establecer el rectángulo de la escena para abarcar todo el contenido
        self.scene.setSceneRect(self.scene.itemsBoundingRect())

    def _draw_node(self, node, depth, x, parent_x):
        # Calcular posición
        y = depth * self.level_gap + self.node_radius * 2

        # Modificar el texto del nodo para mostrar más información
        text = QGraphicsTextItem(f"{node.clave}")
        text.setDefaultTextColor(Qt.black)
        # Centrar el texto dentro del nodo
        text_width = text.boundingRect().width()
        text_height = text.boundingRect().height()
        text.setPos(x - text_width / 2, y - text_height / 2)
        self.scene.addItem(text)

        # Dibujar líneas a los hijos primero (para que queden detrás del nodo)
        if node.izquierda:
            child_x = x - self.horizontal_gap / (depth + 1)
            child_y = y + self.level_gap
            line = QGraphicsLineItem(x, y, child_x, child_y)
            line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(line)
            self._draw_node(node.izquierda, depth + 1, child_x, x)
        if node.derecha:
            child_x = x + self.horizontal_gap / (depth + 1)
            child_y = y + self.level_gap
            line = QGraphicsLineItem(x, y, child_x, child_y)
            line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(line)
            self._draw_node(node.derecha, depth + 1, child_x, x)

        # Determinar si el nodo debe ser resaltado
        if node.clave in self.highlighted_nodes:
            ellipse_color = QColor(250, 100, 100)  # Rojo para resaltar
        else:
            ellipse_color = QColor(100, 200, 250)  # Azul claro

        # Dibujar el nodo (elipse) después de las líneas para que quede por encima de ellas
        ellipse = QGraphicsEllipseItem(x - self.node_radius, y - self.node_radius,
                                       self.node_radius * 2, self.node_radius * 2)
        ellipse.setBrush(QBrush(ellipse_color))
        ellipse.setPen(QPen(Qt.black, 2))
        self.scene.addItem(ellipse)

        # Agregar texto en el nodo (por encima del elipse)
        text = QGraphicsTextItem(str(node.clave))
        text.setDefaultTextColor(Qt.black)
        # Centrar el texto dentro del nodo
        text_width = text.boundingRect().width()
        text_height = text.boundingRect().height()
        text.setPos(x - text_width / 2, y - text_height / 2)
        self.scene.addItem(text)
        
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventario de Productos")
        self.avl = AVLTree()
        self.avl.set_rotation_callback(self.handle_rotation)
        self.init_ui()

    def init_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Área de control (insertar, eliminar, buscar)
        control_layout = QHBoxLayout()

        # Formulario de inserción
        insert_form_layout = QFormLayout()
        self.insert_key_input = QLineEdit()
        self.insert_nombre_input = QLineEdit()
        self.insert_cantidad_input = QLineEdit()
        self.insert_precio_input = QLineEdit()
        self.insert_categoria_input = QLineEdit()

        insert_form_layout.addRow("Clave:", self.insert_key_input)
        insert_form_layout.addRow("Nombre:", self.insert_nombre_input)
        insert_form_layout.addRow("Cantidad:", self.insert_cantidad_input)
        insert_form_layout.addRow("Precio:", self.insert_precio_input)
        insert_form_layout.addRow("Categoría:", self.insert_categoria_input)

        insert_button = QPushButton("Insertar")
        insert_button.clicked.connect(self.insert_node)
        insert_form_layout.addRow(insert_button)

        control_layout.addLayout(insert_form_layout)

        # Eliminación
        delete_layout = QVBoxLayout()
        self.delete_key_input = QLineEdit()
        self.delete_key_input.setPlaceholderText("Clave")
        delete_button = QPushButton("Eliminar")
        delete_button.clicked.connect(self.delete_node)
        delete_layout.addWidget(QLabel("Eliminar:"))
        delete_layout.addWidget(self.delete_key_input)
        delete_layout.addWidget(delete_button)
        control_layout.addLayout(delete_layout)

        # Búsqueda
        search_layout = QVBoxLayout()
        self.search_key_input = QLineEdit()
        self.search_key_input.setPlaceholderText("Clave")
        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.search_node)
        search_layout.addWidget(QLabel("Buscar:"))
        search_layout.addWidget(self.search_key_input)
        search_layout.addWidget(search_button)
        control_layout.addLayout(search_layout)

        main_layout.addLayout(control_layout)

        # Layout para la visualización del árbol y los logs de rotación
        visualization_layout = QHBoxLayout()

        # Visualización del árbol
        self.tree_view = AVLVisualizer(self.avl)
        visualization_layout.addWidget(self.tree_view)

        # Layout para las listas de inventario y rotaciones
        lists_layout = QVBoxLayout()

        # Lista de inventario (in-order traversal)
        inventory_label = QLabel("Inventario (In-Order):")
        self.inventory_list = QListWidget()
        lists_layout.addWidget(inventory_label)
        lists_layout.addWidget(self.inventory_list)

        # Lista de rotaciones
        rotation_label = QLabel("Registro de Rotaciones:")
        self.rotation_list = QListWidget()
        lists_layout.addWidget(rotation_label)
        lists_layout.addWidget(self.rotation_list)

        visualization_layout.addLayout(lists_layout)

        main_layout.addLayout(visualization_layout)

        # Agregar botones para cargar y guardar JSON
        json_layout = QHBoxLayout()
        load_json_button = QPushButton("Cargar JSON")
        load_json_button.clicked.connect(self.load_json)
        save_json_button = QPushButton("Guardar JSON")
        save_json_button.clicked.connect(self.save_json)
        json_layout.addWidget(load_json_button)
        json_layout.addWidget(save_json_button)
        main_layout.addLayout(json_layout)

    def insert_node(self):
        key_text = self.insert_key_input.text()
        nombre = self.insert_nombre_input.text()
        cantidad_text = self.insert_cantidad_input.text()
        precio_text = self.insert_precio_input.text()
        categoria = self.insert_categoria_input.text()

        if not all([key_text, nombre, cantidad_text, precio_text, categoria]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return

        try:
            key = int(key_text)
            cantidad = int(cantidad_text)
            precio = float(precio_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "Clave y cantidad deben ser enteros, y precio debe ser un número.")
            return

        self.avl.insertar(key, nombre, cantidad, precio, categoria)
        self.update_ui()
        self.clear_insert_inputs()

    def clear_insert_inputs(self):
        self.insert_key_input.clear()
        self.insert_nombre_input.clear()
        self.insert_cantidad_input.clear()
        self.insert_precio_input.clear()
        self.insert_categoria_input.clear()

    def delete_node(self):
        key_text = self.delete_key_input.text()

        if not key_text:
            QMessageBox.warning(self, "Error", "La clave no puede estar vacía.")
            return

        try:
            key = int(key_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "La clave debe ser un número entero.")
            return

        if self.avl.buscar(key) is None:
            QMessageBox.information(self, "Información", f"La clave {key} no existe en el árbol.")
            return

        self.avl.eliminar(key)
        self.update_ui()
        self.delete_key_input.clear()

    def search_node(self):
        key_text = self.search_key_input.text()

        if not key_text:
            QMessageBox.warning(self, "Error", "La clave no puede estar vacía.")
            return

        try:
            key = int(key_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "La clave debe ser un número entero.")
            return

        result = self.avl.buscar(key)
        if result is not None:
            message = f"Clave: {result['clave']}\n"
            message += f"Nombre: {result['nombre']}\n"
            message += f"Cantidad: {result['cantidad']}\n"
            message += f"Precio: {result['precio']}\n"
            message += f"Categoría: {result['categoria']}"
            QMessageBox.information(self, "Resultado de Búsqueda", message)
        else:
            QMessageBox.information(self, "Resultado de Búsqueda", f"La clave {key} no se encontró en el árbol.")

    def update_ui(self):
        # Actualizar la visualización del árbol
        self.tree_view.draw_tree()

        # Actualizar la lista de inventario
        self.inventory_list.clear()
        in_order = self.avl.in_order_traversal()
        for producto in in_order:
            self.inventory_list.addItem(
                f"Clave: {producto['clave']}, Nombre: {producto['nombre']}, "
                f"Cantidad: {producto['cantidad']}, Precio: {producto['precio']}, "
                f"Categoría: {producto['categoria']}"
            )

    def handle_rotation(self, tipo_rotacion, clave_y, clave_x):
        """
        Callback para manejar rotaciones desde el árbol AVL.
        Agrega el evento de rotación a la visualización y al registro de rotaciones.
        """
        event = (tipo_rotacion, clave_y, clave_x)
        self.tree_view.add_rotation_event(event)
        # Agregar el mensaje al registro de rotaciones
        if tipo_rotacion == "rotacion_derecha":
            mensaje = f"Rotación Derecha: y={clave_y} ↦ x={clave_x}"
        elif tipo_rotacion == "rotacion_izquierda":
            mensaje = f"Rotación Izquierda: y={clave_y} ↦ x={clave_x}"
        else:
            mensaje = f"Rotación {tipo_rotacion}: y={clave_y} ↦ x={clave_x}"
        self.rotation_list.addItem(mensaje)

    def load_json(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Cargar archivo JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                self.avl.cargar_desde_json(file_name)
                self.update_ui()
                QMessageBox.information(self, "Éxito", "Datos cargados correctamente desde JSON.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al cargar el archivo JSON: {str(e)}")

    def save_json(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar archivo JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                self.avl.guardar_en_json(file_name)
                QMessageBox.information(self, "Éxito", "Datos guardados correctamente en JSON.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al guardar el archivo JSON: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()