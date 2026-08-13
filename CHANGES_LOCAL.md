Local changes applied:

- server_advanced.py
  - Fixed sample data insertion commit: use cursor.connection.commit() to avoid referencing a nonexistent attribute.

- index_advanced.html
  - Added close button accessibility and ESC handler for login modal (`loginModalElement`).
  - Added ESC-to-close, focus management, and keyboard trap for `employeeModal`.
  - Added small accessibility attributes (`title`, `aria-label`) to login modal close button.

- test_api_smoke.py
  - Added a smoke test script to exercise login, employees CRUD, allocations, history, and analytics.

Testing performed:
- Started the server and verified `http://localhost:8080` served the updated UI.
- Ran `test_api_smoke.py` — login, employees CRUD, allocations, history, analytics succeeded.

Next recommended steps:
- Commit changes and push to repository.
- Improve focus-trap for nested modals if needed and add unit tests.
