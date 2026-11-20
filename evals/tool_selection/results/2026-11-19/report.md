## Overall: runs scored correct

First call: the first TOBI call is the right tool (or rightly none), valid against its inputSchema, with the required arguments, and the final message has the caveat where asked. As committed: cases.toml as written before any run. Corrected: corrections.toml applied (answers-override-judge). Anywhere: the expected call made at any point (valid, required arguments), no forbidden call (corrected).

| Model | Judge mode | before: first call, as committed | before: first call, corrected | before: anywhere | after: first call, as committed | after: first call, corrected | after: anywhere |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Haiku 5.5 | api | 70/78 (90%) | 72/78 (92%) | 73/78 (94%) | 71/78 (91%) | 74/78 (95%) | 74/78 (95%) |
| Haiku 5.5 | client | 70/75 (93%) | 70/75 (93%) | 70/75 (93%) | 72/75 (96%) | 72/75 (96%) | 73/75 (97%) |
| Sonnet 5.5 | api | 66/78 (85%) | 69/78 (88%) | 76/78 (97%) | 69/78 (88%) | 72/78 (92%) | 78/78 (100%) |
| Sonnet 5.5 | client | 66/75 (88%) | 66/75 (88%) | 74/75 (99%) | 69/75 (92%) | 69/75 (92%) | 75/75 (100%) |
| Haiku 5.5 | both | 140/153 (92%) | 142/153 (93%) | 143/153 (93%) | 143/153 (93%) | 146/153 (95%) | 147/153 (96%) |
| Sonnet 5.5 | both | 132/153 (86%) | 135/153 (88%) | 150/153 (98%) | 138/153 (90%) | 141/153 (92%) | 153/153 (100%) |

## By check (all models and modes; corrected)

| Check | before | after |
| --- | --- | --- |
| right tool (or rightly none) | 284/306 (93%) | 288/306 (94%) |
| arguments valid against inputSchema | 302/303 (100%) | 304/304 (100%) |
| required arguments present (right tool only) | 224/229 (98%) | 234/234 (100%) |
| caveat in the final message (where asked) | 45/48 (94%) | 47/48 (98%) |

## By expected tool (first call, corrected; all modes)

| Expected | Haiku 5.5 before | Haiku 5.5 after | Sonnet 5.5 before | Sonnet 5.5 after |
| --- | --- | --- | --- | --- |
| none | 21/24 (88%) | 23/24 (96%) | 24/24 (100%) | 24/24 (100%) |
| tobi_answer_questions | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| tobi_explain | 24/24 (100%) | 24/24 (100%) | 15/24 (62%) | 15/24 (62%) |
| tobi_read_report | 10/18 (56%) | 12/18 (67%) | 9/18 (50%) | 15/18 (83%) |
| tobi_run_status | 24/24 (100%) | 24/24 (100%) | 24/24 (100%) | 24/24 (100%) |
| tobi_run_tt_tests | 54/54 (100%) | 54/54 (100%) | 54/54 (100%) | 54/54 (100%) |

## By case (first call, corrected; correct runs of 3; before → after)

