# gui.py

import sys
from PyQt5.QtWidgets import ( # type: ignore
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem,
    QFileDialog, QFormLayout, QGroupBox, QComboBox
)
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QIcon  #type: ignore
from PyQt5.QtCore import Qt, QPointF, QTimer #type: ignore
from models.avl import AVLTree
from collections import deque

class AVLVisualizer(QGraphicsView):
    def __init__(self, avl_tree, parent=None):
        super().__init__(parent)
        self.avl_tree = avl_tree
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.node_radius = 15
        self.level_gap = 40
        self.horizontal_gap = 240
        self.setMinimumHeight(300)
        self.setMinimumWidth(500)
        
        self.search_path = []
        self.search_index = 0
        self.search_timer = QTimer()
        self.search_timer.timeout.connect(self.highlight_next_search_step)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.rotation_events = deque()
        self.is_animating = False
        self.highlighted_nodes = set()

        self.timer = QTimer()
        self.timer.timeout.connect(self.process_rotation_event)

    def add_rotation_event(self, event):
        self.rotation_events.append(event)
        if not self.is_animating:
            self.is_animating = True
            self.timer.start(1000)  # 1000 ms entre eventos

    def process_rotation_event(self):
        if self.rotation_events:
            event = self.rotation_events.popleft()
            tipo_rotacion, clave_y, clave_x = event
            print(f"Realizando {tipo_rotacion} en nodos y: {clave_y}, x: {clave_x}")
            
            self.highlighted_nodes = {clave_y, clave_x}
            self.draw_tree()

            QTimer.singleShot(800, self.clear_highlight)  # 800 ms de resaltado
        else:
            self.timer.stop()
            self.is_animating = False

    def clear_highlight(self):
        self.highlighted_nodes = set()
        self.draw_tree()

    def draw_tree(self):
        self.scene.clear()
        if self.avl_tree.raiz:
            self._draw_node(self.avl_tree.raiz, 0, self.width() / 2, 0)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())

    def _draw_node(self, node, depth, x, parent_x):
        y = depth * self.level_gap + self.node_radius * 2

        if node.izquierda:
            child_x = x - self.horizontal_gap / (depth + 1)
            child_y = y + self.level_gap
            line = self.scene.addLine(x, y, child_x, child_y, QPen(Qt.black, 2))
            self._draw_node(node.izquierda, depth + 1, child_x, x)
        if node.derecha:
            child_x = x + self.horizontal_gap / (depth + 1)
            child_y = y + self.level_gap
            line = self.scene.addLine(x, y, child_x, child_y, QPen(Qt.black, 2))
            self._draw_node(node.derecha, depth + 1, child_x, x)

        # Determinar el color del nodo
        if node.clave in self.highlighted_nodes:
            ellipse_color = QColor(250, 100, 100)  # Rojo para resaltar
        elif node.clave in self.search_path[:self.search_index + 1]:
            ellipse_color = QColor(100, 250, 100)  # Verde para el camino de búsqueda
        elif node.cantidad == 0:
            ellipse_color = QColor(200, 200, 200)  # Gris para productos fuera de stock
        else:
            ellipse_color = QColor(100, 200, 250)  # Azul claro por defecto

        ellipse = self.scene.addEllipse(x - self.node_radius, y - self.node_radius,
                                        self.node_radius * 2, self.node_radius * 2,
                                        QPen(Qt.black, 2), QBrush(ellipse_color))

        text = self.scene.addText(str(node.clave))
        text.setDefaultTextColor(Qt.black)
        text_width = text.boundingRect().width()
        text_height = text.boundingRect().height()
        text.setPos(x - text_width / 2, y - text_height / 2)

    def update_tree(self):
        self.draw_tree()
        
    def highlight_search_path(self, path):
        self.search_path = path
        self.search_index = -1
        self.search_timer.start(500)  
        
        

    def highlight_next_search_step(self):
        self.search_index += 1
        if self.search_index >= len(self.search_path):
            self.search_timer.stop()
            QTimer.singleShot(2000, self.clear_search_path)  # Limpiar después de 2 segundos
        self.draw_tree()

    def clear_search_path(self):
        self.search_path = []
        self.search_index = -1
        self.draw_tree()
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventario de Productos")
        self.setWindowIcon(QIcon("archivos\\inventario-icono-png.png"))
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
        control_layout = QVBoxLayout()

        # Estilo mejorado para los campos de entrada
        input_style = """
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: #f8f8f8;
                selection-background-color: #a6a6a6;
            }
            QLineEdit:focus {
                border-color: #66afe9;
            }
        """

        # Formulario de inserción horizontal
        insert_group = QGroupBox("Insertar Nuevo Producto")
        insert_layout = QHBoxLayout()
        
        self.insert_key_input = QLineEdit()
        self.insert_nombre_input = QLineEdit()
        self.insert_cantidad_input = QLineEdit()
        self.insert_precio_input = QLineEdit()
        self.insert_categoria_input = QLineEdit()

        self.insert_key_input.setPlaceholderText("Clave")
        self.insert_nombre_input.setPlaceholderText("Nombre")
        self.insert_cantidad_input.setPlaceholderText("Cantidad")
        self.insert_precio_input.setPlaceholderText("Precio")
        self.insert_categoria_input.setPlaceholderText("Categoría")

        for input_field in [self.insert_key_input, self.insert_nombre_input, 
                            self.insert_cantidad_input, self.insert_precio_input, 
                            self.insert_categoria_input]:
            input_field.setStyleSheet(input_style)
            insert_layout.addWidget(input_field)

        insert_button = QPushButton("Insertar")
        insert_button.clicked.connect(self.insert_node)
        insert_layout.addWidget(insert_button)

        insert_group.setLayout(insert_layout)
        control_layout.addWidget(insert_group)
        
        # Agregar nuevo grupo para actualizar cantidad y precio
        update_group = QGroupBox("Actualizar Producto")
        update_layout = QHBoxLayout()
        
        self.update_key_input = QLineEdit()
        self.update_cantidad_input = QLineEdit()
        self.update_precio_input = QLineEdit()

        self.update_key_input.setPlaceholderText("Clave")
        self.update_cantidad_input.setPlaceholderText("Nueva Cantidad")
        self.update_precio_input.setPlaceholderText("Nuevo Precio")

        for input_field in [self.update_key_input, self.update_cantidad_input, self.update_precio_input]:
            input_field.setStyleSheet(input_style)
            update_layout.addWidget(input_field)

        update_button = QPushButton("Actualizar")
        update_button.clicked.connect(self.update_product)
        update_layout.addWidget(update_button)

        update_group.setLayout(update_layout)
        control_layout.addWidget(update_group)

        # Eliminación y Búsqueda (mantenidos como estaban)
        actions_layout = QHBoxLayout()

        # Eliminación
        delete_layout = QVBoxLayout()
        self.delete_key_input = QLineEdit()
        self.delete_key_input.setPlaceholderText("Clave")
        self.delete_key_input.setStyleSheet(input_style)
        delete_button = QPushButton("Eliminar")
        delete_button.clicked.connect(self.delete_node)
        delete_layout.addWidget(QLabel("Eliminar:"))
        delete_layout.addWidget(self.delete_key_input)
        delete_layout.addWidget(delete_button)
        actions_layout.addLayout(delete_layout)

        # Búsqueda
        search_layout = QVBoxLayout()
        self.search_key_input = QLineEdit()
        self.search_key_input.setPlaceholderText("Clave")
        self.search_key_input.setStyleSheet(input_style)
        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.search_node)
        search_layout.addWidget(QLabel("Buscar:"))
        search_layout.addWidget(self.search_key_input)
        search_layout.addWidget(search_button)
        actions_layout.addLayout(search_layout)

        control_layout.addLayout(actions_layout)
        main_layout.addLayout(control_layout)
        
        price_range_layout = QVBoxLayout()
        price_range_group = QGroupBox("Buscar por Rango de Precios")
        price_range_form = QFormLayout()

        self.min_price_input = QLineEdit()
        self.max_price_input = QLineEdit()
        self.min_price_input.setPlaceholderText("Precio mínimo")
        self.max_price_input.setPlaceholderText("Precio máximo")

        price_range_form.addRow("Precio mínimo:", self.min_price_input)
        price_range_form.addRow("Precio máximo:", self.max_price_input)

        search_price_range_button = QPushButton("Buscar por Rango")
        search_price_range_button.clicked.connect(self.search_by_price_range)

        price_range_group.setLayout(price_range_form)
        price_range_layout.addWidget(price_range_group)
        price_range_layout.addWidget(search_price_range_button)

        actions_layout.addLayout(price_range_layout)
        
        # Agregar un nuevo grupo para la búsqueda por categoría
        category_search_group = QGroupBox("Buscar por Categoría")
        category_search_layout = QHBoxLayout()

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Hogar", "Cocina", "Electrodomesticos", "Deportes"])
        category_search_layout.addWidget(self.category_combo)

        search_category_button = QPushButton("Buscar por Categoría")
        search_category_button.clicked.connect(self.search_by_category)
        category_search_layout.addWidget(search_category_button)

        category_search_group.setLayout(category_search_layout)
        control_layout.addWidget(category_search_group)
        
        # Agregar un nuevo grupo para la búsqueda combinada
        combined_search_group = QGroupBox("Búsqueda Combinada")
        combined_search_layout = QFormLayout()

        self.combined_min_price_input = QLineEdit()
        self.combined_max_price_input = QLineEdit()
        self.combined_category_combo = QComboBox()
        self.combined_category_combo.addItems(["Todas", "Hogar", "Cocina", "Electrodomesticos", "Deportes"])

        combined_search_layout.addRow("Precio mínimo:", self.combined_min_price_input)
        combined_search_layout.addRow("Precio máximo:", self.combined_max_price_input)
        combined_search_layout.addRow("Categoría:", self.combined_category_combo)

        combined_search_button = QPushButton("Buscar")
        combined_search_button.clicked.connect(self.perform_combined_search)
        combined_search_layout.addRow(combined_search_button)

        combined_search_group.setLayout(combined_search_layout)
        main_layout.addWidget(combined_search_group)

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

        # Verificar si la clave ya existe
        if self.avl.buscar(key)[0] is not None:
            QMessageBox.warning(self, "Error", "La clave ya existe en el inventario.")
            return

        self.avl.insertar(key, nombre, cantidad, precio, categoria)
        self.update_ui()
        self.clear_insert_inputs()
        
    def update_product(self):
        key_text = self.update_key_input.text()
        quantity_text = self.update_cantidad_input.text()
        price_text = self.update_precio_input.text()

        if not key_text:
            QMessageBox.warning(self, "Error", "La clave es obligatoria.")
            return

        try:
            key = int(key_text)
            quantity = int(quantity_text) if quantity_text else None
            price = float(price_text) if price_text else None
        except ValueError:
            QMessageBox.warning(self, "Error", "Clave y cantidad deben ser enteros, y precio debe ser un número.")
            return

        if quantity is None and price is None:
            QMessageBox.warning(self, "Error", "Debe ingresar al menos una nueva cantidad o un nuevo precio.")
            return

        result = self.avl.actualizar_producto(key, quantity, price)
        if result:
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
            self.update_ui()
        else:
            QMessageBox.warning(self, "Error", "No se encontró un producto con la clave especificada.")

        self.update_key_input.clear()
        self.update_cantidad_input.clear()
        self.update_precio_input.clear()

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

        rotations = self.avl.eliminar(key)
        self.update_ui()
        self.delete_key_input.clear()

        # Crear mensaje detallado de las rotaciones
        if rotations:
            rotation_message = "Se realizaron las siguientes rotaciones:\n" + "\n".join(rotations)
        else:
            rotation_message = "No se requirieron rotaciones para balancear el árbol."

        QMessageBox.information(self, "Éxito", 
                                f"El nodo con clave {key} ha sido eliminado y el árbol se ha balanceado.\n\n{rotation_message}")

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

        result, search_path = self.avl.buscar(key)
        if result is not None:
            message = f"Clave: {result['clave']}\n"
            message += f"Nombre: {result['nombre']}\n"
            message += f"Cantidad: {result['cantidad']}\n"
            message += f"Precio: {result['precio']}\n"
            message += f"Categoría: {result['categoria']}"
            QMessageBox.information(self, "Resultado de Búsqueda", message)
            
            # Resaltar el camino de búsqueda
            self.tree_view.highlight_search_path(search_path)
        else:
            QMessageBox.information(self, "Resultado de Búsqueda", f"La clave {key} no se encontró en el árbol.")
        
        self.search_key_input.clear()

    def update_ui(self):
        self.tree_view.update_tree()
        self.inventory_list.clear()
        in_order = self.avl.in_order_traversal()
        for producto in in_order:
            self.inventory_list.addItem(
                f"Clave: {producto['clave']}, Nombre: {producto['nombre']}, "
                f"Cantidad: {producto['cantidad']}, Precio: {producto['precio']}, "
                f"Categoría: {producto['categoria']}"
            )
            
    def handle_rotation(self, tipo_rotacion, clave_y, clave_x):
        event = (tipo_rotacion, clave_y, clave_x)
        self.tree_view.add_rotation_event(event)
        mensaje = f"Rotación {'Derecha' if tipo_rotacion == 'rotacion_derecha' else 'Izquierda'}: y={clave_y} ↦ x={clave_x}"
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
        if not self.avl.json_file:
            file_name, _ = QFileDialog.getSaveFileName(self, "Guardar archivo JSON", "", "JSON Files (*.json)")
            if not file_name:
                return
            self.avl.set_json_file(file_name)
        
        try:
            self.avl.guardar_en_json()
            QMessageBox.information(self, "Éxito", "Datos guardados correctamente en JSON.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar el archivo JSON: {str(e)}")
            
    def search_by_price_range(self):
        try:
            min_price = float(self.min_price_input.text())
            max_price = float(self.max_price_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor, ingrese valores numéricos válidos para los precios.")
            return

        if min_price > max_price:
            QMessageBox.warning(self, "Error", "El precio mínimo no puede ser mayor que el precio máximo.")
            return

        results, search_path = self.avl.buscar_por_rango_precios(min_price, max_price)
        self.tree_view.highlight_search_path(search_path)

        if results:
            result_text = "Productos encontrados:\n\n"
            for producto in results:
                result_text += f"Clave: {producto['clave']}, Nombre: {producto['nombre']}, "
                result_text += f"Precio: {producto['precio']}, Cantidad: {producto['cantidad']}, "
                result_text += f"Categoría: {producto['categoria']}\n\n"
            
            QMessageBox.information(self, "Resultados de Búsqueda", result_text)
        else:
            QMessageBox.information(self, "Resultados de Búsqueda", "No se encontraron productos en el rango de precios especificado.")

        self.min_price_input.clear()
        self.max_price_input.clear()
        
    def search_by_category(self):
        categoria = self.category_combo.currentText()
        results, search_path = self.avl.buscar_por_categoria(categoria)
        self.tree_view.highlight_search_path(search_path)

        if results:
            result_text = f"Productos en la categoría '{categoria}':\n\n"
            for producto in results:
                result_text += f"ID: {producto['clave']}, Nombre: {producto['nombre']}, "
                result_text += f"Precio: {producto['precio']}, Cantidad: {producto['cantidad']}\n\n"
            
            QMessageBox.information(self, "Resultados de Búsqueda por Categoría", result_text)
        else:
            QMessageBox.information(self, "Resultados de Búsqueda por Categoría", 
                                    f"No se encontraron productos en la categoría '{categoria}'.")
                
    def perform_combined_search(self):
        try:
            precio_min = float(self.combined_min_price_input.text()) if self.combined_min_price_input.text() else None
            precio_max = float(self.combined_max_price_input.text()) if self.combined_max_price_input.text() else None
            categoria = self.combined_category_combo.currentText()
            categoria = None if categoria == "Todas" else categoria

            results, search_path = self.avl.busqueda_combinada(precio_min, precio_max, categoria)

            # Resaltar el camino de búsqueda en la visualización
            self.tree_view.highlight_search_path(search_path)

            if results:
                result_text = "Resultados de la búsqueda combinada:\n\n"
                for producto in results:
                    result_text += f"ID: {producto['clave']}, Nombre: {producto['nombre']}, "
                    result_text += f"Precio: {producto['precio']}, Cantidad: {producto['cantidad']}, "
                    result_text += f"Categoría: {producto['categoria']}\n\n"
                
                QMessageBox.information(self, "Resultados de Búsqueda Combinada", result_text)
            else:
                QMessageBox.information(self, "Resultados de Búsqueda Combinada", 
                                        "No se encontraron productos que cumplan con los criterios especificados.")

        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor, ingrese valores numéricos válidos para los precios.")

    # Agregar un método para limpiar la visualización del camino de búsqueda
    def clear_search_visualization(self):
        self.tree_view.clear_search_path()


                

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()