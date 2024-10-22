from datetime import datetime
from customtkinter import *
from CTkTable import CTkTable
from tkinter import messagebox
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pywinstyles
from pyzbar.pyzbar import decode
import cv2
import logic

class InventoryApp(CTk):
    def __init__(self):
        super().__init__()

        self.title("ICMS")
        self.logo = Image.open(r"code\img\logo.ico")
        self.iconbitmap(r"code\img\logo.ico")
        self.geometry("1000x550")
        self.resizable(0, 0)
        set_appearance_mode("light")

        self.camera_ip = "http://192.168.xx.x:8080/video" # can use ip based camera for barcode scanning [replace with your camera ip address]

        # Initialize frames
        self.content_frame = None
        self.login_frame = CTkFrame(self)
        self.sidebar_frame = CTkFrame(master=self, fg_color="#2A8C55", width=200, height=600, corner_radius=0)
        self.main_view = CTkFrame(master=self, fg_color="#fff", width=800, height=550, corner_radius=0)

        # Load the login screen first
        self.load_login()

    def load_login(self):
        self.geometry("600x480")
        # Load images
        side_img_data = Image.open(r"code\img\side-img.jpeg")
        email_icon_data = Image.open(r"code\img\email-icon.png")
        password_icon_data = Image.open(r"code\img\password-icon.png")

        side_img = CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(300, 480))
        email_icon = CTkImage(dark_image=email_icon_data, light_image=email_icon_data, size=(20, 20))
        password_icon = CTkImage(dark_image=password_icon_data, light_image=password_icon_data, size=(17, 17))

        # Create the main frame for the login screen
        frame = CTkFrame(master=self.login_frame, width=600, height=480, fg_color="#ffffff")
        frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid layout
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Side image on the left
        side_image_label = CTkLabel(master=frame, text="", image=side_img)
        side_image_label.grid(row=0, column=0, sticky="nsew")

        # Login form on the right
        login_form_frame = CTkFrame(master=frame, width=300, height=480, fg_color="#ffffff")
        login_form_frame.grid(row=0, column=1, sticky="nsew")
        login_form_frame.grid_propagate(0)  # Prevent the frame from resizing based on its content

        # Login form content
        CTkLabel(master=login_form_frame, text="Welcome Back!", text_color="#2A8C55", anchor="w", justify="left", font=("Arial Bold", 24)).grid(row=0, column=0, pady=(50, 5), padx=(25, 0), sticky="w")
        CTkLabel(master=login_form_frame, text="Sign in to your account", text_color="#7E7E7E", anchor="w", justify="left", font=("Arial Bold", 12)).grid(row=1, column=0, padx=(25, 0), sticky="w")

        CTkLabel(master=login_form_frame, text="  Email:", text_color="#2A8C55", anchor="w", justify="left", font=("Arial Bold", 14), image=email_icon, compound="left").grid(row=2, column=0, pady=(38, 0), padx=(25, 0), sticky="w")
        email_entry = CTkEntry(master=login_form_frame, width=225, fg_color="#EEEEEE", border_color="#2A8C55", border_width=1, text_color="#000000")
        email_entry.grid(row=3, column=0, padx=(25, 0), sticky="w")

        CTkLabel(master=login_form_frame, text="  Password:", text_color="#2A8C55", anchor="w", justify="left", font=("Arial Bold", 14), image=password_icon, compound="left").grid(row=4, column=0, pady=(21, 0), padx=(25, 0), sticky="w")
        password_entry = CTkEntry(master=login_form_frame, width=225, fg_color="#EEEEEE", border_color="#2A8C55", border_width=1, text_color="#000000", show="*")
        password_entry.grid(row=5, column=0, padx=(25, 0), sticky="w")

        CTkButton(master=login_form_frame, text="Login", fg_color="#2A8C55", hover_color="#207945", font=("Arial Bold", 12), text_color="#ffffff", width=225, command=lambda: self.login(email_entry.get(), password_entry.get())).grid(row=6, column=0, pady=(40, 0), padx=(25, 0), sticky="w")

        # Show the login frame
        self.login_frame.pack(fill="both", expand=True)
        
    def login(self, email, password):
        # Call the authenticate_user function from logic.py
        success, user_data = logic.authenticate_user(email, password)

        if success:
            # Store session data with username, email, and login time
            self.session_data = {
                "username": user_data["username"],
                "email": user_data["email"],
                "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Hide the login frame and show the sidebar and dashboard
            self.login_frame.pack_forget()
            self.geometry("1000x550")
            self.sidebar_frame.pack_propagate(0)
            self.sidebar_frame.pack(fill="y", side="left")
            self.create_sidebar()

            self.main_view.pack_propagate(0)
            self.main_view.pack(side="left", fill="both", expand=True)
            self.load_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")
                
    def load_inventory(self):
        self.clear_main_view()

        # Function to update table data based on search query
        def update_table(event=None):
            search_query = search_entry.get()
            sort_by = sort_by_combo.get()

            # Fetch filtered data from logic based on search query, sort order, and status
            table_data = logic.fetch_inventory_data_filtered(search_query, sort_by)
            
            # Clear and update table with new data
            table.update_values(table_data)

        def capture_image():
            # Open the default camera
            cap = cv2.VideoCapture(self.camera_ip)

            # Check if the camera opened successfully
            if not cap.isOpened():
                print("Could not open camera")
                return None

            # Read a frame from the camera
            ret, frame = cap.read()

            # Save the image
            image_path = "captured_image.jpg"
            cv2.imwrite(image_path, frame)

            # Release the camera
            cap.release()

            print("Image captured and saved as", image_path)
            return image_path

        def scan():
            image_path = capture_image()
            # Open the image using PIL
            image = Image.open(image_path)

            # Decode the barcode from the image
            barcodes = decode(image)

            # If no barcode is found
            if not barcodes:
                print("No barcode found.")
                return None

            # Extract data from the first barcode found
            barcode_data = barcodes[0].data.decode('utf-8')

            search_entry.delete(0, "end")
            search_entry.insert(0, barcode_data)
            update_table() 

        # Inventory management frame
        inventory_frame = CTkFrame(master=self.main_view, fg_color="transparent")
        inventory_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        CTkLabel(master=inventory_frame, text="Inventory Management", font=("Arial Black", 20), text_color="#2A8C55").pack(anchor="nw", pady=(0, 20))


        # Search container
        search_container = CTkFrame(master=inventory_frame, height=50, fg_color="#F0F0F0")
        search_container.pack(fill="x", pady=(0, 0), padx=0)

        # Search widgets
        search_entry = CTkEntry(master=search_container, width=305, placeholder_text="Search Product", border_color="#2A8C55", border_width=2)
        search_entry.pack(side="left", padx=(13, 0), pady=15, expand=True, fill="x")

        # Adding a rounded square button with a camera logo
        camera_image = Image.open(r"code\img\camera.png")  # Replace with your camera logo path
        camera_image_resized = camera_image.resize((20, 20))  # Adjust size as needed
        camera_photo = CTkImage(dark_image=camera_image_resized, size=(20, 20))

        camera_button = CTkButton(master=search_container, image=camera_photo, text="", fg_color="#2A8C55", hover_color="#207244", width=40, height=20, corner_radius=5, command=scan)
        camera_button.pack(side="left", padx=(13, 0), pady=15)

        # Sort by combo box
        sort_by_combo = CTkComboBox(master=search_container, width=125, values=["Date", "Most Recent Order", "Least Recent Order"], button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=update_table)
        sort_by_combo.pack(side="right", padx=(13, 0), pady=15)

        # Bind search entry to update table when the user types
        search_entry.bind("<Return>", update_table)

        # Table data
        table_data = logic.fetch_inventory_data()

        # Table frame
        table_frame = CTkScrollableFrame(master=inventory_frame, fg_color="transparent")
        table_frame.pack(expand=True, fill="both", padx=0, pady=0)
        table = CTkTable(master=table_frame, values=table_data, colors=["#E6E6E6", "#EEEEEE"], header_color="#2A8C55", hover_color="#B4B4B4")
        table.edit_row(0, text_color="#fff", hover_color="#2A8C55")
        table.pack(expand=True, fill="both")

        # Floating button to add new product
        def add_product():
            self.clear_main_view()

            # Main view
            add_frame = CTkFrame(master=self.main_view, fg_color="#fff", width=650, height=500, corner_radius=0)
            add_frame.pack_propagate(0)
            add_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)

            # Load the image for the back button
            back_image = Image.open(r"code\img\back.png")  # Replace with the path to your image file
            back_image_resized = back_image.resize((18, 18))  # Resize the image to fit the button
            back_photo = CTkImage(dark_image=back_image_resized, size=(18, 18))

            # Create the back button with the image
            back_button = CTkButton(master=add_frame, image=back_photo, text="", fg_color="transparent", hover=False, command=self.load_inventory, height=25, width=25)
            back_button.place(relx=0, rely=0, anchor="nw", x=5, y=5)

            # Product ID
            CTkLabel(master=add_frame, text="Product ID", font=("Arial Bold", 14), text_color="#52A476").pack(anchor="nw", pady=(30, 5), padx=8)
            product_id_entry = CTkEntry(master=add_frame, fg_color="#F0F0F0", border_width=0)
            product_id_entry.pack(fill="x", pady=(5, 8), padx=8, ipady=5)

            # Product Name
            CTkLabel(master=add_frame, text="Product Name", font=("Arial Bold", 14), text_color="#52A476").pack(anchor="nw", pady=(5, 5), padx=8)
            product_name_entry = CTkEntry(master=add_frame, fg_color="#F0F0F0", border_width=0)
            product_name_entry.pack(fill="x", pady=(5, 8), padx=8, ipady=5)

            # Description
            CTkLabel(master=add_frame, text="Description", font=("Arial Bold", 14), text_color="#52A476").pack(anchor="nw", pady=(5, 5), padx=8)
            description_entry = CTkTextbox(master=add_frame, fg_color="#F0F0F0", corner_radius=8, height=60)
            description_entry.pack(fill="x", pady=(5, 8), padx=8)

            # Price
            CTkLabel(master=add_frame, text="Price", font=("Arial Bold", 14), text_color="#52A476").pack(anchor="nw", pady=(5, 5), padx=8)
            price_entry = CTkEntry(master=add_frame, fg_color="#F0F0F0", border_width=0)
            price_entry.pack(fill="x", pady=(5, 8), padx=8, ipady=5)

            # functions to increase or decrease product quantity
            def decrease_quantity():
                current_value = int(quantity_entry.cget("text"))
                if current_value > 0:
                    quantity_entry.configure(text=f"{current_value - 1:02d}")

            def increase_quantity():
                current_value = int(quantity_entry.cget("text"))
                quantity_entry.configure(text=f"{current_value + 1:02d}")

            # Quantity
            CTkLabel(master=add_frame, text="Quantity", font=("Arial Bold", 14), text_color="#52A476").pack(anchor="nw", pady=(5, 5), padx=8)
            quantity_frame = CTkFrame(master=add_frame, fg_color="transparent")
            quantity_frame.pack(anchor="nw", pady=(5, 8), padx=8)
            CTkButton(master=quantity_frame, text="-", width=20, fg_color="#2A8C55", hover_color="#207244", font=("Arial Black", 12), command=decrease_quantity).pack(side="left", anchor="w")
            quantity_entry = CTkLabel(master=quantity_frame, text="01", text_color="#2A8C55", font=("Arial Black", 12))
            quantity_entry.pack(side="left", anchor="w", padx=6)
            CTkButton(master=quantity_frame, text="+", width=20, fg_color="#2A8C55", hover_color="#207244", font=("Arial Black", 12), command=increase_quantity).pack(side="left", anchor="w")

            def add():
                product_id = product_id_entry.get()
                product_name = product_name_entry.get()
                description = description_entry.get("1.0", "end-1c")
                price = price_entry.get()
                quantity = quantity_entry.cget("text")
                logic.add_product_to_db(product_id, product_name, description, price, quantity)
                self.clear_main_view()
                self.load_inventory()

            def update():
                product_id = product_id_entry.get()
                product_name = product_name_entry.get()
                description = description_entry.get("1.0", "end-1c")
                price = price_entry.get()
                quantity = quantity_entry.cget("text")
                logic.update_product_in_db(product_id, product_name, description, price, quantity)
                self.clear_main_view()
                self.load_inventory()

            # Actions
            actions = CTkFrame(master=add_frame, fg_color="transparent")
            actions.pack(fill="both", pady=(20, 0), padx=(8, 8))
            # Update Product Button
            CTkButton(master=actions, text="Add Product", width=150, font=("Arial Bold", 14), hover_color="#207244", fg_color="#2A8C55", text_color="#fff", command=add).pack(side="right", anchor="se",  padx=(10, 10))
            CTkButton(master=actions, text="Update Product", width=150, font=("Arial Bold", 14), hover_color="#207244", fg_color="#2A8C55", text_color="#fff", command=update).pack(side="right", anchor="se")


        floating_button = CTkButton(master=self.main_view, text="+ Add Product", command=add_product, fg_color="#2A8C55", hover_color="#207244")
        floating_button.place(relx=1, rely=1, anchor="se", x=-20, y=-20)

        

    def load_orders(self):
        self.clear_main_view()

        # Function to update table data based on search query
        def update_table(event=None):
            search_query = search_entry.get()
            sort_by = sort_by_combo.get()
            status_filter = status_combo.get()

            # Fetch filtered data from logic based on search query, sort order, and status
            table_data = logic.fetch_orders_data_filtered(search_query, sort_by, status_filter)
            
            # Clear and update table with new data
            table.update_values(table_data)

        def capture_image():
            # Open the default camera
            cap = cv2.VideoCapture(self.camera_ip)

            # Check if the camera opened successfully
            if not cap.isOpened():
                print("Could not open camera")
                return None

            # Read a frame from the camera
            ret, frame = cap.read()

            # Save the image
            image_path = "captured_image.jpg"
            cv2.imwrite(image_path, frame)

            # Release the camera
            cap.release()

            print("Image captured and saved as", image_path)
            return image_path

        def scan():
            image_path = capture_image()
            # Open the image using PIL
            image = Image.open(image_path)

            # Decode the barcode from the image
            barcodes = decode(image)

            # If no barcode is found
            if not barcodes:
                print("No barcode found.")
                return None

            # Extract data from the first barcode found
            barcode_data = barcodes[0].data.decode('utf-8')

            search_entry.delete(0, "end")
            search_entry.insert(0, barcode_data)
            update_table() 

        # Orders management frame
        orders_frame = CTkFrame(master=self.main_view, fg_color="transparent")
        orders_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_frame = CTkFrame(master=orders_frame, fg_color="transparent")
        title_frame.pack(anchor="n", fill="x", padx=0, pady=(0, 0))

        CTkLabel(master=title_frame, text="Orders", font=("Arial Black", 25), text_color="#2A8C55").pack(anchor="nw", side="left")
        
        # Metrics container
        metrics_frame = CTkFrame(master=orders_frame, fg_color="transparent")
        metrics_frame.pack(anchor="n", fill="x", padx=0, pady=(23, 0))

        metrics_data = logic.fetch_order_metrics()

        # Orders metric
        orders_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
        orders_metric.grid_propagate(0)
        orders_metric.pack(side="left", expand=True, fill="both", padx=(0, 10), pady=0)

        logistics_img_data = Image.open(r"code\img\logistics_icon.png")
        logistics_img = CTkImage(light_image=logistics_img_data, dark_image=logistics_img_data, size=(43, 43))

        CTkLabel(master=orders_metric, image=logistics_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
        CTkLabel(master=orders_metric, text="Orders", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
        CTkLabel(master=orders_metric, text=metrics_data['total_orders'], text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

        # Shipped metric
        shipped_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
        shipped_metric.grid_propagate(0)
        shipped_metric.pack(side="left", expand=True, fill="both", padx=(10, 10), pady=0)

        shipping_img_data = Image.open(r"code\img\shipping_icon.png")
        shipping_img = CTkImage(light_image=shipping_img_data, dark_image=shipping_img_data, size=(43, 43))

        CTkLabel(master=shipped_metric, image=shipping_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
        CTkLabel(master=shipped_metric, text="Shipping", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
        CTkLabel(master=shipped_metric, text=metrics_data['shipped_orders'], text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

        # Delivered metric
        delivered_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
        delivered_metric.grid_propagate(0)
        delivered_metric.pack(side="right", expand=True, fill="both", padx=(10, 0), pady=0)

        delivered_img_data = Image.open(r"code\img\delivered_icon.png")
        delivered_img = CTkImage(light_image=delivered_img_data, dark_image=delivered_img_data, size=(43, 43))

        CTkLabel(master=delivered_metric, image=delivered_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
        CTkLabel(master=delivered_metric, text="Delivered", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
        CTkLabel(master=delivered_metric, text=metrics_data['delivered_orders'], text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

        # Search container
        search_container = CTkFrame(master=orders_frame, height=50, fg_color="#F0F0F0")
        search_container.pack(fill="x", pady=(23, 0), padx=0)

        # Search bar
        search_entry = CTkEntry(master=search_container, width=305, placeholder_text="Search Order", border_color="#2A8C55", border_width=2)
        search_entry.pack(side="left", padx=(13, 0), pady=15, expand=True, fill="x")

        # Adding a rounded square button with a camera logo
        camera_image = Image.open(r"code\img\camera.png")  # Replace with your camera logo path
        camera_image_resized = camera_image.resize((20, 20))  # Adjust size as needed
        camera_photo = CTkImage(dark_image=camera_image_resized, size=(20, 20))

        camera_button = CTkButton(master=search_container, image=camera_photo, text="", fg_color="#2A8C55", hover_color="#207244", width=40, height=20, corner_radius=5, command=scan)
        camera_button.pack(side="left", padx=(13, 0), pady=15)

        # Sort By Combo
        sort_by_combo = CTkComboBox(master=search_container, width=125, values=["Order Date","Most Recent Order", "Least Recent Order"], button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=update_table)
        sort_by_combo.pack(side="left", padx=(13, 0), pady=15)

        # Status Combo
        status_combo = CTkComboBox(master=search_container, width=125, values=["Status", "Processing", "Confirmed", "Packing", "Shipping", "Delivered", "Cancelled"], button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=update_table)
        status_combo.pack(side="right", padx=(13, 0), pady=15)

        # Bind search entry to update table when the user types
        search_entry.bind("<Return>", update_table)

        # Table data
        table_data = logic.fetch_orders_data()

        # Table frame
        table_frame = CTkScrollableFrame(master=orders_frame, fg_color="transparent")
        table_frame.pack(expand=True, fill="both", padx=0, pady=0)
        table = CTkTable(master=table_frame, values=table_data, colors=["#E6E6E6", "#EEEEEE"], header_color="#2A8C55", hover_color="#B4B4B4")
        table.edit_row(0, text_color="#fff", hover_color="#2A8C55")
        table.pack(expand=True, fill="both")

        def add_order():
            self.clear_main_view()

            # Main view - using CTkScrollableFrame for scrollable functionality
            add_frame = CTkScrollableFrame(master=self.main_view, fg_color="#fff", width=700, height=550, corner_radius=0)
            add_frame.pack_propagate(0)
            add_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)

            # Load the image for the back button
            back_image = Image.open(r"code\img\back.png")  # Replace with the path to your image file
            back_image_resized = back_image.resize((18, 18))  # Resize the image to fit the button
            back_photo = CTkImage(dark_image=back_image_resized, size=(18, 18))

            # Create the back button with the image
            back_button = CTkButton(master=add_frame, image=back_photo, text="", fg_color="transparent", hover=False, command=self.load_inventory, height=25, width=25)
            back_button.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

            # Frame for order and product ID's
            top_frame = CTkFrame(master=add_frame, fg_color="transparent")
            top_frame.grid(row=1, column=0, padx=27, pady=(31, 10), sticky="nsew")

            # Order ID
            CTkLabel(master=top_frame, text="Order ID", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=0, column=0, sticky="w")
            order_id_entry = CTkEntry(master=top_frame, fg_color="#F0F0F0", border_width=0, width=350)
            order_id_entry.grid(row=1, column=0, ipady=10)

            # Product ID
            CTkLabel(master=top_frame, text="Product Id", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=0, column=1, sticky="w", padx=(25, 0))
            product_id_entry = CTkEntry(master=top_frame, fg_color="#F0F0F0", border_width=0, width=350)
            product_id_entry.grid(row=1, column=1, ipady=10, padx=(24, 0))

            # Product Name
            CTkLabel(master=add_frame, text="Product Name", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=2, column=0, sticky="nw", pady=(5, 5), padx=27)
            product_name_entry = CTkEntry(master=add_frame, fg_color="#F0F0F0", border_width=0)
            product_name_entry.grid(row=3, column=0, sticky="ew", pady=(5, 8), padx=27)
            # Frame for Customer Name and Customer Address
            customer_frame = CTkFrame(master=add_frame, fg_color="transparent")
            customer_frame.grid(row=4, column=0, padx=27, pady=(31, 10), sticky="nsew")

            # Grid layout for Customer Name and Customer Address
            CTkLabel(master=customer_frame, text="Customer Name", font=("Arial Bold", 14), text_color="#52A476").grid(row=0, column=0, sticky="w")
            customer_name_entry = CTkEntry(master=customer_frame, fg_color="#F0F0F0", border_width=0, width=350)
            customer_name_entry.grid(row=1, column=0, ipady=10)

            CTkLabel(master=customer_frame, text="Customer Address", font=("Arial Bold", 14), text_color="#52A476").grid(row=0, column=1, sticky="w", padx=(25, 0))
            customer_address_entry = CTkEntry(master=customer_frame, fg_color="#F0F0F0", border_width=0, width=350)
            customer_address_entry.grid(row=1, column=1, ipady=10, padx=(24, 0))

            # Frame for Order Date and Delivery Date
            dates_frame = CTkFrame(master=add_frame, fg_color="transparent")
            dates_frame.grid(row=5, column=0, padx=27, pady=(31, 10), sticky="nsew")

            # Order Date
            CTkLabel(master=dates_frame, text="Order Date", font=("Arial Bold", 14), text_color="#52A476").grid(row=0, column=0, sticky="w")
            order_date_entry = CTkEntry(master=dates_frame, fg_color="#F0F0F0", border_width=0, width=350)
            order_date_entry.grid(row=1, column=0, ipady=10)

            # Delivery Date
            CTkLabel(master=dates_frame, text="Delivery Date", font=("Arial Bold", 14), text_color="#52A476").grid(row=0, column=1, sticky="w", padx=(25, 0))
            delivery_date_entry = CTkEntry(master=dates_frame, fg_color="#F0F0F0", border_width=0, width=350)
            delivery_date_entry.grid(row=1, column=1, ipady=10, padx=(24, 0))

            # Frame for Status, Quantity, and Total Amount
            status_quantity_frame = CTkFrame(master=add_frame, fg_color="transparent")
            status_quantity_frame.grid(row=6, column=0, padx=27, pady=(31, 10), sticky="nsew")

            # Left side - Statuses
            statuses_frame = CTkFrame(master=status_quantity_frame, fg_color="transparent")
            statuses_frame.grid(row=0, column=0, sticky="ns", padx=(0, 300))

            CTkLabel(master=statuses_frame, text="Status", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=0, column=0, sticky="nw", pady=(5, 5))
            status_var = StringVar(value="Processing")
            statuses = ["processing", "confirmed", "shipped", "delivered"]
            for i, status in enumerate(statuses):
                CTkRadioButton(master=statuses_frame, text=status, variable=status_var, value=status, text_color="#2A8C55", font=("Arial Bold", 12), fg_color="#52A476", border_color="#52A476", hover_color="#207244").grid(row=i+1, column=0, sticky="w", padx=5, pady=(16,0))

            # Right side - Quantity and Total Amount
            right_frame = CTkFrame(master=status_quantity_frame, fg_color="transparent")
            right_frame.grid(row=0, column=1, sticky="nsew")

            # Top layer for Quantity
            quantity_frame = CTkFrame(master=right_frame, fg_color="transparent")
            quantity_frame.grid(row=0, column=0, padx=5, pady=(5, 10))

            CTkLabel(master=quantity_frame, text="Quantity", font=("Arial Bold", 14), text_color="#52A476").grid(row=0, column=0, sticky="nw")
            
            def decrease_quantity():
                current_value = int(quantity_entry.cget("text"))
                if current_value > 0:
                    quantity_entry.configure(text=f"{current_value - 1:02d}")

            def increase_quantity():
                current_value = int(quantity_entry.cget("text"))
                quantity_entry.configure(text=f"{current_value + 1:02d}")

            quantity_control_frame = CTkFrame(master=quantity_frame, fg_color="transparent")
            quantity_control_frame.grid(row=1, column=0, pady=(5, 0))

            CTkButton(master=quantity_control_frame, text="-", width=20, fg_color="#2A8C55", hover_color="#207244", font=("Arial Black", 12), command=decrease_quantity).grid(row=0, column=0, sticky="w")
            quantity_entry = CTkLabel(master=quantity_control_frame, text="01", text_color="#2A8C55", font=("Arial Black", 12))
            quantity_entry.grid(row=0, column=1, padx=6, sticky="w")
            CTkButton(master=quantity_control_frame, text="+", width=20, fg_color="#2A8C55", hover_color="#207244", font=("Arial Black", 12), command=increase_quantity).grid(row=0, column=2, sticky="w")

            # Bottom layer for Total Amount
            total_amount_frame = CTkFrame(master=right_frame, fg_color="transparent")
            total_amount_frame.grid(row=1, column=0, padx=5, pady=(10, 0))

            CTkLabel(master=total_amount_frame, text="Total Amount", font=("Arial Bold", 14), text_color="#52A476").grid(row=0, column=0, sticky="nw")
            total_amount_entry = CTkEntry(master=total_amount_frame, fg_color="#F0F0F0", border_width=0)
            total_amount_entry.grid(row=1, column=0, ipady=10)

            # Actions
            def add():
                order_id = order_id_entry.get()
                product_id = product_id_entry.get()
                product_name = product_name_entry.get()
                customer_name = customer_name_entry.get()
                customer_address = customer_address_entry.get()
                order_date = order_date_entry.get()
                delivery_date = delivery_date_entry.get()
                status = status_var.get()
                quantity = quantity_entry.cget("text")
                total_amount = total_amount_entry.get()
                id_exist = logic.ProductExist(product_id)
                if id_exist == False:
                     messagebox.showerror("Error", "Product does not exist in inventory.")
                quan = logic.check_quantity_available(product_id, quantity)
                if quan == True:
                    messagebox.showerror("Error", "Not enough stock to fulfill the order.")
                logic.add_order_to_db(order_id, product_id, product_name, customer_name, customer_address, order_date, delivery_date, status, quantity, total_amount)
                self.clear_main_view()
                self.load_orders()

            def update():
                order_id = order_id_entry.get()
                product_id = product_id_entry.get()
                product_name = product_name_entry.get()
                customer_name = customer_name_entry.get()
                customer_address = customer_address_entry.get()
                order_date = order_date_entry.get()
                delivery_date = delivery_date_entry.get()
                status = status_var.get()
                quantity = quantity_entry.cget("text")
                total_amount = total_amount_entry.get()
                logic.update_order_in_db(order_id, product_id, product_name, customer_name, customer_address, order_date, delivery_date, status, quantity, total_amount)
                self.clear_main_view()
                self.load_orders()


            # Frame for actions (Add and Update buttons)
            actions = CTkFrame(master=add_frame, fg_color="transparent")
            actions.grid(row=7, column=0, sticky="nsew", padx=8, pady=(31, 15))
            CTkButton(master=actions, text="Add Order", font=("Arial Black", 14), fg_color="#2A8C55", hover_color="#207244", command=add).grid(row=0, column=0, padx=(0, 15))
            CTkButton(master=actions, text="Update Order", font=("Arial Black", 14), fg_color="#52A476", hover_color="#3B9A5A", command=update).grid(row=0, column=1, padx=(15, 0))

        floating_button = CTkButton(master=self.main_view, text="+ Add Order", command=add_order, fg_color="#2A8C55", hover_color="#207244")
        floating_button.place(relx=1, rely=1, anchor="se", x=-20, y=-20)

    def load_supply(self):
        self.clear_main_view()

        def widget_destroy(widget):
            widget.destroy()

        total_suppliers, pending_orders, avg_lead_time = logic.fetch_supply_metrics()

        # Supply Management frame
        supply_frame = CTkFrame(master=self.main_view, fg_color="transparent")
        supply_frame.pack(expand=True, fill="both", padx=20, pady=0)

        # Title
        CTkLabel(master=supply_frame, text="Supply Management", font=("Arial Black", 20), text_color="#2A8C55").pack(anchor="nw", pady=(0, 3))

        # Metrics container
        metrics_frame = CTkFrame(master=supply_frame, fg_color="transparent")
        metrics_frame.pack(anchor="n", fill="x", padx=0, pady=(23, 0))

        # Total Suppliers metric
        total_suppliers_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=180, height=60)
        total_suppliers_metric.grid_propagate(0)
        total_suppliers_metric.pack(side="left", fill="both", padx=(0, 7.5), pady=0)

        suppliers_img_data = Image.open(r"code\img\person_icon.png")
        suppliers_img = CTkImage(light_image=suppliers_img_data, dark_image=suppliers_img_data, size=(45, 45))

        CTkLabel(master=total_suppliers_metric, image=suppliers_img, text="").grid(row=0, column=0, rowspan=2, padx=(12, 5), pady=10)
        CTkLabel(master=total_suppliers_metric, text="Total Suppliers", text_color="#fff", font=("Arial Black", 13.5)).grid(row=0, column=1, sticky="sw")
        CTkLabel(master=total_suppliers_metric, text=total_suppliers, text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0, 10))

        def total_suppliers_clicked():
            if self.content_frame is not None:
                self.content_frame.destroy()

            # Function to update table data based on search query
            def update_table(event=None):
                search_query = search_entry.get()
                sort_by = sort_by_combo.get()
                performance_filter = performance_combo.get()

                # Fetch filtered data from logic based on search query, sort order, and status
                table_data = logic.fetch_supplier_details_filtered(search_query, sort_by, performance_filter)
                
                # Clear and update table with new data
                table.update_values(table_data)

            def capture_image():
                # Open the default camera
                cap = cv2.VideoCapture(self.camera_ip)

                # Check if the camera opened successfully
                if not cap.isOpened():
                    print("Could not open camera")
                    return None

                # Read a frame from the camera
                ret, frame = cap.read()

                # Save the image
                image_path = "captured_image.jpg"
                cv2.imwrite(image_path, frame)

                # Release the camera
                cap.release()

                print("Image captured and saved as", image_path)
                return image_path

            def scan():
                image_path = capture_image()
                # Open the image using PIL
                image = Image.open(image_path)

                # Decode the barcode from the image
                barcodes = decode(image)

                # If no barcode is found
                if not barcodes:
                    print("No barcode found.")
                    return None

                # Extract data from the first barcode found
                barcode_data = barcodes[0].data.decode('utf-8')

                search_entry.delete(0, "end")
                search_entry.insert(0, barcode_data)
                update_table() 


            #content frame
            self.content_frame = CTkFrame(master=supply_frame, fg_color="transparent")
            self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Search widgets
            search_container = CTkFrame(master=self.content_frame)
            search_container.pack(side="top", fill="x", padx=10, pady=5)

            # Search widgets
            search_entry = CTkEntry(master=search_container, width=305, placeholder_text="Search Supplier", border_color="#2A8C55", border_width=2)
            search_entry.pack(side="left", padx=(13, 0), pady=15, expand=True, fill="x")

            # Adding a rounded square button with a camera logo
            camera_image = Image.open(r"code\img\camera.png")  # Replace with your camera logo path
            camera_image_resized = camera_image.resize((20, 20))  # Adjust size as needed
            camera_photo = CTkImage(dark_image=camera_image_resized, size=(20, 20))

            camera_button = CTkButton(master=search_container, image=camera_photo, text="", fg_color="#2A8C55", hover_color="#207244", width=40, height=20, corner_radius=5, command=scan)
            camera_button.pack(side="left", padx=(13, 0), pady=15)

            sort_by_combo = CTkComboBox(master=search_container, width=125, values=["Status","Active", "In Active"], button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=update_table)
            sort_by_combo.pack(side="left", padx=(13, 0), pady=15)

            performance_combo = CTkComboBox(master=search_container, width=125, values=[ "All Performances","High", "Low", "Medium"], button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=update_table)
            performance_combo.pack(side="right", padx=(13, 0), pady=15)

            # Bind search entry to update table when the user types
            search_entry.bind("<Return>", update_table)

            # Table data
            table_data = logic.fetch_supplier_details()

            # Table frame
            table_frame = CTkScrollableFrame(master=self.content_frame, fg_color="transparent")
            table_frame.pack(expand=True, fill="both", padx=10, pady=10)

            # Creating a table widget
            table = CTkTable(master=table_frame, values=table_data, colors=["#E6E6E6", "#EEEEEE"], header_color="#2A8C55", hover_color="#B4B4B4")

            # Customize the header row (row 0)
            table.edit_row(0, text_color="#fff", hover_color="#2A8C55")

            # Pack the table
            table.pack(expand=True, fill="both")

            def add_supplier():
                self.clear_main_view()

                def add():
                    # Fetch values from the text boxes
                    supplier_id = supplier_id_entry.get()
                    supplier_name = supplier_name_entry.get()
                    product_count = product_count_label.cget("text")
                    average_lead_time = lead_time_entry.get()
                    contact_phone = contact_phone_entry.get()
                    contact_email = contact_email_entry.get()

                    # Fetch values from the radio buttons
                    performance = performance_var.get()
                    status = status_var.get()

                    # Adding supplier to DataBase
                    logic.add_supplier_to_db(supplier_id, supplier_name, product_count, average_lead_time, contact_phone, contact_email, performance, status)

                    self.clear_main_view()
                    self.load_supply()

                def update():
                    # Fetch values from the text boxes
                    supplier_id = supplier_id_entry.get()
                    supplier_name = supplier_name_entry.get()
                    product_count = product_count_label.cget("text")
                    average_lead_time = lead_time_entry.get()
                    contact_phone = contact_phone_entry.get()
                    contact_email = contact_email_entry.get()

                    # Fetch values from the radio buttons
                    performance = performance_var.get()
                    status = status_var.get()

                    # Updating supplier details in the database
                    logic.update_supplier_in_db(supplier_id, supplier_name, product_count, average_lead_time, contact_phone, contact_email, performance, status)

                    self.clear_main_view()
                    self.load_supply()

                # Main view - using CTkScrollableFrame for scrollable functionality
                add_frame = CTkScrollableFrame(master=self.main_view, fg_color="#fff", width=700, height=550, corner_radius=0)
                add_frame.pack_propagate(0)
                add_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)

                # Load the image for the back button
                back_image = Image.open(r"code\img\back.png")  # Replace with the path to your image file
                back_image_resized = back_image.resize((18, 18))  # Resize the image to fit the button
                back_photo = CTkImage(dark_image=back_image_resized, size=(18, 18))

                # Create the back button with the image
                back_button = CTkButton(master=add_frame, image=back_photo, text="", fg_color="transparent", hover=False, command=self.load_supply, height=25, width=25)
                back_button.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

                # Frame for Supplier ID, Supplier Name, and Average Lead Time
                top_frame = CTkFrame(master=add_frame, fg_color="transparent")
                top_frame.grid(row=1, column=0, padx=27, pady=(10, 10), sticky="nsew")

                # Supplier ID
                CTkLabel(master=top_frame, text="Supplier ID", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=0, column=0, sticky="w")
                supplier_id_entry = CTkEntry(master=top_frame, fg_color="#F0F0F0", border_width=0, width=350)
                supplier_id_entry.grid(row=1, column=0, ipady=10)

                # Supplier Name
                CTkLabel(master=top_frame, text="Supplier Name", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=0, column=1, sticky="w", padx=(25, 0))
                supplier_name_entry = CTkEntry(master=top_frame, fg_color="#F0F0F0", border_width=0, width=350)
                supplier_name_entry.grid(row=1, column=1, ipady=10, padx=(24, 0))

                # Average Lead Time
                CTkLabel(master=top_frame, text="Average Lead Time", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=2, column=1, sticky="w", padx=(25, 0), pady=(20, 0))
                lead_time_entry = CTkEntry(master=top_frame, fg_color="#F0F0F0", border_width=0, width=350)
                lead_time_entry.grid(row=3, column=1, ipady=10, padx=(24, 0), pady=(5, 0))

                # Product Count with Increment/Decrement Buttons
                def decrease_product_count():
                    current_value = int(product_count_label.cget("text"))
                    if current_value > 0:
                        product_count_label.configure(text=f"{current_value - 1:02d}")

                def increase_product_count():
                    current_value = int(product_count_label.cget("text"))
                    product_count_label.configure(text=f"{current_value + 1:02d}")

                product_count_frame = CTkFrame(master=top_frame, fg_color="transparent")
                product_count_frame.grid(row=3, column=0, pady=(20, 0), sticky="w")

                CTkLabel(master=top_frame, text="Product Count", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=2, column=0, sticky="w", pady=(20, 0))
                
                CTkButton(master=product_count_frame, text="-", width=20, fg_color="#2A8C55", hover_color="#207244", font=("Arial Black", 12), command=decrease_product_count).pack(side="left")
                product_count_label = CTkLabel(master=product_count_frame, text="01", text_color="#2A8C55", font=("Arial Black", 12))
                product_count_label.pack(side="left", padx=(10, 10))
                CTkButton(master=product_count_frame, text="+", width=20, fg_color="#2A8C55", hover_color="#207244", font=("Arial Black", 12), command=increase_product_count).pack(side="left")

                # Contact Phone
                CTkLabel(master=add_frame, text="Contact Phone", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=6, column=0, sticky="w", padx=27, ipady=10)
                contact_phone_entry = CTkEntry(master=add_frame, fg_color="#F0F0F0", border_width=0, width=725)
                contact_phone_entry.grid(row=7, column=0, ipady=10, padx=27, pady=(5, 20), sticky="w")

                # Contact Email
                CTkLabel(master=add_frame, text="Contact Email", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=8, column=0, sticky="w", padx=27)
                contact_email_entry = CTkEntry(master=add_frame, fg_color="#F0F0F0", border_width=0, width=725)
                contact_email_entry.grid(row=9, column=0, ipady=10, padx=27, pady=(5, 20), sticky="w")

                # Performance Radio Buttons
                CTkLabel(master=add_frame, text="Performance", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=10, column=0, sticky="w", padx=27)
                performance_frame = CTkFrame(master=add_frame, fg_color="transparent")
                performance_frame.grid(row=11, column=0, padx=27, pady=(5, 20), sticky="w")

                performance_var = StringVar(value="High")
                performances = ["High", "Medium", "Low"]

                for i, performance in enumerate(performances):
                    CTkRadioButton(master=performance_frame, text=performance, variable=performance_var, value=performance, text_color="#2A8C55", font=("Arial Bold", 12), fg_color="#52A476", border_color="#52A476", hover_color="#207244").grid(row=i, column=0, sticky="w", padx=5, pady=(0, 10))

                # Status Radio Buttons
                CTkLabel(master=add_frame, text="Status", font=("Arial Bold", 14), text_color="#2A8C55", justify="left").grid(row=12, column=0, sticky="w", padx=27)
                statuses_frame = CTkFrame(master=add_frame, fg_color="transparent")
                statuses_frame.grid(row=13, column=0, padx=27, pady=(5, 20), sticky="w")

                status_var = StringVar(value="Active")
                statuses = ["Active", "Inactive"]

                for i, status in enumerate(statuses):
                    CTkRadioButton(master=statuses_frame, text=status, variable=status_var, value=status, text_color="#2A8C55", font=("Arial Bold", 12), fg_color="#52A476", border_color="#52A476", hover_color="#207244").grid(row=i, column=0, sticky="w", padx=5, pady=(0, 10))

                # Button Frame for 'Update Supplier' and 'Add Supplier'
                button_frame = CTkFrame(master=add_frame, fg_color="transparent")
                button_frame.grid(row=14, column=0, padx=27, pady=20, sticky="e")

                # Update Supplier Button
                update_button = CTkButton(master=button_frame, text="Update Supplier", command=update, fg_color="#2A8C55", hover_color="#207244", font=("Arial Bold", 14))
                update_button.grid(row=0, column=0, padx=(0, 10))

                # Add Supplier Button
                add_button = CTkButton(master=button_frame, text="Add Supplier", command=add, fg_color="#2A8C55", hover_color="#207244", font=("Arial Bold", 14))
                add_button.grid(row=0, column=1)


            self.floating_button = CTkButton(master=self.main_view, text="+ Add Supplier", command=add_supplier, fg_color="#2A8C55", hover_color="#207244")
            self.floating_button.place(relx=1, rely=1, anchor="se", x=-20, y=-20)

        transparent_button = CTkButton(master=total_suppliers_metric, text="", command=total_suppliers_clicked, fg_color="transparent", bg_color="transparent", hover_color="#2A8C55", width=180, height=60, border_width=0 )
        transparent_button.place(relx=0, rely=0, relwidth=1, relheight=1)
        pywinstyles.set_opacity(transparent_button, value=0.01)
        
        
        # Pending Orders metric
        pending_orders_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=180, height=60)
        pending_orders_metric.grid_propagate(0)
        pending_orders_metric.pack(side="left", expand=True, fill="both", padx=(0, 7.5), pady=0)

        pending_img_data = Image.open(r"code\img\logistics_icon.png")
        pending_img = CTkImage(light_image=pending_img_data, dark_image=pending_img_data, size=(43, 43))

        CTkLabel(master=pending_orders_metric, image=pending_img, text="").grid(row=0, column=0, rowspan=2, padx=(12, 5), pady=10)
        CTkLabel(master=pending_orders_metric, text="Pending Orders", text_color="#fff", font=("Arial Black", 13.5)).grid(row=0, column=1, sticky="sw")
        CTkLabel(master=pending_orders_metric, text=pending_orders, text_color="#fff", font=("Arial Black", 13.5), justify="left").grid(row=1, column=1, sticky="nw", pady=(0, 10))

        def pending_orders_clicked():
            self.content_frame.destroy()

            # Create a new content frame
            self.content_frame = CTkFrame(master=supply_frame, fg_color="transparent")
            self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Search widgets
            search_container = CTkFrame(master=self.content_frame)
            search_container.pack(side="top", fill="x", padx=10, pady=5)

            # Function to update table data based on search query
            def update_table(event=None):
                search_query = search_entry.get()
                sort_by = sort_by_combo.get()
                status = status_combo.get()

                # Fetch filtered data from logic based on search query, sort order, and status
                table_data = logic.fetch_supplier_orders_filtered(search_query, sort_by, status)
                
                # Clear and update table with new data
                table.update_values(table_data)

            def capture_image():
                # Open the default camera
                cap = cv2.VideoCapture(self.camera_ip)

                # Check if the camera opened successfully
                if not cap.isOpened():
                    print("Could not open camera")
                    return None

                # Read a frame from the camera
                ret, frame = cap.read()

                # Save the image
                image_path = "captured_image.jpg"
                cv2.imwrite(image_path, frame)

                # Release the camera
                cap.release()

                print("Image captured and saved as", image_path)
                return image_path

            def scan():
                image_path = capture_image()
                # Open the image using PIL
                image = Image.open(image_path)

                # Decode the barcode from the image
                barcodes = decode(image)

                # If no barcode is found
                if not barcodes:
                    print("No barcode found.")
                    return None

                # Extract data from the first barcode found
                barcode_data = barcodes[0].data.decode('utf-8')

                search_entry.delete(0, "end")
                search_entry.insert(0, barcode_data)
                update_table() 


            # Search widgets
            search_entry = CTkEntry(master=search_container, width=305, placeholder_text="Search Supplier", border_color="#2A8C55", border_width=2)
            search_entry.pack(side="left", padx=(13, 0), pady=15, expand=True, fill="x")

            # Adding a rounded square button with a camera logo
            camera_image = Image.open(r"code\img\camera.png")  # Replace with your camera logo path
            camera_image_resized = camera_image.resize((20, 20))  # Adjust size as needed
            camera_photo = CTkImage(dark_image=camera_image_resized, size=(20, 20))

            camera_button = CTkButton(master=search_container, image=camera_photo, text="", fg_color="#2A8C55", hover_color="#207244", width=40, height=20, corner_radius=5, command=scan)
            camera_button.pack(side="left", padx=(13, 0), pady=15)

            sort_by_combo = CTkComboBox(master=search_container, width=125, values=["Order Date","Most Recent Order", "Least Recent Order"], button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=update_table)
            sort_by_combo.pack(side="left", padx=(13, 0), pady=15)
            status_combo = CTkComboBox(master=search_container, width=125, values=[ "Status","Pending", "delivered"], button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=update_table)
            status_combo.pack(side="left", padx=(13, 0), pady=15)

            # Bind search entry to update table when the user types
            search_entry.bind("<Return>", update_table)
            
            # Table data
            table_data = logic.fetch_supplier_orders()

            # Table frame
            table_frame = CTkScrollableFrame(master=self.content_frame, fg_color="transparent")
            table_frame.pack(expand=True, fill="both", padx=10, pady=10)

            # Creating a table widget
            table = CTkTable(master=table_frame, values=table_data, colors=["#E6E6E6", "#EEEEEE"], header_color="#2A8C55", hover_color="#B4B4B4")

            # Customize the header row (row 0)
            table.edit_row(0, text_color="#fff", hover_color="#2A8C55")

            # Pack the table
            table.pack(expand=True, fill="both")

            # Floating button to add new supplier
            def add_supplier_order():
                self.clear_main_view()

                def add_order():
                    # Fetch values from the text boxes
                    order_id = order_id_entry.get()
                    supplier_id = supplier_id_entry.get()
                    supplier_name = supplier_name_entry.get()
                    product_name = product_name_entry.get()
                    order_count = int(order_count_entry.get())
                    order_date = order_date_entry.get()
                    expected_delivery_date = expected_delivery_date_entry.get()
                    total_amount = float(total_amount_entry.get())
                    status = status_var.get()
                    
                    # Adding supplier order to the database
                    logic.add_supplier_order_to_db(order_id, supplier_id, supplier_name, product_name, order_count, order_date, expected_delivery_date, status, total_amount)

                    self.clear_main_view()
                    self.load_supply()

                def update_order():
                    # Fetch values from the text boxes
                    order_id = order_id_entry.get()
                    supplier_id = supplier_id_entry.get()
                    supplier_name = supplier_name_entry.get()
                    product_name = product_name_entry.get()
                    order_count = int(order_count_entry.get())
                    order_date = order_date_entry.get()
                    expected_delivery_date = expected_delivery_date_entry.get()
                    total_amount = float(total_amount_entry.get())
                    status = status_var.get()

                    # Updating supplier order in the database
                    logic.update_supplier_order_in_db(order_id, supplier_id, supplier_name, product_name, order_count, order_date, expected_delivery_date, status, total_amount)                    
                    self.clear_main_view()
                    self.load_supply()

                # Main view - using CTkScrollableFrame for scrollable functionality
                order_frame = CTkScrollableFrame(master=self.main_view, fg_color="#fff", width=700, height=550, corner_radius=0)
                order_frame.pack_propagate(0)
                order_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)

                # Back Button
                back_image = Image.open(r"code\img\back.png")  # Replace with your image path
                back_image_resized = back_image.resize((18, 18))  # Resize the image
                back_photo = CTkImage(dark_image=back_image_resized, size=(18, 18))

                back_button = CTkButton(master=order_frame, image=back_photo, text="", fg_color="transparent", hover=False, command=self.load_orders, height=25, width=25)
                back_button.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

                # Supplier ID
                CTkLabel(master=order_frame, text="Order ID", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=1, column=0, sticky="w", padx=20)
                order_id_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
                order_id_entry.grid(row=2, column=0, ipady=10, padx=20, pady=(5, 10))

                # Supplier Name
                CTkLabel(master=order_frame, text="Supplier ID", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=1, column=1, sticky="w", padx=20)
                supplier_id_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
                supplier_id_entry.grid(row=2, column=1, ipady=10, padx=20, pady=(5, 10))

                # Supplier Name
                CTkLabel(master=order_frame, text="Supplier Name", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=3, column=0, sticky="w", padx=20)
                supplier_name_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=725)
                supplier_name_entry.grid(row=4, column=0, columnspan=2, ipady=10, padx=20, pady=(5, 10))

                # Product Name
                CTkLabel(master=order_frame, text="Product Name", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=5, column=0, sticky="w", padx=20)
                product_name_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
                product_name_entry.grid(row=6, column=0, ipady=10, padx=20, pady=(5, 10))

                # Order Count
                CTkLabel(master=order_frame, text="Order Count", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=5, column=1, sticky="w", padx=20)
                order_count_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
                order_count_entry.grid(row=6, column=1, ipady=10, padx=20, pady=(5, 10))

                # Order Date
                CTkLabel(master=order_frame, text="Order Date", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=7, column=0, sticky="w", padx=20)
                order_date_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
                order_date_entry.grid(row=8, column=0, ipady=10, padx=20, pady=(5, 10))

                # Expected Delivery Date
                CTkLabel(master=order_frame, text="Expected Delivery Date", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=7, column=1, sticky="w", padx=20)
                expected_delivery_date_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
                expected_delivery_date_entry.grid(row=8, column=1, ipady=10, padx=20, pady=(5, 10))

                # Total Amount
                CTkLabel(master=order_frame, text="Total Amount", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=9, column=0, sticky="w", padx=20)
                total_amount_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
                total_amount_entry.grid(row=10, column=0, ipady=10, padx=20, pady=(5, 10))

                # Status
                CTkLabel(master=order_frame, text="Status", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=9, column=1, sticky="w", padx=20)
                status_var = StringVar(value="pending")
                status_frame = CTkFrame(master=order_frame, fg_color="transparent")
                status_frame.grid(row=10, column=1, padx=20, pady=(5, 20), sticky="w")

                statuses = ["pending", "delivered"]
                for i, status in enumerate(statuses):
                    CTkRadioButton(master=status_frame, text=status, variable=status_var, value=status, text_color="#2A8C55", font=("Arial Bold", 12), fg_color="#52A476", border_color="#52A476", hover_color="#207244").grid(row=i, column=0, sticky="w", padx=5, pady=(0, 10))

                # Button Frame for 'Update Order' and 'Add Order'
                button_frame = CTkFrame(master=order_frame, fg_color="transparent")
                button_frame.grid(row=11, column=0, columnspan=2, padx=20, pady=20, sticky="e")

                # Update Order Button
                update_button = CTkButton(master=button_frame, text="Update Order", command=update_order, fg_color="#2A8C55", hover_color="#207244", font=("Arial Bold", 14))
                update_button.grid(row=0, column=0, padx=(0, 10))

                # Add Order Button
                add_button = CTkButton(master=button_frame, text="Add Order", command=add_order, fg_color="#2A8C55", hover_color="#207244", font=("Arial Bold", 14))
                add_button.grid(row=0, column=1)

            self.floating_button = CTkButton(master=self.main_view, text="+ Add Order", command=add_supplier_order, fg_color="#2A8C55", hover_color="#207244")
            self.floating_button.place(relx=1, rely=1, anchor="se", x=-20, y=-20)
            
        transparent_button = CTkButton(pending_orders_metric, text="", command=pending_orders_clicked, fg_color="transparent", hover_color="#2A8C55", width=180, height=60)
        transparent_button.place(relx=0, rely=0, relwidth=1, relheight=1)
        pywinstyles.set_opacity(transparent_button, value=0.01)
        

        # Average Lead Time metric
        average_lead_time_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=180, height=60)
        average_lead_time_metric.grid_propagate(0)
        average_lead_time_metric.pack(side="right", expand=True, fill="both", padx=(0, 0), pady=0)

        lead_time_img_data = Image.open(r"code\img\analytics_icon.png")
        lead_time_img = CTkImage(light_image=lead_time_img_data, dark_image=lead_time_img_data, size=(43, 43))

        CTkLabel(master=average_lead_time_metric, image=lead_time_img, text="").grid(row=0, column=0, rowspan=2, padx=(12, 5), pady=10)
        CTkLabel(master=average_lead_time_metric, text="Avg Lead Time", text_color="#fff", font=("Arial Black", 13.5)).grid(row=0, column=1, sticky="sw")
        CTkLabel(master=average_lead_time_metric, text=f"{avg_lead_time:.2f} days", text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0, 10))

        def avg_lead_time_clicked():
            # Destroy the existing content frame if it exists
            self.content_frame.destroy()

            widget_destroy(self.floating_button)

            # Create a new content frame
            self.content_frame = CTkFrame(master=supply_frame, fg_color="transparent")
            self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Fetch the data from the database
            suppliers, lead_times = logic.fetch_average_lead_times()

            # Create the bar chart
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(suppliers, lead_times, color='#2A8C55')
            ax.set_xlabel('Supplier Name')
            ax.set_ylabel('Lead Time (days)')
            ax.set_title('Average Lead Time of Different Suppliers')
            ax.set_xticklabels(suppliers, rotation=45, ha="right")  # Rotate labels for better readability

            # Embed the plot in a Tkinter window
            canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        transparent_button = CTkButton(average_lead_time_metric, text="", command=avg_lead_time_clicked, fg_color="transparent", hover_color="#2A8C55", width=180, height=60)
        transparent_button.place(relx=0, rely=0, relwidth=1, relheight=1)
        pywinstyles.set_opacity(transparent_button, value=0.01)

        total_suppliers_clicked()
  
    def load_reports(self):
        self.clear_main_view()

        # Scrollable reports management frame
        reports_frame = CTkScrollableFrame(master=self.main_view, fg_color="transparent")
        reports_frame.pack(expand=True, fill="both", padx=0, pady=0)

        # Title frame
        title_frame = CTkFrame(master=reports_frame, fg_color="transparent")
        title_frame.pack(anchor="n", fill="x", padx=0, pady=(0, 0))

        # Set up grid in title frame
        title_frame.grid_columnconfigure(0, weight=1)
        title_frame.grid_columnconfigure(1, weight=0)

        # Title label
        title_label = CTkLabel(master=title_frame, text="Today's Report", font=("Arial Black", 20), text_color="#2A8C55")
        title_label.grid(row=0, column=0, sticky="w", padx=(10, 0), pady=(10, 0))

        # Function to update the title
        def update_title(report_title):
            title_label.configure(text=report_title)
        
        def handle_today():
            # Clear previous content
            for widget in reports_frame.winfo_children():
                if widget != title_frame:
                    widget.destroy()
            
            revenue, profit, fulfillment_rate, supplier_names, supplier_values, total_units_sold, max_units, hourly_revenue, hourly_costs = logic.fetch_today_metrics()

            # Update title
            update_title("Today's report")

            # Metrics container
            metrics_frame = CTkFrame(master=reports_frame, fg_color="transparent")
            metrics_frame.pack(anchor="n", fill="x", padx=20, pady=(10, 0))

            # Revenue metric
            revenue_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            revenue_metric.grid_propagate(0)
            revenue_metric.pack(side="left", expand=True, fill="both", padx=(0, 10), pady=5)

            revenue_img_data = Image.open(r"code\img\revenue.png")  # replace with your revenue icon path
            revenue_img = CTkImage(light_image=revenue_img_data, dark_image=revenue_img_data, size=(43, 43))

            CTkLabel(master=revenue_metric, image=revenue_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=revenue_metric, text="Revenue", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=revenue_metric, text=f"${revenue}", text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Profit metric
            profit_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            profit_metric.grid_propagate(0)
            profit_metric.pack(side="left", expand=True, fill="both", padx=(10, 10), pady=5)

            profit_img_data = Image.open(r"code\img\profit.png")  # replace with your profit icon path
            profit_img = CTkImage(light_image=profit_img_data, dark_image=profit_img_data, size=(43, 43))

            CTkLabel(master=profit_metric, image=profit_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=profit_metric, text="Profit", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=profit_metric, text=f"${profit}", text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Order Fulfillment Rate metric
            order_fulfillment_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            order_fulfillment_metric.grid_propagate(0)
            order_fulfillment_metric.pack(side="left", expand=True, fill="both", padx=(10, 0), pady=5)

            fulfillment_img_data = Image.open(r"code\img\fullfill.png")  # replace with your order fulfillment icon path
            fulfillment_img = CTkImage(light_image=fulfillment_img_data, dark_image=fulfillment_img_data, size=(43, 43))

            CTkLabel(master=order_fulfillment_metric, image=fulfillment_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=order_fulfillment_metric, text="Order Fulfillment", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=order_fulfillment_metric, text=f"{fulfillment_rate}%", text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Container for line chart and bottom elements
            top_section = CTkFrame(master=reports_frame, fg_color="transparent")
            top_section.pack(fill="x", padx=20, pady=(10, 10))

            # Revenue vs. Cost line chart for today
            line_chart_frame = CTkFrame(master=top_section, fg_color="transparent", height=175, width=300)
            line_chart_frame.pack(side="left", fill="both", padx=(0, 10), pady=10)

            # Sample data for today's hourly revenue and cost
            hours = [f'{i}:00' for i in range(9, 18)]  # From 9 AM to 5 PM
            revenue = hourly_revenue[9:18]  
            cost =  hourly_costs[9:18]  

            # Create a matplotlib figure
            fig, ax = plt.subplots(figsize=(9, 4))  # Adjusted size to fit the frame
            ax.plot(hours, revenue, label='Revenue', marker='o')
            ax.plot(hours, cost, label='Cost', marker='o')

            ax.set_title('Today\'s Revenue vs. Cost')
            ax.set_xlabel('Hour')
            ax.set_ylabel('Amount')
            ax.legend()

            # Embed the matplotlib figure in the CustomTkinter frame
            canvas = FigureCanvasTkAgg(fig, master=line_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Container for bar graph and donut chart
            bottom_section = CTkFrame(master=reports_frame, fg_color="transparent")
            bottom_section.pack(fill="x", padx=20, pady=(10, 10))

            # Top Suppliers bar graph
            bar_graph = CTkFrame(master=bottom_section, fg_color="#2A8C55", height=150, width=250)
            bar_graph.pack(side="left", fill="both", padx=(0, 10), pady=10)

            # Data for the bar graph
            suppliers = supplier_names
            values = supplier_values
            print(suppliers)

            # Create the bar graph
            fig, ax = plt.subplots(figsize=(5, 4))  # Adjusted size to fit the frame
            ax.bar(suppliers, values, color='#66b3ff')
            ax.set_title('Top Suppliers')
            ax.set_xlabel('Supplier')
            ax.set_ylabel('Value')

            # Embed the bar graph in the CustomTkinter frame
            canvas = FigureCanvasTkAgg(fig, master=bar_graph)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Create a frame to hold the donut chart
            donut_chart_container = CTkFrame(master=bottom_section, fg_color="transparent")
            donut_chart_container.pack(side="right", fill="both", padx=(10, 0), pady=10)

            # Create a label for the chart title
            chart_header = CTkLabel(master=donut_chart_container, text="Units sold", text_color="#000000", font=("calibri", 25))
            chart_header.pack(pady=(50, 20))

            # Create a figure for the pie chart
            fig = plt.Figure(figsize=(4, 4))
            ax = fig.add_subplot(111)

            # Sample data for the pie chart
            units_sold = total_units_sold
            maxi_units = max_units

            ax.pie([units_sold, maxi_units], labels=['Units Sold', 'Max Units'], colors=['#2A8C55', '#9CCF9D'])

            # Create a canvas to display the pie chart
            canvas = FigureCanvasTkAgg(fig, master=donut_chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=0, pady=0)

            # Create a frame to hold the chart details
            details_frame = CTkFrame(master=donut_chart_container, fg_color="transparent")
            details_frame.pack(padx=0, pady=10)

            # Add legend items to the details frame
            values = {
                "Units Sold": {"color": "#2A8C55", "value": units_sold},
                "Max Units": {"color": "#9CCF9D", "value": max_units}
            }

            for key, data in values.items():
                data_circle = CTkRadioButton(details_frame, hover=False, text=f"{key}: {data['value']}",
                                                width=1, fg_color="#2A8C55")
                data_circle.select()
                data_circle.pack(pady=5)

        def handle_this_week():
            # Clear previous content
            for widget in reports_frame.winfo_children():
                if widget != title_frame:
                    widget.destroy()

            revenue, profit, fulfillment_rate, supplier_names, supplier_values, units_sold, maxi_units, weekly_revenue, weekly_costs = logic.fetch_this_week_metrics()


            # Update title
            update_title("This week's report,")

            # Metrics container
            metrics_frame = CTkFrame(master=reports_frame, fg_color="transparent")
            metrics_frame.pack(anchor="n", fill="x", padx=20, pady=(10, 0))

            # Revenue metric
            revenue_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            revenue_metric.grid_propagate(0)
            revenue_metric.pack(side="left", expand=True, fill="both", padx=(0, 10), pady=5)

            revenue_img_data = Image.open(r"code\img\revenue.png")  # replace with your revenue icon path
            revenue_img = CTkImage(light_image=revenue_img_data, dark_image=revenue_img_data, size=(43, 43))

            CTkLabel(master=revenue_metric, image=revenue_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=revenue_metric, text="Revenue", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=revenue_metric, text=f'${revenue}' ,text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Profit metric
            profit_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            profit_metric.grid_propagate(0)
            profit_metric.pack(side="left", expand=True, fill="both", padx=(10, 10), pady=5)

            profit_img_data = Image.open(r"code\img\profit.png")  # replace with your profit icon path
            profit_img = CTkImage(light_image=profit_img_data, dark_image=profit_img_data, size=(43, 43))

            CTkLabel(master=profit_metric, image=profit_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=profit_metric, text="Profit", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=profit_metric, text=f'${profit}', text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Order Fulfillment Rate metric
            order_fulfillment_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            order_fulfillment_metric.grid_propagate(0)
            order_fulfillment_metric.pack(side="left", expand=True, fill="both", padx=(10, 0), pady=5)

            fulfillment_img_data = Image.open(r"code\img\fullfill.png")  # replace with your order fulfillment icon path
            fulfillment_img = CTkImage(light_image=fulfillment_img_data, dark_image=fulfillment_img_data, size=(43, 43))

            CTkLabel(master=order_fulfillment_metric, image=fulfillment_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=order_fulfillment_metric, text="Order Fulfillment", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=order_fulfillment_metric, text=f'${fulfillment_rate}', text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Container for line chart and bottom elements
            top_section = CTkFrame(master=reports_frame, fg_color="transparent")
            top_section.pack(fill="x", padx=20, pady=(10, 10))

            # Revenue vs. Cost line chart for today
            line_chart_frame = CTkFrame(master=top_section, fg_color="transparent", height=175, width=300)
            line_chart_frame.pack(side="left", fill="both", padx=(0, 10), pady=10)

            # Sample data for today's hourly revenue and cost
            hours = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']  # From 9 AM to 5 PM
            revenue = weekly_revenue
            cost = weekly_costs

            # Create a matplotlib figure
            fig, ax = plt.subplots(figsize=(9, 4))  # Adjusted size to fit the frame
            ax.plot(hours, revenue, label='Revenue', marker='o')
            ax.plot(hours, cost, label='Cost', marker='o')

            ax.set_title('This Week\'s Revenue vs. Cost')
            ax.set_xlabel('Day')
            ax.set_ylabel('Amount')
            ax.legend()

            # Embed the matplotlib figure in the CustomTkinter frame
            canvas = FigureCanvasTkAgg(fig, master=line_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Container for bar graph and donut chart
            bottom_section = CTkFrame(master=reports_frame, fg_color="transparent")
            bottom_section.pack(fill="x", padx=20, pady=(10, 10))

            # Top Suppliers bar graph
            bar_graph = CTkFrame(master=bottom_section, fg_color="#2A8C55", height=150, width=250)
            bar_graph.pack(side="left", fill="both", padx=(0, 10), pady=10)

            # Data for the bar graph
            suppliers = supplier_names
            values = supplier_values

            # Create the bar graph
            fig, ax = plt.subplots(figsize=(5, 4))  # Adjusted size to fit the frame
            ax.bar(suppliers, values, color='#66b3ff')
            ax.set_title('Top Suppliers')
            ax.set_xlabel('Supplier')
            ax.set_ylabel('Value')

            # Embed the bar graph in the CustomTkinter frame
            canvas = FigureCanvasTkAgg(fig, master=bar_graph)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Create a frame to hold the donut chart
            donut_chart_container = CTkFrame(master=bottom_section, fg_color="transparent")
            donut_chart_container.pack(side="right", fill="both", padx=(10, 0), pady=10)

            # Create a label for the chart title
            chart_header = CTkLabel(master=donut_chart_container, text="Units sold", text_color="#000000", font=("calibri", 25))
            chart_header.pack(pady=(50, 20))

            # Create a figure for the pie chart
            fig = plt.Figure(figsize=(4, 4))
            ax = fig.add_subplot(111)

            # Sample data for the pie chart
            units_sold = units_sold
            max_units = maxi_units

            ax.pie([units_sold, max_units], labels=['Units Sold', 'Max Units'], colors=['#2A8C55', '#9CCF9D'])

            # Create a canvas to display the pie chart
            canvas = FigureCanvasTkAgg(fig, master=donut_chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=0, pady=0)

            # Create a frame to hold the chart details
            details_frame = CTkFrame(master=donut_chart_container, fg_color="transparent")
            details_frame.pack(padx=0, pady=10)

            # Add legend items to the details frame
            values = {
                "Units Sold": {"color": "#2A8C55", "value": units_sold},
                "Max Units": {"color": "#9CCF9D", "value": max_units}
            }

            for key, data in values.items():
                data_circle = CTkRadioButton(details_frame, hover=False, text=f"{key}: {data['value']}",
                                                width=1, fg_color="#2A8C55")
                data_circle.select()
                data_circle.pack(pady=5)

        def handle_this_month():
            # Clear previous content
            for widget in reports_frame.winfo_children():
                if widget != title_frame:
                    widget.destroy()

            # Update title
            update_title("This month's report,")

            revenue, profit, fulfillment_rate, supplier_names, supplier_values, units_sold, maxi_units, monthly_revenue, monthly_costs = logic.fetch_this_month_metrics()

            # Metrics container
            metrics_frame = CTkFrame(master=reports_frame, fg_color="transparent")
            metrics_frame.pack(anchor="n", fill="x", padx=20, pady=(10, 0))

            # Revenue metric
            revenue_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            revenue_metric.grid_propagate(0)
            revenue_metric.pack(side="left", expand=True, fill="both", padx=(0, 10), pady=5)

            revenue_img_data = Image.open(r"code\img\revenue.png")  # replace with your revenue icon path
            revenue_img = CTkImage(light_image=revenue_img_data, dark_image=revenue_img_data, size=(43, 43))

            CTkLabel(master=revenue_metric, image=revenue_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=revenue_metric, text="Revenue", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=revenue_metric, text=f'${revenue}', text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Profit metric
            profit_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            profit_metric.grid_propagate(0)
            profit_metric.pack(side="left", expand=True, fill="both", padx=(10, 10), pady=5)

            profit_img_data = Image.open(r"code\img\profit.png")  # replace with your profit icon path
            profit_img = CTkImage(light_image=profit_img_data, dark_image=profit_img_data, size=(43, 43))

            CTkLabel(master=profit_metric, image=profit_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=profit_metric, text="Profit", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=profit_metric, text=f'${profit}', text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Order Fulfillment Rate metric
            order_fulfillment_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            order_fulfillment_metric.grid_propagate(0)
            order_fulfillment_metric.pack(side="left", expand=True, fill="both", padx=(10, 0), pady=5)

            fulfillment_img_data = Image.open(r"code\img\fullfill.png")  # replace with your order fulfillment icon path
            fulfillment_img = CTkImage(light_image=fulfillment_img_data, dark_image=fulfillment_img_data, size=(43, 43))

            CTkLabel(master=order_fulfillment_metric, image=fulfillment_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=order_fulfillment_metric, text="Order Fulfillment", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=order_fulfillment_metric, text=f'{fulfillment_rate}%', text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Container for line chart and bottom elements
            top_section = CTkFrame(master=reports_frame, fg_color="transparent")
            top_section.pack(fill="x", padx=20, pady=(10, 10))

            # Revenue vs. Cost line chart for today
            line_chart_frame = CTkFrame(master=top_section, fg_color="transparent", height=175, width=300)
            line_chart_frame.pack(side="left", fill="both", padx=(0, 10), pady=10)

            # Sample data for revenue and cost by day in a month
            days = [f'{i}' for i in range(1, 31)]  # From Day 1 to Day 30
            revenue = monthly_revenue
            cost = monthly_costs

            # Create a matplotlib figure
            fig, ax = plt.subplots(figsize=(9, 4))  # Adjusted size to fit the frame
            ax.plot(days, revenue, label='Revenue', marker='o')
            ax.plot(days, cost, label='Cost', marker='o')

            ax.set_title('This Month\'s Revenue vs. Cost')
            ax.set_xlabel('Days')
            ax.set_ylabel('Amount')
            ax.legend()

            # Embed the matplotlib figure in the CustomTkinter frame
            canvas = FigureCanvasTkAgg(fig, master=line_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Container for bar graph and donut chart
            bottom_section = CTkFrame(master=reports_frame, fg_color="transparent")
            bottom_section.pack(fill="x", padx=20, pady=(10, 10))

            # Top Suppliers bar graph
            bar_graph = CTkFrame(master=bottom_section, fg_color="#2A8C55", height=150, width=250)
            bar_graph.pack(side="left", fill="both", padx=(0, 10), pady=10)

            # Data for the bar graph
            suppliers = supplier_names
            values = supplier_values

            # Create the bar graph
            fig, ax = plt.subplots(figsize=(5, 4))  # Adjusted size to fit the frame
            ax.bar(suppliers, values, color='#66b3ff')
            ax.set_title('Top Suppliers')
            ax.set_xlabel('Supplier')
            ax.set_ylabel('Value')

            # Embed the bar graph in the CustomTkinter frame
            canvas = FigureCanvasTkAgg(fig, master=bar_graph)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Create a frame to hold the donut chart
            donut_chart_container = CTkFrame(master=bottom_section, fg_color="transparent")
            donut_chart_container.pack(side="right", fill="both", padx=(10, 0), pady=10)

            # Create a label for the chart title
            chart_header = CTkLabel(master=donut_chart_container, text="Units sold", text_color="#000000", font=("calibri", 25))
            chart_header.pack(pady=(50, 20))

            # Create a figure for the pie chart
            fig = plt.Figure(figsize=(4, 4))
            ax = fig.add_subplot(111)

            # Sample data for the pie chart
            units_sold = units_sold
            max_units = maxi_units

            ax.pie([units_sold, max_units], labels=['Units Sold', 'Max Units'], colors=['#2A8C55', '#9CCF9D'])

            # Create a canvas to display the pie chart
            canvas = FigureCanvasTkAgg(fig, master=donut_chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=0, pady=0)

            # Create a frame to hold the chart details
            details_frame = CTkFrame(master=donut_chart_container, fg_color="transparent")
            details_frame.pack(padx=0, pady=10)

            # Add legend items to the details frame
            values = {
                "Units Sold": {"color": "#2A8C55", "value": units_sold},
                "Max Units": {"color": "#9CCF9D", "value": max_units}
            }

            for key, data in values.items():
                data_circle = CTkRadioButton(details_frame, hover=False, text=f"{key}: {data['value']}",
                                                width=1, fg_color="#2A8C55")
                data_circle.select()
                data_circle.pack(pady=5)

        def handle_this_year():
             # Clear previous content
            for widget in reports_frame.winfo_children():
                if widget != title_frame:
                    widget.destroy()

            # Update title
            update_title("This year's report,")

            revenue, profit, fulfillment_rate, supplier_names, supplier_values, units_sold, maxi_units, monthly_revenue, monthly_costs = logic.fetch_this_year_metrics()

            # Metrics container
            metrics_frame = CTkFrame(master=reports_frame, fg_color="transparent")
            metrics_frame.pack(anchor="n", fill="x", padx=20, pady=(10, 0))

            # Revenue metric
            revenue_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            revenue_metric.grid_propagate(0)
            revenue_metric.pack(side="left", expand=True, fill="both", padx=(0, 10), pady=5)

            revenue_img_data = Image.open(r"code\img\revenue.png")  # replace with your revenue icon path
            revenue_img = CTkImage(light_image=revenue_img_data, dark_image=revenue_img_data, size=(43, 43))

            CTkLabel(master=revenue_metric, image=revenue_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=revenue_metric, text="Revenue", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=revenue_metric, text=f'${revenue}', text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Profit metric
            profit_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            profit_metric.grid_propagate(0)
            profit_metric.pack(side="left", expand=True, fill="both", padx=(10, 10), pady=5)

            profit_img_data = Image.open(r"code\img\profit.png")  # replace with your profit icon path
            profit_img = CTkImage(light_image=profit_img_data, dark_image=profit_img_data, size=(43, 43))

            CTkLabel(master=profit_metric, image=profit_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=profit_metric, text="Profit", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=profit_metric, text=f'${profit}', text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Order Fulfillment Rate metric
            order_fulfillment_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=200, height=60)
            order_fulfillment_metric.grid_propagate(0)
            order_fulfillment_metric.pack(side="left", expand=True, fill="both", padx=(10, 0), pady=5)

            fulfillment_img_data = Image.open(r"code\img\fullfill.png")  # replace with your order fulfillment icon path
            fulfillment_img = CTkImage(light_image=fulfillment_img_data, dark_image=fulfillment_img_data, size=(43, 43))

            CTkLabel(master=order_fulfillment_metric, image=fulfillment_img, text="").grid(row=0, column=0, rowspan=2, padx=(12,5), pady=10)
            CTkLabel(master=order_fulfillment_metric, text="Order Fulfillment", text_color="#fff", font=("Arial Black", 15)).grid(row=0, column=1, sticky="sw")
            CTkLabel(master=order_fulfillment_metric, text=f'{fulfillment_rate:.2f}%', text_color="#fff", font=("Arial Black", 15), justify="left").grid(row=1, column=1, sticky="nw", pady=(0,10))

            # Container for line chart and bottom elements
            top_section = CTkFrame(master=reports_frame, fg_color="transparent")
            top_section.pack(fill="x", padx=20, pady=(10, 10))

            # Revenue vs. Cost line chart for today
            line_chart_frame = CTkFrame(master=top_section, fg_color="transparent", height=175, width=300)
            line_chart_frame.pack(side="left", fill="both", padx=(0, 10), pady=10)

            # Sample data for today's hourly revenue and cost
            hours = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']  # From 9 AM to 5 PM
            revenue = monthly_revenue
            cost = monthly_costs

            # Create a matplotlib figure
            fig, ax = plt.subplots(figsize=(9, 4))  # Adjusted size to fit the frame
            ax.plot(hours, revenue, label='Revenue', marker='o')
            ax.plot(hours, cost, label='Cost', marker='o')

            ax.set_title('This Year\'s Revenue vs. Cost')
            ax.set_xlabel('Month')
            ax.set_ylabel('Amount')
            ax.legend()

            # Embed the matplotlib figure in the CustomTkinter frame
            canvas = FigureCanvasTkAgg(fig, master=line_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Container for bar graph and donut chart
            bottom_section = CTkFrame(master=reports_frame, fg_color="transparent")
            bottom_section.pack(fill="x", padx=20, pady=(10, 10))

            # Top Suppliers bar graph
            bar_graph = CTkFrame(master=bottom_section, fg_color="#2A8C55", height=150, width=250)
            bar_graph.pack(side="left", fill="both", padx=(0, 10), pady=10)

            # Data for the bar graph
            suppliers = supplier_names
            values = supplier_values

            # Create the bar graph
            fig, ax = plt.subplots(figsize=(5, 4))  # Adjusted size to fit the frame
            ax.bar(suppliers, values, color='#66b3ff')
            ax.set_title('Top Suppliers')
            ax.set_xlabel('Supplier')
            ax.set_ylabel('Value')

            # Embed the bar graph in the CustomTkinter frame
            canvas = FigureCanvasTkAgg(fig, master=bar_graph)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Create a frame to hold the donut chart
            donut_chart_container = CTkFrame(master=bottom_section, fg_color="transparent")
            donut_chart_container.pack(side="right", fill="both", padx=(10, 0), pady=10)

            # Create a label for the chart title
            chart_header = CTkLabel(master=donut_chart_container, text="Units sold", text_color="#000000", font=("calibri", 25))
            chart_header.pack(pady=(50, 20))

            # Create a figure for the pie chart
            fig = plt.Figure(figsize=(4, 4))
            ax = fig.add_subplot(111)

            # Sample data for the pie chart
            units_sold = units_sold
            max_units = maxi_units

            ax.pie([units_sold, max_units], labels=['Units Sold', 'Max Units'], colors=['#2A8C55', '#9CCF9D'])

            # Create a canvas to display the pie chart
            canvas = FigureCanvasTkAgg(fig, master=donut_chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=0, pady=0)

            # Create a frame to hold the chart details
            details_frame = CTkFrame(master=donut_chart_container, fg_color="transparent")
            details_frame.pack(padx=0, pady=10)

            # Add legend items to the details frame
            values = {
                "Units Sold": {"color": "#2A8C55", "value": units_sold},
                "Max Units": {"color": "#9CCF9D", "value": max_units}
            }

            for key, data in values.items():
                data_circle = CTkRadioButton(details_frame, hover=False, text=f"{key}: {data['value']}",
                                                width=1, fg_color="#2A8C55")
                data_circle.select()
                data_circle.pack(pady=5)

        def perform_action(event=None):
            choice = combo.get()
            if choice == "Today":
                handle_today()
            elif choice == "This Week":
                handle_this_week()
            elif choice == "This Month":
                handle_this_month()
            elif choice == "This Year":
                handle_this_year()

        # Combo box for selecting the report type
        combo = CTkComboBox(master=title_frame, values=["Today", "This Week", "This Month", "This Year"])
        combo.configure(fg_color="white", text_color="black", button_color="#2A8C55", dropdown_hover_color="#1F7040", width=200, command= perform_action)
        combo.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=(10, 0))
        combo.set("Today")  # Default selection

        # Initialize with the default "Today" report
        handle_today()

    def load_notifications(self):
        self.clear_main_view()

        # Example of a possible restock method
        def restock_product():
            self.clear_main_view()

            def add_order():
                # Fetch values from the text boxes
                order_id = order_id_entry.get()
                supplier_id = supplier_id_entry.get()
                supplier_name = supplier_name_entry.get()
                product_name = product_name_entry.get()
                order_count = int(order_count_entry.get())
                order_date = order_date_entry.get()
                expected_delivery_date = expected_delivery_date_entry.get()
                total_amount = float(total_amount_entry.get())
                status = status_var.get()
                
                # Adding supplier order to the database
                logic.add_supplier_order_to_db(order_id, supplier_id, supplier_name, product_name, order_count, order_date, expected_delivery_date, status, total_amount)

                self.clear_main_view()
                self.load_supply()

            def update_order():
                # Fetch values from the text boxes
                order_id = order_id_entry.get()
                supplier_id = supplier_id_entry.get()
                supplier_name = supplier_name_entry.get()
                product_name = product_name_entry.get()
                order_count = int(order_count_entry.get())
                order_date = order_date_entry.get()
                expected_delivery_date = expected_delivery_date_entry.get()
                total_amount = float(total_amount_entry.get())
                status = status_var.get()

                # Updating supplier order in the database
                logic.update_supplier_order_in_db(order_id, supplier_id, supplier_name, product_name, order_count, order_date, expected_delivery_date, status, total_amount)                    
                self.clear_main_view()
                self.load_supply()

            # Main view - using CTkScrollableFrame for scrollable functionality
            order_frame = CTkScrollableFrame(master=self.main_view, fg_color="#fff", width=700, height=550, corner_radius=0)
            order_frame.pack_propagate(0)
            order_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)

            # Back Button
            back_image = Image.open(r"code\img\back.png")  # Replace with your image path
            back_image_resized = back_image.resize((18, 18))  # Resize the image
            back_photo = CTkImage(dark_image=back_image_resized, size=(18, 18))

            back_button = CTkButton(master=order_frame, image=back_photo, text="", fg_color="transparent", hover=False, command=self.load_notifications, height=25, width=25)
            back_button.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

            # Supplier ID
            CTkLabel(master=order_frame, text="Order ID", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=1, column=0, sticky="w", padx=20)
            order_id_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
            order_id_entry.grid(row=2, column=0, ipady=10, padx=20, pady=(5, 10))

            # Supplier Name
            CTkLabel(master=order_frame, text="Supplier ID", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=1, column=1, sticky="w", padx=20)
            supplier_id_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
            supplier_id_entry.grid(row=2, column=1, ipady=10, padx=20, pady=(5, 10))

            # Supplier Name
            CTkLabel(master=order_frame, text="Supplier Name", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=3, column=0, sticky="w", padx=20)
            supplier_name_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=725)
            supplier_name_entry.grid(row=4, column=0, columnspan=2, ipady=10, padx=20, pady=(5, 10))

            # Product Name
            CTkLabel(master=order_frame, text="Product Name", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=5, column=0, sticky="w", padx=20)
            product_name_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
            product_name_entry.grid(row=6, column=0, ipady=10, padx=20, pady=(5, 10))

            # Order Count
            CTkLabel(master=order_frame, text="Order Count", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=5, column=1, sticky="w", padx=20)
            order_count_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
            order_count_entry.grid(row=6, column=1, ipady=10, padx=20, pady=(5, 10))

            # Order Date
            CTkLabel(master=order_frame, text="Order Date", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=7, column=0, sticky="w", padx=20)
            order_date_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
            order_date_entry.grid(row=8, column=0, ipady=10, padx=20, pady=(5, 10))

            # Expected Delivery Date
            CTkLabel(master=order_frame, text="Expected Delivery Date", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=7, column=1, sticky="w", padx=20)
            expected_delivery_date_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
            expected_delivery_date_entry.grid(row=8, column=1, ipady=10, padx=20, pady=(5, 10))

            # Total Amount
            CTkLabel(master=order_frame, text="Total Amount", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=9, column=0, sticky="w", padx=20)
            total_amount_entry = CTkEntry(master=order_frame, fg_color="#F0F0F0", border_width=0, width=325)
            total_amount_entry.grid(row=10, column=0, ipady=10, padx=20, pady=(5, 10))

            # Status
            CTkLabel(master=order_frame, text="Status", font=("Arial Bold", 14), text_color="#2A8C55").grid(row=9, column=1, sticky="w", padx=20)
            status_var = StringVar(value="pending")
            status_frame = CTkFrame(master=order_frame, fg_color="transparent")
            status_frame.grid(row=10, column=1, padx=20, pady=(5, 20), sticky="w")

            statuses = ["pending", "delivered"]
            for i, status in enumerate(statuses):
                CTkRadioButton(master=status_frame, text=status, variable=status_var, value=status, text_color="#2A8C55", font=("Arial Bold", 12), fg_color="#52A476", border_color="#52A476", hover_color="#207244").grid(row=i, column=0, sticky="w", padx=5, pady=(0, 10))

            # Button Frame for 'Update Order' and 'Add Order'
            button_frame = CTkFrame(master=order_frame, fg_color="transparent")
            button_frame.grid(row=11, column=0, columnspan=2, padx=20, pady=20, sticky="e")

            # Update Order Button
            update_button = CTkButton(master=button_frame, text="Update Order", command=update_order, fg_color="#2A8C55", hover_color="#207244", font=("Arial Bold", 14))
            update_button.grid(row=0, column=0, padx=(0, 10))

            # Add Order Button
            add_button = CTkButton(master=button_frame, text="Add Order", command=add_order, fg_color="#2A8C55", hover_color="#207244", font=("Arial Bold", 14))
            add_button.grid(row=0, column=1)
            

        # Create a scrollable frame
        scrollable_frame = CTkScrollableFrame(master=self.main_view, 
                                                width=self.main_view.winfo_width(), 
                                                height=self.main_view.winfo_height(), 
                                                corner_radius=0,
                                                fg_color="transparent")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add a heading at the top
        heading_label = CTkLabel(master=scrollable_frame, 
                                text="Stock Alerts and Notifications", 
                                text_color="#2A8C55",  # Darker green text
                                font=("Arial", 20, "bold"))
        heading_label.pack(pady=20, padx=20)

        # Fetch low-stock products (assuming the threshold is set within the logic function)
        low_stock_products = logic.fetch_low_stock_inventory()

        # Loop through the fetched products and create a card for each
        for product in low_stock_products:
            # Create the card frame
            card_frame = CTkFrame(master=scrollable_frame, 
                                    width=350, 
                                    height=150, 
                                    corner_radius=10, 
                                    fg_color="#E9F7EF",  # Soft light green background
                                    border_color="#2A8C55",  # Darker green border
                                    border_width=2)
            card_frame.pack(pady=10, padx=20, fill="x")  # Adjust padding as needed

            # Low Stock Message
            low_stock_label = CTkLabel(card_frame, 
                                        text=f"Low Stock Alert: {product['product_name']}", 
                                        text_color="#2A8C55",  # Darker green text
                                        font=("Arial", 16, "bold"))
            low_stock_label.pack(pady=(10, 5), padx=10, anchor="w")

            # Remaining Quantity
            remaining_qty_label = CTkLabel(card_frame, 
                                            text=f"Remaining Quantity: {product['quantity']}", 
                                            text_color="#6C757D",  # Medium grey text
                                            font=("Arial", 14))
            remaining_qty_label.pack(pady=(5, 0), padx=10, anchor="w")

            # Last Restock Date
            last_restock_label = CTkLabel(card_frame, 
                                            text=f"Last Restock Date: {product['date']}", 
                                            text_color="#6C757D",  # Medium grey text
                                            font=("Arial", 14))
            last_restock_label.pack(pady=(5, 10), padx=10, anchor="w")

            # Restock Button
            restock_button = CTkButton(card_frame, 
                                        text="Restock Now", 
                                        width=120, 
                                        fg_color="#34C759",  # Brighter green button background
                                        hover_color="#28A745",  # Darker green hover effect
                                        text_color="white",  # White text color
                                        font=("Arial", 14),
                                        command= restock_product)
            restock_button.pack(pady=(5, 10), padx=10, anchor="e")
        

    def create_sidebar(self):
        def load_image(path, size=None):
            try:
                img_data = Image.open(path)
                if size:
                    img_data = img_data.resize(size)
                return CTkImage(dark_image=img_data, light_image=img_data)
            except Exception as e:
                print(f"Error loading image {path}: {e}")
                return None

        # Logo
        logo_img_data = Image.open(r"C:\Users\rajesh\OneDrive\Desktop\customtkinter-examples-master\Inventory Management\logo.png")
        logo_img = CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(50, 50))
        CTkLabel(master=self.sidebar_frame, text="", image=logo_img).pack(pady=(38, 0), anchor="center")

        # Sidebar buttons
        sidebar_buttons = [
            ("Dashboard", r"code\img\analytics_icon.png", self.load_dashboard),
            ("Inventory Management", r"code\img\inventory.png", self.load_inventory),
            ("Order Management", r"code\img\list_icon.png", self.load_orders),
            ("Supply Management", r"code\img\settings_icon.png", self.load_supply),
            ("Reports & Analytics", r"code\img\analytics_icon.png", self.load_reports),
        ]

        for text, icon_path, command in sidebar_buttons:
            img = load_image(icon_path, (30, 30))
            if img:
                CTkButton(master=self.sidebar_frame, image=img, text=text, fg_color="transparent", font=("Arial Bold", 12), hover_color="#207244", anchor="w", command=command).pack(anchor="center", ipady=5, pady=(10, 0))

        # Settings and Notification
        settings_frame = CTkFrame(master=self.sidebar_frame, fg_color="transparent")
        settings_frame.pack(anchor="s", pady=(10, 0), padx=10, side="bottom", fill="x")

        notification_img = load_image(r"code\img\notification.png", (25, 25))
        if notification_img:
            settings_button = CTkButton(master=settings_frame, image=notification_img, text="Alerts and Notification", fg_color="transparent", font=("Arial Bold", 12), hover_color="#207244", anchor="w", command=self.load_notifications)
            settings_button.pack(side="left", padx=(0, 5), anchor="s")


    def clear_main_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

    def load_dashboard(self):
        self.clear_main_view()

        # Scrollable frame for the dashboard content
        dashboard_frame = CTkScrollableFrame(master=self.main_view, fg_color="transparent", width=800, height=550, corner_radius=0)
        dashboard_frame.pack(expand=True, fill="both")

        # Title
        title_frame = CTkFrame(master=dashboard_frame, fg_color="transparent")
        title_frame.pack(anchor="n", fill="x", padx=20, pady=(20, 0))
        CTkLabel(master=title_frame, text="Dashboard", font=("Arial Black", 20), text_color="#2A8C55").pack(anchor="nw", side="left")

        # Metrics frame
        metrics_frame = CTkFrame(master=dashboard_frame, fg_color="transparent")
        metrics_frame.pack(anchor="n", fill="x", padx=20, pady=(20, 0))

        data = logic.fetch_dashboard_data()

        # Orders metric
        orders_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=240, height=80)
        orders_metric.grid_propagate(0)
        orders_metric.grid(row=0, column=0, padx=(0, 10))

        logistics_img_data = Image.open(r"code\img\logistics_icon.png")
        logistics_img = CTkImage(light_image=logistics_img_data, dark_image=logistics_img_data, size=(30, 30))
        CTkLabel(master=orders_metric, image=logistics_img, text="").grid(row=0, column=0, rowspan=2, padx=(10, 5), pady=5)
        CTkLabel(master=orders_metric, text="Orders", text_color="#fff", font=("Arial Black", 12)).grid(row=0, column=1, sticky="sw")
        CTkLabel(master=orders_metric, text=str(data['orders_count']), text_color="#fff", font=("Arial Black", 12), justify="left").grid(row=1, column=1, sticky="nw", pady=(0, 5))

        # Deliveries metric
        deliveries_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=240, height=80)
        deliveries_metric.grid_propagate(0)
        deliveries_metric.grid(row=0, column=1, padx=(0, 10))

        deliveries_img_data = Image.open(r"code\img\logistics_icon.png")
        deliveries_img = CTkImage(light_image=deliveries_img_data, dark_image=deliveries_img_data, size=(30, 30))
        CTkLabel(master=deliveries_metric, image=deliveries_img, text="").grid(row=0, column=0, rowspan=2, padx=(10, 5), pady=5)
        CTkLabel(master=deliveries_metric, text="Deliveries", text_color="#fff", font=("Arial Black", 12)).grid(row=0, column=1, sticky="sw")
        CTkLabel(master=deliveries_metric, text=str(data['deliveries_count']), text_color="#fff", font=("Arial Black", 12), justify="left").grid(row=1, column=1, sticky="nw", pady=(0, 5))

        # Revenue metric
        revenue_metric = CTkFrame(master=metrics_frame, fg_color="#2A8C55", width=240, height=80)
        revenue_metric.grid_propagate(0)
        revenue_metric.grid(row=0, column=2, padx=(0, 10))

        delivered_img_data = Image.open(r"code\img\delivered_icon.png")
        delivered_img = CTkImage(light_image=delivered_img_data, dark_image=delivered_img_data, size=(30, 30))
        CTkLabel(master=revenue_metric, image=delivered_img, text="").grid(row=0, column=0, rowspan=2, padx=(10, 5), pady=5)
        CTkLabel(master=revenue_metric, text="Revenue", text_color="#fff", font=("Arial Black", 12)).grid(row=0, column=1, sticky="sw")
        CTkLabel(master=revenue_metric, text=str(data['revenue_total']), text_color="#fff", font=("Arial Black", 12), justify="left").grid(row=1, column=1, sticky="nw", pady=(0, 5))

        # Main content frame
        content_frame = CTkFrame(master=dashboard_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=20, pady=(20, 0))

        # Charts frame
        charts_frame = CTkFrame(master=content_frame, fg_color="transparent")
        charts_frame.pack(fill="x", padx=20, pady=(10, 0))

        # Donut chart frame
        donut_chart_frame = CTkFrame(master=charts_frame, fg_color="#f5f5f5", width=200, height=200, corner_radius=10)
        donut_chart_frame.pack(side="left", padx=(0, 10), pady=(0, 10))
        self.create_donut_chart(donut_chart_frame)

        # Bar chart frame
        bar_chart_frame = CTkFrame(master=charts_frame, fg_color="#f5f5f5", width=300, height=200, corner_radius=10)
        bar_chart_frame.pack(side="left", pady=(0, 10))
        self.create_bar_chart(bar_chart_frame)

        # Create a frame for tables to be side-by-side
        tables_frame = CTkFrame(master=content_frame, fg_color="transparent")
        tables_frame.pack(expand=True, fill="both")

        # Grid to place the tables side-by-side
        tables_frame.grid_rowconfigure(0, weight=1)
        tables_frame.grid_columnconfigure(0, weight=1)
        tables_frame.grid_columnconfigure(1, weight=1)

        # Left frame for the first table
        left_frame = CTkFrame(master=tables_frame, fg_color="#f5f5f5", corner_radius=10)
        left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        table_data = logic.fetch_recent_orders()
        self.create_large_table(left_frame, "Recent Orders", table_data)

        # Right frame for the second table
        right_frame = CTkFrame(master=tables_frame, fg_color="#f5f5f5", corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew")
        table_data1 = logic.fetch_recently_added_items()
        self.create_large_table(right_frame, "Recently Added Items", table_data1)

    def create_donut_chart(self, parent_frame):
        data = logic.fetch_warehouse_utilization()
        used_space = data[0]
        available_space = data[1]
        colors = ['#2A8C55', '#e0e0e0']
        percentage = (used_space/10000)* 100

        fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(aspect="equal"))

        # Create the donut chart without auto text
        wedges, texts = ax.pie(
            [used_space, available_space],
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.3, edgecolor='w')
        )

        # Center circle for the donut shape
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)

        # Customize the percentage text in the center
        ax.text(0, 0, f"{percentage}%", ha='center', va='center', fontsize=14, color='black')

        ax.set(aspect="equal")

        chart_canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Add label below the chart
        CTkLabel(master=parent_frame, text="Warehouse Utilization", font=("Arial Black", 12), text_color="black").pack(pady=(10, 0))

    def create_bar_chart(self, parent_frame):
        data = logic.fetch_top_selling_products()
        products = [row[0] for row in data]  # Product names
        sales = [row[1] for row in data]     # Units sold


        fig, ax = plt.subplots(figsize=(16, 3))
        bars = ax.bar(products, sales, color='#2A8C55')

        ax.set_xlabel('Products')
        ax.set_ylabel('Sales')
        ax.set_title('Top Selling Products')

        chart_canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_large_table(self, parent_frame, title, data):
        # Title
        CTkLabel(master=parent_frame, text=title, font=("calibri", 14), text_color="black").pack(anchor="n", pady=(10, 0))

        # Create a frame for the table within the parent frame
        table_frame = CTkFrame(master=parent_frame, fg_color="transparent")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create and pack the table within the frame
        table = CTkTable(master=table_frame, values=data, colors=["#E6E6E6", "#EEEEEE"], header_color="#2A8C55", hover_color="#B4B4B4")
        table.edit_row(0, text_color="#fff", hover_color="#2A8C55")
        table.pack(fill='both', expand=True)


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()