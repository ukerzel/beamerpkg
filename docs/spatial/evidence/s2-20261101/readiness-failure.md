# Retained probe failure: implicit five-second readiness timeout

An additional run after adding same-node overlay swaps failed DOM readiness:
the default Playwright assertion timeout was 5,000 ms, with status still
`dom: loading`. React Flow passed in that run. No geometry/media assertion
failed. The browser trace and error context were copied to
`build/spatial-evidence/s2-readiness-failure/` before rerunning.

The plan declares startup timings diagnostic, with no five-second speed gate.
The unintended default assertion deadline was replaced by a bounded 45-second
readiness wait within the existing 60-second test timeout. Actual startup
measurements remain reported; this change does not establish acceptable
lecture startup performance. Production should show progressive loading.
