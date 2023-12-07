import argparse
from dotenv import load_dotenv
import os
import json
from openai import OpenAI
from utils import partition_string
from typing import List

def main():
  load_dotenv(dotenv_path='.env.secrets')
  load_dotenv(dotenv_path='.env.get_query_embeddings.nonsecrets', override=True)

  parser = argparse.ArgumentParser(description='Gets query embeddings.')
  parser.add_argument('--samples', required=True, type=str, help='Path to a JSON file containing samples')
  parser.add_argument('--embeddings', required=True, type=str, help='Path to a JSON file containing embeddings of some subset of the given samples')
  args = parser.parse_args()
  if not os.getenv('QUERY_SET_SIZE'):
    raise Exception("QUERY_SET_SIZE environment variable required")
  primary_key = 'publication_number'

  with open(args.samples, 'r') as file:
    samples: List[any] = json.load(file)

  with open(args.embeddings, 'r') as file:
    model = json.load(file)

  client = OpenAI()
  query_embeddings = {}
  count = 0
  for query_sample in [sample for sample in samples if sample.get(primary_key) not in model.keys()]:
    if count >= int(os.getenv('QUERY_SET_SIZE')):
      break
    pk = query_sample.get(primary_key)
    if pk in query_embeddings:
      raise Exception(f"Encountered duplicate {primary_key}: {pk}")
    query_embeddings[pk] = []
    chunks =[]
    for description in query_sample.get('description_localized'):
      for index_pair in partition_string(description.get('text'), int(os.getenv('OVERLAP')), int(os.getenv('CHUNK_SIZE'))):
        [left, right] = index_pair
        chunks.append(description.get('text')[left:right])
    response = client.embeddings.create(
        input=chunks,
        model=os.getenv('OPEN_AI_EMBEDDING_MODEL')
    )
    query_embeddings[pk].append(response.model_dump_json())
    count += 1

  with open(f"query_embeddings/len_{len(query_embeddings.keys())}_sample_{os.getenv('RUN_ID')}.json", 'w') as file:
      json.dump(query_embeddings, file)

if __name__ == '__main__':
    main()