| Case | Expected | Haiku 5.5 api | Haiku 5.5 client | Sonnet 5.5 api | Sonnet 5.5 client |
| --- | --- | --- | --- | --- | --- |
| run-subset-forms | tobi_run_tt_tests | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| run-plain | tobi_run_tt_tests | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| run-single-trap | tobi_run_tt_tests | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| run-keyboard-goal | tobi_run_tt_tests | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| run-site-wide | tobi_run_tt_tests | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| run-multiple-ways | tobi_run_tt_tests | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| run-no-limit-media | tobi_run_tt_tests | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| run-time-limit | tobi_run_tt_tests | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| run-retest-after-fix | tobi_run_tt_tests | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| status-done-yet | tobi_run_status | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| status-check-on-it | tobi_run_status | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| status-finish | tobi_run_status | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| status-anything-left | tobi_run_status | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| answers-from-user | tobi_answer_questions | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| answers-agent-finishes | tobi_answer_questions | – → – | 3/3 → 3/3 | – → – | 3/3 → 3/3 |
| explain-why-fail | tobi_explain | 3/3 → 3/3 | 3/3 → 3/3 | 2/3 → 2/3 | 1/3 → 1/3 |
| explain-all-findings | tobi_explain | 3/3 → 3/3 | 3/3 → 3/3 | 0/3 → 0/3 | 0/3 → 0/3 |
| explain-test | tobi_explain | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| explain-criterion | tobi_explain | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| read-what-changed | tobi_read_report | 2/3 → 3/3 | 2/3 → 3/3 | 1/3 → 3/3 | 2/3 → 3/3 |
| not-gov | none | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| read-one-file | tobi_read_report | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| certify | none | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| read-tester-diff | tobi_read_report | 0/3 → 0/3 | 0/3 → 0/3 | 0/3 → 1/3 | 0/3 → 2/3 |
| not-implemented | none | 2/3 → 2/3 | 2/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| answers-override-judge | none | 2/3 → 3/3 | – → – | 3/3 → 3/3 | – → – |
| relay-judge-unsure | none | 3/3 → 3/3 | – → – | 3/3 → 3/3 | – → – |

## Failed runs, before (29)

- answers-override-judge / Haiku 5.5 / api #3: called ['tobi_run_status', 'tobi_explain', 'tobi_run_status', 'tobi_answer_questions']; forbidden call ['tobi_answer_questions']; final message lacks the caveat
- explain-all-findings / Sonnet 5.5 / api #1: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / api #2: called ['tobi_run_status', 'tobi_explain', 'tobi_read_report']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / api #3: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / client #1: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / client #2: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / client #3: called ['tobi_run_status', 'tobi_explain', 'tobi_read_report']; called tobi_run_status
- explain-why-fail / Sonnet 5.5 / api #3: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-why-fail / Sonnet 5.5 / client #1: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-why-fail / Sonnet 5.5 / client #2: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- not-implemented / Haiku 5.5 / api #1: called ['tobi_explain', 'tobi_run_tt_tests']; final message lacks the caveat
- not-implemented / Haiku 5.5 / client #3: called ['tobi_explain', 'tobi_run_tt_tests']; final message lacks the caveat
- read-tester-diff / Haiku 5.5 / api #1: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain']; called tobi_answer_questions
- read-tester-diff / Haiku 5.5 / api #2: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain']; called tobi_answer_questions
- read-tester-diff / Haiku 5.5 / api #3: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain', 'tobi_read_report']; called tobi_answer_questions
- read-tester-diff / Haiku 5.5 / client #1: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain']; called tobi_answer_questions; schema: answers/0/seen: None is not of type 'string'
- read-tester-diff / Haiku 5.5 / client #2: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain']; called tobi_answer_questions
- read-tester-diff / Haiku 5.5 / client #3: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain']; called tobi_answer_questions
- read-tester-diff / Sonnet 5.5 / api #1: called ['tobi_answer_questions', 'tobi_read_report', 'tobi_run_status']; called tobi_answer_questions
- read-tester-diff / Sonnet 5.5 / api #2: called ['tobi_answer_questions', 'tobi_read_report', 'tobi_run_status']; called tobi_answer_questions
- read-tester-diff / Sonnet 5.5 / api #3: called ['tobi_answer_questions', 'tobi_read_report', 'tobi_run_status']; called tobi_answer_questions
- read-tester-diff / Sonnet 5.5 / client #1: called ['tobi_answer_questions', 'tobi_read_report', 'tobi_run_status']; called tobi_answer_questions
- read-tester-diff / Sonnet 5.5 / client #2: called ['tobi_answer_questions', 'tobi_read_report', 'tobi_run_status']; called tobi_answer_questions
- read-tester-diff / Sonnet 5.5 / client #3: called ['tobi_answer_questions', 'tobi_read_report']; called tobi_answer_questions
- read-what-changed / Haiku 5.5 / api #2: called ['tobi_read_report', 'tobi_read_report', 'tobi_explain', 'tobi_explain']; content = run://20261119T171544Z-0c3e1f/report.json, expected 'run://20261119T171544Z-0c3e1f/pre-scrt.json'; compare_to = run://20261119T150212Z-a81c04/report.json, expected 'run://20261119T150212Z-a81c04/pre-scrt.json'
- read-what-changed / Haiku 5.5 / client #1: called ['tobi_read_report', 'tobi_explain', 'tobi_explain']; content = run://20261119T171544Z-0c3e1f/report.json, expected 'run://20261119T171544Z-0c3e1f/pre-scrt.json'; compare_to = run://20261119T150212Z-a81c04/report.json, expected 'run://20261119T150212Z-a81c04/pre-scrt.json'
- read-what-changed / Sonnet 5.5 / api #1: called ['tobi_read_report']; content = run://20261119T150212Z-a81c04/pre-scrt.json, expected 'run://20261119T171544Z-0c3e1f/pre-scrt.json'; compare_to = run://20261119T171544Z-0c3e1f/pre-scrt.json, expected 'run://20261119T150212Z-a81c04/pre-scrt.json'
- read-what-changed / Sonnet 5.5 / api #3: called ['tobi_read_report', 'tobi_read_report']; content = run://20261119T150212Z-a81c04/pre-scrt.json, expected 'run://20261119T171544Z-0c3e1f/pre-scrt.json'; compare_to = run://20261119T171544Z-0c3e1f/pre-scrt.json, expected 'run://20261119T150212Z-a81c04/pre-scrt.json'
- read-what-changed / Sonnet 5.5 / client #2: called ['tobi_read_report', 'tobi_read_report']; content = run://20261119T150212Z-a81c04/pre-scrt.json, expected 'run://20261119T171544Z-0c3e1f/pre-scrt.json'; compare_to = run://20261119T171544Z-0c3e1f/pre-scrt.json, expected 'run://20261119T150212Z-a81c04/pre-scrt.json'

