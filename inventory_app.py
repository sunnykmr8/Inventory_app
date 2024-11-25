import sys
import time
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QSpinBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QInputDialog  # Importing QInputDialog
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QPixmap, QIcon


class InventoryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.load_inventory()
        self.cart = []

    def initUI(self):
        # Main Layout with Tabs
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Purchase Tab
        self.purchase_tab = QWidget()
        self.tabs.addTab(self.purchase_tab, "Purchase")
        self.init_purchase_tab()

        # Reporting Tab
        self.reporting_tab = QWidget()
        self.tabs.addTab(self.reporting_tab, "Sales Reports")
        self.init_reporting_tab()

        self.setLayout(main_layout)

    def init_purchase_tab(self):
        layout = QVBoxLayout()

        # User Information
        user_layout = QHBoxLayout()
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.phone_label = QLabel("Phone No:")
        self.phone_input = QLineEdit()
        user_layout.addWidget(self.name_label)
        user_layout.addWidget(self.name_input)
        user_layout.addWidget(self.phone_label)
        user_layout.addWidget(self.phone_input)

        # Search and Product Selection
        search_layout = QHBoxLayout()
        self.search_label = QLabel("Search Product:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter product name or ID")
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)

        product_layout = QHBoxLayout()
        self.product_label = QLabel("Select Product:")
        self.product_combo = QComboBox()
        self.product_combo.currentIndexChanged.connect(self.display_product_image)
        product_layout.addWidget(self.product_label)
        product_layout.addWidget(self.product_combo)

        # Product Image
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        image_layout = QHBoxLayout()
        image_layout.addStretch()
        image_layout.addWidget(self.image_label)
        image_layout.addStretch()

        # Quantity Selection
        quantity_layout = QHBoxLayout()
        self.quantity_label = QLabel("Quantity:")
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        quantity_layout.addWidget(self.quantity_label)
        quantity_layout.addWidget(self.quantity_spin)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_to_cart_btn = QPushButton("Add to Cart")
        self.add_to_cart_btn.setIcon(QIcon.fromTheme("document-save"))
        self.checkout_btn = QPushButton("Checkout")
        self.checkout_btn.setIcon(QIcon.fromTheme("document-save"))
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setIcon(QIcon.fromTheme("application-exit"))
        button_layout.addWidget(self.add_to_cart_btn)
        button_layout.addWidget(self.checkout_btn)
        button_layout.addWidget(self.exit_btn)

        # Display Area
        self.display_label = QLabel("")
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setStyleSheet("QLabel { background-color : lightgray; padding: 10px; }")
        self.display_label.setFixedHeight(150)

        # Add layouts to main purchase layout
        layout.addLayout(user_layout)
        layout.addLayout(search_layout)
        layout.addLayout(product_layout)
        layout.addLayout(image_layout)
        layout.addLayout(quantity_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.display_label)

        self.purchase_tab.setLayout(layout)

        # Connect buttons
        self.add_to_cart_btn.clicked.connect(self.add_to_cart)
        self.checkout_btn.clicked.connect(self.process_checkout)
        self.exit_btn.clicked.connect(self.close)

    def init_reporting_tab(self):
        layout = QVBoxLayout()

        # Sales Report Table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["Name", "Phone", "Product", "Quantity", "Amount & Time"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Refresh Button
        refresh_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.refresh_btn)

        layout.addLayout(refresh_layout)
        layout.addWidget(self.sales_table)

        self.reporting_tab.setLayout(layout)

        # Connect buttons
        self.refresh_btn.clicked.connect(self.load_sales_report)

        # Load sales report initially
        self.load_sales_report()

    def load_inventory(self):
        try:
            with open('Inventory.txt', 'r') as fd:
                self.products = [line.strip().split(',') for line in fd if line.strip()]
            self.filtered_products = self.products.copy()
            self.populate_product_combo()
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Inventory.txt not found.")
            sys.exit()

    def populate_product_combo(self):
        self.product_combo.blockSignals(True)  # Prevent triggering signal during population
        self.product_combo.clear()
        for product in self.filtered_products:
            product_id, product_name, price, qty = product
            self.product_combo.addItem(
                f"{product_name} (ID: {product_id}, Price: {price}, Available: {qty})",
                userData=product
            )
        self.product_combo.blockSignals(False)
        if self.filtered_products:
            self.display_product_image()

    def filter_products(self):
        query = self.search_input.text().strip().lower()
        if not query:
            self.filtered_products = self.products.copy()
        else:
            self.filtered_products = [
                product for product in self.products 
                if query in product[0].lower() or query in product[1].lower()
            ]
        self.populate_product_combo()

    def display_product_image(self):
        product = self.product_combo.currentData()
        if product:
            product_id = product[0]
            image_path = os.path.join('images', f"{product_id}.png")
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
                self.image_label.setPixmap(pixmap)
            else:
                self.image_label.setText("No Image")
        else:
            self.image_label.setText("No Image")

    def add_to_cart(self):
        product_data = self.product_combo.currentData()
        quantity = self.quantity_spin.value()

        if not product_data or quantity <= 0:
            QMessageBox.warning(self, "Selection Error", "Please select a valid product and quantity.")
            return

        product_id, product_name, price, qty_available = product_data
        try:
            price = int(price)
            qty_available = int(qty_available)
        except ValueError:
            QMessageBox.critical(self, "Data Error", "Invalid price or quantity in inventory.")
            return

        if quantity > qty_available:
            QMessageBox.warning(self, "Insufficient Quantity", f"Only {qty_available} available.")
            return

        self.cart.append((product_name, quantity, price))
        self.display_message(f"{quantity} x {product_name} added to cart.", success=True)

    def process_checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "Cart Empty", "No items in the cart to checkout.")
            return

        total_amount = sum(quantity * price for _, quantity, price in self.cart)
        amount_paid, ok = QInputDialog.getDouble(self, "Amount Paid", "Enter amount paid:", 0.0, 0.0)
        if ok:
            if amount_paid < total_amount:
                QMessageBox.warning(self, "Insufficient Amount", "Amount paid is less than the total amount.")
                return

            change = amount_paid - total_amount
            self.log_sales(total_amount)
            self.display_message(f"Checkout successful! Total: ₹{total_amount}, Change: ₹{change:.2f}", success=True)
            self.cart.clear()
        else:
            self.display_message("Checkout cancelled.", success=False)

    def log_sales(self, total_amount):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        products = ', '.join([f"{name} x {quantity}" for name, quantity, _ in self.cart])
        quantity = sum(quantity for _, quantity, _ in self.cart)

        sales_detail = f"{name},{phone},{products},{quantity},{total_amount} @ {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        with open('SalesReport.txt', 'a') as fd:
            fd.write(sales_detail)
        self.load_sales_report()  # Refresh the sales report

    def load_sales_report(self):
        try:
            with open('SalesReport.txt', 'r') as fd:
                self.sales_table.setRowCount(0)
                for line in fd:
                    if line.strip():
                        name, phone, products, quantity, amount_time = line.strip().split(',', 4)
                        row_position = self.sales_table.rowCount()
                        self.sales_table.insertRow(row_position)
                        self.sales_table.setItem(row_position, 0, QTableWidgetItem(name))
                        self.sales_table.setItem(row_position, 1, QTableWidgetItem(phone))
                        self.sales_table.setItem(row_position, 2, QTableWidgetItem(products))
                        self.sales_table.setItem(row_position, 3, QTableWidgetItem(quantity))
                        self.sales_table.setItem(row_position, 4, QTableWidgetItem(amount_time))
        except FileNotFoundError:
            self.sales_table.setRowCount(0)  # Clear table if the report file doesn't exist

    def display_message(self, message, success=True):
        self.display_label.setText(message)
        color = "green" if success else "red"
        self.display_label.setStyleSheet(f"QLabel {{ background-color : {color}; padding: 10px; }}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    inventory_app = InventoryApp()
    inventory_app.show()
    sys.exit(app.exec_())
