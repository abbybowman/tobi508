# Restarts and hand-restored files

Development pages; a rerun that never replaces round 3's blind score. Agent-assisted, not certified.

- 2026-11-19 ~00:56 UTC: the container restarted (uptime 0 min) while arm A run 1, group 1
  (pages 1-2) was in its first `tobi_run_tt_tests` call, about 15 min in. No report had been
  written. The partial output (`results/arm-a-1`, a step log and one unfinished run folder) was
  moved out, and group 1 of run 1 was started again from nothing. `UPSTREAM_PROXY` was set again
  from the new `HTTPS_PROXY`. C repeats 1-3 had finished before the restart and were not touched.
- Arm A groups are labelled g<group>-<run> (results/arm-a-g1-1 ...), because one label cannot hold five groups. The first finished group was renamed from arm-a-1 to arm-a-g1-1; its summary.json still names code_commit 563c83e (src/ and specs/ are unchanged since the stated base).
- 2026-11-19 ~01:10 UTC: second container restart, after group 1 of run 1 had finished; nothing lost. Started chainA.sh (skips finished groups; start it again after any restart).
- 2026-11-19 01:29:31 UTC: third container restart, group 3 of run 1 in flight (about 12 min in) was lost; the watchdog restarted chainA.sh, which removed the partial folder and reran the group.
