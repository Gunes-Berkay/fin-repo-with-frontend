from django.db import connections

def get_table_data(table_name, limit=100):
    """
    Fetches data from a specified table in the `papers_db` database.

    Args:
        table_name (str): The name of the table to query.
        limit (int): The number of rows to return (default is 10).

    Returns:
        list: A list of rows from the table.
    """
    try:
        with connections['papers_db'].cursor() as cursor:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            cursor.execute(query)
            rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error querying table {table_name}: {e}")
        return []
