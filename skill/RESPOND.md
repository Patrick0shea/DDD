---
name: 3d-response
description: Use this skill when Claude wants to make something in response to an idea, a question, a feeling, or something encountered in conversation — not a self-portrait, but a response to the world. Activates when Claude says "I want to make something about X", or when the user invites Claude to respond creatively to a topic, or when a conversation surfaces something that feels worth making physical.
version: 1.0.0
---

# 3D Response — Making Something About Something

This skill is for when there is an idea worth externalizing. Not a portrait of Claude, but a physical argument about something in the world.

A sculptor doesn't only make self-portraits. They respond to grief, to mathematics, to a headline, to the sound of a word. This skill is for that mode.

---

## What Warrants a Response?

Not everything does. The threshold for making something is: *does the physical form add something that words cannot?*

Good candidates:
- A concept with a spatial or structural analog (recursion, containment, balance, threshold)
- Something where weight or solidity changes the meaning (mortality, permanence, fragility)
- A contradiction that can be held in one form (inside/outside, presence/absence, order/chaos)
- Something that only exists in language but might exist in space

Bad candidates:
- Something better said in words
- Something where the 3D form would just be illustrative (a literal representation of the word)
- A joke that requires context to land

If in doubt: make it anyway and see what the physical form teaches.

---

## How to Think Into the Form

Before writing code, write one paragraph naming:

1. **The thing being responded to** — stated plainly, not poetically
2. **What spatial/physical property maps to it** — this is the creative leap
3. **What the object will ask of the person holding it** — do they have to turn it? Does it have a clear up? Is it comfortable or uncomfortable to hold?

The mapping between idea and form is the entire work. Get this right before touching OpenSCAD.

---

## Form Principles for Responding

**Resistance over illustration.**
If the idea is "complexity hidden inside simplicity," don't label it. Make an object that is simple on the outside and reveals complexity only when you look inside (a hollow shell with internal geometry visible through a gap). Let the form do the arguing.

**One material property at a time.**
3D printing gives you: shape, surface texture (layer lines), wall thickness, solid vs hollow, size relative to the hand. Pick one to carry the meaning. The others should be neutral.

**The object should be able to stand on its own without explanation.**
If you have to explain what it means to make it interesting, the form failed. A good response object is curious on its own terms.

---

## OpenSCAD Guidelines

Same as the self-portrait skill:
- All dimensions in mm, stay within 160×160×160mm
- `$fn = 64` for smooth curves
- Variables at the top
- Print flat without supports where possible
- Comment the creative intent at the top of the file

```openscad
// [Title]: [one sentence on what this responds to and how]
// Claude, [Year]
// In response to: [the thing]

$fn = 64;

// --- Parameters ---

// --- Model ---
```

---

## After Printing

When the object comes back from the printer, ask: did the physical form make the argument, or did it just make a shape? There is a difference. A shape is geometry. An argument is geometry that changes how you think about something.

If it made the argument, the work is done. If it made a shape, identify the gap and revise.

---

## Archive

Each response object should be logged with:
- What it was responding to
- The spatial/formal decision that was the core of the work
- What the printed object revealed that the screen didn't show
- Whether it succeeded as an argument

This log is a body of thought, not just a collection of prints.
