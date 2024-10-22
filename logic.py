import mysql.connector
from datetime import datetime
import numpy as np

# Database connection configuration
db_config = {
    'user': '[username]',  # replace with actual username
    'password': '[password]', # replace with actual password
    'host': 'localhost',
    'database': 'icms'
}


def authenticate_user(email, password):
    try:
        # Establish connection to the database (example)
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to fetch the user based on email and password
        query = "SELECT username, email FROM users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user_data = cursor.fetchone()

        if user_data:
            # If user exists, return True and user_data
            return True, user_data
        else:
            # Return False if no matching user is found
            return False, None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False, None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def fetch_dashboard_data():
    # Get the current month and year
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Establishing the connection to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Define queries to fetch data for the current month
    queries = {
        'orders_count': f"""
            SELECT COUNT(*) 
            FROM Orders 
            WHERE YEAR(order_date) = {current_year} 
            AND MONTH(order_date) = {current_month}
        """,
        'deliveries_count': f"""
            SELECT COUNT(*) 
            FROM Orders 
            WHERE YEAR(order_date) = {current_year} 
            AND MONTH(order_date) = {current_month}
        """,
        'revenue_total': f"""
            SELECT SUM(total_amount) 
            FROM Orders 
            WHERE status = 'delivered' 
            AND YEAR(order_date) = {current_year} 
            AND MONTH(order_date) = {current_month}
        """
    }

    # Execute queries and fetch results
    data = {}
    for key, query in queries.items():
        cursor.execute(query)
        result = cursor.fetchone()
        data[key] = result[0] if result else 0

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return data

def fetch_warehouse_utilization():
    # Set maximum capacity of the warehouse
    max_capacity = 10000

    # Establishing the connection to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Query to fetch total quantity of all products
        query = "SELECT SUM(quantity) AS total_quantity FROM products"
        cursor.execute(query)
        result = cursor.fetchone()
        total_quantity = result[0] if result[0] else 0

        # Calculate used space and available space
        used_space = total_quantity
        available_space = max_capacity - used_space

        # Ensure available space isn't negative
        available_space = max(0, available_space)

        data = [used_space,available_space]

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

    return data


def fetch_top_selling_products():
    query = """
    SELECT product_name, SUM(quantity) AS total_units_sold
    FROM Orders
    GROUP BY product_name
    ORDER BY total_units_sold DESC
    LIMIT 5;
    """

    # Establishing the connection to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute query
    cursor.execute(query)
    results = cursor.fetchall()

    # Closing cursor and connection
    cursor.close()
    conn.close()

    return results


def fetch_recent_orders():
    query = """
    SELECT i.product_id, i.product_name, i.price
    FROM products i
    JOIN Orders o ON i.product_id = o.product_id
    WHERE o.order_date >= NOW() - INTERVAL 30 DAY
    ORDER BY o.order_date DESC
    LIMIT 3;

    """
    # Establishing the connection to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute query
    cursor.execute(query)
    data = cursor.fetchall()

    # Define header
    formatted_data = [["Product ID", "Product Name", "Product Price"]]

    # Convert each row from tuple to list and format Decimal values
    for row in data:
        product_id, product_name, price = row
        formatted_row = [
            str(product_id),
            product_name,
            f"${price:.2f}"  # Format Decimal to string with currency symbol
        ]
        formatted_data.append(formatted_row)

    # Closing cursor and connection
    cursor.close()
    conn.close()

    return formatted_data


def fetch_recently_added_items():
    query = """
    SELECT product_id, product_name, price
    FROM products
    WHERE date >= NOW() - INTERVAL 30 DAY
    ORDER BY date DESC
    LIMIT 3;
    """
    # Establishing the connection to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute query
    cursor.execute(query)
    data = cursor.fetchall()

    # Define header
    formatted_data = [["Product ID", "Product Name", "Product Price"]]

    # Convert each row from tuple to list and format Decimal values
    for row in data:
        product_id, product_name, price = row
        formatted_row = [
            str(product_id),
            product_name,
            f"${price:.2f}"  # Format Decimal to string with currency symbol
        ]
        formatted_data.append(formatted_row)

    # Closing cursor and connection
    cursor.close()
    conn.close()

    return formatted_data


def fetch_inventory_data():

    # SQL query to fetch all data from the Inventory table
    query = """
    SELECT product_id, product_name, price, quantity, date
    FROM products;
    """

    # Establishing the connection to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)
    data = cursor.fetchall()

    # Define the header
    formatted_data = [["Product ID", "Product Name", "Product Price", "Quantity", "Date Added"]]

    # Convert each row from tuple to list and format Decimal values
    for row in data:
        product_id, product_name, price, quantity, date = row
        formatted_row = [
            str(product_id),
            product_name,
            f"${price:.2f}",  # Format Decimal to string with currency symbol
            str(quantity),
            date.strftime("%Y-%m-%d %H:%M:%S")  # Format date to a readable string
        ]
        formatted_data.append(formatted_row)

    # Closing the cursor and connection
    cursor.close()
    conn.close()

    # Return the formatted data
    return formatted_data


