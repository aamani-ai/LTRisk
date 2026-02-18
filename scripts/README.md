# scripts/

Runnable Python scripts for the LTRisk project.

---

## What Belongs Here vs `notebook_analysis/`

| Location | Use for |
|---|---|
| `scripts/` | Standalone Python scripts: data pipelines, batch jobs, utilities |
| `scripts/tests/` | Quick validation scripts — run before notebooks to confirm APIs and math work |
| `notebook_analysis/` | Jupyter notebooks for exploratory analysis and visualisation |

Scripts in this folder should be importable and runnable from the project root
with the venv activated:

```bash
source .venv/bin/activate
python scripts/some_script.py
```

---

## Sub-folders

### `tests/`

Quick validation scripts — not a test framework, just short scripts that confirm
a specific thing works (API connectivity, file I/O, a calculation). See
`tests/README.md` for details.

---

## Coming Scripts (planned)

- `fetch_cmip6_site.py` — CLI wrapper to pull and cache CMIP6 data for any site in `sites.json`
- `compute_scvr.py` — Batch SCVR computation across multiple sites and scenarios
