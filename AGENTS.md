# AGENTS.md

- The shared frontend navbar fragment at `src/frontend/src/main/resources/templates/fragments/nav.html` is part of the automation contract. Keep the header logo DOM path and cart icon attributes stable when refactoring, because UI automation depends on those selectors.