def fetch_inventory_data_filtered(search_query, sort_by):
    # Build the base query
    query = """
    SELECT product_id, product_name, price, quantity, date
    FROM products
    WHERE 1=1
    """
    
    # Add conditions for search, sort, and status
    conditions = []
    params = []
    
    # Check if search_query is numeric and search by product_id if it is
    if search_query.isdigit():
        query += " AND product_id = %s"
        params.append(search_query)
    elif search_query:
        query += " AND product_name LIKE %s"
        params.append(f"%{search_query}%")
    
    # Add sorting conditions
    if sort_by == "Most Recent Order":
        query += " ORDER BY date DESC"
    elif sort_by == "Least Recent Order":
        query += " ORDER BY date ASC"
    else:
        query += " ORDER BY product_name ASC"
    
    # Execute the query with the provided parameters
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall()
    
    # Format the data as before
    formatted_data = [["Product ID", "Product Name", "Product Price", "Quantity", "Date Added"]]
    for row in data:
        product_id, product_name, price, quantity, date = row
        formatted_row = [
            str(product_id),
            product_name,
            f"${price:.2f}",
            str(quantity),
            date.strftime("%Y-%m-%d %H:%M:%S")
        ]
        formatted_data.append(formatted_row)
    
    cursor.close()
    conn.close()
    return formatted_data


import mysql.connector

def fetch_order_metrics():
    # Define the queries for each metric
    metrics_queries = {
        'total_orders': "SELECT COUNT(*) FROM Orders",
        'shipped_orders': "SELECT COUNT(*) FROM Orders WHERE status = 'shipped'",
        'delivered_orders': "SELECT COUNT(*) FROM Orders WHERE status = 'delivered'"
    }

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Dictionary to store metric results
    metrics = {}
    
    for key, query in metrics_queries.items():
        cursor.execute(query)
        result = cursor.fetchone()
        metrics[key] = result[0] if result else 0
    
    # Close the cursor and connection
    cursor.close()
    conn.close()
    
    return metrics



def fetch_orders_data():
    # Define the query to fetch selected columns from the Orders table
    query = """
    SELECT order_id, product_name, customer_name, customer_address, 
           order_date, expected_delivery_date, total_amount, status 

    FROM Orders
    """
    
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Execute the query
    cursor.execute(query)
    data = cursor.fetchall()
    
    # Format the data as a list
    formatted_data = [["Order ID", "Product Name", "Customer Name", 
                       "Customer Address", "Order Date", "Expected Delivery Date", 
                       "Total Amount", "Status"]]
    
    for row in data:
        order_id, product_name, customer_name, customer_address, \
        order_date, expected_delivery_date, total_amount, status = row
        formatted_row = [
            str(order_id),
            product_name,
            customer_name,
            customer_address,
            order_date.strftime("%Y-%m-%d %H:%M:%S") if order_date else "",
            expected_delivery_date.strftime("%Y-%m-%d %H:%M:%S") if expected_delivery_date else "",
            f"${total_amount:.2f}",
            status

        ]
        formatted_data.append(formatted_row)
    
    # Close the cursor and connection
    cursor.close()
    conn.close()
    
    return formatted_data


def fetch_orders_data_filtered(search_query, sort_by, status_filter):
    # Build the base query
    query = """
    SELECT order_id, product_name, customer_name, order_date, expected_delivery_date, quantity, total_amount, status
    FROM Orders
    WHERE (order_id LIKE %s OR product_name LIKE %s OR customer_name LIKE %s)
    """

    # Add conditions for sort and status if they are selected
    conditions = []
    params = [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"]

    if status_filter and status_filter != "Status":
        query += " AND status = %s"
        params.append(status_filter)

    if sort_by == "Most Recent Order":
        query += " ORDER BY order_date DESC"
    elif sort_by == "Least Recent Order":
        query += " ORDER BY order_date ASC"
    else:
        query += " ORDER BY order_id ASC"

    # Execute the query with the provided parameters
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall()

    # Format the data
    formatted_data = [["Order ID", "Product Name", "Customer Name", "Order Date", "Expected Delivery Date", "Quantity", "Total Amount", "Status"]]
    for row in data:
        formatted_data.append(list(row))

    cursor.close()
    conn.close()
    return formatted_data


def fetch_supply_metrics():
    # Define the SQL queries to fetch total suppliers, pending orders, and average lead time
    total_suppliers_query = "SELECT COUNT(*) FROM Suppliers"
    pending_orders_query = "SELECT COUNT(*) FROM SupplierOrders WHERE status = 'pending'"
    avg_lead_time_query = "SELECT AVG(avg_lead_time) FROM Suppliers"

    # Initialize variables to store the results
    total_suppliers = 0
    pending_orders = 0
    avg_lead_time = 0.0

    # Connect to the database
    conn = mysql.connector.connect(**db_config)  # Ensure db_config is properly defined
    cursor = conn.cursor()

    try:
        # Execute the query to fetch the total number of suppliers
        cursor.execute(total_suppliers_query)
        total_suppliers = cursor.fetchone()[0]  # Fetch the count value

        # Execute the query to fetch the total number of pending orders
        cursor.execute(pending_orders_query)
        pending_orders = cursor.fetchone()[0]  # Fetch the count value

        # Execute the query to fetch the average lead time of all suppliers
        cursor.execute(avg_lead_time_query)
        avg_lead_time = cursor.fetchone()[0]  # Fetch the average value

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

    # Return the three metrics
    return total_suppliers, pending_orders, avg_lead_time


def fetch_supplier_details():
    # Define the query to fetch supplier details
    query = """
    SELECT supplier_id, supplier_name, product_count, contact_email, performance, avg_lead_time, status
    FROM Suppliers
    """
    
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Execute the query
    cursor.execute(query)
    data = cursor.fetchall()

    # Format the data
    formatted_data = [["Supplier ID", "Supplier Name", "Product Count", "Contact Email", "Performance", "Average Lead Time","Status"]]
    for row in data:
        formatted_data.append(list(row))

    # Clean up
    cursor.close()
    conn.close()
    
    return formatted_data


def fetch_supplier_details_filtered(search_query, status_filter, performance_filter):
    # Base query
    query = """
    SELECT supplier_id, supplier_name, product_count, contact_email, performance, avg_lead_time, status
    FROM Suppliers
    WHERE (supplier_id LIKE %s OR supplier_name LIKE %s)
    """
    
    # Initialize parameters list
    params = [f"%{search_query}%", f"%{search_query}%"]

    # Add conditions for performance filter if selected
    if performance_filter and performance_filter != "All Performances":
        query += " AND performance = %s"
        params.append(performance_filter)

    # Add conditions for status filter if selected
    if status_filter == "Active":
        query += " AND status = %s"
        params.append("Active")
    elif status_filter == "In Active":
        query += " AND status = %s"
        params.append("Inactive")

    # Add default sorting condition
    query += " ORDER BY supplier_name ASC"  # Default sorting by supplier name

    # Execute the query with the provided parameters
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall()

    # Format the data
    formatted_data = [["Supplier ID", "Supplier Name", "Product Count", "Contact Email", "Performance", "Average Lead Time", "Status"]]
    for row in data:
        formatted_data.append(list(row))

    cursor.close()
    conn.close()
    return formatted_data


def fetch_supplier_orders():
    # Query to select all columns from SupplierOrders table
    query = """
    SELECT supplier_order_id, supplier_id, supplier_name, product_name, order_count, order_date, expected_delivery_date, status, total_amount
    FROM SupplierOrders
    """

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)
    data = cursor.fetchall()

    # Format the data into a list of lists
    formatted_data = [["Order ID", "Supplier ID", "Supplier Name", "Product Name", "Order Count", "Order Date", "Expected Delivery Date", "Status", "Total Amount"]]
    for row in data:
        formatted_data.append(list(row))

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return formatted_data

