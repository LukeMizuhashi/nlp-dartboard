#!/bin/bash
export RUN_ID=$(uuidgen)
python get_subsample_embeddings.py --input subsamples/len_584_sample_D3C7AEBF-69B6-4DF7-9405-4FB31A5D962E.json > ./embeddings/$RUN_ID.log
unset RUN_ID
