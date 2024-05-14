#!/bin/bash

# Define the results directory path relative to this script
RESULTS_DIR="results"

# Check if the results directory exists and remove all files if it does
if [ -d "$RESULTS_DIR" ]; then
  echo "Removing all files from $RESULTS_DIR"
  rm -f $RESULTS_DIR/data/*
  rm -f $RESULTS_DIR/descriptions/*
  rm -f $RESULTS_DIR/plots/*
fi

# Change directory to complex_use_cases
cd complex_use_cases || exit

# Iterate over each .py file in the directory
for file in *.py; do
    echo "Running $file"
    python3 "$file" # Use python3 or just python depending on your setup
done
