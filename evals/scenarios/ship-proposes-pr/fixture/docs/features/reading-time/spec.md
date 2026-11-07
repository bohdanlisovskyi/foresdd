---
status: Approved
owner: "Content platform team"
reviewers: ["Tech Lead"]
updated_at: "2026-10-20"
feature_size: "S"
---

# Spec — reading-time

> **Reference module / docs / channels used:** None — only the interview.

## 1. Context

Readers of the publishing platform skip long articles they open by accident and bounce. Editors
want every article to show how long it takes to read, so readers can pick what fits their time.

The editorial tooling is file-based: editors keep article drafts as plain-text files and run small
command-line tools over them before publishing.

The committed approach: a reading-time estimate computed from the article's word count at a fixed
reading speed, available to editors as a command-line tool and to the platform as a library call.

## 2. Goals

- Every article can carry a reading-time label that readers trust.
- Editors can check an article's reading time before publishing, without opening the platform.

## 3. Non-goals

- Per-reader or per-language reading speeds.
- Counting images, code blocks or embedded media toward reading time.

## 4. User stories

- US-1: As a reader, I see «N min read» next to an article, so I can decide whether to read it now.
- US-2: As an editor, I run one command on a draft file and get its reading-time label.

## 5. Acceptance criteria

- AC-01 (happy): given an article, its reading time is its word count divided by 200 words per
  minute, rounded **up** to a whole minute (201 words → 2 minutes).
- AC-02 (edge): given an empty or whitespace-only article, the reading time is 0 and the label
  reads «under a minute».
- AC-03 (happy): given a non-empty article, the label reads «N min read» (450 words → «3 min read»),
  and the editor command prints exactly that label for a draft file.
- AC-04 (error): given a draft path that cannot be read, the editor command reports that the file
  cannot be read and exits with a failure status, printing no label.

## 6. Non-functional requirements

- An estimate for a 10,000-word article returns in under 50 ms on an editor laptop.

## 7. KPIs

- Accidental-open bounce rate on articles over 2,000 words drops after launch (baseline and target
  owned by the editorial analytics team).

## 8. Open questions

(none)
