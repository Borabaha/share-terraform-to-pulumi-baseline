#!/usr/bin/env bash
# Wave 2 and later: the rest of the 408-task base set, in the order given by seed 20261006, as 4 shards.
# Each shard waits until its wave-1 run is done and then reuses the same run folder, where setup, .terraform and the
# venv are already in place. This way no first-time provider installs run in parallel; that collision broke task 304
# in wave 1.
# Paths are relative to this folder (pipeline/). Task lists: tasks/shards/. Logs: runs/ext-w1/.
cd "$(dirname "$0")" || exit 1
W=runs/ext-w1
shard () {
  s=$1; R=ext-w1-$s
  export THESIS_TF_PLUGIN_CACHE_DIR="$PWD/runs/$R/_plugin-cache"; mkdir -p "$THESIS_TF_PLUGIN_CACHE_DIR"   # one plugin cache per shard
  until grep -q "^== done" $W/shard-$s.log 2>/dev/null; do sleep 20; done
  for f in $(ls tasks/shards/w[2-9]-$s.txt | sort -V); do
    w=$(basename $f .txt)
    {
      echo "== $w tf $(date +%T)";         python pilot_runner.py tf     --run $R --tasks "$PWD/$f"
      echo "== $w typescript $(date +%T)"; python pilot_runner.py pulumi --run $R --lang typescript --tasks "$PWD/$f"
      echo "== $w python $(date +%T)";     python pilot_runner.py pulumi --run $R --lang python     --tasks "$PWD/$f"
      echo "== $w done $(date +%T)"
    } >> $W/waves-$s.log 2>&1
  done
}
for s in a b c d; do shard $s & sleep 5; done
wait
echo "ALL WAVES DONE $(date +%T)"
