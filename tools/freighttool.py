
def create_freight_record(conn, freight_data):  # Todo Check again if this works
    cursor = conn.cursor()

    cursor.execute("""
            INSERT INTO freight_main (
                from_location, to_location, from_warehouse, to_warehouse,
                pickup_date, delivery_date, priority, comment, status, transport_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
        freight_data["from_location"],
        freight_data["to_location"],
        freight_data["from_warehouse"],
        freight_data["to_warehouse"],
        freight_data["pickup_date"],
        freight_data["delivery_date"],
        freight_data["priority"],
        freight_data["comment"],
        "Live",
        "Live"
    ))

    freight_id = cursor.lastrowid

    for contact in freight_data["contacts"]:  # expect list of dicts
        cursor.execute("""
               INSERT INTO freight_contacts (freight_id, name, email, phone)
               VALUES (?, ?, ?, ?)
           """, (freight_id, contact["name"], contact["email"], contact["phone"]))

    for package in freight_data["packages"]:  # expect list of dicts
        cursor.execute("""
               INSERT INTO freight_packages (freight_id, mat_id, mat_id_b, quantity)
               VALUES (?, ?, ?, ?)
           """, (freight_id, package["mat_id"], package.get("mat_id_b"), package["qty"]))

    conn.commit()

def delete_freight_record(conn, freight_id):
    cursor = conn.cursor()

    # Delete from related tables first due to foreign keys
    cursor.execute("DELETE FROM freight_contacts WHERE freight_id = ?", (freight_id,))
    cursor.execute("DELETE FROM freight_packages WHERE freight_id = ?", (freight_id,))
    cursor.execute("DELETE FROM freight_main WHERE freight_id = ?", (freight_id,))

    conn.commit()

def filter_freights(conn, filters):
    cursor = conn.cursor()
    query = "SELECT freight_id, transport_status, from_location, to_location, from_warehouse, to_warehouse, pickup_date, delivery_date, priority FROM freight_main WHERE 1=1"
    params = []

    # Status filtering (Live / Archived)
    if "live_status" in filters and "archived_status" in filters:
        query += " AND status IN (?, ?)"
        params.extend([filters["live_status"], filters["archived_status"]])
    elif "live_status" in filters:
        query += " AND status = ?"
        params.append(filters["live_status"])
    elif "archived_status" in filters:
        query += " AND status = ?"
        params.append(filters["archived_status"])


    # Unique ID (assuming it’s an int)
    if "unique_id" in filters:
        query += " AND freight_id = ?"  # or freight_id depending on your schema
        params.append(filters["unique_id"])

    if "from_location" in filters:
        query += " AND from_location LIKE  ?"
        params.append(f"%{filters['from_location']}%")

    if "to_location" in filters:
        query += " AND to_location LIKE  ?"
        params.append(f"%{filters['to_location']}%")

    if "priority" in filters:
        query += " AND priority = ?"
        params.append(filters["priority"])

    if "transport_status" in filters:
        query += " AND transport_status = ?"
        params.append(filters["transport_status"])

    if "pickup_date" in filters:
        query += " AND pickup_date LIKE ?"
        params.append(f"%{filters['pickup_date']}%")

    if "delivery_date" in filters:
        query += " AND delivery_date LIKE ?"
        params.append(f"%{filters['delivery_date']}%")

    cursor.execute(query, params)

    return cursor.fetchall()

def update_freight_status(conn, freight_id, new_status):
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE freight_main
        SET transport_status = ?
        WHERE freight_id = ?
    """, (new_status, freight_id))

    conn.commit()

def auto_archive(conn):
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE freight_main
        SET status = 'Archived'
        WHERE transport_status = 'Delivered'
    """)

    conn.commit()