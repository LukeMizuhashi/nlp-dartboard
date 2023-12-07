#!/bin/bash
export RUN_ID=$(uuidgen)
python analyze_query_results.py \
  --sample samples/len_1000_sample_b139366c-8c7c-4b99-9684-089c28e7edbe.json \
  --query_results eval/len_416_queries_D5CE34FD-AFF0-4EBE-BA70-E9551D3D62E6.json # > ./analyze/$RUN_ID.log
unset RUN_ID
