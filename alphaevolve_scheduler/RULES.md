# Project Rules

## Asset Organization & Placement Invariant
- **Asset Placement:** Always place binary, external, or large non-code asset files (e.g., PDFs, images, reference documents) in a dedicated `docs/` or `assets/` subdirectory rather than cluttering the project root.

## Architectural Agility & Simplicity Over Legacy Mandates
- **Architectural Simplicity:** Do not treat legacy or predefined `tech-stack.md` constraints as unchangeable laws if they introduce unnecessary complexity. Always prioritize structural simplicity, agility, and lightweight implementations (e.g., opting for standard package installations or lightweight custom HTTP handlers over complex git submodules or heavy frameworks), and proactively propose these simplifications to the user during the Specification Phase.