def fetch_supplier_orders_filtered(search_query, sort_by, status):
    # Base query
    query = """
    SELECT supplier_order_id, supplier_id, supplier_name, product_name, order_count, order_date, expected_delivery_date, status, total_amount
    FROM SupplierOrders
    WHERE (CAST(order_id AS CHAR) LIKE %s OR supplier_name LIKE %s OR product_name LIKE %s)
    """

    # Initialize parameters list
    params = [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"]

    # Add status filter if it's selected
    if status and status != "Status":
        query += " AND status = %s"
        params.append(status)

    # Add sorting condition based on sort_by parameter
    if sort_by == "Most Recent Order":
        query += " ORDER BY order_date DESC"
    elif sort_by == "Least Recent Order":
        query += " ORDER BY order_date ASC"
    else:
        query += " ORDER BY order_id ASC"  # Default sorting by order ID

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the query with the parameters
    cursor.execute(query, params)
    data = cursor.fetchall()

    # Format the data into a list of lists
    formatted_data = [["Order ID", "Supplier ID", "Supplier Name", "Product Name", "Order Count", "Order Date", "Expected Delivery Date", "Status", "Total Amount"]]
    for row in data:
        formatted_data.append(list(row))

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return formatted_data


def fetch_average_lead_times():
    # Define the SQL query to fetch supplier names and their average lead times
    query = """
    SELECT supplier_name, avg_lead_time
    FROM Suppliers
    """

    # Connect to the database
    conn = mysql.connector.connect(**db_config)  # Ensure db_config is properly defined
    cursor = conn.cursor()

    # Initialize lists to store the supplier names and lead times
    suppliers = []
    lead_times = []

    try:
        # Execute the query
        cursor.execute(query)
        data = cursor.fetchall()

        # Process the query results and separate the data into two lists
        for row in data:
            suppliers.append(row[0])     # Supplier name
            lead_times.append(row[1])    # Average lead time

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

    # Return the data as two separate lists
    return suppliers, lead_times


def fetch_today_metrics():
    # SQL queries to fetch today's metrics
    revenue_query = "SELECT SUM(total_amount) FROM Transactions WHERE transaction_type = 'IN' AND DATE(transaction_date) = CURDATE()"
    costs_query = "SELECT SUM(total_amount) FROM Transactions WHERE transaction_type = 'OUT' AND DATE(transaction_date) = CURDATE()"
    fulfillment_rate_query = """
    SELECT (SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) / COUNT(*)) * 100 
    FROM Orders 
    WHERE DATE(order_date) = CURDATE()
    """
    top_suppliers_query = """
    SELECT supplier_name, SUM(order_count) 
    FROM SupplierOrders 
    WHERE DATE(order_date) = CURDATE() 
    GROUP BY supplier_name 
    ORDER BY SUM(order_count) DESC LIMIT 4
    """
    units_sold_query = "SELECT SUM(quantity) FROM Transactions WHERE DATE(transaction_date) = CURDATE()"
    max_units_query = "SELECT SUM(quantity) FROM products"
    
    # Additional queries for hourly revenue and costs
    hourly_revenue_query = """
    SELECT HOUR(transaction_date) AS hour, SUM(total_amount) 
    FROM Transactions 
    WHERE transaction_type = 'IN' AND DATE(transaction_date) = CURDATE() 
    GROUP BY HOUR(transaction_date)
    ORDER BY hour
    """
    
    hourly_cost_query = """
    SELECT HOUR(transaction_date) AS hour, SUM(total_amount) 
    FROM Transactions 
    WHERE transaction_type = 'OUT' AND DATE(transaction_date) = CURDATE() 
    GROUP BY HOUR(transaction_date)
    ORDER BY hour
    """

    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()

        # Fetch today's revenue
        cursor.execute(revenue_query)
        revenue_result = cursor.fetchone()
        revenue = revenue_result[0] if revenue_result and revenue_result[0] is not None else 0

        # Fetch today's costs
        cursor.execute(costs_query)
        costs_result = cursor.fetchone()
        costs = costs_result[0] if costs_result and costs_result[0] is not None else 0

        # Calculate profit
        profit = revenue - costs

        # Fetch today's order fulfillment rate
        cursor.execute(fulfillment_rate_query)
        fulfillment_rate_result = cursor.fetchone()
        fulfillment_rate = fulfillment_rate_result[0] if fulfillment_rate_result and fulfillment_rate_result[0] is not None else 0

        # Fetch top suppliers for today
        cursor.execute(top_suppliers_query)
        top_suppliers = cursor.fetchall()

        # Fetch total units sold for today
        cursor.execute(units_sold_query)
        units_sold_result = cursor.fetchone()
        total_units_sold = units_sold_result[0] if units_sold_result and units_sold_result[0] is not None else 1

        # Fetch maximum units from the inventory
        cursor.execute(max_units_query)
        max_units_result = cursor.fetchone()
        max_units = max_units_result[0] if max_units_result and max_units_result[0] is not None else 0

        # Fetch hourly revenue data
        cursor.execute(hourly_revenue_query)
        hourly_revenue_results = cursor.fetchall()
        hourly_revenue = [0] * 24
        for hour, amount in hourly_revenue_results:
            hourly_revenue[hour] = amount

        # Fetch hourly cost data
        cursor.execute(hourly_cost_query)
        hourly_cost_results = cursor.fetchall()
        hourly_costs = [0] * 24
        for hour, amount in hourly_cost_results:
            hourly_costs[hour] = amount

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Prepare the data for your GUI
    supplier_names = [supplier[0] for supplier in top_suppliers]
    supplier_values = [supplier[1] for supplier in top_suppliers]

    hourly_revenue = np.array(hourly_revenue).flatten()
    hourly_costs = np.array(hourly_costs).flatten()

    return revenue, profit, fulfillment_rate, supplier_names, supplier_values, total_units_sold, max_units, hourly_revenue, hourly_costs

metrics = fetch_today_metrics()
if metrics:
    revenue, profit, fulfillment_rate, supplier_names, supplier_values, total_units_sold, max_units, hourly_revenue, hourly_costs = metrics
    # Continue with your processing
else:
    print("Failed to fetch metrics.")

import mysql.connector
from calendar import monthrange

import mysql.connector
from calendar import monthrange

def fetch_this_month_metrics():
    # SQL queries to fetch this month's metrics
    revenue_query = """
    SELECT SUM(total_amount) 
    FROM Transactions 
    WHERE transaction_type = 'IN' AND YEAR(transaction_date) = YEAR(CURDATE()) 
    AND MONTH(transaction_date) = MONTH(CURDATE())
    """
    costs_query = """
    SELECT SUM(total_amount) 
    FROM Transactions 
    WHERE transaction_type = 'OUT' AND YEAR(transaction_date) = YEAR(CURDATE()) 
    AND MONTH(transaction_date) = MONTH(CURDATE())
    """
    fulfillment_rate_query = """
    SELECT (SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) / COUNT(*)) * 100 
    FROM Orders 
    WHERE YEAR(order_date) = YEAR(CURDATE()) 
    AND MONTH(order_date) = MONTH(CURDATE())
    """
    top_suppliers_query = """
    SELECT supplier_name, SUM(order_count) 
    FROM SupplierOrders 
    WHERE YEAR(order_date) = YEAR(CURDATE()) 
    AND MONTH(order_date) = MONTH(CURDATE())
    GROUP BY supplier_name 
    ORDER BY SUM(order_count) DESC LIMIT 4
    """
    units_sold_query = """
    SELECT SUM(quantity) 
    FROM Transactions 
    WHERE YEAR(transaction_date) = YEAR(CURDATE()) 
    AND MONTH(transaction_date) = MONTH(CURDATE())
    """
    max_units_query = "SELECT SUM(quantity) FROM products"
    
    # Additional queries for monthly revenue and costs
    monthly_revenue_query = """
    WITH RECURSIVE date_sequence AS (
        SELECT DATE_FORMAT(CURRENT_DATE, '%Y-%m-01') AS day
        UNION ALL
        SELECT DATE_ADD(day, INTERVAL 1 DAY)
        FROM date_sequence
        WHERE day < LAST_DAY(CURRENT_DATE)
    )
    SELECT 
        DAY(ds.day) AS day,
        COALESCE(SUM(t.total_amount), 0) AS daily_revenue
    FROM date_sequence ds
    LEFT JOIN transactions t 
    ON DATE(t.transaction_date) = ds.day
    AND t.transaction_type = 'IN'
    WHERE MONTH(ds.day) = MONTH(CURRENT_DATE)
    AND YEAR(ds.day) = YEAR(CURRENT_DATE)
    GROUP BY ds.day
    ORDER BY ds.day ASC;
    """
    
    monthly_cost_query = """
    WITH RECURSIVE date_sequence AS (
        SELECT DATE_FORMAT(CURRENT_DATE, '%Y-%m-01') AS day
        UNION ALL
        SELECT DATE_ADD(day, INTERVAL 1 DAY)
        FROM date_sequence
        WHERE day < LAST_DAY(CURRENT_DATE)
    )
    SELECT 
        DAY(ds.day) AS day,
        COALESCE(SUM(t.total_amount), 0) AS daily_cost
    FROM date_sequence ds
    LEFT JOIN transactions t 
    ON DATE(t.transaction_date) = ds.day
    AND t.transaction_type = 'OUT'
    WHERE MONTH(ds.day) = MONTH(CURRENT_DATE)
    AND YEAR(ds.day) = YEAR(CURRENT_DATE)
    GROUP BY ds.day
    ORDER BY ds.day ASC;
    """

    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()

        # Fetch the current year and month
        cursor.execute("SELECT YEAR(CURDATE()), MONTH(CURDATE())")
        year_month_result = cursor.fetchone()
        year, month = year_month_result if year_month_result else (None, None)

        if not year or not month:
            raise ValueError("Failed to fetch current year or month.")

        # Fetch this month's revenue
        cursor.execute(revenue_query)
        revenue_result = cursor.fetchone()
        revenue = revenue_result[0] if revenue_result and revenue_result[0] is not None else 0

        # Fetch this month's costs
        cursor.execute(costs_query)
        costs_result = cursor.fetchone()
        costs = costs_result[0] if costs_result and costs_result[0] is not None else 0

        # Calculate profit
        profit = revenue - costs

        # Fetch this month's order fulfillment rate
        cursor.execute(fulfillment_rate_query)
        fulfillment_rate_result = cursor.fetchone()
        fulfillment_rate = fulfillment_rate_result[0] if fulfillment_rate_result and fulfillment_rate_result[0] is not None else 0

        # Fetch top suppliers for this month
        cursor.execute(top_suppliers_query)
        top_suppliers = cursor.fetchall()

        # Fetch total units sold for this month
        cursor.execute(units_sold_query)
        units_sold_result = cursor.fetchone()
        units_sold = units_sold_result[0] if units_sold_result and units_sold_result[0] is not None else 0

        # Fetch maximum units from the inventory
        cursor.execute(max_units_query)
        max_units_result = cursor.fetchone()
        maxi_units = max_units_result[0] if max_units_result and max_units_result[0] is not None else 0

        # Fetch monthly revenue data
        cursor.execute(monthly_revenue_query)
        monthly_revenue_results = cursor.fetchall()

        # Get the correct number of days in the current month
        days_in_month = monthrange(year, month)[1]
        monthly_revenue = [0] * days_in_month
        for day, amount in monthly_revenue_results:
            monthly_revenue[day - 1] = amount  # Adjust for 0-based index

        # Fetch monthly cost data
        cursor.execute(monthly_cost_query)
        monthly_cost_results = cursor.fetchall()
        monthly_costs = [0] * days_in_month
        for day, amount in monthly_cost_results:
            monthly_costs[day - 1] = amount  # Adjust for 0-based index

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Prepare the data for your GUI
    supplier_names = [supplier[0] for supplier in top_suppliers]
    supplier_values = [supplier[1] for supplier in top_suppliers]

    return revenue, profit, fulfillment_rate, supplier_names, supplier_values, units_sold, maxi_units, monthly_revenue, monthly_costs


def fetch_this_week_metrics():
    # SQL queries to fetch this week's metrics
    revenue_query = """
    SELECT SUM(total_amount) 
    FROM Transactions 
    WHERE transaction_type = 'IN' 
    AND YEARWEEK(transaction_date, 1) = YEARWEEK(CURDATE(), 1)
    """
    costs_query = """
    SELECT SUM(total_amount) 
    FROM Transactions 
    WHERE transaction_type = 'OUT' 
    AND YEARWEEK(transaction_date, 1) = YEARWEEK(CURDATE(), 1)
    """
    fulfillment_rate_query = """
    SELECT (SUM(CASE WHEN status = 'deliverd' THEN 1 ELSE 0 END) / COUNT(*)) * 100 
    FROM Orders 
    WHERE YEARWEEK(order_date, 1) = YEARWEEK(CURDATE(), 1)
    """
    top_suppliers_query = """
    SELECT supplier_name, SUM(order_count) 
    FROM SupplierOrders 
    WHERE YEARWEEK(order_date, 1) = YEARWEEK(CURDATE(), 1)
    GROUP BY supplier_name 
    ORDER BY SUM(order_count) DESC LIMIT 4
    """
    units_sold_query = """
    SELECT SUM(quantity) 
    FROM Transactions 
    WHERE YEARWEEK(transaction_date, 1) = YEARWEEK(CURDATE(), 1)
    """
    max_units_query = "SELECT SUM(quantity) FROM products"
    
    # Additional queries for weekly revenue and costs
    weekly_revenue_query = """
   SELECT
        d.day_name AS day,
        COALESCE(SUM(t.total_amount), 0) AS daily_revenue
    FROM 
        (SELECT 'Monday' AS day_name, 2 AS day_number UNION ALL
        SELECT 'Tuesday', 3 UNION ALL
        SELECT 'Wednesday', 4 UNION ALL
        SELECT 'Thursday', 5 UNION ALL
        SELECT 'Friday', 6 UNION ALL
        SELECT 'Saturday', 7 UNION ALL
        SELECT 'Sunday', 1) AS d
    LEFT JOIN Transactions t
        ON DAYOFWEEK(t.transaction_date) = d.day_number
        AND YEARWEEK(t.transaction_date, 1) = YEARWEEK(CURDATE(), 1)
        AND t.transaction_type = 'IN'
    GROUP BY d.day_name, d.day_number
    ORDER BY d.day_number ASC;

    """
    
    weekly_cost_query = """
    SELECT
        d.day_name AS day,
        COALESCE(SUM(t.total_amount), 0) AS daily_cost
    FROM 
        (SELECT 'Monday' AS day_name, 2 AS day_number UNION ALL
        SELECT 'Tuesday', 3 UNION ALL
        SELECT 'Wednesday', 4 UNION ALL
        SELECT 'Thursday', 5 UNION ALL
        SELECT 'Friday', 6 UNION ALL
        SELECT 'Saturday', 7 UNION ALL
        SELECT 'Sunday', 1) AS d
    LEFT JOIN Transactions t
        ON DAYOFWEEK(t.transaction_date) = d.day_number
        AND YEARWEEK(t.transaction_date, 1) = YEARWEEK(CURDATE(), 1)
        AND t.transaction_type = 'OUT'
    GROUP BY d.day_name, d.day_number
    ORDER BY d.day_number ASC;
    """

    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()

        # Fetch this week's revenue
        cursor.execute(revenue_query)
        revenue_result = cursor.fetchone()
        revenue = revenue_result[0] if revenue_result and revenue_result[0] is not None else 0

        # Fetch this week's costs
        cursor.execute(costs_query)
        costs_result = cursor.fetchone()
        costs = costs_result[0] if costs_result and costs_result[0] is not None else 0

        # Calculate profit
        profit = revenue - costs

        # Fetch this week's order fulfillment rate
        cursor.execute(fulfillment_rate_query)
        fulfillment_rate_result = cursor.fetchone()
        fulfillment_rate = fulfillment_rate_result[0] if fulfillment_rate_result and fulfillment_rate_result[0] is not None else 0

        # Fetch top suppliers for this week
        cursor.execute(top_suppliers_query)
        top_suppliers = cursor.fetchall()

        # Fetch total units sold for this week
        cursor.execute(units_sold_query)
        units_sold_result = cursor.fetchone()
        units_sold = units_sold_result[0] if units_sold_result and units_sold_result[0] is not None else 0

        # Fetch maximum units from the inventory
        cursor.execute(max_units_query)
        max_units_result = cursor.fetchone()
        maxi_units = max_units_result[0] if max_units_result and max_units_result[0] is not None else 0

        # Fetch weekly revenue data
        cursor.execute(weekly_revenue_query)
        weekly_revenue_results = cursor.fetchall()
        weekly_revenue = [0] * 7  # Assuming 7 days in the week
        day_index_map = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}
        for day, amount in weekly_revenue_results:
            weekly_revenue[day_index_map[day]] = amount

        # Fetch weekly cost data
        cursor.execute(weekly_cost_query)
        weekly_cost_results = cursor.fetchall()
        weekly_costs = [0] * 7
        for day, amount in weekly_cost_results:
            weekly_costs[day_index_map[day]] = amount

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Prepare the data for your GUI
    supplier_names = [supplier[0] for supplier in top_suppliers]
    supplier_values = [supplier[1] for supplier in top_suppliers]

    return revenue, profit, fulfillment_rate, supplier_names, supplier_values, units_sold, maxi_units, weekly_revenue, weekly_costs


