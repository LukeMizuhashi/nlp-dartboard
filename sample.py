import json
import os
from google.cloud.bigquery.table import RowIterator, Row 
import uuid
from typing import List

class Patent:
    special_keys = [
        'cpc',
        'uspc',
        'citation',
    ]

    def __init__(self, row):
        self._row: Row = row
    
    def _get_code(self, key: str) -> List[str]:
        return [obj.get('code') for obj in self._row.get(key)]

    @property
    def cpc(self) -> List[str]:
        return self._get_code('cpc')
    
    @property
    def uspc(self) -> List[str]:
        return self._get_code('uspc')

    @property
    def citation(self) -> List[str]:
        return [list(obj.values()) for obj in self._row.get('citation')]

    @property
    def unique_id(self) -> str:
        return self._row.get('publication_number')

class Sample:
    def __init__(self, rows_or_filepath: (str | RowIterator)):
        if isinstance(rows_or_filepath, str) and os.path.exists(rows_or_filepath):
            self._open_file(rows_or_filepath)
        elif isinstance(rows_or_filepath, RowIterator):
            self._save_rows_to_file(rows_or_filepath)
        else:
            raise Exception("rows_or_filepath must be a string or an instance of RowIterator")

    def _open_file(self, filepath) -> str:
        with open(filepath, 'r') as file:
            rows = json.load(file)
            self._patents = [Patent(row) for row in rows]
        parts = filepath.split('_')
        self.uuid = parts[-1].replace('.json', '')

    def _save_rows_to_file(self, rows: RowIterator):
        """Saves the rows as a JSON file."""
        self._patents = [Patent(row) for row in list(rows)]
        rows = [dict(patent._row) for patent in self._patents]
        id = str(uuid.uuid4())
        file_path = f"samples/len_{len(self._patents)}_sample_{id}.json"
        with open(file_path, 'w') as file:
            json.dump(rows, file)
        self.uuid = id
