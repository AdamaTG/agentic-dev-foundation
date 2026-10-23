# Stack adapters – ADF V2.1

These are **runnable command adapters** once your actual projects, dependencies and scripts exist. No project application is bundled, and no E2E execution is claimed. Each config is a starting recipe and must be adapted to the application structure.

## General (Windows PowerShell)

```powershell
python tools/stack_verify.py --stack next-fastapi --profile quick
python tools/stack_verify.py --stack next-fastapi --profile full
python tools/stack_verify.py --stack next-fastapi --profile e2e
python tools/stack_verify.py --stack expo --profile full
python tools/stack_verify.py --stack flutter --profile e2e
```

Codes: 0 pass; 1 test/check failed; 2 invalid or missing project/config; 3 tool unavailable; 4 timeout. Missing commands **never pass silently**. Reports in `reports/stack-*.json`; copied evidence in `evidence/stacks/<stack>/` with sha256 and size. Scripts don't interpret AI text as proof. Do not publish reports containing secrets.

## Next.js + FastAPI

- Place application in `apps/web` and backend in `apps/api`; adapt directory paths in `config/stacks/next-fastapi.json`.
- In `apps/web/package.json`, add `lint` (`eslint .`), `typecheck` (`tsc --noEmit`), `test:unit` (Vitest/Jest in non-watch mode), `test:e2e` (`playwright test`). Install corresponding dependencies, lockfile, Playwright browser (`npx playwright install chromium`).
- Example Playwright config/test under `examples/adapters/`. Copy to `apps/web/playwright.config.ts` and `apps/web/tests/e2e/home.spec.ts`; execute a production build before webServer `npm run start`, or change the server command for local testing.
- Install Python project's `pytest`, `httpx`, `fastapi` and test dependencies. Add actual endpoint code and copy/adapt `examples/adapters/fastapi-integration-test.py` to `apps/api/tests/integration/test_health.py`.
- Adapter's lint, typing, unit refer to **web only**; you must add separate FastAPI Ruff/mypy/pytest unit checks to config before treating the complete full-stack project as covered. Integration tests use FastAPI TestClient, **not** real external services by default.

## React Native / Expo

- Place project at `apps/expo` (`npx create-expo-app@latest apps/expo`).
- Install `jest-expo`, `jest`, `@types/jest`, `@testing-library/react-native` using `npx expo install ... --dev` as appropriate.
- Add package scripts `lint` (`expo lint`), `typecheck` (`tsc --noEmit`), `test:unit` (`jest --ci --runInBand`), `test:integration` (`jest --ci --runInBand --testPathPattern=integration` or corresponding current Jest syntax).
- Copy/adapt `examples/adapters/expo-home.test.tsx` to your project; actual home-screen implementation is required.
- Maestro E2E requires installed Maestro, an emulator/device running your app and configured `appId`. Copy example YAML into `apps/expo/.maestro/home.yaml`. `takeScreenshot` creates a visual artifact but doesn't automatically assert UI quality. Capture destinations may need adjustment for installed Maestro version.
- On Windows, check Maestro's current support/runtime and prefer a verified local configuration or compatible CI runner. Do not assume Android emulation is available.

## Flutter

- Place project in `apps/flutter` (requires Flutter SDK, Android Studio/SDK for Android or Windows desktop support).
- Use `flutter analyze`, `dart analyze`, `flutter test test` and `flutter test integration_test -d windows` for an enabled Windows desktop target. For Android devices, replace `windows` with device ID from `flutter devices`.
- Add `integration_test: { sdk: flutter }` to dev_dependencies; copy example to `apps/flutter/integration_test/app_test.dart`, fix package import and UI assertion.
- `integration` and `e2e` point at the same command by default: do **not** interpret as two independent test suites. Split them when separate suites exist.
- Integrations need a running compatible device/target. Flutter integration_test does not validate native permission dialogs.

## CI

`verify.yml` continues to validate the framework only; the new manual `stack-adapters.yml` runs with a selected stack on Windows, installs no app dependencies on your behalf, and fails if application/tooling is missing. Once app setup is complete, configure an application-specific CI workflow (lockfile installs, browser/SDK/emulator and build preparation) and make it required by branch protection.

## Acceptance and visual evidence

`config/acceptance.json` in V2 still covers the Python sample only. New app-specific criteria must be added with stable IDs and mapped to actual executed tests; stack run report and artifact hashes are *execution evidence*, not automatic evidence of criterion coverage. Have a reviewer inspect visuals and approve the criteria. Avoid snapshots containing personal data. Disable production credentials for test environments.
