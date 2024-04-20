import sqlite3


def display_data_tables(con):
    """Fetches and displays a list of all tables in the database connection, excluding the ID column.

    Args:
        con: A sqlite3 connection object.
    """

    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    if tables:
        print("\nAvailable Data Tables:")
        for i, table in enumerate(tables):
            print(f"{i+1}. {table}")
        print("0. exit...")

        while True:
            try:
                choice = int(input("> "))
                if 0 <= choice <= len(tables):
                    break
                else:
                    print("!!! Invalid choice. Please enter a number between 0 and", len(tables))
            except ValueError:
                print("!!! Invalid input. Please enter a number.")

        if choice == 3:
            selected_table = tables[choice - 1]
            print(f"\nData in table '{selected_table}': ")

            # Fetch column names excluding the first one (assuming ID)
            cursor.execute(f"SELECT * FROM {selected_table}")
            column_names = [desc[0] for desc in cursor.description[0:]]  # Skip first column

            # Fetch and display data with column names
            print(f"{column_names}\n")
            for row in cursor.fetchall():
                print(f"{' | '.join(str(x) for x in row)}")  # Skip first element (ID)


        elif choice > 0:
            selected_table = tables[choice - 1]
            print(f"\nData in table '{selected_table}': ")

            # Fetch column names excluding the first one (assuming ID)
            cursor.execute(f"SELECT * FROM {selected_table}")
            column_names = [desc[0] for desc in cursor.description]  # Skip first column

            # Fetch and display data with column names
            print(f"{column_names[1:]}\n")
            for row in cursor.fetchall():
                print(f"{' | '.join(str(x) for x in row[1:])}")  # Skip first element (ID)

    else:
        print("No data tables found in the database.")


