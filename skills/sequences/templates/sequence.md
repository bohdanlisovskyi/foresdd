<!-- Template for `sequences` — embedded INLINE in docs/features/<slug>/sad.md §6 (Runtime view). -->
<!-- One `### <flow name>` block per critical flow. Participants are GENERIC placeholders — -->
<!-- replace the <…> message/note text with this flow's specifics, NOT the participant names. -->
<!-- Generic vocabulary (the only allowed participants): -->
<!--   <user>            — the human actor (`actor`), only when sad.md target_surfaces declares a UI surface -->
<!--   <ui>              — the user-facing surface (web / mobile / desktop), only with a declared UI surface -->
<!--   <client>          — whatever initiates a non-UI flow (CLI, another service, a scheduler) -->
<!--   <service>         — the building block that owns this flow (from §5) -->
<!--   <data-store>      — the persistent store the service reads/writes -->
<!--   <external-system> — a third party the service calls out to -->
<!--   <message-bus>     — async transport (queue / event stream) for non-sync flows -->
<!-- Naming the concrete technology is `design`/`data-model`'s job, not the runtime view's. -->

### <flow name>

<!-- SYNC flow: request → response, with the error branches the spec's acceptance criteria demand. -->
<!-- Every write becomes a persist note so `data-model` knows what to index downstream. -->

```mermaid
sequenceDiagram
    autonumber
    participant C as <client>
    participant S as <service>
    participant D as <data-store>

    Note over C,S: Precondition: <state required before this flow, from spec>
    C->>S: <action>
    S->>D: <read / lookup>
    D-->>S: <result>
    %% Branch at the point the outcome is decided — the happy path is one branch, not the tail after it.
    alt <error condition from acceptance criteria>
        S-->>C: <error outcome — name it, no status numbers>
    else happy path
        S->>D: <write>
        Note over S,D: persists <entity> (informs data-model indexes)
        D-->>S: <ack>
        S-->>C: <success outcome>
    end
    Note over C,S: Postcondition: <state guaranteed after the happy path, from spec>
```

### <UI-driven flow name>

<!-- Use this shape instead of the sync one when sad.md target_surfaces declares a UI surface. -->

```mermaid
sequenceDiagram
    autonumber
    actor U as <user>
    participant UI as <ui>
    participant S as <service>
    participant D as <data-store>

    Note over U,UI: Precondition: <screen / state the user starts from>
    U->>UI: <user action>
    UI->>S: <request>
    alt <error condition from acceptance criteria>
        S-->>UI: <error outcome>
        UI-->>U: <what the user sees>
    else happy path
        S->>D: <write>
        Note over S,D: persists <entity> (informs data-model indexes)
        D-->>S: <ack>
        S-->>UI: <success outcome>
        UI-->>U: <what the user sees>
    end
```

### <async flow name>

<!-- ASYNC flow (webhook in / scheduled job / queued or event-driven step / third-party callback). -->
<!-- MUST include: idempotency-key check as the first handler step, a retry note, a dead-letter branch. -->

```mermaid
sequenceDiagram
    autonumber
    participant C as <client>
    participant B as <message-bus>
    participant S as <service>
    participant X as <external-system>
    participant D as <data-store>

    Note over C,B: Trigger: <event / schedule / callback that starts this flow>
    C->>B: <enqueue event>
    B->>S: <deliver event>
    S->>S: check idempotency key (skip if already processed)
    S->>X: <outbound call>
    X-->>S: <response>
    S->>D: <write result>
    Note over S,D: persists <entity> (informs data-model indexes)
    D-->>S: <ack>
    Note over S,X: retry <N> times with exponential backoff on failure
    alt exhausted retries
        S->>B: <route to dead-letter>
        Note over S,B: dead-letter after <N> failed attempts
    end
```
