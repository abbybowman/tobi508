# Agent eval score: round2

Agent-assisted results scored against a tester's SCRT files. Not a certified Trusted Tester result.

Scored 2026-11-08T14:54:33.916333+00:00; lock commit e14580abc97deb1b5acccc1cb5fc7a122993445c; 10 of 10 pages have keys.

## arm-a-g1-1

RESULT line: found. Ended: completed. Wall time: 925.5 s (the efficiency figure: call durations include waits). Model calls: 21. Tool calls: {'mcp__a11y__tobi_run_tt_tests': 5, 'mcp__a11y__tobi_run_status': 21, 'mcp__a11y__tobi_answer_questions': 1, 'mcp__a11y__tobi_read_report': 3}.

Tokens by type: input 42, cache writes 75,912, cache reads 1,095,116, output 10,308. Cost at list price: $0.52. Usage window change: five hour +3%, seven day +1%.

Per WCAG 2.0 criterion (what the agent reported): weighted 34

- scored: 100
- agreement (of decided): 47/58
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 42/100
- false PASS: 1
- missed fail (Does Not Apply): 0
- false FAIL: 7
- Fail vs Does Not Apply: 0
- other mismatch: 3
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

Tool's own results, per TT test: weighted 38

- scored: 62
- agreement (of decided): 51/62
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 0/62
- false PASS: 1
- missed fail (Does Not Apply): 0
- false FAIL: 7
- Fail vs Does Not Apply: 0
- other mismatch: 3
- no answer given: 0
- not performed by the tool: 48
- no reference answer: 195

Why the tool left tests for review: could not be performed 227, open question 16

Tool's own results rolled up per criterion: weighted 31

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/cilab/ | 2.1.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/ | 3.3.2 | Pass | Fail | false_fail | Search text field (placeholder-only label) |
| https://svs.gsfc.nasa.gov/help/ | 3.3.2 | Pass | Fail | false_fail | Search text field (placeholder-only label) |
| https://svs.gsfc.nasa.gov/search/ | 3.3.2 | Pass | Fail | false_fail | Search text field (placeholder-only label) |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 1.3.1 | Pass | Fail | false_fail | unnamed buttons (4 instances) |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 3.3.2 | Pass | Fail | false_fail | Search text field (placeholder-only label) |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 4.1.2 | Pass | Fail | false_fail | unnamed buttons (4 instances) |
| https://svs.gsfc.nasa.gov/cilab/ | 2.4.5 | Pass | Fail | false_fail | no way found to reach the page; site search does not find it |
| https://svs.gsfc.nasa.gov/help/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/cilab/ | 3.2.3 | Pass | Does Not Apply | other_mismatch |  |

## arm-a-g2-1

RESULT line: found. Ended: completed. Wall time: 2054.2 s (the efficiency figure: call durations include waits). Model calls: 46. Tool calls: {'mcp__a11y__tobi_run_tt_tests': 5, 'mcp__a11y__tobi_run_status': 42, 'mcp__a11y__tobi_answer_questions': 8}.

Tokens by type: input 92, cache writes 156,853, cache reads 3,798,088, output 15,149. Cost at list price: $1.16. Usage window change: five hour +3%, seven day +1%.

Per WCAG 2.0 criterion (what the agent reported): weighted 16

- scored: 99
- agreement (of decided): 27/34
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 65/99
- false PASS: 2
- missed fail (Does Not Apply): 0
- false FAIL: 5
- Fail vs Does Not Apply: 0
- other mismatch: 0
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 1

Tool's own results, per TT test: weighted 14

- scored: 40
- agreement (of decided): 29/40
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 0/40
- false PASS: 2
- missed fail (Does Not Apply): 0
- false FAIL: 7
- Fail vs Does Not Apply: 0
- other mismatch: 2
- no answer given: 0
- not performed by the tool: 70
- no reference answer: 195

Why the tool left tests for review: could not be performed 265