def add_data_to_table(con, table_name):
    """Prompts user for data and inserts it into the specified table, handling foreign keys.

        Args:
            con: A sqlite3 connection object.
            table_name: The name of the table to add data to.
        """

    cursor = con.cursor()

    if table_name == "event":
        event_name = input("Enter event name: ")
        address = input("Enter event address: ")
        cursor.execute("INSERT INTO event (event_name, address) VALUES (?, ?)", (event_name, address))

    elif table_name in ("guest", "host", "band"):
        # Get a list of valid event names
        cursor.execute("SELECT event_name FROM event")
        valid_events = [row[0] for row in cursor.fetchall()]

        # Prompt for event selection and ensure it's a valid option
        while True:
            print("Select the event for this entry:")
            for i, event in enumerate(valid_events):
                print(f"{i + 1}. {event}")
            choice = int(input()) - 1
            if 0 <= choice < len(valid_events):
                selected_event = valid_events[choice]
                break
            else:
                print("Invalid choice. Please enter a number between 1 and", len(valid_events))

        # Prompt for specific data based on the table
        if table_name == "guest":
            last_name = input("Enter guest last name: ")
            first_name = input("Enter guest first name: ")
            email = input("Enter guest email (optional): ")
            birthday = input("Enter guest birthday (YYYY-MM-DD format, optional): ")
            rsvp = input("Enter RSVP (Going or Not Going): ").upper()
            if rsvp not in ("GOING", "NOT GOING"):
                rsvp = "NOT GOING"  # Default to Not Going if invalid
            cursor.execute(
                """INSERT INTO guest (last_name, first_name, email, birthday, RSVP, event_name) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (last_name, first_name, email, birthday, rsvp, selected_event),
            )
        elif table_name == "host":
            last_name = input("Enter host last name: ")
            first_name = input("Enter host first name: ")
            email = input("Enter host email (optional): ")
            birthday = input("Enter host birthday (YYYY-MM-DD format, optional): ")
            cursor.execute(
                """INSERT INTO host (last_name, first_name, email, birthday, event_name) 
                VALUES (?, ?, ?, ?, ?)""",
                (last_name, first_name, email, birthday, selected_event),
            )
        else:  # table_name == "band"
            band_name = input("Enter band name: ")
            email = input("Enter band email (optional): ")
            birthday = input("Enter any band member birthday (YYYY-MM-DD format, optional): ")
            cursor.execute(
                """INSERT INTO band (band_name, email, birthday, event_name) 
                VALUES (?, ?, ?, ?)""",
                (band_name, email, birthday, selected_event),
            )

    else:
        print("Invalid table name provided for data entry.")

    con.commit()  # Commit changes to the database


def delete_data_from_table(con, table_name, opt):
    """Prompts user to select an entry for deletion from the specified table.

        Args:
            con: A sqlite3 connection object.
            table_name: The name of the table to delete from.
        """

    cursor = con.cursor()

    # Get all data from the table (assuming ID is the first column)
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()

    if data:
        print(f"\nData in table '{table_name}':")
        print("ID  | Other Columns...")  # Display headers with "ID" for clarity
        for row in data:
            print(f"{row[0]} | {' | '.join(str(x) for x in row[1:])}")  # Format output

        if opt == 1:
            choice = input("\nEnter the ID of the entry to delete, or 0 to cancel: ")
            # Delete the entry with the chosen ID
            cursor.execute(f"DELETE FROM {table_name} WHERE event_name = ?", (choice,))
            con.commit()
            print(f"Entry with ID {choice} deleted successfully.")
            return  # Exit the function after successful deletion
        else:
            while True:
                try:
                    choice = input("\nEnter the ID of the entry to delete, or 0 to cancel: ")
                    if choice == 0:
                        return  # Exit the function if user cancels
                    elif 1 <= int(choice) <= len(data):
                        # Delete the entry with the chosen ID
                        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (int(choice),))
                        con.commit()
                        print(f"Entry with ID {choice} deleted successfully.")
                        return  # Exit the function after successful deletion
                    else:
                        print("Invalid ID. Please enter a valid ID or 0 to cancel.")
                except ValueError:
                    print("!!! Invalid input. Please enter a number.")
    else:
        print(f"No data found in table '{table_name}'.")


def print_event_data(con):
    """Prompts user to select an event by name and prints all associated data.

    Args:
        con: A sqlite3 connection object.
    """

    cursor = con.cursor()

    # Get a list of all event names
    cursor.execute("SELECT event_name FROM event")
    event_names = [row[0] for row in cursor.fetchall()]

    if event_names:
        print("\nSelect an event to view details:")
        for i, event in enumerate(event_names):
            print(f"{i+1}. {event}")
        while True:
            try:
                choice = int(input("> "))
                if 1 <= choice <= len(event_names):
                    selected_event = event_names[choice - 1]
                    print_event_data_by_name(con, selected_event)  # Call function with chosen event
                    return  # Exit after successful selection
                else:
                    print("Invalid choice. Please enter a number between 1 and", len(event_names))
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        print("No events found in the database.")


def print_event_data_by_name(con, event_name):
    """Prints all data associated with a specific event name.

    Args:
        con: A sqlite3 connection object.
        event_name: The name of the event to display data for.
    """

    cursor = con.cursor()

    # Get event details
    cursor.execute(f"SELECT address FROM event WHERE event_name = ?", (event_name,))
    event_data = cursor.fetchone()

    if event_data:
        print(f"\nEvent Name: {event_name}")
        print(f"Address: {event_data[0]}")

        # Get and print hosts
        cursor.execute(f"SELECT first_name, last_name, email, birthday FROM host WHERE event_name = ?", (event_name,))
        hosts = cursor.fetchall()
        if hosts:
            print("\nHosts:")
            for row in hosts:
                print(f"- {row[0]} {row[1]} (Email: {row[2] if row[2] else 'N/A'})")

        # Get and print bands
        cursor.execute(f"SELECT band_name, email FROM band WHERE event_name = ?", (event_name,))
        bands = cursor.fetchall()
        if bands:
            print("\nBands:")
            for row in bands:
                print(f"- {row[0]} (Email: {row[1] if row[1] else 'N/A'})")

        # Get and print guests categorized by RSVP
        cursor.execute(f"SELECT first_name, last_name, email, rsvp FROM guest WHERE event_name = ?", (event_name,))
        guests = cursor.fetchall()
        if guests:
            print("\nGuests:")
            going_guests = [guest for guest in guests if guest[3].upper() == "GOING"]
            not_going_guests = [guest for guest in guests if guest[3].upper() == "NOT GOING"]

            if going_guests:
                print("\n  Going:")
                for row in going_guests:
                    print(f"- {row[0]} {row[1]} (Email: {row[2] if row[2] else 'N/A'})")

            if not_going_guests:
                print("\n  Not Going:")
                for row in not_going_guests:
                    print(f"- {row[0]} {row[1]} (Email: {row[2] if row[2] else 'N/A'})")

        else:
            print("No hosts, bands, or guests found for this event.")

    else:
        print(f"Event '{event_name}' not found.")


def main():
    con = sqlite3.connect(r".\data.sqlite")

    while True:
        print("\n\nEvent Manager")
        print("1. View Events")
        print("2. Data Manipulation")
        print("0. exit...")
        choice = int(input("> "))
        if choice == 0:
            print("< closing application...")
            break
        if choice == 1:
            print_event_data(con)
        elif choice == 2:
            print("\nMenu:")
            print("1. View Data Tables")
            print("2. Add Data to a Table")
            print("3. Delete Data from a Table")
            print("0. exit...")
            choice = int(input("> "))

            if choice == 1:
                display_data_tables(con)
            elif choice == 2:
                print("\nChoose:")
                print("1. Events")
                print("2. Guests")
                print("3. Hosts")
                print("4. Bands")
                print("0. exit...")
                table_choice = int(input("> "))
                table_names = ["event", "guest", "host", "band"]

                if 1 <= table_choice <= len(table_names):
                    add_data_to_table(con, table_names[table_choice - 1])
                elif table_choice == 0:
                    print("< returned to menu")
                else:
                    print("!!! Invalid table selection.")
            elif choice == 3:
                print("\nChoose:")
                print("1. Events")
                print("2. Guests")
                print("3. Hosts")
                print("4. Bands")
                print("0. exit...")
                table_choice = int(input("> "))
                table_names = ["event", "guest", "host", "band"]

                if 1 <= table_choice <= len(table_names):
                    delete_data_from_table(con, table_names[table_choice - 1], table_choice)
                elif table_choice == 0:
                    print("< returned to menu")
                else:
                    print("!!! Invalid table selection.")
            elif choice == 0:
                print("< exiting...")
                break
            else:
                print("!!! Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":

    main()