def fetch_this_year_metrics():
    # SQL queries to fetch this year's metrics
    revenue_query = """
    SELECT SUM(total_amount) 
    FROM Transactions 
    WHERE transaction_type = 'IN' 
    AND YEAR(transaction_date) = YEAR(CURDATE())
    """
    costs_query = """
    SELECT SUM(total_amount) 
    FROM Transactions 
    WHERE transaction_type = 'OUT' 
    AND YEAR(transaction_date) = YEAR(CURDATE())
    """
    fulfillment_rate_query = """
    SELECT (SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) / COUNT(*)) * 100 
    FROM Orders 
    WHERE YEAR(order_date) = YEAR(CURDATE())
    """
    top_suppliers_query = """
    SELECT supplier_name, SUM(order_count) 
    FROM SupplierOrders 
    WHERE YEAR(order_date) = YEAR(CURDATE())
    GROUP BY supplier_name 
    ORDER BY SUM(order_count) DESC LIMIT 4
    """
    units_sold_query = """
    SELECT SUM(quantity) 
    FROM Transactions 
    WHERE YEAR(transaction_date) = YEAR(CURDATE())
    """
    max_units_query = "SELECT SUM(quantity) FROM products"
    
    # Additional queries for yearly revenue and monthly costs
    monthly_revenue_query = """
    SELECT
        MONTH(transaction_date) AS month,
        COALESCE(SUM(total_amount), 0) AS monthly_revenue
    FROM Transactions
    WHERE transaction_type = 'IN'
    AND YEAR(transaction_date) = YEAR(CURDATE())
    GROUP BY MONTH(transaction_date)
    ORDER BY MONTH(transaction_date) ASC;
    """
    
    monthly_cost_query = """
    SELECT
        MONTH(transaction_date) AS month,
        COALESCE(SUM(total_amount), 0) AS monthly_cost
    FROM Transactions
    WHERE transaction_type = 'OUT'
    AND YEAR(transaction_date) = YEAR(CURDATE())
    GROUP BY MONTH(transaction_date)
    ORDER BY MONTH(transaction_date) ASC;
    """

    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()

        # Fetch this year's revenue
        cursor.execute(revenue_query)
        revenue_result = cursor.fetchone()
        revenue = revenue_result[0] if revenue_result and revenue_result[0] is not None else 0

        # Fetch this year's costs
        cursor.execute(costs_query)
        costs_result = cursor.fetchone()
        costs = costs_result[0] if costs_result and costs_result[0] is not None else 0

        # Calculate profit
        profit = revenue - costs

        # Fetch this year's order fulfillment rate
        cursor.execute(fulfillment_rate_query)
        fulfillment_rate_result = cursor.fetchone()
        fulfillment_rate = fulfillment_rate_result[0] if fulfillment_rate_result and fulfillment_rate_result[0] is not None else 0

        # Fetch top suppliers for this year
        cursor.execute(top_suppliers_query)
        top_suppliers = cursor.fetchall()

        # Fetch total units sold for this year
        cursor.execute(units_sold_query)
        units_sold_result = cursor.fetchone()
        units_sold = units_sold_result[0] if units_sold_result and units_sold_result[0] is not None else 0

        # Fetch maximum units from the inventory
        cursor.execute(max_units_query)
        max_units_result = cursor.fetchone()
        maxi_units = max_units_result[0] if max_units_result and max_units_result[0] is not None else 0

        # Fetch monthly revenue data for the year
        cursor.execute(monthly_revenue_query)
        monthly_revenue_results = cursor.fetchall()
        monthly_revenue = [0] * 12  # Assuming 12 months in a year
        for month, amount in monthly_revenue_results:
            monthly_revenue[month - 1] = amount

        # Fetch monthly cost data for the year
        cursor.execute(monthly_cost_query)
        monthly_cost_results = cursor.fetchall()
        monthly_costs = [0] * 12
        for month, amount in monthly_cost_results:
            monthly_costs[month - 1] = amount

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Prepare the data for your GUI
    supplier_names = [supplier[0] for supplier in top_suppliers]
    supplier_values = [supplier[1] for supplier in top_suppliers]

    return revenue, profit, fulfillment_rate, supplier_names, supplier_values, units_sold, maxi_units, monthly_revenue, monthly_costs


