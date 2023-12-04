from google.cloud import bigquery

# Initialize a BigQuery client with your own project for billing purposes
client = bigquery.Client(project='cpc-labeling')

# Define the public dataset ID you wish to access
public_dataset_id = 'patents'
public_project = 'patents-public-data'  # This is the public project containing the dataset

# Get the dataset reference from the public project
dataset_ref = client.dataset(public_dataset_id, project=public_project)

# Access the dataset
dataset = client.get_dataset(dataset_ref)

total_size = 0
# List all tables in the public dataset
tables = list(client.list_tables(dataset))
for table in tables:
    table_ref = dataset_ref.table(table.table_id)
    # Use the client object which uses your project for billing
    table_obj = client.get_table(table_ref)
    total_size += table_obj.num_bytes

# Convert bytes to terabytes and print the result
print(f"The total size of the dataset is: {round(total_size / (1024 ** 4), 2)} terabytes")
