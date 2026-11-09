SUBFUSION
Subdomain Enumeration Wrapper
=============================

OVERVIEW
--------
SubFusion runs Subfinder and Sublist3r against a domain, combines their
results, removes duplicates, and can optionally perform DNS resolution
to identify subdomains that resolve to an IP address.

SubFusion is a wrapper. It does not replace or reimplement Subfinder
or Sublist3r.

FEATURES
--------
- Runs Subfinder and Sublist3r.
- Combines results from both tools.
- Removes duplicate entries.
- Normalizes results to lowercase.
- Optionally resolves discovered names using DNS.
- Saves all results and, when requested, live results to text files.
- Allows either enumeration tool to be skipped.

REQUIREMENTS
------------
1. Python 3.8 or newer.
2. Subfinder installed and available on PATH, unless --skip-subfinder
   is used.
3. Sublist3r installed and available on PATH, or its Python script path
   supplied with --sublist3r-path, unless --skip-sublist3r is used.
4. Python package listed in requirements.txt (Colorama; optional at
   runtime because the script has a fallback when it is absent).

INSTALLATION
------------
1. Install Python 3.
2. Install the Python dependency:

       python3 -m pip install -r requirements.txt

3. Install Subfinder:

       go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

   Ensure the Go binary directory (commonly ~/go/bin) is on PATH.

4. Install Sublist3r. For example:

       git clone https://github.com/aboul3la/Sublist3r.git
       python3 -m pip install -r Sublist3r/requirements.txt

   If the `sublist3r` command is not available, pass the script path
   with --sublist3r-path.

USAGE
-----
Basic scan:

       python3 subfusion.py -d example.com

Choose an output prefix:

       python3 subfusion.py -d example.com -o results

Enumerate and resolve discovered subdomains:

       python3 subfusion.py -d example.com -o results --resolve

Set DNS resolution thread count:

       python3 subfusion.py -d example.com -o results --resolve --threads 50

Use a local Sublist3r script:

       python3 subfusion.py -d example.com --sublist3r-path Sublist3r/sublist3r.py

Skip Sublist3r:

       python3 subfusion.py -d example.com --skip-sublist3r

Skip Subfinder:

       python3 subfusion.py -d example.com --skip-subfinder

Show commands being executed:

       python3 subfusion.py -d example.com -v

Show all command-line options:

       python3 subfusion.py --help

OUTPUT FILES
------------
For an output prefix of "results":

- results_all.txt
  Contains the merged, deduplicated subdomain list.

When --resolve is used:

- results_alive.txt
  Contains resolving subdomains with their IP addresses.
- results_alive_only.txt
  Contains resolving subdomain names only.

OPTIONS
-------
-d, --domain              Target domain (required).
-o, --output              Output filename prefix.
--subfinder-path          Subfinder command or path.
--sublist3r-path          Path to sublist3r.py.
--skip-subfinder          Do not run Subfinder.
--skip-sublist3r          Do not run Sublist3r.
--subfinder-timeout       Subfinder timeout in seconds.
--sublist3r-timeout       Sublist3r timeout in seconds.
--resolve                 Perform DNS resolution.
--threads                 Number of DNS worker threads.
--resolve-timeout         DNS timeout per host.
-v, --verbose             Print the commands being run.

IMPORTANT NOTES
---------------
- Only scan domains that you own or are explicitly authorized to test.
- Subdomain enumeration may generate requests to third-party services.
- DNS resolution only confirms that a name resolves at the time of the
  check; it does not prove that a web service is available or secure.
- Results depend on the data sources and configuration of Subfinder
  and Sublist3r.
- Use the tools in accordance with their own licenses and terms.

TROUBLESHOOTING
---------------
"subfinder not found":
  Install Subfinder and ensure its executable directory is on PATH.

"sublist3r not found":
  Install Sublist3r, or provide its script path using --sublist3r-path.

No results:
  Check the target domain, tool installations, network connectivity,
  and the output of each underlying tool. Try -v for command details.

Color output unavailable:
  Install dependencies with `python3 -m pip install -r requirements.txt`.
  Colorama is optional; the script can run without it.

PROJECT FILES
-------------
subfusion.py     Main application.
README.txt       Project overview, usage, and troubleshooting.
requirements.txt Python dependency list.
INSTALL.txt      Short installation checklist.
.gitignore       Common generated files to ignore.