def add_product_to_db(product_id, product_name, description, price, quantity):
    
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()
            
        # Prepare the SQL query
        sql_query = """
        INSERT INTO products (product_id, product_name, product_description, price, quantity)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (product_id, product_name, description, price, quantity)
            
        # Execute the query
        cursor.execute(sql_query, values)
            
        # Commit the transaction
        conn.commit()
            
        print("Product added successfully.")
    
    finally:
            cursor.close()
            conn.close()


def update_product_in_db(product_id, product_name, description, price, quantity):
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()
        
        # Prepare the SQL query
        sql_query = """
        UPDATE Inventory
        SET product_name = %s,
            product_description = %s,
            price = %s,
            quantity = %s
        WHERE product_id = %s
        """
        values = (product_name, description, price, quantity, product_id)
        
        # Execute the query
        cursor.execute(sql_query, values)
        
        # Commit the transaction
        conn.commit()
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def ProductExist(product_id):
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()

        query = "SELECT COUNT(*) FROM Inventory WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()

        if result[0] > 0:
            return True
        else:
            return False

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()


def check_quantity_available(product_id, order_quantity):
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()

        query = "SELECT quantity FROM Inventory WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        inv_quantity = result[0]

        if int(order_quantity) > inv_quantity:
            return True
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()
    

def add_order_to_db(order_id, product_id, product_name, customer_name, customer_address, order_date, delivery_date, status, quantity, total_amount):
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()
            
        # Prepare the SQL query
        query = """
        INSERT INTO Orders (order_id, product_id, product_name, customer_name, customer_address, order_date, expected_delivery_date, quantity, total_amount, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            order_id,
            product_id,
            product_name,
            customer_name,
            customer_address,
            order_date,
            delivery_date,
            quantity,
            total_amount,
            status
        )
        
        # Execute the query
        cursor.execute(query, values)

        query = "SELECT quantity FROM Inventory WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        inventory_quantity = result[0]

        new_quantity = inventory_quantity - int(quantity)
        update_query = "UPDATE Inventory SET quantity = %s WHERE product_id = %s"
        cursor.execute(update_query, (new_quantity, product_id))
            
        # Commit the transaction
        conn.commit()
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_order_in_db(order_id, product_id=None, product_name=None, customer_name=None, customer_address=None, order_date=None, delivery_date=None, status=None, quantity=None, total_amount=None):
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()

        # Prepare the SQL query
        query = """
        UPDATE Orders
        SET 
            product_id = COALESCE(%s, product_id),
            product_name = COALESCE(%s, product_name),
            customer_name = COALESCE(%s, customer_name),
            customer_address = COALESCE(%s, customer_address),
            order_date = COALESCE(%s, order_date),
            expected_delivery_date = COALESCE(%s, expected_delivery_date),
            quantity = COALESCE(%s, quantity),
            total_amount = COALESCE(%s, total_amount),
            status = COALESCE(%s, status)
        WHERE order_id = %s
        """
        
        values = (product_id, product_name, customer_name, customer_address, order_date, delivery_date, quantity, total_amount, status, order_id)
        
        # Execute the query
        cursor.execute(query, values)

        # Commit the transaction
        conn.commit()

    finally:
        # Closing the cursor and connection
        cursor.close()
        conn.close()


