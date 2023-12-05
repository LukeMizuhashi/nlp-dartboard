import argparse
from dotenv import load_dotenv
import os
import json
from google_bigquery_patents_dataset import BigQueryTableReader
from sample import Sample
from utils import fully_minimize_json
from google_to_openai import Converter 

def main():
  load_dotenv(dotenv_path='.env.secrets')
  load_dotenv(dotenv_path='.env.nonsecrets', override=True)

  parser = argparse.ArgumentParser(description='Fetch samples from BigQuery or JSON file.')
  parser.add_argument('--samples', type=int, help='Number of samples to fetch from BigQuery')
  parser.add_argument('--file', type=str, help='Path to a JSON file containing samples')
  args = parser.parse_args()
  
  if args.samples and args.file:
    raise Exception("Please pass --samples or --file but not both")
  elif args.samples:
    raise Exception("Use a preapred sample via the --file flag; samples are really expensive to collect")
    # validate_n(args.samples)
    # reader = BigQueryTableReader(os.getenv('GOOGLE_CLOUD_PROJECT'), os.getenv('GOOGLE_PATENTS_CLOUD_PROJECT'), os.getenv('COOGLE_CLOUD_DATASET'))
    # rows = reader.get_random_rows(os.getenv('TABLE_ID'), args.samples, "ARRAY_LENGTH(description_localized) > 0")
    # sample = Sample(rows)
  elif args.file:
    sample = Sample(args.file)
  else:
    raise Exception("Please specify either --samples or --file to fetch samples.")

  conv = Converter(
    sample,
    os.getenv('OPEN_AI_EMBEDDING_MODEL'),
    int(os.getenv('OPEN_AI_EMBEDDING_MAX_TOKENS')),
    int(os.getenv('SUB_SAMPLE_SIZE')),
    os.getenv('BASE_KEYS').split(','),
    int(os.getenv('OPEN_AI_TOKEN_SLACK')),
    fully_minimize_json,
    )
  prepared_subsample = conv.prepare_for_embedding()
  print(f"Prepared {len(prepared_subsample.keys())} subsamples from {os.getenv('SUB_SAMPLE_SIZE')} requested")
  file_path = f"subsamples/len_{len(prepared_subsample.keys())}_sample_{os.getenv('RUN_ID')}.json"
  with open(file_path, 'w') as file:
    json.dump(prepared_subsample, file)

if __name__ == '__main__':
    main()
