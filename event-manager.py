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
    """Prompts user for criteria and deletes entries from the specified table,
           handling foreign key constraints.

        Args:
            con: A sqlite3 connection object.
            table_name: The name of the table to delete entries from.
        """

    cursor = con.cursor()

    if table_name in ("guest", "host", "band"):
        # Ensure no orphaned entries are created due to foreign key constraints
        print("Deleting entries from", table_name, "might leave orphaned entries in the 'event' table.")
        print("Consider deleting related events first or setting foreign keys to CASCADE on delete if appropriate.")
        confirm = input("Do you want to proceed with deletion (y/N)? ").lower()
        if confirm not in ("y", "yes"):
            print("Deletion cancelled.")
            return

    print("Enter the criteria for deletion:")

    # Construct the WHERE clause based on user input
    where_clause = ""
    while True:
        column_name = input("Enter the column name to filter by (or leave blank to delete all): ")
        if column_name:
            operator = input("Enter comparison operator (=, !=, LIKE, etc.): ")
            value = input("Enter the value to compare with: ")
            where_clause += f" {column_name} {operator} ?"
            break

    # Build the DELETE statement
    delete_stmt = f"DELETE FROM {table_name}"
    if where_clause:
        delete_stmt += f" WHERE {where_clause}"

    cursor.execute(delete_stmt, (value,))  # Assuming a single value for comparison

    # Confirm deletion and commit changes
    deleted_count = cursor.rowcount
    if deleted_count > 0:
        print(f"{deleted_count} entries from '{table_name}' deleted successfully.")
    else:
        print("No entries found matching the deletion criteria.")

    con.commit()


def delete_data_from_table(con, table_name):
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

        while True:
            try:
                choice = int(input("\nEnter the ID of the entry to delete, or 0 to cancel: "))
                if choice == 0:
                    return  # Exit the function if user cancels
                elif 1 <= choice <= len(data):
                    # Delete the entry with the chosen ID
                    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (choice,))
                    con.commit()
                    print(f"Entry with ID {choice} deleted successfully.")
                    return  # Exit the function after successful deletion
                else:
                    print("Invalid ID. Please enter a valid ID or 0 to cancel.")
            except ValueError:
                print("Invalid input. Please enter a number.")
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
                    delete_data_from_table(con, table_names[table_choice - 1])
                elif table_choice == 0:
                    print("< returned to menu")
                else:
                    print("!!! Invalid table selection.")
            elif choice == 0:
                print("< exiting...")
            else:
                print("!!! Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":

    main()