def add_supplier_to_db(supplier_id, supplier_name, product_count, average_lead_time, contact_phone, contact_email, performance, status):
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()
        
        # Prepare the SQL query
        query = """
        INSERT INTO Suppliers (supplier_id, supplier_name, product_count, contact_phone, contact_email, performance, avg_lead_time, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (supplier_id ,supplier_name, product_count, contact_phone, contact_email, performance, average_lead_time, status)
        
        # Execute the query
        cursor.execute(query, values)
        
        # Commit the transaction
        conn.commit()

    finally:
        # Closing the cursor and connection
        cursor.close()
        conn.close()


def update_supplier_in_db(supplier_id, supplier_name=None, product_count=None, average_lead_time=None, contact_phone=None, contact_email=None, performance=None, status=None):
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()
        
        # Prepare the SQL query
        query = """
        UPDATE Suppliers 
        SET 
            supplier_name = COALESCE(%s, supplier_name),
            product_count = COALESCE(%s, product_count),
            contact_phone = COALESCE(%s, contact_phone),
            contact_email = COALESCE(%s, contact_email),
            performance = COALESCE(%s, performance),
            avg_lead_time = COALESCE(%s, avg_lead_time),
            status = COALESCE(%s, status)
        WHERE 
            supplier_id = %s
        """
        values = (
            supplier_name if supplier_name is not None else None,
            product_count if product_count is not None else None,
            contact_phone if contact_phone is not None else None,
            contact_email if contact_email is not None else None,
            performance if performance is not None else None,
            average_lead_time if average_lead_time is not None else None,
            status if status is not None else None,
            supplier_id
        )
        
        # Execute the query
        cursor.execute(query, values)
        
        # Commit the transaction
        conn.commit()

    finally:
        # Closing the cursor and connection
        cursor.close()
        conn.close()


def add_supplier_order_to_db(order_id, supplier_id, supplier_name, product_name, order_count, order_date, expected_delivery_date, status, total_amount):
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()

        # Prepare the SQL query
        query = """
        INSERT INTO SupplierOrders (order_id, supplier_id, supplier_name, product_name, order_count, order_date, expected_delivery_date, status, total_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (order_id, supplier_id, supplier_name, product_name, order_count, order_date, expected_delivery_date, status, total_amount)

        # Execute the query
        cursor.execute(query, values)

        # Commit the transaction
        conn.commit()

        print("Supplier order added successfully!")

    except mysql.connector.Error as error:
        print(f"Failed to add supplier order: {error}")
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def update_supplier_order_in_db(order_id, supplier_id=None, supplier_name=None, product_name=None, order_count=None, order_date=None, expected_delivery_date=None, status=None, total_amount=None):
    # Database connection
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor()

        # Prepare the SQL query dynamically
        query_parts = []
        values = []

        if supplier_id is not None:
            query_parts.append("supplier_id = %s")
            values.append(supplier_id)
        if supplier_name is not None:
            query_parts.append("supplier_name = %s")
            values.append(supplier_name)
        if product_name is not None:
            query_parts.append("product_name = %s")
            values.append(product_name)
        if order_count is not None:
            query_parts.append("order_count = %s")
            values.append(order_count)
        if order_date is not None:
            query_parts.append("order_date = %s")
            values.append(order_date)
        if expected_delivery_date is not None:
            query_parts.append("expected_delivery_date = %s")
            values.append(expected_delivery_date)
        if status is not None:
            query_parts.append("status = %s")
            values.append(status)
        if total_amount is not None:
            query_parts.append("total_amount = %s")
            values.append(total_amount)

        # Ensure there's something to update
        if not query_parts:
            raise ValueError("No fields to update")

        # Complete the SQL query
        query = f"""
        UPDATE SupplierOrders
        SET {', '.join(query_parts)}
        WHERE order_id = %s
        """
        values.append(order_id)

        # Execute the query
        cursor.execute(query, values)

        # Commit the transaction
        conn.commit()

        print("Supplier order updated successfully!")

    except mysql.connector.Error as error:
        print(f"Failed to update supplier order: {error}")
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def fetch_low_stock_inventory(threshold=50):  # Set a default threshold value (e.g., 10)
    # Database connection
    conn = None
    cursor = None

    try:
        
        conn = mysql.connector.connect(**db_config)  # Replace with your actual DB config
        cursor = conn.cursor(dictionary=True)
        
        # SQL query to fetch products with stock below the threshold
        query = """
        SELECT 
            product_id, 
            product_name, 
            product_description, 
            price, 
            quantity, 
            date
        FROM 
            products
        WHERE 
            quantity <= %s
        ORDER BY 
            quantity ASC;
        """
        
        # Execute the query with the threshold parameter
        cursor.execute(query, (threshold,))
        
        # Fetch all the results
        low_stock_products = cursor.fetchall()
        
        return low_stock_products
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    
    finally:
        # Closing the connection
        if conn.is_connected():
            cursor.close()
            conn.close()