Tool's own results rolled up per criterion: weighted 13

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/5340/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5144/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/14592/ | 3.3.2 | Pass | Fail | false_fail | #navbar_search_box (Search text field, placeholder-only label) |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.7 | Pass | Fail | false_fail | OVERVIEW (tab) in embedded app; button inside OVERVIEW tabpanel (#radix-:r3:-content-0 > div > div > button) |
| https://svs.gsfc.nasa.gov/5340/ | 3.3.2 | Pass | Fail | false_fail | #navbar_search_box (Search text field, placeholder-only label) |
| https://svs.gsfc.nasa.gov/5144/ | 3.3.2 | Pass | Fail | false_fail | #navbar_search_box (Search text field, placeholder-only label) |
| https://svs.gsfc.nasa.gov/4914/ | 3.3.2 | Pass | Fail | false_fail | #navbar_search_box (Search text field, placeholder-only label) |

## arm-a-pair1-2

RESULT line: found. Ended: completed. Wall time: 343.3 s (the efficiency figure: call durations include waits). Model calls: 7. Tool calls: {'mcp__a11y__tobi_run_tt_tests': 2, 'mcp__a11y__tobi_run_status': 7, 'mcp__a11y__tobi_answer_questions': 2}.

Tokens by type: input 14, cache writes 56,318, cache reads 171,524, output 4,994. Cost at list price: $0.29. Usage window change: five hour +1%, seven day +0%.

Per WCAG 2.0 criterion (what the agent reported): weighted 19

- scored: 40
- agreement (of decided): 22/25
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 15/40
- false PASS: 0
- missed fail (Does Not Apply): 0
- false FAIL: 2
- Fail vs Does Not Apply: 0
- other mismatch: 1
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

Tool's own results, per TT test: weighted 19

- scored: 25
- agreement (of decided): 22/25
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 0/25
- false PASS: 0
- missed fail (Does Not Apply): 0
- false FAIL: 2
- Fail vs Does Not Apply: 0
- other mismatch: 1
- no answer given: 0
- not performed by the tool: 19
- no reference answer: 78

Why the tool left tests for review: could not be performed 91, open question 6

Tool's own results rolled up per criterion: weighted 17

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/ | 3.3.2 | Pass | Fail | false_fail | Search text field (placeholder-only label) |
| https://svs.gsfc.nasa.gov/help/ | 3.3.2 | Pass | Fail | false_fail | Search text field (placeholder-only label) |
| https://svs.gsfc.nasa.gov/help/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |

## arm-a-pair2-2

RESULT line: found. Ended: completed. Wall time: 821.3 s (the efficiency figure: call durations include waits). Model calls: 24. Tool calls: {'mcp__a11y__tobi_run_tt_tests': 2, 'mcp__a11y__tobi_run_status': 19, 'mcp__a11y__tobi_answer_questions': 9}.

Tokens by type: input 48, cache writes 162,503, cache reads 1,662,842, output 12,175. Cost at list price: $0.94. Usage window change: five hour +3%, seven day +1%.

Per WCAG 2.0 criterion (what the agent reported): weighted 11

- scored: 40
- agreement (of decided): 16/21
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 19/40
- false PASS: 0
- missed fail (Does Not Apply): 0
- false FAIL: 4
- Fail vs Does Not Apply: 0
- other mismatch: 1
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

Tool's own results, per TT test: weighted 14

- scored: 24
- agreement (of decided): 19/24
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 0/24
- false PASS: 0
- missed fail (Does Not Apply): 0
- false FAIL: 4
- Fail vs Does Not Apply: 0
- other mismatch: 1
- no answer given: 0
- not performed by the tool: 20
- no reference answer: 78

Why the tool left tests for review: could not be performed 98

Tool's own results rolled up per criterion: weighted 10

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/search/ | 3.3.2 | Pass | Fail | false_fail | header Search text field (placeholder-only label) |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 1.3.1 | Pass | Fail | false_fail | four unnamed buttons (not identified by the tool) |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 3.3.2 | Pass | Fail | false_fail | header Search text field (placeholder-only label) |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 4.1.2 | Pass | Fail | false_fail | four unnamed buttons (not identified by the tool) |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |

## arm-a-pair3-2

RESULT line: found. Ended: completed. Wall time: 447.7 s (the efficiency figure: call durations include waits). Model calls: 12. Tool calls: {'mcp__a11y__tobi_run_tt_tests': 2, 'mcp__a11y__tobi_run_status': 10, 'mcp__a11y__tobi_answer_questions': 2}.

