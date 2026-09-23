---
name: drawio
description: "Use only when the user explicitly asks to use drawio, draw.io or Draw IO, or directly requests work on a .drawio file. Create, edit, validate, or export native draw.io diagrams, flowcharts, architecture diagrams, ER/sequence/class/network diagrams, mockups, wireframes, and UI sketches. Do not infer this skill from a generic diagram request alone; incidental or quoted mentions are not invocations."
---

# Draw.io

Produce a native editable `.drawio` artifact. Prefer Mermaid for standard
flow, sequence, class, state, ER, gantt, mind-map, timeline, journey, C4, and
similar diagrams when the desktop CLI is available. Use draw.io XML for precise
placement, special shape libraries, or when the CLI is unavailable.

Always make a `.drawio` file before an image export. For Mermaid, convert
`.mmd → .drawio` first, then export the `.drawio`; do not directly export
Mermaid to PNG. If the CLI is unavailable, author XML and deliver `.drawio` or
a browser URL. Use ELK layout only for XML that needs automatic placement.

When requested, export PNG/SVG/PDF with embedded diagram XML so the result can
be reopened in draw.io. If no format is named, deliver the `.drawio` file. Keep
a local `.drawio` copy for URL delivery; report an absolute path if opening
fails.

Before delivery, validate XML well-formedness and confirm the requested format
opens or is structurally usable. Do not emit invalid XML comments or unescaped
characters. This skill has no bundled helper resources; consult the active
draw.io installation only for format-specific details that this compact route
does not cover.
