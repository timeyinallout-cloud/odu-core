# Episode 3 — shot runbook

Everything below is real. No mock-ups, no staged output. Where a beat needs the
project as it was *before* verification, there is a live checkout of that
commit rather than an edited screenshot.

## Setup, once

```sh
# the "before" state — the project as it stood the day before verification
git worktree add --detach /tmp/odu-before 9f41165
```

Two terminals, side by side or on separate desktops:

| Terminal | Working directory | Shows |
|---|---|---|
| **BEFORE** | `/tmp/odu-before` | `0 of 16 figures verified` |
| **NOW** | `~/odu-core` | `16 of 16 figures verified` |

Make the prompt quiet before recording:

```sh
PS1='$ '
clear
```

Remove the worktree when you're done: `git worktree remove /tmp/odu-before`

---

## Shot list

### 0:00 — cold open · NOW

```sh
make test
```

Let it run to the green line. The count on screen is the count in the script;
if they diverge, the script is wrong, not the terminal.

### 0:25 — the foundation · NOW

```sh
$EDITOR data/principal_odu.json
```

Scroll slowly through two or three entries. What should read on camera is that
each figure carries `marks`, `nibble`, and a `verification` block — the
verification block being the thing that did not exist a fortnight ago.

### 1:00 — the structural checks · NOW

```sh
python3 -m pytest tests/test_core.py -q -k "permutation or complements"
```

Then show the test itself — `test_seniority_pairs_are_complements_or_reversals`
in `tests/test_core.py`. The docstring says exactly why it catches a
transcription error and not a wrong table.

### 1:45 — the paper · BROWSER

`https://doi.org/10.1016/j.sciaf.2023.e01729`

Let the CAPTCHA land on camera. Do not solve it — the point of the beat is that
an open-access paper was unreachable.

### 2:20 — the trap · BEFORE terminal

```sh
cd /tmp/odu-before && PYTHONPATH=src python3 -m odu_core.cli verify
```

Real output: `0 of 16 figures verified against a source`.

For the conflicting claim itself, read it aloud over the terminal rather than
reconstructing a search result you no longer have. The claim was that Ọ̀sá is
`0010` and Òtúrúpọ̀n is `0111` — the two swapped.

### 3:00 — the check that saved it · NOW

```sh
python3 -c "
import json
d = json.load(open('data/principal_odu.json'))
print(json.dumps(d['verification']['history'], indent=2, ensure_ascii=False))"
```

The failed attempt is recorded in the data itself. That is the beat: the
project wrote down that it could not verify, rather than quietly moving on.

### 4:30 — resolution · BROWSER, then NOW

Borrow the book on your own account, open **page 4**, and film Table 1 briefly
while you narrate. Keep it short — you are showing that the table exists and
matches, not republishing it.

Then, on camera:

```sh
python3 scripts/verify_odu.py --status
```

Sixteen rows, every one citing Table 1 p. 4 and Table 3 col. B p. 48.

### 5:15 — twenty-one other orderings · BROWSER, then NOW

Page 47 for the passage about 86 lists from 61 sources. Then:

```sh
python3 -c "
import json
d = json.load(open('data/principal_odu.json'))
a = d['alternativeOrders'][0]
print(a['label'], '—', a['source'])
print(a['note'])"
```

### 6:10 — why bit patterns are the key · NOW

```sh
odu show 255
```

`byte 255` and `seniority 1 of 256` on the same screen is the whole argument.
Then `src/odu_core/seniority.py` — the module docstring states it plainly.

### 6:45 — it happened twice more · BROWSER

1. `https://unesdoc.unesco.org/ark:/48223/pf0000019827` — the record says
   *Niamey: OAU Centre…*, note *"Pub. with the financial assistance of UNESCO"*.
2. `https://archive.org/details/sixteencowriesyo0000basc` — catalogued as
   *Sixteen Cowries*; borrow it and show the cover reading
   *Explorations in African Systems of Thought*.

The second lands hardest. Let the mismatch sit for a second before speaking.

### 7:30 — the correction I could not make · NOW

```sh
git show ccc5782 --stat
git show ccc5782 -- data/compound_names.json | head -40
```

The diff shows `Ogbè Yẹ̀kú` becoming `Ogbè Ọ̀yẹ̀kú`. Say on camera that this
came from a speaker, after verification was already complete.

### 8:15 — close · NOW

```sh
clear
odu verify
```

Then the repository, the green CI badge, and the release page.

---

## Notes

- **Do not solve the CAPTCHA on camera.** The beat is that it blocked a
  legitimate reader.
- **Film Bascom from your own borrowed copy**, briefly, as illustration. Show
  that the table matches; don't publish the scan.
- The near-miss is the spine of the episode. Don't soften it — the fact that
  the false claim was *convincing* is the entire lesson.
- Credit the Internet Archive by name. Controlled lending is what made the
  verification possible at all.
- If a take feels like it's defending the project rather than examining it,
  stop and go again. The episode is stronger as an account of being wrong
  three times than as a demonstration of being right.
