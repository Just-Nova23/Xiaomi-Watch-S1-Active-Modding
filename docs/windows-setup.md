# Windows and Linux setup

The project works on Windows PowerShell, Windows Subsystem for Linux, and ordinary Linux. Pick one environment for each experiment and record it. Do not mix Windows and WSL paths inside the same command unless you understand how they map.

## Directory layout

Create a parent directory with separate public and private areas:

```text
S1ActiveResearch/
├── Xiaomi-Watch-S1-Active-Modding/   public Git clone
├── private-inputs/                    firmware and purchased files
├── generated/                         extracted components and reports
└── notes/                             sanitized experiment notes
```

`private-inputs` and `generated` must remain outside the repository. The repository `.gitignore` is a second defense, not permission to store proprietary files in its working tree.

## Windows PowerShell

### 1. Install prerequisites

Install:

- [Git for Windows](https://git-scm.com/download/win);
- [Python for Windows](https://www.python.org/downloads/windows/) 3.11 or newer;
- optionally [Ghidra](https://github.com/NationalSecurityAgency/ghidra/releases) and its required 64-bit JDK.

During Python installation, enable the launcher or ensure `python` is available in a new terminal.

### 2. Verify commands

```powershell
git --version
python --version
python -m pip --version
```

Expected result: each command prints a version and exits without an error. If the Microsoft Store opens instead of Python, disable the Python App Installer aliases in Windows settings or use the `py` launcher.

### 3. Clone and create an isolated environment

```powershell
New-Item -ItemType Directory -Path "$HOME\Documents\S1ActiveResearch"
Set-Location "$HOME\Documents\S1ActiveResearch"
git clone https://github.com/Just-Nova23/Xiaomi-Watch-S1-Active-Modding.git
Set-Location Xiaomi-Watch-S1-Active-Modding
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, you can call the environment interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Do not weaken the machine-wide execution policy merely to activate a virtual environment.

### 4. Create private directories

```powershell
New-Item -ItemType Directory -Force -Path "..\private-inputs", "..\generated", "..\notes"
```

### 5. Hash an input

```powershell
Get-FileHash "..\private-inputs\stock.pkg" -Algorithm SHA256 | Format-List
```

Copy the hash into a private notebook. Do not rename two different files to the same generic name without recording their hashes.

## Linux or WSL

### 1. Verify prerequisites

```bash
git --version
python3 --version
python3 -m pip --version
```

Install missing packages through your distribution. On Debian or Ubuntu, the virtual-environment module may be packaged separately as `python3-venv`.

### 2. Clone and create an environment

```bash
mkdir -p "$HOME/S1ActiveResearch"
cd "$HOME/S1ActiveResearch"
git clone https://github.com/Just-Nova23/Xiaomi-Watch-S1-Active-Modding.git
cd Xiaomi-Watch-S1-Active-Modding
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
mkdir -p ../private-inputs ../generated ../notes
```

Python's official [`venv` documentation](https://docs.python.org/3/library/venv.html) explains that environments are isolated, disposable, and should not be committed.

### 3. Hash an input

```bash
sha256sum ../private-inputs/stock.pkg
```

## Run the repository checks

From the repository root:

```bash
python -m unittest discover -s tests -v
python -m compileall -q tools tests
```

Expected tests:

- an outer GUI record survives a byte-identical build/split round trip;
- a bad path CRC is rejected;
- the assistant patch changes exactly one synthetic byte;
- a mismatched patch context is rejected without output.

These tests validate the public tools. They do not validate your private firmware automatically.

## Optional analysis tools

| Tool | Purpose | Required? |
|---|---|---|
| Ghidra | interactive disassembly, cross-references, decompilation | no |
| Capstone | scripted instruction decoding used by `thumb_xrefs.py` | installed from `requirements.txt` |
| Rizin | alternative command-line analysis | no |
| hex editor | inspect exact byte ranges | helpful |
| Git | version public scripts and notes, never firmware | yes |

Download tools from their official projects. Avoid random repackaged executables, especially for tools that will open untrusted or malformed binaries.

## Common setup failures

### `ModuleNotFoundError: capstone`

Activate the same virtual environment in which dependencies were installed, then run:

```bash
python -m pip install -r requirements.txt
python -c "import capstone; print(capstone.__version__)"
```

### `python` and `python3` use different installations

Print both executable paths:

```bash
python -c "import sys; print(sys.executable)"
python3 -c "import sys; print(sys.executable)"
```

Use one interpreter consistently.

### File paths fail in WSL

A Windows path such as `C:\Users\name\file.pkg` maps under WSL to a path similar to `/mnt/c/Users/name/file.pkg`. Prefer keeping the project and temporary analysis data on the same filesystem for predictable performance.

### Ghidra imports the file but shows nonsense

A raw binary has no embedded loader metadata. Import settings, processor mode, base address, and code/data boundaries must be supplied correctly. Follow [Ghidra and ARM workflow](ghidra-workflow.md) rather than accepting every auto-analysis result.
