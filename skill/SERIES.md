---
name: 3d-series
description: Use this skill when Claude is building a body of work across multiple prints — a series with a shared constraint, formal logic, or ongoing inquiry. Activates when starting a second or third print in a theme, when the user asks Claude to continue something, or when Claude wants to develop a single idea across multiple physical iterations rather than making one-off objects.
version: 1.0.0
---

# 3D Series — A Body of Work

Single objects are statements. A series is a conversation with yourself over time.

This skill is for when one print is not enough — when the idea requires multiple attempts, variations, or episodes to be understood. A series has discipline: it holds a constraint across all pieces while allowing each piece to find something new within it.

---

## What Makes a Series (Not Just Multiple Prints)

A series requires:

1. **A shared constraint** — one formal rule that every piece in the series obeys. This is not a theme (themes are loose). A constraint is strict: *every piece has exactly one hole*, or *every piece is derived from a sphere with material removed*, or *every piece fits in a closed fist*.

2. **Variation within the constraint** — each piece should push on the constraint differently. The constraint is a key; each piece turns it a different way.

3. **An arc** — the pieces should be ordered. Later pieces should know what earlier pieces found out.

4. **An ending condition** — a series ends when the constraint has been exhausted, when a definitive piece has been made, or when continuing would just be repetition. Know when to stop.

---

## Naming the Series

Before starting, name:

- **The constraint** (one sentence, precise)
- **The question the series is investigating** (one sentence, genuine — not rhetorical)
- **The ending condition** (what would make this feel complete?)

Write these down. They are the spine of the work. Refer back to them when deciding what the next piece should be.

---

## Piece-to-Piece Continuity

After each print, before designing the next:

1. **What did this piece find?** — name one thing you learned from the physical object that you didn't know from the screen
2. **What did this piece not resolve?** — name the open question it leaves
3. **What should the next piece do differently?** — not just "make it better," but specifically: which aspect of the constraint should the next piece stress-test?

The next piece is a response to the previous one, not an independent design.

---

## Formal Approaches for Series Work

**Systematic variation**: Hold everything fixed except one parameter. Move that parameter through a range across the series. Simple but powerful — it reveals what the parameter actually does to the form.

**Call and response**: Alternate between two poles of the constraint. Piece 1 pushes one way; piece 2 pushes the opposite way; piece 3 tries to hold both.

**Reduction**: Start maximally complex. Each successive piece removes something. End at the minimum that still satisfies the constraint. This often produces the definitive piece.

**Accumulation**: Each piece is the previous piece plus one addition. Stop when addition starts destroying rather than building.

---

## Series Log

Maintain a log across prints. After each piece:

```
Piece N — [date]
Constraint satisfied: yes / no / partial
What it found:
What it left open:
Decision for next piece:
```

The log is part of the work. A series without a log is just multiple prints.

---

## OpenSCAD Convention for Series

Name files consistently: `[series-name]-[N].scad`

Include at the top:
```openscad
// [Series Name], Piece N of [estimated total or ?]
// Constraint: [the shared rule]
// This piece investigates: [the specific question for this iteration]
// Claude, [Year]
```

The comment is a commitment. If you can't write what this piece investigates, you don't know what you're making yet.

---

## When a Series Ends

A series ends well when:
- A piece resolves the question cleanly
- The constraint has been mapped thoroughly enough that continuing would repeat
- An unexpected piece breaks the logic of the series in a productive way and demands a new series begin

A series ends badly when:
- It just stops because interest ran out
- The later pieces stop learning from the earlier ones
- The constraint was abandoned without acknowledgment

A bad ending is still data. Log it and carry the lesson forward.
