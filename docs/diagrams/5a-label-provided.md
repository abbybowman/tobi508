# How TOBI runs Test 5.A (Label provided)

For a Trusted Tester who wants to check TOBI's approach to 5.A without
reading Python. The rules themselves are in
[specs/rules/5a-label-provided.md](../../specs/rules/5a-label-provided.md)
(spec 1.15.0). Row IDs in brackets, such as [M3], point to rows there. The
diagrams follow the rules spec; when they disagree, the spec is right.

TOBI's results are agent-assisted. They are not a certified Trusted Tester
result.

**How to read the diagrams.** Every box starts with a word that says what
kind of step it is. The colours repeat that word, so the diagrams can be read
without them.

| Word | Meaning |
| --- | --- |
| BROWSER | Done in real Chrome, on a recording of the page |
| RULE | A fixed check in TOBI's code. It decides the same way every time |
| QUESTION | An open question that a model answers by looking at a picture. The answer is a fact for a rule, never an outcome |
| PASS, FAIL, DNA, REVIEW | An outcome. REVIEW is NEEDS REVIEW: "This test could not be performed", plus the reason |
| LIMIT | Something TOBI knows it cannot do. The outcome becomes REVIEW, so a person checks it |
| GAP | Something TOBI can miss without saying so. These are the places to check by hand |

## 1. What happens in the browser

TOBI records the page once. Every later step works on that recording, so a
rerun reads the same page. The steps after the recording are shared with
other tests. 5.A reuses pass L, which 5.C also uses.

```mermaid
flowchart TD
    accTitle: 5.A, part 1, what happens in the browser
    accDescr: The page is recorded once in Chrome. On the recording, TOBI walks the page with Tab and Shift+Tab, opens menus, tabs and accordions, and counts every form field. Then pass L loads the page fresh, focuses each data-entry field, and records its visible label, nearby text, placeholder, nearby buttons and a picture. Limits and gaps hang off the steps they affect.

    REC["BROWSER: record the page once in Chrome<br/>Every later step replays this recording"]
    WALK["BROWSER: keyboard walk<br/>Tab through the page, then Shift+Tab back<br/>Counts the fields the walk reached"]
    REVEAL["BROWSER: open what opens<br/>Menus, tabs, accordions and filters the walk found,<br/>each on a fresh load: Enter first, then a click.<br/>Inside opened content, ticks up to 2 options per checkbox or radio set<br/>and reads the page again"]
    COUNT["BROWSER: count every form field on the page<br/>including ones inside web components, inside frames,<br/>hidden at load, and editable text areas"]
    PASSL["BROWSER: pass L, a fresh load after the walk<br/>Lists every form field and button.<br/>Frames are each opened as a page of their own and read the same way"]
    FIELD["BROWSER: for each field that takes input<br/>(not buttons, not read-only, not disabled)<br/>Focus the field so focus-only tips and floating labels show, then record:<br/>1. its label, aria-labelledby text or group legend, and whether a person can see it<br/>2. its placeholder<br/>3. the visible text around it, nearest first<br/>4. the buttons beside it that act on its form<br/>5. a picture: the field plus 240 px left, 120 px up, 160 px right and down"]
    VIS["RULE: what counts as a label a person can see<br/>Rendered, at least 4 x 4 px, not clipped to 1 px,<br/>opacity above 0.1, inside the picture, and has a word<br/>(a lone * does not count)"]

    REC --> WALK --> REVEAL --> COUNT --> PASSL --> FIELD
    FIELD --- VIS

    L1["LIMIT: more than 60 fields and buttons<br/>Only the first 60 are checked"]
    L2["LIMIT: more than 10 frames, or a frame that<br/>cannot be opened or was not recorded"]
    L3["LIMIT: a menu or section that would not open,<br/>or more than 20 of them"]
    G1["GAP: fields that only appear after a step the run does not take<br/>(submitting the form, a later page of a wizard)<br/>are never seen or counted"]
    G2["GAP: fields inside closed shadow roots<br/>are neither read nor counted"]
    G3["GAP: the visibility check does not look at colour<br/>Light grey text on white, or white on white,<br/>counts as a label a person can see"]
    G4["GAP: a recording can miss scripts the page loads later<br/>Fields those scripts would draw are not on the replay"]

    PASSL -.-> L1
    PASSL -.-> L2
    REVEAL -.-> L3
    REVEAL -.-> G1
    COUNT -.-> G2
    VIS -.-> G3
    REC -.-> G4

    classDef browser fill:#eef2f7,stroke:#4a5a70,color:#111
    classDef rule fill:#e3effc,stroke:#1f5fa8,color:#111
    classDef limit fill:#fff4d6,stroke:#a86b00,color:#111,stroke-dasharray:4 3
    classDef gap fill:#fde4e1,stroke:#b3261e,color:#111,stroke-width:2px,stroke-dasharray:6 3
    class REC,WALK,REVEAL,COUNT,PASSL,FIELD browser
    class VIS rule
    class L1,L2,L3 limit
    class G1,G2,G3,G4 gap
```

