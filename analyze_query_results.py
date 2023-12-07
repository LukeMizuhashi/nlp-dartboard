import argparse
import os
import json
from typing import List, Dict
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np

def main():
  parser = argparse.ArgumentParser(description='Analyze query model responses.')
  parser.add_argument('--sample', required=True, type=str, help='Path to a JSON file containing the sample from which query model responses were derived')
  parser.add_argument('--query_results', required=True, type=str, help='Path to a JSON file containing query model responses')
  args = parser.parse_args()

  with open(args.sample, 'r') as file:
    raw_sample = json.load(file)
  sample = {}
  for publication in raw_sample:
    if publication.get('publication_number') in sample:
      raise Exception(f"Encountered {publication.get('publication_number')} more than once in raw sample")
    sample[publication.get('publication_number')] = publication

  with open(args.query_results, 'r') as file:
    query_results: Dict(Dict(List(float))) = json.load(file)

  search_results = []
  for query_source_publication_id, query_result in query_results.items():
    if query_source_publication_id not in sample:
      raise Exception(f"Query document {query_source_publication_id} not found in sample")
    similarities = []
    search_result = {
      'query_document': sample[query_source_publication_id],
      'matching_documents': []
    }
    for response_source_publication_id, similarity in query_result.items():
      similarities.append(similarity)
    cut_off = np.percentile(similarities, 75)
    for response_source_publication_id, similarity in query_result.items():
      if similarity >= cut_off:
        if response_source_publication_id not in sample:
          raise Exception(f"Matching document {response_source_publication_id} not found in sample")
        search_result.get('matching_documents').append(sample[response_source_publication_id])
    search_results.append(search_result) 

if __name__ == '__main__':
    main()
