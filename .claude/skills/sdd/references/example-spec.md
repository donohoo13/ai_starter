# Example: a spec at `status: ready`

The artifact `sdd` writes, shown for a mid-sized feature. Read it for altitude before writing one: product and design sections say what and why in a few lines each, engineering carries the weight, every slice ends in a check a build session can run, and a trailing `†` sits only on the lines the user drove. The template is a spine; sections that do not apply are omitted, and a small chore's spec might be fifteen lines.

---

```
---
status: ready
---
```

# Show who is viewing a record in real time

While viewing a customer record, a support agent sees which teammates have the same record open right now.

† marks a decision the user drove, in the ask or under interview.

## Product Requirements

### Problem

Support agents collide on shared records: two edit the same field, or one contacts a customer a colleague is already handling. Collisions surface after the fact in retros, costing duplicate work and mixed messages to customers. Nothing today signals that a teammate has the record open.

### User Stories

- As a support agent, I see who else is viewing the record I have open so that I coordinate before acting.
- As a support agent, I stop appearing on a record when I leave it so that presence reflects reality without a sign-off step.

## Design Requirements

The surface's job is one glance: is anyone else here. It never competes with the record's own content.

### Controls

- An avatar cluster in the record header, an instance of the existing `AvatarStack` component; no new control.

### Layout and Hierarchy

- Sits at the header's trailing edge at reference weight; zero viewers renders as absence, never an empty frame.
- Names appear on hover or focus of an avatar, one level of disclosure.

## Engineering Requirements

- Best-effort presence over short-interval polling; no new real-time infrastructure. Sub-second freshness is explicitly not required. †
- Presence never reveals a record the viewer could not already open; reuse the existing record access check.
- Presence data is non-durable and lives in the cache layer, never Postgres.
- The in-process cache is per instance, so viewers on different app instances may not see each other; accepted for v1.

### Slices

- [ ] `PresenceStore` with TTL semantics. Done when: a marked viewer is listed, and is absent after the TTL, through the store's interface alone.
- [ ] Heartbeat endpoint with auth and identity resolution. Done when: a second viewer appears within one poll interval, a caller without record access gets 403, and a store outage returns an empty list rather than an error.
- [ ] `useRecordPresence` hook. Done when: the hook polls while mounted and no heartbeat fires after unmount.
- [ ] Avatar cluster in the record header. Done when: a second browser session on the same record shows the first session's avatar, and zero viewers renders nothing. †

### Architecture

- `PresenceStore` is a deep module behind a small interface (`markViewing(recordId, viewer, ttl)`, `listViewers(recordId)`, implicit expiry) backed by the existing in-process cache. The backing store is hidden entirely, so a later transport swap touches nothing above it.
- `presenceService` orchestrates: heartbeat marks the caller, returns viewers resolved through the existing identity resolver (name, avatar), and reuses the record service's access check.
- API: `POST /records/:id/presence/heartbeat`, empty body, viewer from session; responds `{ viewers: [{ id, name, avatarUrl }] }` excluding the caller; 403 unauthorized, 404 unknown record.
- Follows the record-lock hook and service pairing, which already models open-record-scoped polling against per-record server state.
- Existing implementation: kept; nothing tracks presence today.

## Evidence

- Polling over a socket transport: the record-lock feature ships on the same shape at the same scale with no reported staleness complaints, which settles v1 on polling.

## References

- `apps/web/src/hooks/useRecordLock.ts`: the polling hook pattern to mirror, including clear-on-unmount.
- `apps/api/src/records/lockService.ts`: the service and access-check pairing the heartbeat follows.
- `apps/api/test/records/lock.test.ts`: the integration harness and fixtures to reuse.

## Out of Scope

- Edit locks or any enforcement. †
- Presence anywhere other than an open record.
- History of past viewers.
- A team-lead aggregate view of multi-viewer records.

## Rejections

- Storing presence in Postgres: rejected because high-churn writes on the primary for ephemeral data buys nothing over the cache.
- WebSocket transport: rejected because it adds infrastructure for freshness nobody asked for; the store interface leaves the door open. †
