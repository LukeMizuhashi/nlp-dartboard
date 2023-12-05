#!/bin/bash
export RUN_ID=$(uuidgen)
python prepare_subsample.py --file samples/len_1000_sample_b139366c-8c7c-4b99-9684-089c28e7edbe.json > ./subsamples/$RUN_ID.log
unset RUN_ID
