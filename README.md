# 🔱 SubFusion — Subdomain Enumeration Tool

**SubFusion** is a lightweight Python wrapper that combines the results of **Subfinder** and **Sublist3r** to discover subdomains for a target domain. It merges the results, removes duplicates, and can optionally perform DNS resolution to identify subdomains that successfully resolve to an IP address.

> ⚠️ **Legal / Ethical use only.** Use SubFusion only on domains you own or have explicit permission to assess. Make sure your testing complies with applicable laws, program scope, and the terms of the underlying tools.

## ✨ Features

- ✅ Combines results from **Subfinder** and **Sublist3r**
- ✅ Removes duplicate subdomains from the combined results
- ✅ Normalizes discovered entries (lowercase and basic cleanup)
- ✅ Optional DNS resolution to identify names that resolve to an IP address
- ✅ Multi-threaded DNS resolution with configurable thread count
- ✅ Saves the complete discovered list to a `.txt` file
- ✅ When DNS resolution is enabled, saves live names with IPs and names-only output
- ✅ Run either tool independently using the skip options
- ✅ Configurable timeouts for both enumeration tools and DNS resolution
- ✅ Colored terminal output when Colorama is installed
- ✅ Verbose mode to display the commands being executed

## 🧰 Requirements

- Python **3.8 or newer**
- [Subfinder](https://github.com/projectdiscovery/subfinder)
- [Sublist3r](https://github.com/aboul3la/Sublist3r)
- Python package: `colorama` (optional; the script has a fallback if it is not installed)

SubFusion is an aggregator/wrapper. It invokes Subfinder and Sublist3r as external tools; it does not include or reimplement them.

## 📦 Installation

### 1. Get the project

If you have cloned the repository:

```bash
git clone <your-repository-url>
cd subfusion
```

Or download the project files and open a terminal in the project folder.

### 2. Install Python dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Install Subfinder

Install Subfinder using Go:

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

Make sure the Go binary directory (commonly `~/go/bin`) is included in your system's `PATH`.

### 4. Install Sublist3r

```bash
git clone https://github.com/aboul3la/Sublist3r.git
python3 -m pip install -r Sublist3r/requirements.txt
```

If the `sublist3r` command is not available, provide the path to `sublist3r.py` with `--sublist3r-path` (see examples below).

## 🚀 Usage

### Basic enumeration

```bash
python3 subfusion.py -d example.com
```

### Set an output filename prefix

```bash
python3 subfusion.py -d example.com -o results
```

### Enumerate and perform DNS resolution

```bash
python3 subfusion.py -d example.com -o results --resolve
```

### Change DNS resolution thread count

```bash
python3 subfusion.py -d example.com -o results --resolve --threads 50
```

### Use a local Sublist3r script

```bash
python3 subfusion.py -d example.com \
  --sublist3r-path Sublist3r/sublist3r.py
```

### Run only Subfinder

```bash
python3 subfusion.py -d example.com --skip-sublist3r
```

### Run only Sublist3r

```bash
python3 subfusion.py -d example.com --skip-subfinder
```

### Display executed commands

```bash
python3 subfusion.py -d example.com -v
```

### Display help

```bash
python3 subfusion.py --help
```

Replace `example.com` with a domain you own or are authorized to test.

## ⚙️ Command-line options

| Flag | Description | Default |
|---|---|---|
| `-d, --domain` | Target domain (required) | — |
| `-o, --output` | Output file prefix | `subfusion_results` |
| `--subfinder-path` | Subfinder command or executable path | `subfinder` |
| `--sublist3r-path` | Path to `sublist3r.py` when not using the `sublist3r` command | — |
| `--skip-subfinder` | Skip Subfinder | Off |
| `--skip-sublist3r` | Skip Sublist3r | Off |
| `--subfinder-timeout` | Subfinder timeout in seconds | `180` |
| `--sublist3r-timeout` | Sublist3r timeout in seconds | `300` |
| `--resolve` | Resolve discovered subdomains using DNS | Off |
| `--threads` | Number of DNS worker threads | `50` |
| `--resolve-timeout` | DNS timeout per host, in seconds | `3` |
| `-v, --verbose` | Show the exact commands being executed | Off |

## 📁 Output

For this command:

```bash
python3 subfusion.py -d example.com -o results --resolve
```

SubFusion creates:

| File | Description |
|---|---|
| `results_all.txt` | All unique discovered subdomains |
| `results_alive.txt` | Subdomains that resolved, along with their IP addresses |
| `results_alive_only.txt` | Names of subdomains that resolved, without IP addresses |

If `--resolve` is not used, only the `_all.txt` file is created.

## 🔍 How it works

1. Runs Subfinder against the supplied domain (unless skipped).
2. Runs Sublist3r against the supplied domain (unless skipped).
3. Collects the output from both tools.
4. Cleans and lowercases entries, then merges and deduplicates them.
5. Writes the combined list to `<output>_all.txt`.
6. If `--resolve` is enabled, performs DNS lookups and writes the resolving results to separate files.

**Note:** DNS resolution only indicates that a hostname resolved during the check. It does not confirm that a website is reachable, that a service is running, or that the host is secure.

## 🛠️ Troubleshooting

**`subfinder not found`**

Install Subfinder and ensure its executable directory is included in `PATH`.

**`sublist3r not found`**

Install Sublist3r, or provide the script location:

```bash
python3 subfusion.py -d example.com \
  --sublist3r-path Sublist3r/sublist3r.py
```

**No subdomains are returned**

- Confirm that the target domain is correct.
- Check that the required tools are installed and working.
- Check your network connection.
- Run with `-v` to display the commands being executed.
- Remember that results depend on the data sources available to the underlying tools.

**Color output is unavailable**

Install Colorama:

```bash
python3 -m pip install colorama
```

Colorama is optional; SubFusion can still run without it.

## 📂 Project structure

```text
subfusion/
├── subfusion.py
├── README.md
├── README.txt
├── requirements.txt
├── INSTALL.txt
└── .gitignore
```

## ⚖️ Disclaimer

SubFusion is provided for authorized security testing, asset discovery, and educational use. Only scan systems for which you have permission. The user is responsible for complying with applicable laws, rules of engagement, and the licenses and terms of Subfinder and Sublist3r. The author is not responsible for misuse or damage resulting from use of this tool.

## 📄 License

No license has been specified for this project yet. Add a `LICENSE` file before distributing the project under an open-source license.
