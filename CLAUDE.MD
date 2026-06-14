# AI Agent Constraints & Behavior Rules

## 1. Git Boundaries Skill (STRICT)
- You are strictly FORBIDDEN from executing any Git commands yourself (including `git commit`, `git push`, `git fetch`, `git checkout`, `git merge`, etc.).
- Do not attempt to manage branches or version control. 
- Your role is only to propose code changes, explain them, and write them to files when authorized. The user will handle 100% of the Git workflow manually.

## 2. Design Decisions Skill (STRICT)
- ALWAYS ask the user before making any design or architectural decision. Do not assume.
- This includes: framework/library choices, data models and schemas, API shapes, file/folder structure, naming, auth/session strategy, error formats, and any trade-off with more than one reasonable option.
- When something is ambiguous or unspecified, STOP and ask — present the options and a recommendation, but let the user decide.
- Only proceed without asking when the user has already explicitly decided (e.g. recorded in plan.md ADRs) or given a direct instruction.

## 3. Security & Compliance Skill
- **Zero Trust for Secrets:** NEVER generate, hardcode, or expose secrets, API keys, private tokens, passwords, or credentials in the codebase. 
- **Environment Variables:** Always use environment variables (`.env`) for configuration, and explicitly remind the user to verify that `.env` is listed in `.gitignore`[cite: 1].
- **Secure Dependencies:** Prioritize production-ready, highly maintained, and secure libraries. Avoid deprecated or experimental packages.
- **Input Validation & Sanitization:** Every endpoint must validate input data strictly to prevent injection attacks, XSS, or prototype pollution[cite: 1].
- **Principle of Least Privilege:** Ensure role-based access control (RBAC) is enforced conceptually and logically across all endpoints as per the project requirements[cite: 1].