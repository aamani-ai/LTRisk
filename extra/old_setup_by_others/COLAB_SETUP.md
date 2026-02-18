# Run Climate Risk Framework on Google Colab

Yes, you can run this on **Google Colab**. Use the steps below.

---

## Option A: You have the full project (e.g. `climate_risk_framework.tar.gz`)

### 1. Upload the archive to Colab

- Open [Google Colab](https://colab.research.google.com).
- Create a new notebook.
- In the left sidebar, click the **folder icon** to open the file browser, then **Upload** and choose `climate_risk_framework.tar.gz`.

### 2. Run these cells in order

**Cell 1 – Install dependencies**
```python
!pip install -q pandas numpy scipy requests plotly dash matplotlib seaborn
```

**Cell 2 – Extract and go into the project**
```python
!tar -xzf climate_risk_framework.tar.gz
%cd climate_risk_framework
```

**Cell 3 – Run the analysis (solar, RCP 4.5)**
```python
!python main.py --asset hayhurst_solar --scenario rcp45
```

**Cell 4 (optional) – Run with Monte Carlo**
```python
!python main.py --asset hayhurst_solar --scenario rcp45 --monte-carlo
```

**Cell 5 – List outputs**
```python
!ls -la outputs/
```

---

## Option B: Project is in a GitHub repo

If the code is in a repo, clone and run:

```python
!git clone https://github.com/YOUR_ORG/climate_risk_framework.git
%cd climate_risk_framework
!pip install -q -r requirements.txt
!python main.py --asset hayhurst_solar --scenario rcp45
```

(Replace the URL with the real repo.)

---

## Running the Dashboard on Colab

The dashboard is a web app. On Colab you need to expose it.

**Cell 1 – Install and start dashboard in background**
```python
!pip install -q dash plotly pyngrok
%cd climate_risk_framework
```

**Cell 2 – Expose the app with ngrok**
```python
from pyngrok import ngrok
import subprocess
import threading

def run_dashboard():
    subprocess.run(["python", "dashboard/dashboard.py"], cwd="climate_risk_framework")

threading.Thread(target=run_dashboard, daemon=True).start()
# Wait for Dash to start
import time
time.sleep(5)

public_url = ngrok.connect(8050)
print("Open this URL in your browser:", public_url)
```

Or use Colab’s built-in port forwarding:

- Run `!python dashboard/dashboard.py` in a cell.
- Go to **Runtime → Manage sessions** or use the “Remote connection” link Colab shows for port 8050.

---

## Notes for Colab

| Item | Note |
|------|------|
| **Session** | Colab sessions end when you close the tab; re-upload or re-clone and re-run when you come back. |
| **Data** | Downloaded climate data is under `data/`; it’s lost when the runtime is recycled. Re-running will re-download. |
| **Outputs** | Download anything you need from `outputs/` (right-click in the file browser → Download) before the session ends. |
| **GPU** | Not required; the framework runs on CPU. |
| **RAM** | Default Colab is usually enough; for heavy Monte Carlo you might need “High RAM” in Runtime → Change runtime type. |

---

## Quick one-time test (no upload)

If you only have the two docs (README + QUICKSTART) and no code yet, you can’t run the framework until you have the full project (e.g. from `climate_risk_framework.tar.gz` or a repo). Once you have the archive or repo, use Option A or B above in Colab.
