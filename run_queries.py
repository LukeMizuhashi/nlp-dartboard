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

def average_of_vectors(vectors):
    if not vectors:
        raise ValueError("No vectors provided for averaging")
    length_of_first_vector = len(vectors[0])
    if any(len(vector) != length_of_first_vector for vector in vectors):
        raise ValueError("All vectors must be of the same length")
    return [sum(components) / len(components) for components in zip(*vectors)]

def main():
  # load_dotenv(dotenv_path='.env.get_query_embeddings.nonsecrets', override=True)

  parser = argparse.ArgumentParser(description='Query model and score response.')
  parser.add_argument('--model', required=True, type=str, help='Path to a JSON file containing model embeddings')
  parser.add_argument('--queries', required=True, type=str, help='Path to a JSON file containing query embeddings')
  args = parser.parse_args()

  # Prepare the model as {publication_number: List[embeddings]}
  with open(args.model, 'r') as file:
    raw_model: List[any] = json.load(file)
  model = {}
  for publication_number, api_response_str in raw_model.items():
    if publication_number in model:
      raise Exception(f"Encountered {publication_number} more than once")
    model[publication_number] = average_of_vectors([embedding_objects.get('embedding') for embedding_objects in json.loads(api_response_str).get('data')])

  # Prepare queries for comparison and compare
  with open(args.queries, 'r') as file:
    raw_queries = json.load(file)
  queries = {}
  results = {}
  # Note: there's only one string in query_embedding_strs per query_source.
  # They are simply the raw JSON encoding of the response from the OpenAI
  # Embedding Service for some batch request. That string itself may contain
  # more than one embedding for the given publicaiton number if the text from
  # that publication had to be chunked to fit into the Embedding Service's
  # max token limit
  for qeuery_source, query_embedding_strs in raw_queries.items():
    if qeuery_source in queries:
      raise Exception(f"Encountered query source {qeuery_source} more than once")
    if len(query_embedding_strs) > 1:
       raise Exception(f"Expected there to be exactly one Embedding Service response string per query source docudment")
    queries[qeuery_source] = average_of_vectors([embedding_objects.get('embedding') for embedding_objects in json.loads(query_embedding_strs[0]).get('data')])
    if qeuery_source in results:
      raise Exception(f"Encountered query source {qeuery_source} in results more than once")
    results[qeuery_source] = {}
    for publication_number, model_embedding in model.items():
      if publication_number in results[qeuery_source]:
         raise Exception(f"Encountered publication number in results for query source {qeuery_source} more than once")
      results[qeuery_source][publication_number] = cosine_similarity(model_embedding, queries[qeuery_source])

  with open(f"eval/len_{len(results.keys())}_queries_{os.getenv('RUN_ID')}.json", 'w') as file:
      json.dump(results, file)

if __name__ == '__main__':
    main()
