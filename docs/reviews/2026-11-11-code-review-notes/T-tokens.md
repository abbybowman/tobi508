# T-tokens: what a calling agent receives per page (measured)

Reviewer T (token measurement). Page tested: `tests/fixtures/budget/agency-home.html`
(default tests, all 22) and `tests/fixtures/no_trap.html` for comparison.
Driver: `/tmp/claude-0/-home-user-tobi508/e409d852-9211-5ad4-9dc1-79e7dbd3df61/scratchpad/t/drive.py`
(in-process `fastmcp.Client(mcp)`, test Settings, local HTTP server, offline DNS
resolver; the result of each call was dumped as every content block plus
`structured_content`; analysis in `an.py`, `an2.py` next to it). Tokens are
chars/4 unless said otherwise. "Content-only" = what Claude Code-style clients put
in the model's context (content blocks); "with structured" adds `structured_content`
in case a client forwards both (unknown, so both are shown). Answers given were
"unsure"/first-choice with a `seen` text: only sizes matter. The agency run took
2 m 9 s end to end (run + 2 answer rounds + status + explain + reads).
Round 1 answered 6 of 10 questions; round 2 the remaining 4, so the session had 2 answer rounds, not 3.

## Measurements

### M1. Fixed cost: tool list and instructions
Measured with `mcp.list_tools()` (description + inputSchema + outputSchema JSON) and `mcp.instructions`.

| Tool | description | input schema | output schema |
|---|---|---|---|
| tobi_run_tt_tests | 4,262 | 2,470 | 9,296 |
| tobi_run_status | 778 | 757 | 11,197 |
| tobi_answer_questions | 833 | 5,165 | 7,818 |
| tobi_read_report | 483 | 860 | 3,141 |
| tobi_explain | 685 | 585 | 119 |
| total | 7,041 | 9,837 | 31,571 |

Total 48,449 chars + server instructions 2,282 = **50,731 chars = 12.7k tokens** before any call. Output schemas are 62% of it.

### M2. `tobi_run_tt_tests` on agency-home (22 findings, 10 open questions)
Measured by dumping `client.call_tool` result blocks.