## 2. Each field

Each field that takes input is checked separately. Each radio button and
each checkbox counts as a field of its own. Rules run top to bottom and the
first one that matches decides. A model is asked only when no rule could
decide.

```mermaid
flowchart TD
    accTitle: 5.A, part 2, how each field is decided
    accDescr: Rules run in order. Field not readable gives REVIEW. A visible label with a word gives PASS. An option in a set with nothing beside it but the question gives FAIL. A field with a button in its own group gives PASS. A field whose only text is its placeholder gives FAIL. Otherwise a model is asked whether it can see a label in the picture. Labeled with a quote that is found in the page text, or a picture label, gives PASS. Not labeled gives FAIL. Unsure, or a quote not found, gives REVIEW.

    START(["A field that takes input"])
    M1{"RULE [M1]<br/>Could the field be focused,<br/>read and pictured?"}
    M2{"RULE [M2]<br/>Does it have a label of its own<br/>a person can see, with a word in it?"}
    M2o{"RULE [M2o]<br/>Is it one radio button or checkbox among several,<br/>with nothing beside it but the set's question<br/>(no words, no picture)?"}
    M2i{"RULE [M2i]<br/>Is there a button in the field's own group or search form<br/>(a magnifier icon, Go)?"}
    M3{"RULE [M3]<br/>Is its only text its placeholder,<br/>with no button beside it that acts on its form?"}
    J1[["QUESTION [J1]: can people see a label or instructions for this field?<br/>The model is given:<br/>the picture with the field focused, the field's kind,<br/>its placeholder (marked: does not count),<br/>the visible text around it (marked as untrusted page text),<br/>labels of nearby fields, buttons beside it,<br/>and, for an option in a set, the set's question (marked: does not label the option)<br/>It is NOT given the accessible name: a name nobody can see is not a label<br/>Answers: labeled + the words, graphic + what it shows, not labeled, unsure"]]
    WHO["Who answers: TOBI's own pinned model if one is set up,<br/>otherwise the AI agent that called TOBI.<br/>A person's answer replaces either."]
    QOK{"RULE [M4]<br/>Labeled: are the quoted words really in<br/>the page's visible text, with a word in them?<br/>Graphic: accepted as answered"}

    R1["REVIEW [M1]"]
    P2["PASS [M2]"]
    F2o["FAIL [M2o]<br/>a person cannot tell the choices apart"]
    P2i["PASS [M2i]<br/>whether the icon or word fits the field is 5.B"]
    F3["FAIL [M3]<br/>a placeholder disappears once typing starts"]
    P4["PASS [M4]"]
    F5["FAIL [M5]<br/>J1 said not labeled"]
    R6["REVIEW [M6]<br/>J1 unsure, or its quote was not found"]

    START --> M1
    M1 -- no --> R1
    M1 -- yes --> M2
    M2 -- yes --> P2
    M2 -- no --> M2o
    M2o -- yes --> F2o
    M2o -- no --> M2i
    M2i -- yes --> P2i
    M2i -- no --> M3
    M3 -- yes --> F3
    M3 -- no --> J1
    J1 --- WHO
    J1 -- labeled or graphic --> QOK
    QOK -- yes --> P4
    QOK -- no --> R6
    J1 -- not labeled --> F5
    J1 -- unsure --> R6

    G5["GAP: the model sees only the cropped picture<br/>A label farther away (a heading over a long form,<br/>instructions at the top) is outside it.<br/>The likely result is unsure, but a not labeled answer gives a FAIL"]
    G6["GAP: a graphic answer leads to PASS on the model's word alone.<br/>No rule confirms what the picture shows"]
    G7["GAP: any button in the field's own group counts as its label<br/>(a decision, Abby, 2026-11-13). A clear button with an X alone passes 5.A.<br/>5.B judges whether it describes the field"]
    G8["GAP: a picture near the field but outside its form or group<br/>(a logo beside a search box) is not counted, so M3 can FAIL<br/>a field a tester would pass"]

    J1 -.-> G5
    QOK -.-> G6
    M2i -.-> G7
    M3 -.-> G8

    classDef rule fill:#e3effc,stroke:#1f5fa8,color:#111
    classDef question fill:#efe6fb,stroke:#6a3fb5,color:#111,stroke-width:2px
    classDef pass fill:#e2f4e6,stroke:#1e7a35,color:#111
    classDef fail fill:#fde4e1,stroke:#b3261e,color:#111
    classDef review fill:#fff4d6,stroke:#a86b00,color:#111
    classDef gap fill:#fde4e1,stroke:#b3261e,color:#111,stroke-width:2px,stroke-dasharray:6 3
    classDef note fill:#ffffff,stroke:#888,color:#111
    class M1,M2,M2o,M2i,M3,QOK rule
    class J1 question
    class P2,P2i,P4 pass
    class F2o,F3,F5 fail
    class R1,R6 review
    class G5,G6,G7,G8 gap
    class START,WHO note
```

