import json
import os
from google.cloud.bigquery.table import RowIterator 
import uuid
from pprint import pprint
from typing import List
import tiktoken
from utils import get_subset

class Patent:
    def __init__(self, row, embedding_model: str, max_tokens: int):
        self.row = row
        self._embedding_model = embedding_model
        self._max_tokens = max_tokens
        self._enc = tiktoken.encoding_for_model(embedding_model)
        self._base_keys = [
            'cpc',
            'uspc',
            'assignee_harmonized',
            'ipc',
            'inventor_harmonized',
            'citation',
            'priority_claim',
            'examiner',
            'inventor',
            'title_localized',
            'assignee',
            'publication_number',
            'application_number',
            'spif_publication_number',
            'application_number_formatted',
            'spif_application_number',
            'family_id',
            'art_unit',
            'country_code',
            'kind_code',
            'publication_date',
            'filing_date',
            'grant_date',
            'priority_date',
            'entity_status',
            'application_kind',
            'pct_number',
            'fi',
            'fterm',
            'locarno',
            'parent',
            'child'
            ]
        self._non_base_keys = [key for key in self.row if key not in self._base_keys]
        self._token_counts_memo = None
        self._base_key_token_overhead_memo = None

    @property
    def _token_counts(self) -> dict:
        if not self._token_counts_memo:
            self._token_counts_memo = {key: len(self._enc.encode(json.dumps(value))) for key, value in self.row.items()}
        return self._token_counts_memo
    
    @property
    def _base_key_token_overhead(self):
        if not self._base_key_token_overhead_memo:
            self._base_key_token_overhead_memo = sum([self._token_counts[key] for key in self._base_keys]) 
        return self._base_key_token_overhead_memo

    def get_average_base_token_overhead(self, as_percent_of_max=True) -> float:
        return (self._base_key_token_overhead / self._max_tokens) * 100 if as_percent_of_max else self._base_key_token_overhead

    @property
    def unique_id(self) -> str:
        return self.row.get('publication_number')

    def _get_base(self) -> dict:
        return get_subset(self.row, self._base_keys)

    def _get_non_base(self) -> dict:
        return get_subset(self.row, self._non_base_keys)

class Sample:
    def __init__(self, rows_or_filepath: (str | RowIterator), embedding_model: str, max_tokens: int):
        self._embedding_model = embedding_model
        self._max_tokens = max_tokens
        if isinstance(rows_or_filepath, str) and os.path.exists(rows_or_filepath):
            self._open_file(rows_or_filepath)
        elif isinstance(rows_or_filepath, RowIterator):
            self._save_rows_to_file(rows_or_filepath)
        else:
            raise Exception("rows_or_filepath must be a string or an instance of RowIterator")
        self._average_base_per_patent_memo = None

    @property
    def _average_base_per_patent(self):
        if not self._average_base_per_patent_memo:
            self._average_base_per_patent_memo = sum([patent._base_key_token_overhead for patent in self._patents]) / len(self._patents) 
        return self._average_base_per_patent_memo

    def _open_file(self, filepath) -> str:
        with open(filepath, 'r') as file:
            rows = json.load(file)
            self._patents = [Patent(row, self._embedding_model, self._max_tokens) for row in rows]
        parts = filepath.split('_')
        self.uuid = parts[-1].replace('.json', '')

    def _save_rows_to_file(self, rows: RowIterator):
        """Saves the rows as a JSON file."""
        self._patents = [Patent(row, self._embedding_model, self._max_tokens) for row in list(rows)]
        rows = [dict(patent.row) for patent in self._patents]
        id = str(uuid.uuid4())
        file_path = f"samples/len_{len(self._patents)}_sample_{id}.json"
        with open(file_path, 'w') as file:
            json.dump(rows, file)
        self.uuid = id

    def get_average_base_token_overhead(self, as_percent_of_max=True) -> float:
        return (self._average_base_per_patent / self._max_tokens) * 100 if as_percent_of_max else self._average_base_per_patent
