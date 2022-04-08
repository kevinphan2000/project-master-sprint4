#!/bin/bash

# run all tests in the test folder
# deposit their output into the test_results folder

mkdir -p test_results
for f in ./tests/*.ak ; do
    echo "Processing $f file..."
    ./execute.sh $f > test_results/$(basename $f .ak).out
done