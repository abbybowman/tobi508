# Agent eval score: round2-armc

Agent-assisted results scored against a tester's SCRT files. Not a certified Trusted Tester result.

Scored 2026-11-08T14:55:24.413087+00:00; lock commit e14580abc97deb1b5acccc1cb5fc7a122993445c; 10 of 10 pages have keys.

## arm-c-1

RESULT line: found. Ended: completed. Wall time: 458.3 s (the efficiency figure: call durations include waits). Model calls: None. Tool calls: None.

Tokens by type: input 388, output 72,438, cache reads 232,795, cache writes 1,475,327. Cost at list price: $6.65. Usage window change: not reported.

Per WCAG 2.0 criterion (what the agent reported): weighted 29

- scored: 199
- agreement (of decided): 84/127
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 72/199
- false PASS: 4
- missed fail (Does Not Apply): 2
- false FAIL: 29
- Fail vs Does Not Apply: 0
- other mismatch: 8
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 1

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/cilab/ | 2.1.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 2.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5144/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/cilab/ | 2.4.1 | Fail | Does Not Apply | missed_fail |  |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.1 | Fail | Does Not Apply | missed_fail |  |
| https://svs.gsfc.nasa.gov/ | 2.1.1 | Pass | Fail | false_fail | 4.A: Some things on this page work with a mouse but not with the keyboard, so keyboard users cannot use them. "NASA Science Category: Universe" (link) works with a m; 4.A: ; 4.A: Screenshot left out t |
| https://svs.gsfc.nasa.gov/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't ; 4.F: ; 4.F: ; 4.F: ; 4.F:  |
| https://svs.gsfc.nasa.gov/ | 3.2.4 | Pass | Fail | false_fail | 9.C: Some links or controls that do the same thing have different names on different pages: "NASA satellites provide data on Earth's land, ecosystems, water, air tem; 9.C:  |
| https://svs.gsfc.nasa.gov/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/help/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't ; 4.F:  |
| https://svs.gsfc.nasa.gov/help/ | 3.2.4 | Pass | Fail | false_fail | 9.C: Some links or controls that do the same thing have different names on different pages: "https://svs.gsfc.nasa.gov/new/gallery/Open this url in a new tab" here a; 9.C:  |
| https://svs.gsfc.nasa.gov/help/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/search/ | 2.1.1 | Pass | Fail | false_fail | 4.A: Some things on this page work with a mouse but not with the keyboard, so keyboard users cannot use them. "(RSS)" (link) has extra information that shows only wh; 4.A: ; 4.A: Screenshot left out t |
| https://svs.gsfc.nasa.gov/search/ | 2.4.5 | Pass | Fail | false_fail | 19.A: We found only links from other pages to reach this page, and nothing else to check. The site search did not find this page when searching for its heading. Add a |
| https://svs.gsfc.nasa.gov/search/ | 2.4.6 | Pass | Fail | false_fail | 5.B: Some labels do not say what to enter or what the button does: the field next to "(RSS)". |
| https://svs.gsfc.nasa.gov/search/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 1.3.1 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name; 5.C: ; 5.C: ; 5.C:  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 4.1.2 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name; 5.C: ; 5.C: ; 5.C:  |
| https://svs.gsfc.nasa.gov/14592/ | 1.3.1 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.5 | Pass | Fail | false_fail | 19.A: We found only no way to reach this page, and nothing else to check. The site search did not find this page when searching for its heading. Add a second way, suc |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.7 | Pass | Fail | false_fail | 4.D: Some elements don't show when they have keyboard focus, so keyboard users can lose track of where they are. We could not get a clear before-and-after view of "S; 4.D: ; 4.D: ; 4.D: ; 4.D: ; 4.D:  |
| https://svs.gsfc.nasa.gov/14592/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/14592/ | 4.1.2 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/14194/ | 1.3.1 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/14194/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/14194/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/14194/ | 4.1.2 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.7 | Pass | Fail | false_fail | 4.D: Some elements don't show when they have keyboard focus, so keyboard users can lose track of where they are. We could not get a clear before-and-after view of "S; 4.D: ; 4.D: ; 4.D: ; 4.D: ; 4.D:  |
| https://svs.gsfc.nasa.gov/5340/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/5144/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/5144/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/help/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/cilab/ | 3.2.3 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/cilab/ | 3.2.4 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 3.2.3 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 3.2.4 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14194/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |

