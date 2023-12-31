import argparse
from dotenv import load_dotenv
import os
from google_bigquery_patents_dataset import BigQueryTableReader
from sample import Sample
from pprint import pprint
from utils import validate_n, fully_minimize_json
from open_ai_client import OpenAiClient
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
    raise Exception("Please use a preapred sample via the --file flag; they are really expensive to collect")
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
  pprint(prepared_subsample)

if __name__ == '__main__':
    main()