| Part | chars | tokens |
|---|---|---|
| content block 0 (result JSON) | 32,045 | 8.0k |
| 8 "Picture for open question..." caption blocks | 1,152 | 0.3k |
| trailing "TO DO" block | 755 | 0.2k |
| text content total | 33,952 | 8.5k |
| `structured_content` (the same JSON again, `{"result":...}`-free here) | 32,056 | 8.0k |
| 8 attached pictures (base64) | 308,296 b64 chars (231 KB) | about 2.1k picture tokens (my estimate, width x height / 750 after the server's downscale: 4.A page 768x1104 = 1,130; 4.F crop 153; 6 label crops 110-171 each) |
| **Total, content only** | | **about 10.9k** |
| **Total with structured** | 66,008 + pictures | **about 18.9k** |

The structured copy equals the text JSON (32,056 vs 32,045 chars): the same JSON is sent twice.

By top-level field (compact JSON length of each value, largest first):

| field | chars | note |
|---|---|---|
| open_questions (10) | 17,367 | avg 1,737 each; 4.F-o1-J1 alone 7,884 |
| findings (22) | 8,088 | avg 367 each |
| question_texts | 1,755 | |
| next_step | 1,553 | |
| evidence (25 URIs) | 1,228 | |
| todo (5 items) | 741 | repeated verbatim in the TO DO block |
| untrusted_content_notice | 143 | |
| tests | 134 | the ids that `findings` already has |
| save_hint | 119 | |
| disclaimer | 114 | required |
| remaining | 112 | |
| walk | 87 | |
| target, final_url | 48 + 48 | identical strings |
| pre_scrt_uri, report_uri, expires_at, run_id, work, status | 45, 43, 29, 25, 12, 6 | |
| follow_up_calls, page_text, shared_inputs, errors, more_questions | 2 each (1) | all empty |

`findings` by sub-field (22 items): summary 3,253 (147 avg); wcag_sc 836 (38); test_name 526 (23); note 478; outcome 231; waiting_on 144; test_id 111; confirmed 88; unconfirmed 22. Outcomes: 13 NEEDS_REVIEW, 5 DNA, 4 PASS. The TT catalogue text (wcag_sc + test_name) is 1,362 chars on every call that lists findings.

`open_questions` by sub-field (10 items): input 9,517 (951 avg; 4.F order list 4,903, 5.H page_text 1,473, 5.B items 1,096); rubric 2,641 (264); question 2,330 (233); evidence_paths 560; choices 465; question_id 115; kind 80; the rest under 70 each. Five 4.A questions are identical except the id and cost 574 chars each (2,870 total) and each holds a "Shared with other questions: read question_texts[...]" placeholder pair (about 130 chars) where `shared_inputs` is empty.

### M3. Repeated, empty and unusable content in the run result
Measured by walking the parsed JSON (strings of 60+ chars, counted across all fields and the TO DO block).

- 12 distinct strings of 60+ chars occur more than once; **2,258 chars wasted** (565 tokens). Largest: the NEEDS_REVIEW boilerplate "We could not finish this test, so a person needs to check it. The page has menus or sections that open..." (215 chars x 4, wasted 645); the two "Shared with other questions: read question_texts["4.A-J2"].question/.rubric" placeholders (x5 each, wasted 536); four of the five TODO lines appear twice (JSON `todo` and TO DO block; 237 + 192 + 136 + 105 wasted).
- Empty, null, false or zero leaves: 108 in this one result: `findings[].confirmed` 22, `unconfirmed` 17, `waiting_on` 17, `note` 9, `open_questions[].also_instances` 10, `.shared` 10, `.input.order[].page_box[]` 10, plus `follow_up_calls`, `page_text`, `errors`, `more_questions`, `remaining.*`. About 1,300 chars of keys and empty values (estimated at 12 chars each).
- Not actionable by an agent: `evidence` (25 URIs, 1,228 chars; the `evidence_paths` of each question already name what is needed), `tests` (134), `walk` (87), `final_url` (48, equal to `target`), `expires_at` is only needed when saving; `next_step` carries run history in every call ("the fourth development run's agent ended with questions and follow-up calls open", 1,553 chars; A-03). `status` and `work` say the same as `remaining`.

### M4. Answer flow (agency-home)
Round 1 answered 6 of 10 questions; round 2 the other 4 (re-asked questions came back; no follow-up questions arose).

| Result | text chars | structured chars | pictures | tokens, content only | with structured |
|---|---|---|---|---|---|
| run | 33,952 | 32,056 | 8 (308k b64) | 10.9k | 18.9k |
| answers round 1 (4 left open) | 14,459 | 12,712 | 7 (136k b64, all already sent) | 3.6k + about 0.9k pictures = 4.5k | 7.7k |
| answers round 2 (0 left) | 3,953 | 3,391 | 0 | 1.0k | 1.8k |

Round 1 by field: open_questions 6,607 (the four still-open questions, whose input, rubric and question are unchanged from the run result), findings 1,780 (5 findings), next_step 1,435, question_texts 1,057, todo 740, untrusted notice 143, save_hint 119, disclaimer 114, unchanged 104.
Round 2 by field: findings 1,117, next_step 667, todo 546, notice 143, save_hint 119, unchanged 116, disclaimer 114, remaining 82.

Repetition: of round 1's text, strings of 40+ chars that already appeared in the run result total 5,355 chars (42% of its JSON); in round 2, 1,034 (30%). `next_step` (1,435) and `todo` (740) are the run result's text with the counts changed; the `question_texts["5.B-J1"]` entry (1,057) is sent again though the run result held it. All 7 pictures of round 1 were attached before (the 5.B crops, ~0.9k picture tokens): see T-06.
Note: round 2's `todo` still says "call tobi_run_status ... until it lists nothing left" and `next_step` tells the agent `work` is incomplete while the result already says `work: complete`.

### M5. Status, explain, read_report, report resource
All by the same dump. `tobi_run_status` (no job_id) and with `finish=true`: identical results.

| Call | text chars | structured | tokens (text) |
|---|---|---|---|
| tobi_run_status (no job_id) | 494 + 91 (TO DO) | 414 | 0.15k |
| tobi_run_status finish=true | same | same | 0.15k |
| tobi_explain run_id (no about), agency | 37,818 | 38,465 | 9.5k |
| tobi_explain run_id, no_trap | 26,568 | 26,890 | 6.6k |
| tobi_explain about="4.C" | 5,121 | 5,235 | 1.3k |
| `run://.../report.json` agency | 148,364 (pretty-printed; 97,466 compact) | | 37.1k (24.4k compact) |
| `run://.../report.json` no_trap | 35,382 (26,265 compact) | | 8.8k |
| `run://.../pre-scrt.json` agency | 69,580 (56,917 compact) | | 17.4k |
| `run://.../pre-scrt.json` no_trap | 65,533 (53,650 compact) | | 16.4k |

Note: status says `"status":"outstanding"` with `runs: []` and "Nothing is left" in the same message (T-11).

`tobi_explain` (agency, 37,818 chars) by line type: "What this tool does for X" 9,627 (22 lines, fixed text per test); bullet lines (places on the page) 7,110; "Summary" 6,476 (repeats the run result's finding summary, plus appended "We looked for..." sentence); "Technical reasoning, for your reference only" 3,346; "Requirements" 3,032; "TT <id> <name>: condition" 2,774; "Rule trail (spec rows, for an audit)" 2,173; "Full text: tt://..." 705; the rest (head instructions 951, Result/Note lines 1,069). 1,646 chars are lines of 60+ chars repeated (the same summary appears under 4 tests). The largest section is 4.D at 8,744 chars (81 bullet lines).

`report.json` by top-level field (compact, agency): findings 41,856; answers 28,671; questions 24,596; versions 1,372; tests 134; disclaimer 114; rest under 100. Each `answers[]` entry embeds the full question (question, rubric, input), which `questions` already holds; each finding carries `instances`, `evidence_refs`, `rationale`, `rows`, `decided_by` and a never-set `confidence`. Pretty-printing adds 51k chars (148,364 vs 97,466).
`pre-scrt.json`: `Criteria` is 54,457 of 69,580 chars: 61 rows of about 890 chars each (TestCondition, DisabilityImpact list, TesterComment, source). For no_trap it is 51,212 of 65,533: the page-specific part is under 5,000 chars.

Largest evidence files (not sent by tools, only reachable as resources): walk.json 693,440; 4d.json 405,707; 5g.json 199,882; 5f.json 199,709; 4f.json 111,617; 2a-2d.json about 41,500 each (in the run folder; total evidence about 2.0 MB).

### M6. Whole session on one page, in tokens
Measured sums from M1-M5; "save" = reading `report.json` and `pre-scrt.json` as the `save_hint` says; "write" = the model re-emitting both files into the user's repository (assumed: an MCP client cannot save a resource without the model; I did not run a client).

| Step | agency-home | no_trap |
|---|---|---|
| tool list + instructions | 12.7k | 12.7k |
| run result (text + pictures) | 8.5k + 2.1k = 10.6k | 4.6k + 0.1k = 4.7k |
| answer rounds (text + pictures) | 4.5k + 1.0k = 5.5k (2 rounds) | 1.0k (1 round) |
| run_status | 0.15k | 0.15k |
| tobi_explain (whole run) | 9.5k | 6.6k |
| read report.json | 37.1k | 8.8k |
| read pre-scrt.json | 17.4k | 16.4k |
| **Read side, content only** | **92.9k** | **50.4k** |
| write both files out (if the model copies them) | +54.5k output | +25.2k output |
| with structured_content forwarded | +21.8k | +11.6k |
| **Worst case** | **about 169k** | about 87k |

Fixed cost (no_trap, 50k read side, of which 12.7k tool list and 16.4k pre-scrt): per-page cost on agency-home over the small page is about 42k tokens, of which 28k is the report resource.

### M7. Estimated savings, largest first (agency-home, content-only basis unless noted)

| Change | tokens saved per session |
|---|---|
| Stop sending `pre-scrt.json` through the model (T-02): remove it from `save_hint`, build it only when asked | 17.4k read + 17.4k write = 34.8k |
| Compact `report.json`, drop the question copy inside each answer (T-03) | about 19k read + 19k write = 38k |
| Drop `structured_content` and output schemas (T-04, A-02) | 21.8k (if forwarded) + 7.9k schemas |
| Trim `tobi_explain` of the whole run (T-05) | 5.4k (10.8k with structured) |
| Answer results: only ids of still-open questions, no repeated pictures (T-06) | 2.5k per round with open questions |
| Slim run result: one todo channel, no empties, no `evidence`/`tests`, no catalogue text per finding (T-07, T-08) | 2.0k on the run + 0.8k per later result |

## Findings

### T-01 Saving the report costs 55k tokens to read and the same again to write on a realistic page
- Severity: P1
- Kind: tokens
- Where: src/tobi508/models.py:604-612 (`SAVE_HINT`), the `todo` item "Save report_uri and pre_scrt_uri", src/tobi508/resources/runs.py (report.json and pre-scrt.json)
- What: every result tells the agent to read `report_uri` and `pre_scrt_uri` and save them in the user's repository. An MCP client has no "save resource to disk" step, so the model reads both files into context (agency-home: 148,364 + 69,580 chars = 54.5k tokens; no_trap: 25k) and then emits them again through a file-write tool (another 54.5k output tokens, the slow and costly kind). This is 59% of the whole read-side session and about as much again in output.
- Evidence: measured resource sizes through `client.read_resource` (M5). The write-out is assumed (not run with a real client), but there is no other path from resource to file.
- Fix: see T-02 and T-03 to shrink the files; also make saving one optional step the user asks for, and let the server write the file when the client has a filesystem (for example `save_to` option on a tool, or a download URL in hosted mode).
- Confidence: confirmed (sizes); likely (copy through the model)

### T-02 pre-scrt.json is 51k chars of fixed catalogue text, copied in full for every page
- Severity: P1
- Kind: tokens
- Where: src/tobi508/scrt.py (pre-SCRT builder), src/tobi508/resources/runs.py
- What: `Criteria` holds 61 rows of about 840-890 chars: TestCondition, a `DisabilityImpact` list of 11 items repeated on every row (7,308 chars), `source`, empty `TesterComment`. Only a few hundred chars per row come from the run. The file is 65.5k chars for a trivial page and 69.6k for agency-home, so it is almost pure fixed cost (16-17k tokens, read and written).
- Evidence: parsed both files (M5): Criteria 51,212 of 65,533 (no_trap) and 54,457 of 69,580 (agency); per-row key sizes: source 10.5k, TesterComment 8.3k, DisabilityImpact 7.3k, TestCondition 5.9k.
- Fix: do not offer it in `save_hint`/`todo` by default; produce it on demand (`tobi_read_report`-style call or a flag) and, if kept, send it compact (this alone is 12.6k chars, 3k tokens) and without the catalogue columns a reader can regenerate from tt.json.
- Confidence: confirmed

### T-03 report.json is pretty-printed and stores every answered question twice
- Severity: P1
- Kind: tokens
- Where: src/tobi508/runlog.py (report write), src/tobi508/models.py (`Report.answers`, `Report.questions`, `Finding.confidence`, `Finding.rows`)
- What: the file is 148,364 chars; compact JSON is 97,466 (indent costs 51k chars, 12.7k tokens). In the compact form `answers` (28,671) embed the full question (question, rubric, input, choices), which `questions` (24,596) also holds, so about 20-25k chars are a second copy. `findings` (41,856) carry `rationale`, `rows`, `evidence_refs`, `decided_by` and the never-set `confidence` on every finding, including the DNA ones.
- Evidence: parsed `report.json` (M5); `answers[0]` starts with `{"question": {"question_id": ..., "rubric": ...}`.
- Fix: write compact JSON; in `answers` keep `question_id` plus the answer; drop `confidence`. Expected: about 70k chars (18k tokens) instead of 148k.
- Confidence: confirmed (sizes); likely (that an indent is safe to drop: check the readers in scrt.py and compare.py)

### T-04 Every result is sent twice: text JSON and structured_content, and tobi_explain wraps its string too
- Severity: P1
- Kind: tokens
- Where: src/tobi508/inline.py:211-251 (`structured_content=...`), src/tobi508/tools/explain.py (string result gets `{"result": ...}`)
- What: measured equal sizes for the two copies: run 33,952 text vs 32,056 structured, round 1 14,459 vs 12,712, round 2 3,953 vs 3,391, explain 37,818 vs 38,465. If the client forwards both, a session pays 21.8k extra tokens (agency) or 11.6k (no_trap). A-02 flagged this; here are the numbers. Together with the 31.6k chars of output schemas (7.9k tokens) the schema-and-duplicate layer is up to 29.7k tokens of 169k.
- Evidence: `ToolResult.content` and `.structured_content` dumped and compared (M2, M4, M5).
- Fix: as A-02: no output schema and text content only; keep `structured_content` only for tests through a flag.
- Confidence: confirmed (sizes); speculative (whether the client forwards both)

### T-05 tobi_explain for a whole run is 9.5k tokens, mostly text the agent already has
- Severity: P2
- Kind: tokens
- Where: src/tobi508/explain.py:106-132, 177-237 (A-10 covers the missing cap)
- What: for agency-home, 37,818 chars. Of these, 9,627 are the per-test "What this tool does for X" paragraphs (identical on every run of that test), 3,032 "Requirements", 2,774 "TT id name: condition", 705 "Full text:" lines (TT text from tt.json, a resource), 6,476 "Summary" lines that repeat the run result's finding summaries (4 tests share one 272-char summary), 3,346 "Technical reasoning, for your reference only" and 2,173 "Rule trail (spec rows, for an audit)" lines of row codes such as "x1:M8; x2:M9; t74:M15". CLAUDE.md principle 8 says row IDs stay in the evidence trace, but they are in the text a user-facing agent reads. About 21.6k chars (5.4k tokens) are catalogue text or codes.
- Evidence: line-type breakdown of `explain_run.json` (M5).
- Fix: for run mode print per finding only the places and the fix source (one link per test), move the tool-description paragraphs to `tt://` resources, and drop the rule trail and technical reasoning lines from text (keep them in report.json).
- Confidence: confirmed

### T-06 A later answer result re-sends the open questions, their pictures and the shared texts it already sent
- Severity: P2
- Kind: tokens
- Where: src/tobi508/inline.py:99-196 (`pictures`, `attached`), src/tobi508/pipeline.py (`answer_questions` result build), A-08 for the picture side
- What: round 1 of the answers returned the 4 still-open questions in full (6,607 chars: input 3,102, rubric 1,206, question 1,146) plus `question_texts["5.B-J1"]` (1,057) and all 7 pictures again (about 0.9k picture tokens), all unchanged since the run result. 5,355 of its 12.7k chars of JSON are strings that were in the previous result (42%). A real agent in a 3-4 round flow pays this each round.
- Evidence: M4; compared strings of 40+ chars between the three results.
- Fix: in an answer result list a question that is unchanged as `{question_id, "unchanged since the last result"}`, send input/rubric/pictures only for new or changed questions (follow-ups), and send `question_texts` only for texts not sent before in this run.
- Confidence: confirmed (sizes); likely (that the agent still has the earlier result in context)

### T-07 One instruction block is written three ways in each result (next_step, todo, TO DO block)
- Severity: P2
- Kind: tokens
- Where: src/tobi508/pipeline.py:1316-1440, src/tobi508/inline.py:211-251 (A-03 is the source)
- What: measured, not estimated: run result `next_step` 1,553 chars + `todo` 741 + the same `todo` in the TO DO block 755 = 3,049 chars (760 tokens), round 1 about 2,930, round 2 about 1,880, status 585. Four of five `todo` lines in the run result appear twice by exact string match (M3). Round 2 says `work: complete` and then `next_step` explains what to do while `work` is incomplete, with the same history sentence as the run result. Over a 3-call session the instruction text is about 1.9k tokens, of which about 1.2k is repeats.
- Evidence: M2-M4, string counts.
- Fix: send `todo` once (the trailing block, excluded from the JSON), shorten `next_step` to the state in one sentence, and remove the history parentheticals.
- Confidence: confirmed

### T-08 Per-finding catalogue text and empty fields make each findings list about 40% bigger than needed
- Severity: P2
- Kind: tokens
- Where: src/tobi508/models.py:559-584 (`FindingView`), 631-697 (`RunResult`)
- What: 22 findings are 8,088 chars. `wcag_sc` (836) and `test_name` (526) repeat TT catalogue text an agent can read in tt://; `confirmed` (88, always null except FAIL), `unconfirmed` (22), `waiting_on` (144), `note` (478, mostly the same sentence "This test could not be performed") restate the outcome. 108 empty/null/false/zero leaves exist in the run result, 30 in round 1, 19 in round 2. The 13 NEEDS_REVIEW summaries begin with the same 62-char boilerplate (800 chars), and `tests` (134), `evidence` (1,228), `final_url` (48) and `target` (48) say what other fields say. About 3.5k chars (0.9k tokens) in the run result and 0.5k tokens per answer round.
- Evidence: M2, M3 breakdowns.
- Fix: `exclude_none`/`exclude_defaults` on the dump, drop `wcag_sc`/`test_name`/`confirmed`/`unconfirmed`/`tests`/`evidence`, and state "could not be performed" once in the findings' header instead of in `note` per finding.
- Confidence: confirmed

### T-09 One 4.F question is 7.9k chars (2k tokens) and 5 of the 4.A questions are the same question
- Severity: P2
- Kind: tokens
- Where: src/tobi508/checks/t4f.py (question input `order`), src/tobi508/checks/t4a.py (J2 per element); src/tobi508/models.py (`shared_inputs`)
- What: `4.F-o1-J1` is 7,884 chars: `order` 4,903 (includes empty `page_box: []` per item), `signals` 466, rubric 1,083, question 822. That one question is 45% of the 17.4k chars of questions. The five `4.A-t7x-J2` questions each cost 574 chars (2,870 total) and differ only in the title, element and id; each also carries a "Shared with other questions" placeholder pair while `shared_inputs` stays `{}`, so the sharing mechanism is used for text but not for evidence.
- Evidence: per-question sizes (M2).
- Fix: drop empty `page_box`, cap `order` at the items whose visual and DOM order differ plus a count, and ask the 4.A tooltips as one question with a list.
- Confidence: confirmed (sizes); likely (that questions can be merged without changing the answer rules)

### T-10 Rule codes and "for your reference only" text reach the user-facing agent
- Severity: P3
- Kind: tokens
- Where: src/tobi508/explain.py (`Technical reasoning`, `Rule trail`), also bullets such as "t74 [M15 NEEDS_REVIEW] T:" in "Places on the page"
- What: CLAUDE.md principle 8 says row IDs stay in the evidence trace and users get plain language; in tobi_explain 5.5k chars (1.4k tokens) are row trails and ids ("Spec G3. x1:M8; x2:M9 ..."), and the page-place bullets carry `[M15 NEEDS_REVIEW]` prefixes. An agent cannot act on them. Counted in T-05 savings.
- Evidence: `explain_run.json` lines starting "Technical reasoning" (3,346) and "Rule trail" (2,173).
- Fix: keep these in `report.json` only.
- Confidence: confirmed

### T-11 tobi_run_status with nothing left says "outstanding" and repeats the disclaimer
- Severity: P3
- Kind: tokens
- Where: src/tobi508/tools/run_status.py, src/tobi508/models.py (`Outstanding`)
- What: with nothing left the result is `"status":"outstanding","runs":[],"running":[],"done":1,"started":[],"for_the_user":[]` plus a next_step and a TO DO block that say "Nothing left" (585 chars, 146 tokens; 908 with structured). The status word contradicts the message and an agent that keys on `status` may poll again. `finish=true` returned the identical result. The output schema for this tool is 11,197 chars (A-02) for a message this small.
- Evidence: `status.json`, `status_finish.json`.
- Fix: status `"complete"` when nothing is left; drop empty lists.
- Confidence: confirmed

## Unverified leads
- Whether Claude Code or other clients forward `structured_content` to the model as well as content: not measured, no client available here.
- Picture token counts are my estimate from pixel counts (width x height / 750 after the server's downscale), not from a tokenizer.
- The write-out half of T-01 assumes the model copies the files; a client with a "save resource" feature would avoid it.
- Round counts: only 2 answer rounds occurred; a page with follow-up questions (4.B) would show a third result I did not measure.
