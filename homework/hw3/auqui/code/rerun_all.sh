for k in 1 2 3 4; do python3 llm_round.py $k --replay > /dev/null; done
python3 tune_compare.py > tune_compare.log 2>&1
python3 run_extra.py > run_extra.log 2>&1
python3 analysis.py > analysis.log 2>&1
echo finished > rerun.done
