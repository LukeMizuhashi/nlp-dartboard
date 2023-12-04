from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client(project='patents-public-data')

# Set your dataset ID.
dataset_id = 'patents'

# Get the dataset reference.
dataset_ref = client.dataset(dataset_id)

# API request - fetch the dataset
dataset = client.get_dataset(dataset_ref)

# List all tables in the dataset
tables = list(client.list_tables(dataset))

# Print information about each table
for table in tables:
    table_ref = dataset_ref.table(table.table_id)
    table_obj = client.get_table(table_ref)
    
    # Print details about the table. You can add more attributes as needed.
    print(f"Table ID: {table.table_id}")
    print(f"Table Description: {table_obj.description}")
    print(f"Number of Rows: {table_obj.num_rows}")
    print(f"Size of Table (MB): {table_obj.num_bytes / (1024 * 1024):.2f}")
    print(f"Schema: {table_obj.schema}")
    print(f"Time Created: {table_obj.created}")
    print(f"Last Modified: {table_obj.modified}")
    print(f"Table Expiration: {table_obj.expires}")
    print(f"Table Type: {table_obj.table_type}")
    print("-------------------------------")