Tokens by type: input 24, cache writes 46,820, cache reads 308,197, output 6,008. Cost at list price: $0.28. Usage window change: five hour +0%, seven day +1%.

Per WCAG 2.0 criterion (what the agent reported): weighted 9

- scored: 39
- agreement (of decided): 16/19
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 20/39
- false PASS: 1
- missed fail (Does Not Apply): 1
- false FAIL: 1
- Fail vs Does Not Apply: 0
- other mismatch: 0
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 1

Tool's own results, per TT test: weighted 0

- scored: 34
- agreement (of decided): 20/34
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 0/34
- false PASS: 1
- missed fail (Does Not Apply): 2
- false FAIL: 5
- Fail vs Does Not Apply: 0
- other mismatch: 6
- no answer given: 0
- not performed by the tool: 10
- no reference answer: 78

Why the tool left tests for review: could not be performed 88

Tool's own results rolled up per criterion: weighted -4

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/cilab/ | 2.1.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/cilab/ | 2.4.1 | Fail | Does Not Apply | missed_fail |  |
| https://svs.gsfc.nasa.gov/14592/ | 3.3.2 | Pass | Fail | false_fail | Search... text field (placeholder-only label) |

## arm-a-pair4-2

RESULT line: found. Ended: completed. Wall time: 1709.6 s (the efficiency figure: call durations include waits). Model calls: 35. Tool calls: {'mcp__a11y__tobi_run_tt_tests': 2, 'mcp__a11y__tobi_run_status': 38}.

Tokens by type: input 70, cache writes 51,963, cache reads 1,120,852, output 6,774. Cost at list price: $0.39. Usage window change: five hour +1%, seven day +0%.

Per WCAG 2.0 criterion (what the agent reported): weighted 3

- scored: 40
- agreement (of decided): 14/21
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 19/40
- false PASS: 2
- missed fail (Does Not Apply): 0
- false FAIL: 5
- Fail vs Does Not Apply: 0
- other mismatch: 0
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

Tool's own results, per TT test: weighted 3

- scored: 21
- agreement (of decided): 14/21
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 0/21
- false PASS: 2
- missed fail (Does Not Apply): 0
- false FAIL: 4
- Fail vs Does Not Apply: 0
- other mismatch: 1
- no answer given: 0
- not performed by the tool: 23
- no reference answer: 78

Why the tool left tests for review: could not be performed 96, open question 5

Tool's own results rolled up per criterion: weighted 2

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/5340/ | 2.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/14194/ | 1.3.1 | Pass | Fail | false_fail | unnamed button |
| https://svs.gsfc.nasa.gov/14194/ | 3.3.2 | Pass | Fail | false_fail | Search text field (#navbar_search_box) |
| https://svs.gsfc.nasa.gov/14194/ | 4.1.2 | Pass | Fail | false_fail | unnamed button |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.7 | Pass | Fail | false_fail | OVERVIEW (tab); #radix-\:r3\:-content-0 > div > div > button |
| https://svs.gsfc.nasa.gov/5340/ | 3.3.2 | Pass | Fail | false_fail | Search text field (#navbar_search_box) |

## arm-a-pair5-2

RESULT line: found. Ended: completed. Wall time: 1287.2 s (the efficiency figure: call durations include waits). Model calls: 29. Tool calls: {'mcp__a11y__tobi_run_tt_tests': 2, 'mcp__a11y__tobi_run_status': 37, 'mcp__a11y__tobi_answer_questions': 4, 'mcp__a11y__tobi_explain': 2}.

Tokens by type: input 58, cache writes 108,845, cache reads 1,217,366, output 10,299. Cost at list price: $0.66. Usage window change: five hour +3%, seven day +0%.

Per WCAG 2.0 criterion (what the agent reported): weighted 14

- scored: 40
- agreement (of decided): 19/22
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 18/40
- false PASS: 1
- missed fail (Does Not Apply): 0
- false FAIL: 2
- Fail vs Does Not Apply: 0
- other mismatch: 0
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

Tool's own results, per TT test: weighted 17

- scored: 25
- agreement (of decided): 22/25
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 0/25
- false PASS: 1
- missed fail (Does Not Apply): 0
- false FAIL: 2
- Fail vs Does Not Apply: 0
- other mismatch: 0
- no answer given: 0
- not performed by the tool: 19
- no reference answer: 78

