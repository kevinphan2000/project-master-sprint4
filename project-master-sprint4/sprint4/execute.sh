#!/bin/bash

#checking if cython is installed
if ! pip freeze | grep -q Cython; then
    echo 'Error: cython is not installed.\n Please run: pip install cython' >&2
    exit 1
fi

# check if an input file is given
if [ $# -eq 0 ]; then
    echo "Error: No input file given." >&2
    exit 1
fi

mkdir -p build
mkdir -p logs
touch logs/files.txt
# run the backend on the specified file
if python3 ./MemeBackend.py $1 | grep **ERROR**; then
    echo "Error: Backend failed to run." >&2
    exit 1
fi

# generate the output file into a cython file
python3 src/setup.py build_ext > logs/out.log
python3 src/setup.py install --user --record logs/files.txt >> logs/out.log

# run the cython file
python3 src/run.py

xargs rm -rf < logs/files.txt