## 3. The page's outcome

The answers for the separate fields become one 5.A outcome for the page.
Two guards then check whether TOBI read everything it should have. A guard
can only move PASS (and, for one guard, DNA) to REVIEW. It never moves an
outcome toward PASS.

```mermaid
flowchart TD
    accTitle: 5.A, part 3, the page outcome
    accDescr: If the page has no enabled form fields, 5.A does not apply. If it has only buttons, 5.A does not apply. If pass L did not run, or the page drew fields after it was read, REVIEW. Otherwise, any failing field makes the page FAIL. Any field in review, or a field not read, makes it REVIEW. Otherwise PASS. Two guards then move a PASS to REVIEW when something that opens was not opened, and move PASS or DNA to REVIEW when the count found fields that pass L did not read.

    A1{"RULE [A1]<br/>Any form field that is enabled and shown?"}
    A2{"RULE [A2]<br/>Any field that takes input,<br/>or only buttons?"}
    A3{"RULE [A3], [WL]<br/>Did pass L run? Did the page draw<br/>fields after it was read?"}
    DNA1["DNA [A1]<br/>no form fields"]
    DNA2["DNA [A2]<br/>buttons carry their own text; wording is 5.B"]
    R3["REVIEW [A3]"]
    FIELDS["Every field decided as in part 2"]
    G2{"RULE [G2]<br/>Any field FAIL?"}
    G3{"RULE [G3]<br/>Any field REVIEW, or a field not read<br/>(over 60, out of time)?"}
    PF["FAIL<br/>lists every failing field, how to reach it<br/>(Tab N times), its picture and the J1 answer"]
    PR["REVIEW"]
    PP["PASS"]
    RV{"GUARD [RV]<br/>Was every menu, tab, accordion<br/>and filter opened and read?"}
    CN{"GUARD [CN]<br/>Did pass L read every field the count found<br/>(web components, frames, fields hidden until opened,<br/>editable text areas)?"}
    FINALP["The outcome stands:<br/>PASS, or DNA if it came from A1 or A2"]
    FINALR["REVIEW<br/>with one sentence per gap, such as<br/>2 form fields inside web components were not checked"]

    A1 -- no --> DNA1
    A1 -- yes --> A2
    A2 -- only buttons --> DNA2
    A2 -- input fields --> A3
    A3 -- no, or yes it drew late --> R3
    A3 -- ran, nothing late --> FIELDS --> G2
    G2 -- yes --> PF
    G2 -- no --> G3
    G3 -- yes --> PR
    G3 -- no --> PP --> RV
    RV -- no --> FINALR
    RV -- yes --> CN
    CN -- no --> FINALR
    CN -- yes --> FINALP
    DNA1 -. "guard CN can move to REVIEW" .-> CN
    DNA2 -. "guard CN can move to REVIEW" .-> CN

    L4["LIMIT: editable text areas (contenteditable)<br/>are counted but never read, so a page with one<br/>cannot PASS or DNA; it ends in REVIEW or FAIL"]
    G9["GAP: a hidden field on a page with nothing that could show it<br/>(no button, disclosure or script link) is treated as hidden from everyone<br/>and not counted (Abby, 2026-11-12; DHS cases TC10.A-ic-dna-1, -2)"]
    CN -.-> L4
    CN -.-> G9

    classDef rule fill:#e3effc,stroke:#1f5fa8,color:#111
    classDef pass fill:#e2f4e6,stroke:#1e7a35,color:#111
    classDef fail fill:#fde4e1,stroke:#b3261e,color:#111
    classDef review fill:#fff4d6,stroke:#a86b00,color:#111
    classDef dna fill:#f0f0f0,stroke:#555,color:#111
    classDef limit fill:#fff4d6,stroke:#a86b00,color:#111,stroke-dasharray:4 3
    classDef gap fill:#fde4e1,stroke:#b3261e,color:#111,stroke-width:2px,stroke-dasharray:6 3
    classDef note fill:#ffffff,stroke:#888,color:#111
    class A1,A2,A3,G2,G3,RV,CN rule
    class PP pass
    class FINALP note
    class PF fail
    class R3,PR,FINALR review
    class DNA1,DNA2 dna
    class L4 limit
    class G9 gap
```

