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
        self.embedding_model = embedding_model
        self.max_tokens = max_tokens
        self.enc = tiktoken.encoding_for_model(embedding_model)
        self.min_keys = [
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

    def count_tokens(self, dictionary: dict) -> dict:
        token_counts = {}
        for key, value in dictionary.items():
            token_count = len(self.enc.encode(json.dumps(value)))
            token_counts[key] = token_count
        return token_counts

    def get_base(self) -> dict:
        return get_subset(self.row, self.min_keys)

    def get_token_count(self, dictionary: dict) -> float:
        return sum(self.count_tokens(dictionary).values())

    def tokenize(self) -> List[int]:
        base = self.get_base() 
        token_overhead = self.get_token_count(base) 
        print(f"Base model token overhead is {token_overhead}, {((token_overhead / self.max_tokens) * 100):.2f} percent of {self.max_tokens} max tokens for embedding model {self.embedding_model}")

        non_base = get_subset(self.row, [key for key in self.row if key not in self.min_keys])
        non_base_token_counts = self.count_tokens(non_base) 
        print(sorted(non_base_token_counts, key=non_base_token_counts.get, reverse=True))

class Sample:
    def __init__(self, rows_or_filepath: (str | RowIterator), embedding_model: str, max_tokens: int):
        self.embedding_model = embedding_model
        self.max_tokens = max_tokens
        if isinstance(rows_or_filepath, str) and os.path.exists(rows_or_filepath):
            self._open_file(rows_or_filepath)
        elif isinstance(rows_or_filepath, RowIterator):
            self._save_rows_to_file(rows_or_filepath)
        else:
            raise Exception("rows_or_filepath must be a string or an instance of RowIterator")
        self._average_base_per_patent = sum([patent.get_token_count(patent.get_base()) for patent in self.patents]) / len(self.patents) 

    def _open_file(self, filepath) -> str:
        with open(filepath, 'r') as file:
            rows = json.load(file)
            self.patents = [Patent(row, self.embedding_model, self.max_tokens) for row in rows]
        parts = filepath.split('_')
        self.uuid = parts[-1].replace('.json', '')

    def _save_rows_to_file(self, rows: RowIterator):
        """Saves the rows as a JSON file."""
        self.patents = [Patent(row, self.embedding_model, self.max_tokens) for row in list(rows)]
        rows = [dict(patent.row) for patent in self.patents]
        id = str(uuid.uuid4())
        file_path = f"samples/len_{len(self.patents)}_sample_{id}.json"
        with open(file_path, 'w') as file:
            json.dump(rows, file)
        self.uuid = id

    def get_average_base_token_overhead(self, as_percent_of_max=True) -> float:
        return (self._average_base_per_patent / self.max_tokens) * 100 if as_percent_of_max else self._average_base_per_patent
