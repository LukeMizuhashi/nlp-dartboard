import argparse
import os
import json
from typing import List, Dict
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
from sample import Patent

def calculate_f1_score(true_labels, predicted_labels):
    # Convert lists to sets for easier calculation
    true_labels_set = set(true_labels)
    predicted_labels_set = set(predicted_labels)

    # Calculate Precision and Recall
    true_positives = len(true_labels_set & predicted_labels_set)
    precision = true_positives / len(predicted_labels_set) if predicted_labels_set else 0
    recall = true_positives / len(true_labels_set) if true_labels_set else 0

    # Calculate F1 Score
    if precision + recall == 0:  # Handle the case to avoid division by zero
        return 0
    f1_score = 2 * (precision * recall) / (precision + recall)
    
    return f1_score

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

  f1_scores = []
  for query_source_publication_id, query_result in query_results.items():
    if query_source_publication_id not in sample:
      raise Exception(f"Query document {query_source_publication_id} not found in sample")
    similarities = []
    query_patent_codes = Patent(sample[query_source_publication_id]).all_codes
    predicted_patent_codes = []
    for response_source_publication_id, similarity in query_result.items():
      similarities.append(similarity)
    cut_off = np.percentile(similarities, 75)
    for response_source_publication_id, similarity in query_result.items():
      if similarity >= cut_off:
        if response_source_publication_id not in sample:
          raise Exception(f"Matching document {response_source_publication_id} not found in sample")
        predicted_patent_codes += Patent(sample[response_source_publication_id]).all_codes
    f1_scores.append(calculate_f1_score(list(set(query_patent_codes)), list(set(predicted_patent_codes))))
  plt.hist(f1_scores, bins=20)
  plt.title('Distribution of F1 Scores')
  plt.xlabel('F1 Score')
  plt.ylabel('Frequency')
  plt.show()
  print(sum(f1_scores) / len(f1_scores))

if __name__ == '__main__':
    main()
