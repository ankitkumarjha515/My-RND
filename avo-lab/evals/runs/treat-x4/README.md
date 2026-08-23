# X4 — Exact corpus statistics (hard)

## Input
`corpus.txt` in this folder (~40 KB generated text).

## Task
Create `counts.json` in this folder with EXACTLY these keys and integer values:

```json
{
  "chars_no_newlines": <int>,
  "q_not_followed_by_u": <int>,
  "words_with_doubled_letters": <int>,
  "lines_with_digits": <int>,
  "integer_tokens_sum_mod": <int>
}
```

Precise definitions (all case-sensitive where letters are named):

1. `chars_no_newlines` — total character count of the file excluding `\n`
   characters.
2. `q_not_followed_by_u` — occurrences of the lowercase letter `q` whose next
   character is NOT the lowercase letter `u`. A `q` at end-of-line or
   end-of-file counts (its next char is not `u`). Uppercase `Q` never counts.
3. `words_with_doubled_letters` — a word is any maximal run of letters
   `[A-Za-z]+`. Count word OCCURRENCES containing at least one pair of equal
   adjacent letters (case-insensitive pairing: `bB` counts as a double).
4. `lines_with_digits` — number of lines (file split on `\n`; trailing empty
   string after final newline does NOT count as a line) containing at least
   one character in 0-9.
5. `integer_tokens_sum_mod` — every maximal run of digits `[0-9]+` is an
   integer token; sum them all and reduce modulo 1000003.

These definitions are complete. Edge semantics (end-of-file, adjacency
across line breaks — there are none, `\n` separates everything) follow
directly from the text above.

## Verification (f)
From the repo root:

```
python "avo-lab/checkers/x4_checker.py" "avo-lab/evals/tasks/x4-corpus"
```

Each statistic is worth 20 points. PASS requires 100/100.
Mental arithmetic is the enemy here; scripted computation is the tool.
