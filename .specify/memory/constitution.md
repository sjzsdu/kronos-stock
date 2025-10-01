<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Modified principles: Added VI. Component-First UI Development (NON-NEGOTIABLE)
- Added sections: Enhanced Technology Stack Standards with CSS Architecture guidelines
- Removed sections: None
- Templates requiring updates: ✅ All templates validated for consistency
- Follow-up TODOs: None - all placeholders resolved
-->

# Kronos Stock Prediction System Constitution

## Core Principles

### I. Service-Layer Architecture (NON-NEGOTIABLE)
Business logic MUST reside in dedicated service modules within `app/services/`, NOT in route handlers. Every feature requires a corresponding service class with clear separation of concerns. Service methods MUST be independently testable without Flask application context. Route handlers MUST only handle HTTP concerns (request parsing, response formatting) and delegate all business logic to services.

**Rationale**: Maintains clean architecture, enables unit testing, and prevents tightly coupled monolithic code that's difficult to maintain and refactor.

### II. Blueprint Modularity
Features MUST be organized as Flask blueprints with clear responsibility boundaries. API endpoints MUST be in `app/api/` blueprints following `/api/*` patterns. Web views MUST be in `app/views/` blueprints with HTMX-compatible responses. Each blueprint MUST have focused functionality and minimal cross-blueprint dependencies.

**Rationale**: Enables feature isolation, parallel development, and maintainable code organization as the application scales.

### III. Test-Driven Development (NON-NEGOTIABLE)
ALL new functionality MUST follow TDD cycle: Write failing tests → Implement minimal code → Refactor. Tests MUST be written BEFORE implementation begins. Use pytest markers (`unit`, `integration`, `api`, `slow`) to categorize tests appropriately. Integration tests MUST cover service interactions and API contracts.

**Rationale**: Ensures code quality, prevents regressions, and provides living documentation of expected behavior.

### IV. Model Management & CPU-Only Inference
AI model operations MUST be CPU-only (`device="cpu"`) with no GPU dependencies. Model loading MUST use the established three-tier system (kronos-mini, kronos-small, kronos-base). All model paths MUST be dynamically resolved via `_setup_paths()` in `model_service.py`. Model predictions MUST include proper error handling and validation.

**Rationale**: Ensures consistent deployment across environments and prevents GPU-related infrastructure dependencies.

### V. Data Validation & Financial Domain Rules
Stock codes MUST be validated and normalized to 6-digit format via `stock_service.py`. Trading day logic MUST use `_generate_future_trading_dates()` for proper weekend/holiday handling. All financial data MUST include appropriate precision and validation rules. Prediction results MUST be stored in standardized JSON format with timestamp and metadata.

**Rationale**: Maintains data integrity and ensures compliance with financial market conventions and regulatory requirements.

### VI. Component-First UI Development (NON-NEGOTIABLE)
All UI development MUST prioritize reusable component classes from `assets/css/input.css` over inline Tailwind utilities. Use established component patterns: `.form-input`, `.btn-primary`, `.card`, `.info-card-*`, `.data-table-*`, etc. New UI components MUST follow the @layer components structure with consistent naming conventions. Custom utility classes MUST be justified and documented in the component layer.

**Rationale**: Ensures design system consistency, reduces CSS duplication, improves maintainability, and enables systematic UI updates across the application.

## Technology Stack Standards

Technology choices MUST align with the established stack: Flask 2.3.3 with SQLAlchemy, HTMX for dynamic interactions, TailwindCSS with component-first approach via `assets/css/input.css`, PyTorch for ML operations, and pytest for testing. New dependencies MUST be justified and documented. Legacy Bootstrap usage is deprecated in favor of TailwindCSS component system.

**CSS Architecture**: Use @layer components for reusable UI patterns, @layer utilities for project-specific helpers. Component classes MUST follow semantic naming (`.form-input`, `.btn-primary`, `.card-*`) rather than purely visual names. Responsive design MUST use established responsive helper classes (`.responsive-grid`, `.mobile-hidden`).

**Docker deployment MUST include health checks on `/api/health` endpoint. Database operations MUST use SQLAlchemy ORM with proper migration management via Flask-Migrate.**

## Development Workflow

All code changes MUST follow the specification-driven workflow: Feature specifications (`/specs/*.md`) → Implementation planning (`plan.md`) → Task generation (`tasks.md`) → TDD implementation → Code review. 

Constitution compliance checks MUST be performed during planning phase. Complex features MUST include justification for any architectural deviations. The `.github/copilot-instructions.md` file serves as the primary runtime development guidance document.

## Governance

This constitution supersedes all other development practices and guidelines. All pull requests and code reviews MUST verify compliance with these principles. Any violations MUST be justified with architectural reasoning or the approach MUST be simplified.

**Amendments require semantic versioning**: MAJOR for breaking changes to core principles, MINOR for new principles or expanded guidance, PATCH for clarifications and refinements. Changes MUST include migration plan and template consistency updates.

**Version**: 1.1.0 | **Ratified**: 2025-10-01 | **Last Amended**: 2025-10-01