## arm-c-2

RESULT line: found. Ended: completed. Wall time: 467.3 s (the efficiency figure: call durations include waits). Model calls: None. Tool calls: None.

Tokens by type: input 388, output 72,344, cache reads 1,599,342, cache writes 108,744. Cost at list price: $1.32. Usage window change: not reported.

Per WCAG 2.0 criterion (what the agent reported): weighted 30

- scored: 199
- agreement (of decided): 84/126
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 73/199
- false PASS: 4
- missed fail (Does Not Apply): 2
- false FAIL: 28
- Fail vs Does Not Apply: 0
- other mismatch: 8
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 1

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/cilab/ | 2.1.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 2.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5144/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/cilab/ | 2.4.1 | Fail | Does Not Apply | missed_fail |  |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.1 | Fail | Does Not Apply | missed_fail |  |
| https://svs.gsfc.nasa.gov/ | 2.1.1 | Pass | Fail | false_fail | 4.A: Some things on this page work with a mouse but not with the keyboard, so keyboard users cannot use them. "NASA Science Category: Universe" (link) works with a m; 4.A: ; 4.A: Screenshot left out t |
| https://svs.gsfc.nasa.gov/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't ; 4.F: ; 4.F: ; 4.F: ; 4.F:  |
| https://svs.gsfc.nasa.gov/ | 3.2.4 | Pass | Fail | false_fail | 9.C: Some links or controls that do the same thing have different names on different pages: "NASA satellites provide data on Earth's land, ecosystems, water, air tem; 9.C:  |
| https://svs.gsfc.nasa.gov/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/help/ | 3.2.4 | Pass | Fail | false_fail | 9.C: Some links or controls that do the same thing have different names on different pages: "https://svs.gsfc.nasa.gov/new/gallery/Open this url in a new tab" here a; 9.C:  |
| https://svs.gsfc.nasa.gov/help/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/search/ | 2.1.1 | Pass | Fail | false_fail | 4.A: Some things on this page work with a mouse but not with the keyboard, so keyboard users cannot use them. "(RSS)" (link) has extra information that shows only wh; 4.A: ; 4.A: Screenshot left out t |
| https://svs.gsfc.nasa.gov/search/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/search/ | 2.4.5 | Pass | Fail | false_fail | 19.A: We found only links from other pages to reach this page, and nothing else to check. The site search did not find this page when searching for its heading. Add a |
| https://svs.gsfc.nasa.gov/search/ | 2.4.6 | Pass | Fail | false_fail | 5.B: Some labels do not say what to enter or what the button does: the field next to "(RSS)"; the button labelled "Sort by:".; 5.B:  |
| https://svs.gsfc.nasa.gov/search/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 1.3.1 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name; 5.C: ; 5.C: ; 5.C:  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 4.1.2 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name; 5.C: ; 5.C: ; 5.C:  |
| https://svs.gsfc.nasa.gov/14592/ | 1.3.1 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.5 | Pass | Fail | false_fail | 19.A: We found only no way to reach this page, and nothing else to check. The site search did not find this page when searching for its heading. Add a second way, suc |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.7 | Pass | Fail | false_fail | 4.D: Some elements don't show when they have keyboard focus, so keyboard users can lose track of where they are. We could not get a clear before-and-after view of "S; 4.D: ; 4.D: ; 4.D: ; 4.D: ; 4.D:  |
| https://svs.gsfc.nasa.gov/14592/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/14592/ | 4.1.2 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/14194/ | 1.3.1 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/14194/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/14194/ | 4.1.2 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.7 | Pass | Fail | false_fail | 4.D: Some elements don't show when they have keyboard focus, so keyboard users can lose track of where they are. We could not get a clear before-and-after view of "S; 4.D: ; 4.D: ; 4.D: ; 4.D: ; 4.D:  |
| https://svs.gsfc.nasa.gov/5340/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/5144/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/5144/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/help/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/cilab/ | 3.2.3 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/cilab/ | 3.2.4 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 3.2.3 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 3.2.4 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14194/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |

## arm-c-3

RESULT line: found. Ended: completed. Wall time: 453.5 s (the efficiency figure: call durations include waits). Model calls: None. Tool calls: None.

Tokens by type: input 388, output 71,340, cache reads 1,599,342, cache writes 108,705. Cost at list price: $1.31. Usage window change: not reported.

