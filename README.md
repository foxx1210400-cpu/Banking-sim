# Banking Life Sim

## Beta release

Version: `beta2.0.0`

This release includes the graphical life simulator with school, jobs, salaries, taxes, college, family generation, events, persistence, and the activity feed.

## Run the GUI

From the project root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe ui\gui_main.py
```

The graphical entry point is `ui/gui_main.py`. `main.py` is the legacy command-line entry point.

## Run tests

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_core
```

## Build the Windows executable

Install PyInstaller into the virtual environment, then run:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller BankingLifeSim.spec --clean
```

The executable is produced in `dist/BankingLifeSim/` or `dist/BankingLifeSim.exe`, depending on the PyInstaller configuration.