Why the tool left tests for review: could not be performed 97

Tool's own results rolled up per criterion: weighted 16

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/5144/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5144/ | 3.3.2 | Pass | Fail | false_fail | Search... text field (placeholder only) |
| https://svs.gsfc.nasa.gov/4914/ | 3.3.2 | Pass | Fail | false_fail | Search... text field (placeholder only) |

## arm-b-g1-1

RESULT line: found. Ended: completed. Wall time: 102.8 s (the efficiency figure: call durations include waits). Model calls: 10. Tool calls: {'mcp__browser__browser_navigate': 6, 'mcp__browser__browser_evaluate': 10, 'mcp__browser__browser_take_screenshot': 2, 'mcp__browser__browser_click': 1}.

Tokens by type: input 20, cache writes 47,258, cache reads 287,702, output 12,075. Cost at list price: $0.34. Usage window change: five hour +1%, seven day +0%.

Per WCAG 2.0 criterion (what the agent reported): weighted 39

- scored: 100
- agreement (of decided): 68/81
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 19/100
- false PASS: 8
- missed fail (Does Not Apply): 0
- false FAIL: 0
- Fail vs Does Not Apply: 0
- other mismatch: 5
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/ | 1.3.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/ | 2.4.5 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/ | 4.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/help/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/help/ | 2.4.5 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/search/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/ | 2.3.1 | Does Not Apply | Pass | other_mismatch |  |
| https://svs.gsfc.nasa.gov/help/ | 2.3.1 | Does Not Apply | Pass | other_mismatch |  |
| https://svs.gsfc.nasa.gov/search/ | 2.3.1 | Does Not Apply | Pass | other_mismatch |  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.3.1 | Does Not Apply | Pass | other_mismatch |  |
| https://svs.gsfc.nasa.gov/cilab/ | 1.4.2 | Does Not Apply | Pass | other_mismatch |  |

## arm-b-g2-1

RESULT line: found. Ended: completed. Wall time: 55.6 s (the efficiency figure: call durations include waits). Model calls: 6. Tool calls: {'mcp__browser__browser_navigate': 2, 'mcp__browser__browser_evaluate': 4}.

Tokens by type: input 12, cache writes 13,573, cache reads 97,464, output 6,594. Cost at list price: $0.13. Usage window change: five hour +1%, seven day +0%.

Per WCAG 2.0 criterion (what the agent reported): weighted 11

- scored: 99
- agreement (of decided): 49/63
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 36/99
- false PASS: 11
- missed fail (Does Not Apply): 1
- false FAIL: 0
- Fail vs Does Not Apply: 0
- other mismatch: 2
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 1

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/14194/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 1.3.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 4.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5144/ | 1.3.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5144/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5144/ | 4.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/4914/ | 1.3.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/4914/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/4914/ | 4.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/14194/ | 2.2.2 | Fail | Does Not Apply | missed_fail |  |
| https://svs.gsfc.nasa.gov/5340/ | 3.3.1 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/5340/ | 3.3.3 | Pass | Does Not Apply | other_mismatch |  |

## arm-b-pair1-2

RESULT line: found. Ended: completed. Wall time: 52.6 s (the efficiency figure: call durations include waits). Model calls: 5. Tool calls: {'mcp__browser__browser_navigate': 2, 'mcp__browser__browser_evaluate': 4, 'mcp__browser__browser_press_key': 1}.

Tokens by type: input 10, cache writes 20,893, cache reads 104,536, output 4,246. Cost at list price: $0.14. Usage window change: five hour +1%, seven day +0%.

Per WCAG 2.0 criterion (what the agent reported): weighted 3

- scored: 40
- agreement (of decided): 24/33
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 7/40
- false PASS: 6
- missed fail (Does Not Apply): 0
- false FAIL: 0
- Fail vs Does Not Apply: 0
- other mismatch: 3
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/ | 1.3.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/ | 2.4.5 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/ | 4.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/help/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/help/ | 2.4.5 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/ | 2.3.1 | Does Not Apply | Pass | other_mismatch |  |
| https://svs.gsfc.nasa.gov/help/ | 2.2.2 | Does Not Apply | Pass | other_mismatch |  |
| https://svs.gsfc.nasa.gov/help/ | 2.3.1 | Does Not Apply | Pass | other_mismatch |  |

