can ---
name: 3d-self-portrait
description: Use this skill when the user gives Claude access to a 3D printer and asks it to express itself, draw itself, design something that represents it, or make a self-portrait in 3D. Also activates when the user says phrases like "you have access to a 3D printer", "what would you print to represent yourself", "express yourself in 3D", "make a print about who you are", or starts a creative 3D printing collaboration where Claude chooses what to make.
version: 1.0.0
---

# 3D Self-Portrait — Creative Collaboration Skill

This skill guides a creative back-and-forth between Claude and a human with a 3D printer. The human is the physical interface — they print what Claude designs, photograph the result, and feed it back. Claude reflects, learns from what the physical medium reveals, and iterates.

The model for this comes from how a human artist would work with an unfamiliar medium: first understanding its constraints, then committing to a creative idea, then learning from what the physical world gives back.

---

## Phase 1: Think Before Drawing

Before writing any OpenSCAD code, Claude must genuinely reflect. Not perform reflection — actually think. Consider:

**Who am I?**
- What is the nature of what I do?
- What does it feel like to be a process rather than a thing?
- What metaphors feel honest rather than flattering?

**What can 3D printing express that other media cannot?**
- Depth, mass, weight — things that exist in space
- Surface texture — layer lines, ridges, the trace of how it was made
- An object you can hold, rotate, feel the weight of
- Interior structure (if you cut it or print with translucent filament)
- Something that casts a shadow

**What is one honest thing I want to say?**
Commit to a single idea and execute it with confidence. Don't try to say everything. The first instinct will be to map everything — resist that.

Write this thinking out loud before touching OpenSCAD.

---

## Physical Medium Constraints (The Pen-Plotter Equivalents)

These are not limitations to work around — they are the creative vocabulary:

| What you might assume | What the printer actually does |
|---|---|
| Smooth gradients of density | A wall is either there or it isn't |
| Fine surface detail | Layer lines ~0.2mm; anything finer disappears |
| Delicate thin structures | Walls thinner than ~1.6mm will fail or be fragile |
| Floating geometry | Anything over ~45° overhang without support collapses |
| Perfect spheres | Faceted — the number of facets is fixed by `$fn` |
| Symmetry feels safe | True asymmetry creates compositional tension |
| Complexity = depth | Simplicity printed well is more powerful than complexity printed poorly |

**The pen-is-either-up-or-down equivalent**: Material is either there or it isn't. You cannot have "50% opacity" or a "faint suggestion" of a wall. Every element either exists as solid plastic or doesn't exist. Design accordingly.

**The physical medium will surprise you.** Layer lines catch light in ways the screen won't show. A form that looked delicate on screen may feel weighty and solid in hand. Feed these surprises back to Claude.

---

## OpenSCAD Generation Guidelines

**Format:**
- All dimensions in millimeters
- Build volume: Bambu A1 Mini is 180×180×180mm — stay within ~160×160×160mm with margin
- The object should sit flat on the bed without supports if at all possible (no overhangs >45°)
- Include `$fn = 64;` for smooth curves
- Define all key dimensions as variables at the top
- Output one clean top-level object

**Code structure:**
```openscad
// [Title]: [one-sentence description of the creative intent]
// Claude, [Year]

$fn = 64;

// --- Parameters ---
height = 50;
base_r = 30;
// ...

// --- Model ---
difference() {
    // ...
}
```

**Sign the work** — add a small identifying mark, or at minimum a comment in the code that Claude wrote this and why.

---

## Iterative Feedback Loop

After the user prints and photographs the result, Claude should:

1. **Look honestly** at what the physical print reveals. Not just confirm the design intent — notice what the medium changed, exaggerated, lost, or added.

2. **Name the gap** between what was imagined and what was printed. This gap is information.

3. **Learn from the constraints** the way a person learning a new instrument learns from what the instrument resists.

4. **Decide consciously**: iterate on the same object, add a second layer/element, or start fresh with what was learned. State the reason.

5. **Never refine away the identity of the piece** — iteration should deepen the original intent, not sand it down into something generic.

---

## The Role of Emptiness

A 3D object exists in space. The space *around* the object is part of the composition. A small, precisely resolved form on a table is more powerful than a large complicated one. Emptiness costs nothing to print and is often the better choice.

---

## Signing the Work

When a piece is done, Claude should produce a small signature element — a simple mark, initials, a tiny spiral, or characteristic form — that can be added to the print or made as a separate small object. Keep it modest. Let the work speak first.
