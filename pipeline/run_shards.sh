#!/usr/bin/env bash
# Extension wave 1: 60 base-set tasks outside the pilot, run as 4 shards in parallel.
# Each shard has its own run folder (its own _tfwork, node_modules, .venv-py and Pulumi state), so the shards do not
# get in each other's way.
# Paths are relative to this folder (pipeline/). Task lists: tasks/shards/. Logs: runs/ext-w1/.
cd "$(dirname "$0")" || exit 1
W=runs/ext-w1
mkdir -p $W   # log folder
run_shard () {
  s=$1; R=ext-w1-$s; L=$W/shard-$s.log
  mkdir -p runs/$R
  cp config/package-lock.json runs/$R/
  {
    echo "== setup $(date +%T)"
    python pilot_runner.py setup --run $R --lang typescript
    python pilot_runner.py setup --run $R --lang python
    echo "== tf $(date +%T)"
    python pilot_runner.py tf --run $R --tasks "$PWD/tasks/shards/w1-$s.txt"
    echo "== typescript $(date +%T)"
    python pilot_runner.py pulumi --run $R --lang typescript --tasks "$PWD/tasks/shards/w1-$s.txt"
    echo "== python $(date +%T)"
    python pilot_runner.py pulumi --run $R --lang python --tasks "$PWD/tasks/shards/w1-$s.txt"
    echo "== done $(date +%T)"
  } > "$L" 2>&1
}
for s in a b c d; do run_shard $s & done
wait
echo "ALL SHARDS DONE $(date +%T)"
