from google.cloud import bigquery

# Initialize a BigQuery client with your project
client = bigquery.Client(project='cpc-labeling')

# Define the public dataset ID from 'patents-public-data' you wish to access
public_dataset_id = 'patents'
public_project = 'patents-public-data'

# Get the dataset reference from the public project
dataset_ref = client.dataset(public_dataset_id, project=public_project)

# List all tables in the public dataset
tables = list(client.list_tables(dataset_ref))

# Keywords for CPC-related information and full patent text
cpc_keywords = ['cpc', 'classification']
text_keywords = ['description', 'text', 'abstract', 'claims']

# Initialize a set for CPC codes and a dictionary for text columns
cpc_codes_set = set()
patent_text_columns = {}

# Check each table and column for names related to CPC codes and patent texts
for table in tables:
    table_ref = dataset_ref.table(table.table_id)
    table_obj = client.get_table(table_ref)
    
    for field in table_obj.schema:
        # Check for CPC-related columns
        if any(keyword in field.name.lower() for keyword in cpc_keywords):
            if field.field_type == 'ARRAY':
                # Handling ARRAY type fields, assuming elements are simple types
                query = f"""
                SELECT DISTINCT element
                FROM `{public_project}.{dataset_ref.dataset_id}.{table_obj.table_id}`,
                UNNEST({field.name}) as element
                """
            else:
                # Handling non-ARRAY fields
                query = f"""
                SELECT DISTINCT {field.name}
                FROM `{public_project}.{dataset_ref.dataset_id}.{table_obj.table_id}`
                """
            query_job = client.query(query)  # Make an API request with the query
            results = query_job.result()  # Wait for the query to finish
            
            for row in results:
                cpc_codes_set.add(row[0])  # Add the CPC code to the set

        # Check for full-text-related columns
        if any(keyword in field.name.lower() for keyword in text_keywords):
            if table.table_id not in patent_text_columns:
                patent_text_columns[table.table_id] = []
            patent_text_columns[table.table_id].append(field.name)

# Print unique CPC codes and tables with columns containing full patent texts
print(f"Unique CPC codes: {cpc_codes_set}")
for table, columns in patent_text_columns.items():
    print(f"Table: {table}, Columns: {columns}")