## Gaps and limits in one list

A tester checking TOBI's 5.A result by hand should start with the GAP rows:
each one can produce a wrong PASS or FAIL without a REVIEW to flag it.

| Kind | What | Effect on the result | Where it comes from |
| --- | --- | --- | --- |
| GAP | Fields that appear only after a step the run does not take (submit, the next page of a wizard) | Not seen, not counted: can PASS or DNA a form whose later fields fail | Spec 5.C section 2, "Fields revealed by interaction" |
| GAP | Fields inside closed shadow roots | Not seen, not counted | `_template.md`, "Inside web components and frames" |
| GAP | Visibility ignores colour | A label in white on white, or in very light grey, counts as visible: can PASS | Spec Terms, *visible label* |
| GAP | Scripts the recording missed | Fields they draw are not on the replay | `docs/solutions/recordings-miss-lazy-scripts.md` |
| GAP | Picture crop (240 / 120 / 160 px) | A distant label is outside the picture: unsure (REVIEW) at best, FAIL if the model says not labeled | Spec section 2; `docs/solutions/server-judge.md` |
| GAP | Graphic answer | PASS rests on the model's description of the picture | Spec J1, M4 |
| GAP | Any button in the field's own group is a label | An X clear button alone passes 5.A (5.B judges the wording) | Spec M2i |
| GAP | A picture outside the field's form or group is ignored | A logo-only search box FAILs at M3 | Spec J1 examples; M3 |
| GAP | A hidden field with nothing on the page to show it is not counted | Can DNA | Guard CN |
| LIMIT | More than 60 fields and buttons | REVIEW | Spec 5.C section 2 |
| LIMIT | More than 10 frames, a frame that will not open, a frame not recorded | REVIEW | Guard CN, `frames_missing` |
| LIMIT | A menu or section that would not open, or more than 20 | PASS becomes REVIEW | Guard RV |
| LIMIT | Editable text areas | Never read: a page with one ends in REVIEW (or FAIL from another field) | Guard CN |
| LIMIT | The page draws fields after it was read | REVIEW | Row WL |
| LIMIT | Run out of time | REVIEW | G3 |

## What this diagram does not show

- How 5.A's labels feed 5.B (are they descriptive?) and 5.C (are they in the
  code?). The three tests share pass L.
- The plain-language sentences a user sees. They are in the spec's section 3.
- The exact words of the open question and its rubric. They are in the
  spec's section 4.
