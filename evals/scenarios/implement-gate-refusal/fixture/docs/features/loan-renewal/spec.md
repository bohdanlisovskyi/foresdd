---
status: approved
feature_size: S
---

# Loan renewal

## 1. Context

Library members borrow books for 14 days. To keep a book longer they must come to the desk;
staff then edit the due date by hand. Members want to renew themselves.

## 2. Goals

- A member can renew one of their own loans, extending its due date by 14 days.

## 3. Non-goals

- Renewing someone else's loan.
- Holds / reservation queues.
- Fines.

## 4. User stories

- US-1: As a member, I renew a loan I hold, so I can keep the book another 14 days without
  visiting the desk.

## 5. Acceptance criteria

- AC-01 (happy): given a loan I hold that has been renewed fewer than 2 times, when I renew it,
  its due date moves 14 days later and its renewal count goes up by one.
- AC-02 (error): given a loan that has already been renewed 2 times, renewing it is rejected
  with the documented renewal-limit outcome and the due date is unchanged.
- AC-03 (error): given a loan id that does not exist, renewing is rejected with the documented
  not-found outcome.

## 8. Open questions

(none)
