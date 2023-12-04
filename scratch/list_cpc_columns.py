from google.cloud import bigquery

# Initialize a BigQuery client with your own project
client = bigquery.Client(project='horizontal-ally-275019')

# Define the public project containing the dataset you wish to query
public_project = 'patents-public-data'
public_dataset_id = 'patents'

# Get the dataset reference from the public project
dataset_ref = client.dataset(public_dataset_id, project=public_project)

# List all tables in the public dataset
tables = list(client.list_tables(dataset_ref))  # Corrected from 'dataset' to 'dataset_ref'

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
            # Construct the query to select the distinct CPC codes from the identified column
            query = f"""
            SELECT DISTINCT {field.name}
            FROM `{public_project}.{dataset_ref.dataset_id}.{table_obj.table_id}`
            WHERE {field.name} IS NOT NULL
            """
            # Specify 'job_config' with your own project as the billing project
            job_config = bigquery.QueryJobConfig(use_query_cache=True, project='horizontal-ally-275019')
            query_job = client.query(query, job_config=job_config)  # Make an API request with the query
            results = query_job.result()  # Wait for the query to finish
            
            # Add the results to the set
            for row in results:
                cpc_codes_set.add(row[0])  # Assuming the row has only one column which is our CPC code

# Output the set of unique CPC codes
print(f"Unique CPC codes: {cpc_codes_set}")
