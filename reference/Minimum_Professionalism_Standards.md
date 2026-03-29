# Minimum Professionalism Standards

**Version:** 1.0
**Status:** Adopted

## 1. Purpose
This document establishes the canonical baseline for all professionalism, quality, and documentation standards within this repository. It serves as the single source of truth, ensuring that all contributions are clear, maintainable, and auditable. The principles herein are non-negotiable and apply to all code, documentation, and architectural decisions.

## 2. Core Principles
- **Clarity over cleverness:** Code should be easy to understand for any developer, not just its author.
- **Show your work:** All non-trivial logic and architectural decisions must be justified with concise, inline rationale.
- **Cite your sources:** Leverage industry best practices and credit them. Do not reinvent the wheel without justification.
- **No redundancy:** Information should exist in one canonical place. Reference it, don't repeat it.

## 3. Standards

### 3.1. Code Quality & Style
All code must adhere to the official style guides for its respective language to ensure consistency and readability.
- **Rationale:** A consistent style dramatically reduces the cognitive load required to read and understand code.
- **Sources:**
  - **Kotlin:** [Kotlin Official Style Guide](https://kotlinlang.org/docs/coding-conventions.html)
  - **Python:** [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)

### 3.2. Documentation
- **Inline Rationale:** Non-obvious code, business logic, or algorithmic adaptations must be explained with inline comments. These comments should answer "why," not "what."
- **File-Level References:** Each file must include a "References" section at the end, citing any external standards, libraries, or articles that informed its implementation.
- **READMEs:** Every module or service must have a `README.md` explaining its purpose, how to build it, how to test it, and its key dependencies.

### 3.3. Version Control
Commits must be atomic, logical, and well-documented.
- **Commit Messages:** Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. A commit message must clearly state what the change is and why it was made.
  - `feat:` for new features.
  - `fix:` for bug fixes.
  - `docs:` for documentation changes.
  - `style:` for code style changes.
  - `refactor:` for code changes that neither fix a bug nor add a feature.
  - `test:` for adding or correcting tests.
- **Branching:** Use feature branches for all new work. All code must be reviewed and pass CI before merging to `main`.

---
*This document is the "curriculum." All code is expected to follow it, referencing it as the foundational text.*
