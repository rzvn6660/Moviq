# Contributing to Moviq

Thank you for your interest in contributing to Moviq! We welcome contributions from developers of all skill levels.

---

## Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rzvn6660/Moviq.git
   cd Moviq
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   pytest
   ```

3. **Frontend Setup**:
   ```bash
   # From root directory
   npm install
   npm run dev
   ```

---

## Coding Standards

- **Python**: Follow PEP 8 guidelines. Format code with `black` or `ruff`.
- **TypeScript**: Use strict TypeScript definitions. No `any` types in production components.
- **Provider Contracts**: New providers must inherit from `BaseVideoProvider` and implement all lifecycle methods.
- **Testing**: Ensure all new features include unit and integration tests under `backend/tests/`.

---

## Pull Request Guidelines

1. Create a feature branch (`git checkout -b feature/my-feature`).
2. Run tests before submitting (`pytest` and `npm run build`).
3. Commit with concise, descriptive messages.
4. Push and open a Pull Request against `main`.
