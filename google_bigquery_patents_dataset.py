from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
from utils import validate_n

class BigQueryTableReader:
    def __init__(self, billing_project_id: str, dataset_project_id: str, dataset_id: str):
        self.client = bigquery.Client(project=billing_project_id)
        self.dataset_project_id = dataset_project_id
        self.dataset_id = dataset_id
        self.dataset_ref = self.client.dataset(self.dataset_id, project=self.dataset_project_id)
        self.dataset = self.client.get_dataset(self.dataset_ref)

    def _get_full_table_id(self, table_id: str):
        return f"{self.dataset_project_id}.{self.dataset_id}.{table_id}"

    def list_tables(self):
        return list(self.client.list_tables(self.dataset))

    def describe_table(self, table_id: str):
        table_ref = self.dataset_ref.table(table_id)
        return self.client.get_table(table_ref)

    def read_table(self, table_id: str, n=None):
        validate_n(n)
        full_table_id = self._get_full_table_id(table_id) 
        query = f"SELECT * FROM `{full_table_id}` LIMIT {n}"
        query_job = self.client.query(query)
        return query_job.result()

    # ['publication_number']
    def find_potential_primary_key(self, table_id: str):
        table_ref = self.dataset_ref.table(table_id)
        table = self.client.get_table(table_ref)
        full_table_id = self._get_full_table_id(table_id) 

        potential_primary_keys = []

        for field in table.schema:
            print(f"Checking column: {field.name}, Type: {field.field_type}")  # Debug print
            if field.field_type == 'RECORD':
                print(f"Skipping RECORD column: {field.name}")
                continue
            if field.field_type == 'ARRAY':
                print(f"Skipping ARRAY column: {field.name}")
                continue
            try:
                column_name = field.name
                query = f"""
                SELECT
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT {column_name}) as distinct_rows
                FROM
                    `{full_table_id}`
                """

                query_job = self.client.query(query)
                result = query_job.result()
                for row in result:
                    if row.total_rows == row.distinct_rows:
                        potential_primary_keys.append(column_name)

            except BadRequest as e:
                print(f"Query failed for column {column_name}: {str(e)}")

        return potential_primary_keys

    def get_random_rows(self, table_id: str, n: int, where_clause: str = None):
        validate_n(n)
        full_table_id = self._get_full_table_id(table_id)
        where_clause_sql = f" WHERE {where_clause}" if where_clause else ""
        query = f"SELECT * FROM `{full_table_id}`{where_clause_sql} ORDER BY RAND() LIMIT {n}"
        query_job = self.client.query(query)
        return query_job.result()

