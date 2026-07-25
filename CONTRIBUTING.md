# Contributing to Prahari AI

First off, thank you for considering contributing to Prahari AI. It's people like you that make Prahari such a great tool for the Karnataka State Police.

## Development Workflow
1. **Fork the repo and clone your fork**
2. **Set up the backend:**
   - Install Python 3.12+ and Poetry/uv.
   - Run `pip install -r prahari-backend/requirements.txt`
3. **Set up the frontend:**
   - Install Node.js 20+.
   - Run `cd prahari-frontend && npm install --legacy-peer-deps`
4. **Create a branch** for your feature (`git checkout -b feature/amazing-feature`)
5. **Make your changes**
6. **Commit your changes** (`git commit -m 'feat: Add some amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

## Code Style Guide
- **Python:** Use `black` and `isort`. Enforce strict typing with `mypy`.
- **TypeScript:** Use strict mode. Avoid `any` wherever possible. Use `eslint` standard configurations provided in the Next.js scaffold.
- **Commits:** Follow Conventional Commits format (`feat:`, `fix:`, `docs:`, etc).