Per WCAG 2.0 criterion (what the agent reported): weighted 31

- scored: 199
- agreement (of decided): 84/125
- validated catches (the tester confirmed the tool): 0
- needs review (of scored): 74/199
- false PASS: 4
- missed fail (Does Not Apply): 2
- false FAIL: 27
- Fail vs Does Not Apply: 0
- other mismatch: 8
- no answer given: 0
- not performed by the tool: 0
- no reference answer: 1

| Page | Criterion | Key | Arm | Verdict | Elements |
| --- | --- | --- | --- | --- | --- |
| https://svs.gsfc.nasa.gov/cilab/ | 2.1.1 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 2.1.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5340/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/5144/ | 3.2.2 | Fail | Pass | false_pass |  |
| https://svs.gsfc.nasa.gov/cilab/ | 2.4.1 | Fail | Does Not Apply | missed_fail |  |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.1 | Fail | Does Not Apply | missed_fail |  |
| https://svs.gsfc.nasa.gov/ | 2.1.1 | Pass | Fail | false_fail | 4.A: Some things on this page work with a mouse but not with the keyboard, so keyboard users cannot use them. "NASA Science Category: Earth" (link) works with a mous; 4.A: ; 4.A: Screenshot left out t |
| https://svs.gsfc.nasa.gov/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't ; 4.F: ; 4.F: ; 4.F: ; 4.F:  |
| https://svs.gsfc.nasa.gov/ | 3.2.4 | Pass | Fail | false_fail | 9.C: Some links or controls that do the same thing have different names on different pages: "NASA satellites provide data on Earth's land, ecosystems, water, air tem; 9.C:  |
| https://svs.gsfc.nasa.gov/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/help/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't ; 4.F:  |
| https://svs.gsfc.nasa.gov/help/ | 3.2.4 | Pass | Fail | false_fail | 9.C: Some links or controls that do the same thing have different names on different pages: "https://svs.gsfc.nasa.gov/new/gallery/Open this url in a new tab" here a; 9.C:  |
| https://svs.gsfc.nasa.gov/help/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/search/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/search/ | 2.4.5 | Pass | Fail | false_fail | 19.A: We found only links from other pages to reach this page, and nothing else to check. The site search did not find this page when searching for its heading. Add a |
| https://svs.gsfc.nasa.gov/search/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 1.3.1 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name; 5.C: ; 5.C: ; 5.C:  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 4.1.2 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name; 5.C: ; 5.C: ; 5.C:  |
| https://svs.gsfc.nasa.gov/14592/ | 1.3.1 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.5 | Pass | Fail | false_fail | 19.A: We found only no way to reach this page, and nothing else to check. The site search did not find this page when searching for its heading. Add a second way, suc |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.7 | Pass | Fail | false_fail | 4.D: Some elements don't show when they have keyboard focus, so keyboard users can lose track of where they are. We could not get a clear before-and-after view of "S; 4.D: ; 4.D: ; 4.D: ; 4.D: ; 4.D:  |
| https://svs.gsfc.nasa.gov/14592/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/14592/ | 4.1.2 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/14194/ | 1.3.1 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/14194/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/14194/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/14194/ | 4.1.2 | Pass | Fail | false_fail | 5.C: Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. an unnamed button has no name |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/5340/ | 2.4.7 | Pass | Fail | false_fail | 4.D: Some elements don't show when they have keyboard focus, so keyboard users can lose track of where they are. We could not get a clear before-and-after view of "S; 4.D: ; 4.D: ; 4.D: ; 4.D: ; 4.D:  |
| https://svs.gsfc.nasa.gov/5340/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/5144/ | 2.4.3 | Pass | Fail | false_fail | 4.F: Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus order doesn't  |
| https://svs.gsfc.nasa.gov/5144/ | 3.3.2 | Pass | Fail | false_fail | 5.A: Some form fields have no label or instructions people can see, so a person may not know what to enter. "Search" (text field)'s only label is the gray example te |
| https://svs.gsfc.nasa.gov/help/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/gallery/the-galleries/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/cilab/ | 3.2.3 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/cilab/ | 3.2.4 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 3.2.3 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14592/ | 3.2.4 | Pass | Does Not Apply | other_mismatch |  |
| https://svs.gsfc.nasa.gov/14194/ | 2.4.6 | Pass | Does Not Apply | other_mismatch |  |
