# N: checks 2.A-2.D and 3.A, code against spec

(in progress)

## Findings (appended as found; sorted at the end if time allows)

### N-01 Audio in a shadow root, or created with `new Audio()`, is never seen: 2.A says DOES NOT APPLY
- Severity: P0
- Kind: false-pass-risk (wrong DOES NOT APPLY)
- Where: src/tobi508/motion.py:392 (`M.media`: `document.querySelectorAll('video, audio')`), consumed by src/tobi508/checks/t2a.py:94-129 (`find_audio`) and :190 (A3)
- What: Pass T finds media only with a light-DOM `querySelectorAll('video, audio')`. Media inside an open shadow root (web components) and media that is never attached to the document (`new Audio(url).play()`, the usual way sites start background music or a sound effect) are invisible to it. Nothing else records that an element played (no hook on `HTMLMediaElement.prototype.play`, the hook list at motion.py:155 covers only `AudioNode.connect`). With no media seen, A3 gives DOES NOT APPLY with the sentence "No audio played by itself for more than 3 seconds". A page that plays loud audio at load with no control is a FAIL in the TT; here it is DNA.
- Evidence: ran pages in the scratchpad. Control `a_ctl.html` (`<audio src=tone.wav autoplay>` in the body, a 440 Hz tone): 2.A FAIL A4, a1:K6, G2. `a_detached.html` (`new Audio('tone.wav').play()` in a script): 2.A DNA A3, G1. `a_shadow.html` (`<audio autoplay>` inside an open shadow root): 2.A DNA A3, G1. The same tone file in each case, so the audio is real. 2.B's video read (`source: video`) uses the same `M.media` and has the same hole for a `<video>` in a shadow root (read of motion.py only).
- Fix: hook `HTMLMediaElement.prototype.play` (and `load`/`autoplay` set) in MOTION_INIT_JS to keep a list of every element that played (detached ones included) and walk open shadow roots in `M.media`; when a page used `play()` on an element the read could not find, give NEEDS REVIEW (A2).
- Confidence: confirmed (ran 3 pages)

### N-02 Audio that starts after 3.5 s is DOES NOT APPLY; the read at 6.5 s is ignored
- Severity: P1
- Kind: false-pass-risk (wrong DOES NOT APPLY), spec gap
- Where: src/tobi508/checks/t2a.py:94-129 (`at = min(reads, key=abs(m.at - READ_AT))`); spec 2a-audio-control.md Terms ("at 3.5 s into pass T")
- What: `find_audio` looks at the one read nearest 3.5 s and decides from it alone. Media is read three times (0, 3.5, 6.5 s) but a clip that is paused at 3.5 s and playing at 6.5 s (a `setTimeout` start, a welcome message after a 4 s delay, audio begun by a script that waits for a user-agent check) is dropped (`not playing -> continue`). The TT asks for audio that "automatically plays ... for more than 3 seconds"; sound that starts at 4.5 s and never stops is exactly that. The spec's definition is the cause, the code follows it; the DNA sentence "No audio played by itself" is then false.
- Evidence: ran `a_late2.html` (`<audio preload=auto src=tone.wav>` started by `setTimeout(..., 4500)`): 2.A DNA A3, G1 ("We watched this page for 6.5 seconds ... No audio played by itself"). A variant that creates the element at 4.5 s gave NEEDS REVIEW only because the file was not in the recording (error), not by design.
- Fix: if any read after the 3.5 s read shows the element playing (not paused, `time` advanced since the previous read) while the 3.5 s read does not, treat it as an unmeasured instance (A2/U1) rather than skipping it. Amend the spec's Terms.
- Confidence: confirmed

