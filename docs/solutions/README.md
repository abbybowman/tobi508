# Solutions: lessons that save the next test time

What happened, what we do now, and how we know. Specs and code link here
instead of repeating the reasoning. Add a lesson when a problem took more
than an hour to understand, to the file of its topic (a new file only for
a new topic), and update it when the answer changes. Every file is listed
here.

## Building a TT test: read these first

| File | What it covers |
| --- | --- |
| [focus-and-walk.md](focus-and-walk.md) | Reading focus through CDP; identifying stops across loads; a fresh browser context per probe; unique paths and top-level positions; shadow roots; listeners from the page's own world; exit checks on small pages; animation against focus indicators; widget items |
| [time-budget.md](time-budget.md) | Measure with `evals/time_budget.py`; where a run's time goes; replay with `ctx.replay`; the tool's own screenshots are DOM changes |
| [recordings-miss-lazy-scripts.md](recordings-miss-lazy-scripts.md) | A recording can lack code the page loads when used: the chunk store and guard GU |
| [andi-output.md](andi-output.md) | Reading ANDI's per-element output; what its wrapper changes; ANDI and scanners run on their own load |
| [tt-pdf-as-data.md](tt-pdf-as-data.md) | The TT PDF as Markdown and JSON; layout traps; where the PDF disagrees with itself |
| [testing-what-no-page-can-trigger.md](testing-what-no-page-can-trigger.md) | Test timing-dependent rows on hand-built evidence |
| [judge-eval.md](judge-eval.md) | Scripted answers test rules, not questions; what an agent needs in a question; keeping the eval unbiased; one agent for all packets, not one per question |
| [tool-output-size.md](tool-output-size.md) | The report as a `run://` link; shared evidence once; results over a client's limit; slow replays of large recordings |

## By test family

| File | What it covers |
| --- | --- |
| [trap-seen-once.md](trap-seen-once.md) | 4.C: a trap seen on one load only is confirmed on a second |
| [form-fields.md](form-fields.md) | 5.x: read vendored cases first; one control kind per stop; date-input parts; changes outside a field |
| [opening-triggers.md](opening-triggers.md) | Opening menus, tabs and sections (`reveal.py`) and what it cost |
| [multi-page.md](multi-page.md) | 9.A-9.C, 19.A: other pages come from the caller; read content, not stops; the live site search |
| [watching-a-page-over-time.md](watching-a-page-over-time.md) | 2.A-2.D: pass T, its own load and browser, regions, the settle rule's ignore list |
| [flashing-needs-stepped-frames.md](flashing-needs-stepped-frames.md) | 3.A: real-time screenshots alias a strobe; step the page's clock |
| [scrt-format.md](scrt-format.md) | SCRT's JSON and its quirks |

## Browsers and environment

| File | What it covers |
| --- | --- |
| [environment.md](environment.md) | The Linux container image; parallel tests and per-worker files; tests that depend on chance; editing formatted code; working beside a running suite; probing recordings |
| [egress-proxy.md](egress-proxy.md) | Every browser connection goes through the egress proxy; what a refused connection looks like; HAR replay |
| [full-chromium-iframes.md](full-chromium-iframes.md) | Pages with cross-site iframes replay in full Chromium, never the headless shell |
| [browser-specific-results.md](browser-specific-results.md) | Results that differ by browser version; load a vendored case in Chrome before trusting it |
| [windows-chrome-results.md](windows-chrome-results.md) | Windows headless and headed Chrome 156 against Linux (2026-11-02): what differed and why |

## Agents, evals and the server judge

| File | What it covers |
| --- | --- |
| [agent-follow-through.md](agent-follow-through.md) | Getting a calling agent to finish: fewer steps, status in the data, the to-do list last, proof the picture was seen |
| [server-judge.md](server-judge.md) | ApiJudge: what to know before changing it; what Agent C showed on real pages |
| [agent-eval.md](agent-eval.md) | The agent eval harness and scoring: what cost time |
