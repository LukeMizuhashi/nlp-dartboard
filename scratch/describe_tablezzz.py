from collections import defaultdict
from google.cloud import bigquery

client = bigquery.Client(project='cpc-labeling')
public_dataset_id = 'patents'
public_project = 'patents-public-data'
dataset_ref = client.dataset(public_dataset_id, project=public_project)

tables = list(client.list_tables(dataset_ref))
columns_of_interest = defaultdict(list)
for table in tables:
    if table.table_id == 'publications_202307':
        table_ref = dataset_ref.table(table.table_id)
        table_obj = client.get_table(table_ref)
        
        for field in table_obj.schema:
            # if any(keyword in field.name.lower() for keyword in strings_of_interest):
            columns_of_interest[table.table_id].append(field.name)

for table, columns in columns_of_interest.items():
    # print(f"Table: {table}, Columns: {columns}")
    # print(table)
    print(columns)
