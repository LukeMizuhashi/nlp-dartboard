import argparse
from dotenv import load_dotenv
import os
import json
from openai import OpenAI

def main():
  load_dotenv(dotenv_path='.env.secrets')
  load_dotenv(dotenv_path='.env.openai.embedding.nonsecrets', override=True)

  parser = argparse.ArgumentParser(description='Fetch samples from BigQuery or JSON file.')
  parser.add_argument('--input', required=True, type=str, help='Path to a JSON file containing samples')
  args = parser.parse_args()

  with open(args.file, 'r') as file:
    prepared_sample = json.load(file)
  
  client = OpenAI()
  embeddings = {}
  for key, value in prepared_sample.items():
    response = client.embeddings.create(
        input=value,
        model=os.getenv('OPEN_AI_EMBEDDING_MODEL')
    )
    embeddings[key] = response.model_dump_json()

  with open(f"embeddings/len_{len(embeddings.keys())}_sample_{os.getenv('RUN_ID')}.json", 'w') as file:
      json.dump(embeddings, file)

if __name__ == '__main__':
    main()
