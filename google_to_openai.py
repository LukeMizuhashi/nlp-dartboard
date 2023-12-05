import tiktoken
from sample import Sample, Patent
import json
from utils import pick_unique_random_numbers, fully_minimize_json, get_subset
from collections import defaultdict
from pprint import pprint
from typing import List

class Converter:
  def __init__(self, sample: Sample, embedding_model: str, max_token: int, sample_size: int, base_keys: List[str], minimization_strategy = fully_minimize_json):
    self._embedding_model = embedding_model
    self._max_token = max_token
    self._sample = sample
    self._sample_size = sample_size
    self._minimization_strategy = minimization_strategy
    self._enc = tiktoken.encoding_for_model(self._embedding_model)
    self._base_keys = base_keys
    self._non_base_keys = [key for key in self._sample._patents[0]._row.keys() if key not in self._base_keys]
    self._subsample_memo = None
    self._token_counts_memo = None
    self._stats_memo = None

  def get_embeddings(self):
    for i, tokenized_patent in enumerate(self._subsample):
      base_patent = get_subset(tokenized_patent, [key for key in self._base_keys if self._token_counts[key][i] > 0])
      non_base_patent = get_subset(tokenized_patent, [key for key in self._non_base_keys if self._token_counts[key][i] > 0])
      pprint(non_base_patent)

  @property
  def _subsample(self) -> dict:
    if not self._subsample_memo:
      self._subsample_memo = [] 
      for i in pick_unique_random_numbers(self._sample._patents, self._sample_size):
        minimized_patent = {}
        for key, value in self._sample._patents[i]._row.items():
          if key in Patent.special_keys: 
            minimized_patent[key] = self._minimization_strategy(json.dumps(getattr(self._sample._patents[i], key)))
          else:
            minimized_patent[key] = self._minimization_strategy(json.dumps(value))
        self._subsample_memo.append(minimized_patent)
    return self._subsample_memo

  @property
  def _token_counts(self):
    if not self._token_counts_memo:
      self._token_counts_memo = defaultdict(list)
      for minimized_patent in self._subsample:
        for key, value in minimized_patent.items():
          self._token_counts_memo[key].append(len(self._enc.encode(value)))
    return self._token_counts_memo

  @property
  def _stats(self) -> defaultdict(list):
    if not self._stats_memo:
      self._stats_memo = defaultdict(float)
      for minimized_patent in self._subsample:
        for key in minimized_patent.keys():
          non_zero_token_counts = [i for i in self._token_counts[key] if i > 0]
          if len(non_zero_token_counts) > 0:
            self._stats_memo[key] = sum(self._token_counts[key]) / len(non_zero_token_counts)
          else:
            self._stats_memo[key] = 0
    return self._stats_memo
