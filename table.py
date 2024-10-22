import mysql.connector

# Database connection configuration
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'icms'
}

# Establishing the connection to the database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# SQL commands to create tables if they don't exist
create_tables_queries = [
    """
    CREATE TABLE IF NOT EXISTS Products (
        product_id INT  PRIMARY KEY,
        product_name VARCHAR(255) NOT NULL,
        product_description TEXT,
        price DECIMAL(10, 2),
        quantity INT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Inventory (
        inventory_id INT  PRIMARY KEY,
        product_id INT,
        quantity INT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INT  PRIMARY KEY,
        product_id INT,
        product_name VARCHAR(225),
        customer_name VARCHAR(255),
        customer_address VARCHAR(255),
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expected_delivery_date TIMESTAMP,
        quantity INT,
        total_amount DECIMAL(10, 2),
        status ENUM('processing', 'confirmed', 'shipped', 'delivered') NOT NULL,
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        transaction_type ENUM('IN', 'OUT') NOT NULL,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10, 2),
        FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Alerts (
        alert_id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT,
        alert_type VARCHAR(255),
        alert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Suppliers (
        supplier_id INT  PRIMARY KEY,
        supplier_name VARCHAR(255) NOT NULL,
        product_count INT NOT NULL,
        contact_phone VARCHAR(255),
        contact_email VARCHAR(255),
        performance ENUM('High', 'Medium', 'Low'),
        avg_lead_time INT,
        status ENUM('Active', 'Inactive')
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS SupplierOrders (
        supplier_order_id INT  PRIMARY KEY,
        supplier_id INT,
        supplier_name VARCHAR(255) NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        order_count INT NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expected_delivery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status ENUM('pending', 'delivered'),
        total_amount DECIMAL(10, 2),
        FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE users (
        id INT NOT NULL AUTO_INCREMENT,
        email VARCHAR(255) NOT NULL UNIQUE,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
    )
    """
]

# Executing the SQL commands
for query in create_tables_queries:
    cursor.execute(query)

# Closing the cursor and connection
cursor.close()
conn.close()

print("All tables created successfully (if they didn't already exist).")
