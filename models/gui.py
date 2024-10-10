# gui.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem, QGridLayout
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
        self.level_gap = 70
        self.horizontal_gap = 60
        self.setMinimumHeight(600)
        self.setMinimumWidth(800)

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
            self.timer.start(500)  # 500 ms entre eventos

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
            self._draw_node(self.avl_tree.raiz, 0, 0, 0)
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def _draw_node(self, node, depth, x, parent_x):
        # Calcular posición
        if depth == 0:
            x = self.width() / 2
        else:
            x = parent_x + x

        y = depth * self.level_gap + self.node_radius * 2

        # Dibujar líneas a los hijos primero (para que queden detrás del nodo)
        if node.izquierda:
            child_x = x - self.horizontal_gap / (depth + 1)
            child_y = y + self.level_gap
            line = QGraphicsLineItem(x, y, child_x, child_y)
            line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(line)
            self._draw_node(node.izquierda, depth + 1, -self.horizontal_gap / (depth + 1), x)
        if node.derecha:
            child_x = x + self.horizontal_gap / (depth + 1)
            child_y = y + self.level_gap
            line = QGraphicsLineItem(x, y, child_x, child_y)
            line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(line)
            self._draw_node(node.derecha, depth + 1, self.horizontal_gap / (depth + 1), x)

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
        self.setWindowTitle("Inventario")
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

        # Inserción de clave
        self.insert_key_input = QLineEdit()
        self.insert_key_input.setPlaceholderText("Clave")
        control_layout.addWidget(QLabel("Insertar Clave:"))
        control_layout.addWidget(self.insert_key_input)

        # Información adicional
        self.label_nombre = QLabel("Nombre del Producto:")
        self.input_nombre = QLineEdit()

        control_layout.addWidget(self.label_nombre)
        control_layout.addWidget(self.input_nombre)

        self.label_cantidad = QLabel("Cantidad Disponible:")
        self.input_cantidad = QLineEdit()

        control_layout.addWidget(self.label_cantidad)
        control_layout.addWidget(self.input_cantidad)


        self.label_precio = QLabel("Precio del Producto:")
        self.input_precio = QLineEdit()


        control_layout.addWidget(self.label_precio)
        control_layout.addWidget(self.input_precio)


        self.label_categoria = QLabel("Categoría del Producto:")
        self.input_categoria = QLineEdit()


        control_layout.addWidget(self.label_categoria)
        control_layout.addWidget(self.input_categoria)


        main_layout.addLayout(control_layout)
        
        #Boton 
        insert_key_button = QPushButton("Insertar Clave")
        insert_key_button.clicked.connect(self.insert_node) 
        control_layout.addWidget(insert_key_button)   
        
        # Eliminación
        self.delete_key_input = QLineEdit()
        self.delete_key_input.setPlaceholderText("Clave")
        delete_button = QPushButton("Eliminar")
        delete_button.clicked.connect(self.delete_node)

        control_layout.addWidget(QLabel("Eliminar:"))
        control_layout.addWidget(self.delete_key_input)
        control_layout.addWidget(delete_button)

        # Búsqueda
        self.search_key_input = QLineEdit()
        self.search_key_input.setPlaceholderText("Clave")
        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.search_node)

        control_layout.addWidget(QLabel("Buscar:"))
        control_layout.addWidget(self.search_key_input)
        control_layout.addWidget(search_button)

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

    def insert_node(self):
        key_text = self.insert_key_input.text()
        # nombre = self.input_nombre.text()
        # cantidad = self.input_cantidad.text()
        # precio = self.input_precio.text()
        # categoria = self.input_categoria.text()

        if not key_text:
            QMessageBox.warning(self, "Error", "La clave no puede estar vacía.")
            return

        try:
            key = int(key_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "La clave debe ser un número entero.")
            return

        # Verificar si la clave ya existe
        if self.avl.buscar(key) is not None:
            QMessageBox.information(self, "Información", f"La clave {key} ya existe en el árbol.")
            return

        self.avl.insertar(key)
        self.update_ui()
        self.insert_key_input.clear()

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
            QMessageBox.information(self, "Resultado de Búsqueda", f"Clave: {result}")
        else:
            QMessageBox.information(self, "Resultado de Búsqueda", f"La clave {key} no se encontró en el árbol.")

    def update_ui(self):
        # Actualizar la visualización del árbol
        self.tree_view.draw_tree()

        # Actualizar la lista de inventario
        self.inventory_list.clear()
        in_order = self.avl.in_order_traversal()
        for clave in in_order:
            self.inventory_list.addItem(f"Clave: {clave}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