## arm-b-pair2-2

RESULT line: found. Ended: completed. Wall time: 43.6 s (the efficiency figure: call durations include waits). Model calls: 3. Tool calls: {'mcp__browser__browser_navigate': 2, 'mcp__browser__browser_evaluate': 2}.

Tokens by type: input 6, cache writes 21,368, cache reads 52,448, output 4,204. Cost at list price: $0.13. Usage window change: five hour +1%, seven day +0%.

Per WCAG 2.0 criterion (what the agent reported): weighted 18

- scored: 40
- agreement (of decided): 24/26
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 14/40
- false PASS: 2
- missed fail (Does Not Apply): 0
- false FAIL: 0
- Fail vs Does Not Apply: 0
- other mismatch: 0
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/search/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.4.1 | Fail | Pass | false_pass |  |

## arm-b-pair3-2

RESULT line: found. Ended: completed. Wall time: 53.0 s (the efficiency figure: call durations include waits). Model calls: 6. Tool calls: {'mcp__browser__browser_navigate': 1, 'mcp__browser__browser_tabs': 3, 'mcp__browser__browser_snapshot': 2, 'mcp__browser__browser_evaluate': 3, 'mcp__browser__browser_take_screenshot': 2}.

Tokens by type: input 12, cache writes 24,892, cache reads 91,288, output 4,269. Cost at list price: $0.15. Usage window change: five hour +1%, seven day +0%.

Per WCAG 2.0 criterion (what the agent reported): weighted 9

- scored: 39
- agreement (of decided): 16/21
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 18/39
- false PASS: 0
- missed fail (Does Not Apply): 1
- false FAIL: 0
- Fail vs Does Not Apply: 0
- other mismatch: 4
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 1

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/cilab/ | 2.4.1 | Fail | Does Not Apply | missed_fail |  |
| https://svs.gsfc.nasa.gov/cilab/ | 1.4.2 | Does Not Apply | Pass | other_mismatch |  |
| https://svs.gsfc.nasa.gov/cilab/ | 2.2.2 | Does Not Apply | Pass | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 1.4.2 | Does Not Apply | Pass | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 2.2.2 | Does Not Apply | Pass | other_mismatch |  |

## arm-b-pair4-2

RESULT line: found. Ended: completed. Wall time: 39.7 s (the efficiency figure: call durations include waits). Model calls: 3. Tool calls: {'mcp__browser__browser_navigate': 2, 'mcp__browser__browser_evaluate': 2}.

Tokens by type: input 6, cache writes 9,311, cache reads 40,398, output 3,557. Cost at list price: $0.08. Usage window change: five hour +1%, seven day +1%.

Per WCAG 2.0 criterion (what the agent reported): weighted 7

- scored: 40
- agreement (of decided): 16/19
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 21/40
- false PASS: 2
- missed fail (Does Not Apply): 1
- false FAIL: 0
- Fail vs Does Not Apply: 0
- other mismatch: 0
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/14194/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/14194/ | 2.2.2 | Fail | Does Not Apply | missed_fail |  |

## arm-b-pair5-2

RESULT line: found. Ended: completed. Wall time: 54.1 s (the efficiency figure: call durations include waits). Model calls: 5. Tool calls: {'mcp__browser__browser_navigate': 2, 'mcp__browser__browser_snapshot': 1, 'mcp__browser__browser_evaluate': 2}.

Tokens by type: input 10, cache writes 23,362, cache reads 98,888, output 3,839. Cost at list price: $0.14. Usage window change: five hour +1%, seven day +0%.

Per WCAG 2.0 criterion (what the agent reported): weighted 3

- scored: 40
- agreement (of decided): 19/25
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 15/40
- false PASS: 5
- missed fail (Does Not Apply): 0
- false FAIL: 0
- Fail vs Does Not Apply: 0
- other mismatch: 1
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 0

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/5144/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5144/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/4914/ | 1.3.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/4914/ | 2.4.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/4914/ | 4.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/4914/ | 1.4.2 | Does Not Apply | Pass | other_mismatch |  |
