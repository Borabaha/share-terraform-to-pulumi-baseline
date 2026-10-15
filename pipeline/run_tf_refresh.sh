#!/usr/bin/env bash
# Runs the Terraform control group again after pinning python-hcl2 to 7.3.1, with which tflocal reads the provider
# region from main.tf. Only the Terraform stage is repeated, because the Pulumi side does not use tflocal.
# 4 shards, each with its own plugin cache, plus the pilot run folder.
# Paths are relative to this folder (pipeline/). Task lists: tasks/shards/. Logs: runs/ext-w1/.
cd "$(dirname "$0")" || exit 1
W=runs/ext-w1
mkdir -p $W   # log folder
one () {
  s=$1; R=ext-w1-$s
  export THESIS_TF_PLUGIN_CACHE_DIR="$PWD/runs/$R/_plugin-cache"
  { echo "== tf-refresh $(date +%T)"; python pilot_runner.py tf --run $R --tasks "$PWD/tasks/shards/tf-refresh-$s.txt"; echo "== tf-refresh done $(date +%T)"; } > $W/tf-refresh-$s.log 2>&1
}
pilot () {
  export THESIS_TF_PLUGIN_CACHE_DIR="$PWD/runs/pilot-aligned/_plugin-cache"; mkdir -p "$THESIS_TF_PLUGIN_CACHE_DIR"
  { echo "== tf-refresh pilot $(date +%T)"; python pilot_runner.py tf --run pilot-aligned --tasks tasks/pilot_tasks.txt; echo "== tf-refresh done $(date +%T)"; } > $W/tf-refresh-pilot.log 2>&1
}
for s in a b c d; do one $s & sleep 5; done
pilot &
wait
echo "TF REFRESH DONE $(date +%T)"
