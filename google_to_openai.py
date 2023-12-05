import tiktoken
from sample import Sample, Patent
import json
from utils import pick_unique_random_numbers, fully_minimize_json, get_subset
from collections import defaultdict
from typing import List

class Converter:
  def __init__(self, sample: Sample, embedding_model: str, max_token: int, sample_size: int, base_keys: List[str], token_slack: int, minimization_strategy = fully_minimize_json):
    self._embedding_model = embedding_model
    self._max_token = max_token
    self._sample = sample
    self._sample_size = sample_size
    self._minimization_strategy = minimization_strategy
    self._enc = tiktoken.encoding_for_model(self._embedding_model)
    self._base_keys = base_keys
    self._non_base_keys = [key for key in self._sample._patents[0]._row.keys() if key not in self._base_keys]
    self._token_slack = token_slack
    self._subsample_memo = None
    self._token_counts_memo = None
    self._stats_memo = None

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

  def _get_base_patent(self, i: int) -> dict:
    minimized_patent = self._subsample[i]
    return get_subset(minimized_patent, [key for key in self._base_keys if self._token_counts[key][i] > 0])

  def _get_non_base_patent(self, i: int) -> dict:
    minimized_patent = self._subsample[i]
    return get_subset(minimized_patent, [key for key in self._non_base_keys if self._token_counts[key][i] > 0])

  def prepare_for_embedding(self) -> List[dict]:
    prepared_patents = []
    for i in range(len(self._subsample)):
      base_patent = self._get_base_patent(i) 
      available_tokens = self._max_token - self._get_token_count(base_patent)
      if available_tokens <= 0:
        print(f"{self._sample._patents[i].unique_id} skipped: too many tokens consumed by base patent")
        continue
      for key in self._non_base_keys:
        non_base_patent = self._get_non_base_patent(i)
        if key in non_base_patent:
          width = self._binary_search(i, key)
          left, right = 0, width 
          non_base_patent = self._get_non_base_patent(i)
          minimized_value = self._minimization_strategy(json.dumps(non_base_patent[key]))
          while left <= len(minimized_value):
            base_patent = self._get_base_patent(i)
            base_patent[key] = minimized_value[left:right]
            prepared_patent = self._minimization_strategy(json.dumps(base_patent))
            encoded_prepared_patent = len(self._enc.encode(prepared_patent))
            if encoded_prepared_patent > self._max_token:
              print(f"{self._sample._patents[i].unique_id} skipped: too many tokens even after preparation")
              continue
            prepared_patents.append(prepared_patent)
            left = right
            right += width
    return prepared_patents

  def _dict_to_tokens(self, dictionary: dict) -> List[int]:
    return self._enc.encode(self._minimization_strategy(json.dumps(dictionary)))

  def _get_token_count(self, dictionary: dict) -> int:
    return len(self._dict_to_tokens(dictionary))

  def _binary_search(self, i: int, key: str) -> int:
    non_base_patent = self._get_non_base_patent(i)
    minimized_value = self._minimization_strategy(json.dumps(non_base_patent[key]))
    left, right = 0, len(minimized_value)
    while left <= right: 
      mid = (left + right) // 2
      base_patent = self._get_base_patent(i)
      base_patent[key] = minimized_value[:mid]
      used_tokens = len(self._dict_to_tokens(base_patent))
      available_tokens = self._max_token - used_tokens 
      if 0 <= available_tokens <= self._token_slack:
        return mid
      elif available_tokens < 0:
        # Too many tokens used, need to decrease mid
        right = mid
      else:
        # Still have space, increase mid
        left = mid + 1
    return left
