#!/bin/bash
export RUN_ID=$(uuidgen)
python run_queries.py \
  --model embeddings/len_584_sample_C745A1EA-2AFC-4F2C-9825-8B8D1B501E75.json \
  --queries query_embeddings/len_416_sample_C2E04460-C257-47F3-BC83-C29B49490012.json > ./eval/$RUN_ID.log
unset RUN_ID
