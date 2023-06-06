import streamlit as st
import datetime
import sqlite3

# Create SQLite database connection
conn = sqlite3.connect('bills.db')
c = conn.cursor()

# Create bills table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS bills (
                bill_id TEXT PRIMARY KEY,
                customer_name TEXT,
                phone_number TEXT,
                date_of_purchase DATE,
                category TEXT,
                total REAL
            )''')

# Create objects table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS objects (
                bill_id TEXT,
                object_name TEXT,
                object_price REAL
            )''')

# Helper function to generate the bill ID
def generate_bill_id(date_str, time_str, serial_number):
    return date_str + time_str + serial_number

# Sidebar options
selected_button = st.sidebar.selectbox("Select an option", ["Generate Bill", "Send Bill to counter", "Edit Bill", "Search Bill"])

# Generate Bill option
if selected_button == "Generate Bill":
    st.header("Generate Bill")

    # Bill details input
    customer_name = st.text_input("Customer Name")
    phone_number = st.text_input("Phone Number")
    date_of_purchase = st.date_input("Date of Purchase", datetime.date.today())
    category = st.text_input("Category")

    # Object details input loop
    objects = []
    total = 0.0

    object_index = 0
    add_object = True

    while add_object:
        object_index += 1
        object_name = st.text_input(f"Object Name {object_index}", key=f"object_name_{object_index}")
        object_price = st.text_input(f"Price {object_index}", key=f"object_price_{object_index}")

        if object_name and object_price:
            try:
                object_price = float(object_price)
                objects.append((object_name, object_price))
                total += object_price
            except ValueError:
                st.warning("Please enter a valid price.")

        add_object = st.button(f"Add Object {object_index + 1}")

    st.text(f"Total: {total}")

    if st.button("Done"):
        now = datetime.datetime.now()
        date_str = now.strftime("%m%d")
        time_str = now.strftime("%H%M")
        serial_number = str(c.execute("SELECT COUNT(*) FROM bills WHERE strftime('%m%d', date_of_purchase) = ?", (date_str,)).fetchone()[0] + 1).zfill(2)
        bill_id = generate_bill_id(date_str, time_str, serial_number)

        # Insert bill into the database
        c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?)",
                  (bill_id, customer_name, phone_number, date_of_purchase, category, total))

        # Insert objects into the database
        for obj_name, obj_price in objects:
            c.execute("INSERT INTO objects VALUES (?, ?, ?)", (bill_id, obj_name, obj_price))

        # Commit changes and close the database connection
        conn.commit()
        conn.close()

        st.success(f"Bill generated! Bill ID: {bill_id}")

        if st.button("Print Bill"):
            st.text(f"Bill ID: {bill_id}")
            st.text(f"Customer Name: {customer_name}")
            st.text(f"Phone Number: {phone_number}")
            st.text(f"Date of Purchase: {date_of_purchase}")
            st.text(f"Category: {category}")
            st.text("Objects:")
            for obj_name, obj_price in objects:
                st.text(f"- {obj_name}: ${obj_price}")
            st.text(f"Total: ${total}")

# Edit Bill option
elif selected_button == "Edit Bill":
    st.header("Edit Bill")

    bill_id = st.text_input("Bill ID")

    # Check if the bill exists
    c.execute("SELECT * FROM bills WHERE bill_id = ?", (bill_id,))
    bill = c.fetchone()
    if bill:
        st.text(f"Bill ID: {bill[0]}")
        st.text(f"Customer Name: {bill[1]}")
        st.text(f"Phone Number: {bill[2]}")
        st.text(f"Date of Purchase: {bill[3]}")
        st.text(f"Category: {bill[4]}")

        # Get the objects for the bill
        c.execute("SELECT * FROM objects WHERE bill_id = ?", (bill_id,))
        objects = c.fetchall()
        if objects:
            st.text("Objects:")
            for obj in objects:
                st.text(f"- {obj[1]}: ${obj[2]}")
        else:
            st.warning("No objects found for this bill.")

        edit_option = st.radio("Select an option", ["Add Objects", "Delete Objects"])
        if edit_option == "Add Objects":
            object_name = st.text_input("Object Name")
            object_price = st.number_input("Object Price", value=0.0)
            if st.button("Add Object"):
                c.execute("INSERT INTO objects VALUES (?, ?, ?)", (bill_id, object_name, object_price))
                conn.commit()
                st.success("Object added successfully.")
        elif edit_option == "Delete Objects":
            object_index = st.number_input("Object Index", min_value=1, max_value=len(objects), step=1)
            if st.button("Delete Object"):
                object_id = objects[object_index-1][0]
                c.execute("DELETE FROM objects WHERE rowid=?", (object_id,))
                conn.commit()
                st.success("Object deleted successfully.")
    else:
        st.warning("Bill not found.")

# Search Bill option
elif selected_button == "Search Bill":
    st.header("Search Bill")

    bill_id = st.text_input("Bill ID")

    # Check if the bill exists
    c.execute("SELECT * FROM bills WHERE bill_id = ?", (bill_id,))
    bill = c.fetchone()
    if bill:
        st.text(f"Bill ID: {bill[0]}")
        st.text(f"Customer Name: {bill[1]}")
        st.text(f"Phone Number: {bill[2]}")
        st.text(f"Date of Purchase: {bill[3]}")
        st.text(f"Category: {bill[4]}")

        # Get the objects for the bill
        c.execute("SELECT * FROM objects WHERE bill_id = ?", (bill_id,))
        objects = c.fetchall()
        if objects:
            st.text("Objects:")
            for obj in objects:
                st.text(f"- {obj[1]}: ${obj[2]}")
        else:
            st.warning("No objects found for this bill.")
    else:
        st.warning("Bill not found.")

# Send Bill to counter option
elif selected_button == "Send Bill to counter":
    st.header("Send Bill to counter")

    counter_number = st.number_input("Counter Number", value=0, min_value=0, step=1)

    if st.button("Send"):
        st.success(f"Bill sent to Counter number {counter_number}!")

# Close the database connection
conn.close()
