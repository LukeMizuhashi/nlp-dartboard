from google.cloud import bigquery

# Initialize a BigQuery client with your project 'cpc-labeling'
client = bigquery.Client(project='cpc-labeling')

# Define the public dataset ID from 'patents-public-data' you wish to access
public_dataset_id = 'patents'
public_project = 'patents-public-data'

# Get the dataset reference from the public project
dataset_ref = client.dataset(public_dataset_id, project=public_project)

# List all tables in the public dataset
tables = list(client.list_tables(dataset_ref))

# Keywords to look for in column names that might indicate CPC-related information
cpc_keywords = ['cpc', 'classification']

# Initialize a set to store unique CPC codes
cpc_codes_set = set()

# Check each table and column for names related to CPC codes
for table in tables:
    table_ref = dataset_ref.table(table.table_id)
    table_obj = client.get_table(table_ref)
    
    for field in table_obj.schema:
        if any(keyword in field.name.lower() for keyword in cpc_keywords):
            if field.field_type == 'ARRAY':
                # If the array elements are STRUCTs, you need to specify which field to select
                # For example, if each array element is a STRUCT with a 'code' field:
                query = f"""
                SELECT DISTINCT element.code
                FROM `{public_project}.{dataset_ref.dataset_id}.{table_obj.table_id}`,
                UNNEST({field.name}) as element
                """
            else:
                # For non-ARRAY fields, we can use SELECT DISTINCT directly
                query = f"""
                SELECT DISTINCT {field.name}
                FROM `{public_project}.{dataset_ref.dataset_id}.{table_obj.table_id}`
                """
            
            query_job = client.query(query)  # Make an API request with the query
            results = query_job.result()  # Wait for the query to finish
            
            for row in results:
                cpc_codes_set.add(row[0])  # Add the CPC code to the set

print(f"Unique CPC codes: {cpc_codes_set}")

