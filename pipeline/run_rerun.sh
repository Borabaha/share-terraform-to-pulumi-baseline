#!/usr/bin/env bash
# Re-run of the tasks whose run broke while the machine was asleep (8 Oct): tf, typescript and python stages,
# each list in its own shard folder, with one plugin cache per shard.
# Paths are relative to this folder (pipeline/). Task lists: tasks/shards/rerun-<shard>.txt. Logs: runs/ext-w1/.
cd "$(dirname "$0")" || exit 1
W=runs/ext-w1
mkdir -p $W
one () {
  s=$1; R=ext-w1-$s; f=tasks/shards/rerun-$s.txt; [ -f $f ] || return
  export THESIS_TF_PLUGIN_CACHE_DIR="$PWD/runs/$R/_plugin-cache"
  {
    echo "== rerun tf $(date +%T)";         python pilot_runner.py tf     --run $R --tasks "$PWD/$f"
    echo "== rerun typescript $(date +%T)"; python pilot_runner.py pulumi --run $R --lang typescript --tasks "$PWD/$f"
    echo "== rerun python $(date +%T)";     python pilot_runner.py pulumi --run $R --lang python     --tasks "$PWD/$f"
    echo "== rerun done $(date +%T)"
  } > $W/rerun-$s.log 2>&1
}
for s in a b c d; do one $s & sleep 5; done
wait
echo "RERUN DONE $(date +%T)"
