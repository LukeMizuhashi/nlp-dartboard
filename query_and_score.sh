#!/bin/bash
export RUN_ID=$(uuidgen)
python query_and_score.py \
  --samples samples/len_1000_sample_b139366c-8c7c-4b99-9684-089c28e7edbe.json \
  --embeddings embeddings/len_584_sample_C745A1EA-2AFC-4F2C-9825-8B8D1B501E75.json > ./query_embeddings/$RUN_ID.log
unset RUN_ID
