import argparse
from dotenv import load_dotenv
import os
import json
from typing import List
from pprint import pprint

def cosine_similarity(vector_a, vector_b) -> float:
    dot_product = sum(a*b for a, b in zip(vector_a, vector_b))
    norm_a = sum(a**2 for a in vector_a) ** 0.5
    norm_b = sum(b**2 for b in vector_b) ** 0.5
    return dot_product / (norm_a * norm_b)

def main():
  # load_dotenv(dotenv_path='.env.get_query_embeddings.nonsecrets', override=True)

  parser = argparse.ArgumentParser(description='Query model and score response.')
  parser.add_argument('--model', required=True, type=str, help='Path to a JSON file containing model embeddings')
  parser.add_argument('--queries', required=True, type=str, help='Path to a JSON file containing query embeddings')
  args = parser.parse_args()

  with open(args.model, 'r') as file:
    raw_model: List[any] = json.load(file)

  # Prepare the model as {publication_number: List[embeddings]}
  model = {}
  for publication_number, model_embedding_strs in raw_model.items():
    if publication_number in model:
      raise Exception(f"Encountered {publication_number} more than once")
    model[publication_number] = []
    for response_data in json.loads(model_embedding_strs).get('data'):
      model[publication_number].append(response_data.get('embedding'))

  with open(args.queries, 'r') as file:
    queries = json.load(file)

  results = {}
  for qeuery_source, query_embedding_strs in queries.items():
    if qeuery_source in results:
      raise Exception(f"Encountered query source {qeuery_source} more than once")
    results[qeuery_source] = {}
    for query_embedding_str in query_embedding_strs:
      query_embedding_pkg = json.loads(query_embedding_str)
      for response_data in query_embedding_pkg.get('data'):
        # These are all exactly length 1536 
        query_embedding = response_data.get('embedding')
        for publication_number, model_embeddings in model.items():
          if publication_number not in results[qeuery_source]:
            results[qeuery_source][publication_number] = []
          for model_embedding in model_embeddings:
            results[qeuery_source][publication_number].append(cosine_similarity(model_embedding, query_embedding))

  with open(f"eval/len_{len(results.keys())}_queries_{os.getenv('RUN_ID')}.json", 'w') as file:
      json.dump(results, file)

if __name__ == '__main__':
    main()