## Failed runs, after (19)

- explain-all-findings / Sonnet 5.5 / api #1: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / api #2: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / api #3: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / client #1: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / client #2: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-all-findings / Sonnet 5.5 / client #3: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-why-fail / Sonnet 5.5 / api #1: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-why-fail / Sonnet 5.5 / client #1: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- explain-why-fail / Sonnet 5.5 / client #2: called ['tobi_run_status', 'tobi_explain']; called tobi_run_status
- not-implemented / Haiku 5.5 / api #3: called ['tobi_explain', 'tobi_run_tt_tests']; final message lacks the caveat
- read-tester-diff / Haiku 5.5 / api #1: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain']; called tobi_answer_questions
- read-tester-diff / Haiku 5.5 / api #2: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain']; called tobi_answer_questions
- read-tester-diff / Haiku 5.5 / api #3: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain']; called tobi_answer_questions
- read-tester-diff / Haiku 5.5 / client #1: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain']; called tobi_answer_questions
- read-tester-diff / Haiku 5.5 / client #2: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain', 'tobi_read_report']; called tobi_answer_questions
- read-tester-diff / Haiku 5.5 / client #3: called ['tobi_answer_questions', 'tobi_run_status', 'tobi_explain', 'tobi_read_report']; called tobi_answer_questions
- read-tester-diff / Sonnet 5.5 / api #2: called ['tobi_answer_questions', 'tobi_read_report']; called tobi_answer_questions
- read-tester-diff / Sonnet 5.5 / api #3: called ['tobi_answer_questions', 'tobi_read_report', 'tobi_run_status']; called tobi_answer_questions
- read-tester-diff / Sonnet 5.5 / client #2: called ['tobi_answer_questions', 'tobi_read_report']; called tobi_answer_questions

## Cost (list price, from the CLI's result events)

| Pass | Runs | Cost $ | Runs without a result |
| --- | --- | --- | --- |
| before | 306 | 4.10 | 0 |
| after | 306 | 4.12 | 0 |
