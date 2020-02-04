#!/usr/bin/env bash

set -e

# determine physical directory of this script
src="${BASH_SOURCE[0]}"
while [ -L "$src" ]; do
  dir="$(cd -P "$(dirname "$src")" && pwd)"
  src="$(readlink "$src")"
  [[ $src != /* ]] && src="$dir/$src"
done
MYDIR="$(cd -P "$(dirname "$src")" && pwd)"

: "${NUM_THREADS:=5}"
: "${JOBS_FILE:=$MYDIR/data/compcert-test-files.txt}"
: "${OUTDIR:=$MYDIR/search-report}"
mkdir -p logs
parallel --tmuxpane -j $NUM_THREADS -a $JOBS_FILE --fg \
         "tmux select-layout even-vertical && ulimit -s unlimited &&
          python3.7 $MYDIR/src/search_file.py -o $OUTDIR $@ {} 2> logs/{/.}.txt --proof-times=logs/{/.}-times.txt"
cat $JOBS_FILE | xargs python3.7 $MYDIR/src/search_report.py -o $OUTDIR $@
