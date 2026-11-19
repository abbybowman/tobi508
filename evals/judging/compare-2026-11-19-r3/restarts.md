# Restarts and hand-restored files

Development pages; a rerun that never replaces round 3's blind score. Agent-assisted, not certified.

- 2026-11-19 ~00:56 UTC: the container restarted (uptime 0 min) while arm A run 1, group 1
  (pages 1-2) was in its first `tobi_run_tt_tests` call, about 15 min in. No report had been
  written. The partial output (`results/arm-a-1`, a step log and one unfinished run folder) was
  moved out, and group 1 of run 1 was started again from nothing. `UPSTREAM_PROXY` was set again
  from the new `HTTPS_PROXY`. C repeats 1-3 had finished before the restart and were not touched.
