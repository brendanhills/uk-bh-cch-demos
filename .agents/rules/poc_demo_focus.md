# Solo Developer & Rapid Prototyping (PoC/Demo) Rule

## Core Philosophy: "Velocity, Simplicity, and Direct Value"
This workspace consists of projects built by a solo developer, specifically designed as interactive demos, prototypes, or Proofs of Concept (PoCs)—not multi-team production software. The paramount goals are rapid iteration, frictionless local setup, and highly responsive interactive feedback.

## Key Design & Execution Invariants:

1. **Prioritize Simplicity & Speed over Enterprise Overhead**:
   - Avoid introducing heavy architecture layers, overly-complex abstraction patterns, or corporate deployment pipelines (e.g. Docker-multistage, Kubernetes setups, or strict CI/CD configs) unless explicitly requested.
   - If a simpler, direct approach works and is easy for a solo developer to read, maintain, and run, always prefer it.

2. **Frictionless and Local Developer Experience (DX)**:
   - Ensure all startup scripts (like `run_demo.sh` or `serve.sh`) can be executed instantly with zero complex dependencies.
   - Keep environments isolated but simple. Cache folders (`.venv`, `node_modules`) and temporary directories should stay local and strictly out of the repository's root workspace, avoiding global developer system clutter.

3. **High-Impact Presentation & Interaction**:
   - Since these are demos, focus heavily on visual elegance, intuitive user interactions, responsive CSS layout, and immediate usability feedback (like meaningful default demo values, instant error feedback, and fluid transitions).
   - Never use empty placeholder text or dummy components where a working demonstration can be quickly implemented.

4. **Pragmatic Dependency Management**:
   - Maintain the locked reproducibility of environments (to prevent breaking changes) but do so without imposing tedious corporate packaging pipelines or overkill dependency trees.
