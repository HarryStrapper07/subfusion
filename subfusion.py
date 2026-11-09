#!/usr/bin/env python3
"""
=========================================================
  SUBFUSION 🔱 - Subdomain Enumeration (Subfinder + Sublist3r)
=========================================================
Runs Subfinder AND Sublist3r against a target domain, merges +
dedupes their results, and (optionally) resolves each subdomain
to filter down to only the LIVE ones.

Author : harry_strapper
Usage  :
    python3 subfusion.py -d example.com -o results
    python3 subfusion.py -d example.com -o results --resolve --threads 50

Requires both tools to actually be installed (see --help / README
for install commands) - SubFusion is a wrapper/aggregator, not a
reimplementation of either tool.
=========================================================
"""

import argparse
import concurrent.futures
import os
import socket
import subprocess
import sys
import tempfile
import time

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _Dummy:
        def __getattr__(self, _):
            return ""
    Fore = Style = _Dummy()

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass


def banner():
    print(Fore.MAGENTA + Style.BRIGHT + r"""
   _____       _     ______           _             
  / ____|     | |   |  ____|         (_)            
 | (___  _   _| |__ | |__ _   _ ___  _  ___  _ __    
  \___ \| | | | '_ \|  __| | | / __|| |/ _ \| '_ \   
  ____) | |_| | |_) | |  | |_| \__ \| | (_) | | | |  
 |_____/ \__,_|_.__/|_|   \__,_|___/|_|\___/|_| |_|  
""" + Style.RESET_ALL + "      Subdomain Enumeration: Subfinder + Sublist3r 🔱\n"
          "      Made by harry_strapper\n")


def run_subfinder(domain, subfinder_path="subfinder", timeout=180, verbose=False):
    """
    Runs subfinder in silent mode (-silent gives clean one-per-line
    output, no banner/noise) and returns the list of subdomains found.
    """
    print(f"[*] Running subfinder for {domain} ...")
    cmd = [subfinder_path, "-d", domain, "-silent", "-all"]
    if verbose:
        print(f"    [cmd] {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        subs = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        print(f"[+] subfinder found {len(subs)} subdomain(s)")
        return subs
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] subfinder not found on PATH. Install it with:\n"
              f"    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest\n"
              f"    (make sure $GOPATH/bin or $HOME/go/bin is in your PATH)\n"
              f"    Skipping subfinder, continuing with other source(s).{Style.RESET_ALL}")
        return []
    except subprocess.TimeoutExpired:
        print(f"{Fore.YELLOW}[!] subfinder timed out after {timeout}s - try increasing "
              f"--subfinder-timeout. Continuing with what else we have.{Style.RESET_ALL}")
        return []


def run_sublist3r(domain, sublist3r_path=None, timeout=300, verbose=False):
    """
    Runs Sublist3r. Sublist3r doesn't give a clean stdout-only mode,
    so we have it write to a temp file with -o and read that back.

    sublist3r_path:
        - None            -> try the `sublist3r` command directly (pip install)
        - path to .py file -> run as `python3 <path> -d domain -o tmp`
    """
    print(f"[*] Running sublist3r for {domain} ...")
    tmp_fd, tmp_path = tempfile.mkstemp(prefix="subfusion_sublist3r_", suffix=".txt")
    os.close(tmp_fd)

    if sublist3r_path:
        cmd = ["python3", sublist3r_path, "-d", domain, "-o", tmp_path]
    else:
        cmd = ["sublist3r", "-d", domain, "-o", tmp_path]

    if verbose:
        print(f"    [cmd] {' '.join(cmd)}")

    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] sublist3r not found. Install it with EITHER:\n"
              f"      pip install sublist3r --break-system-packages\n"
              f"    OR clone it and point to the script:\n"
              f"      git clone https://github.com/aboul3la/Sublist3r.git\n"
              f"      pip install -r Sublist3r/requirements.txt --break-system-packages\n"
              f"      python3 subfusion.py -d {domain} --sublist3r-path Sublist3r/sublist3r.py\n"
              f"    Skipping sublist3r, continuing with other source(s).{Style.RESET_ALL}")
        _cleanup(tmp_path)
        return []
    except subprocess.TimeoutExpired:
        print(f"{Fore.YELLOW}[!] sublist3r timed out after {timeout}s - try increasing "
              f"--sublist3r-timeout. Continuing with what else we have.{Style.RESET_ALL}")
        _cleanup(tmp_path)
        return []

    subs = []
    if os.path.exists(tmp_path):
        with open(tmp_path) as f:
            subs = [line.strip() for line in f if line.strip()]
    _cleanup(tmp_path)
    print(f"[+] sublist3r found {len(subs)} subdomain(s)")
    return subs


def _cleanup(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def resolve_subdomain(sub, timeout=3):
    """DNS-resolves a subdomain. Returns (subdomain, ip_or_None, is_alive)."""
    try:
        socket.setdefaulttimeout(timeout)
        ip = socket.gethostbyname(sub)
        return sub, ip, True
    except Exception:
        return sub, None, False


def resolve_all(subdomains, threads=50, timeout=3):
    print(f"\n[*] Resolving {len(subdomains)} subdomain(s) to find live hosts "
          f"(threads={threads}) ...")
    alive = []
    dead_count = 0
    completed = 0
    start = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(resolve_subdomain, sub, timeout): sub for sub in subdomains}
        for future in concurrent.futures.as_completed(futures):
            sub, ip, is_alive = future.result()
            completed += 1
            if is_alive:
                alive.append((sub, ip))
                print(f"{Fore.GREEN}[alive]{Style.RESET_ALL} {sub} -> {ip}")
            else:
                dead_count += 1

            if completed % 50 == 0 or completed == len(subdomains):
                elapsed = time.time() - start
                print(f"{Fore.CYAN}[progress]{Style.RESET_ALL} {completed}/{len(subdomains)} "
                      f"resolved | alive: {len(alive)} | elapsed: {elapsed:.0f}s")

    print(f"[+] Resolution done: {len(alive)} alive, {dead_count} did not resolve\n")
    # keep original (sorted) order for stable output
    alive_set = {s for s, _ in alive}
    alive_sorted = [(s, ip) for s, ip in sorted(alive, key=lambda x: x[0])]
    return alive_sorted


def main():
    parser = argparse.ArgumentParser(description="SubFusion - Subdomain enumeration via Subfinder + Sublist3r")
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g. example.com)")
    parser.add_argument("-o", "--output", default="subfusion_results",
                         help="Output file prefix (default: subfusion_results)")
    parser.add_argument("--subfinder-path", default="subfinder",
                         help="Path/command for subfinder (default: 'subfinder', assumes it's on PATH)")
    parser.add_argument("--sublist3r-path", default=None,
                         help="Path to sublist3r.py if not installed as a 'sublist3r' command "
                              "(e.g. ./Sublist3r/sublist3r.py)")
    parser.add_argument("--skip-subfinder", action="store_true", help="Don't run subfinder")
    parser.add_argument("--skip-sublist3r", action="store_true", help="Don't run sublist3r")
    parser.add_argument("--subfinder-timeout", type=int, default=180,
                         help="Timeout in seconds for subfinder (default: 180)")
    parser.add_argument("--sublist3r-timeout", type=int, default=300,
                         help="Timeout in seconds for sublist3r (default: 300, it's slower)")
    parser.add_argument("--resolve", action="store_true",
                         help="DNS-resolve every discovered subdomain and additionally save only "
                              "the LIVE ones to a separate file")
    parser.add_argument("--threads", type=int, default=50,
                         help="Threads used for DNS resolution with --resolve (default: 50)")
    parser.add_argument("--resolve-timeout", type=int, default=3,
                         help="Per-host DNS resolution timeout in seconds (default: 3)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show the exact commands being run")
    args = parser.parse_args()

    banner()

    if args.skip_subfinder and args.skip_sublist3r:
        sys.exit("[!] You skipped both tools - nothing to run.")

    all_subs = set()

    if not args.skip_subfinder:
        subfinder_results = run_subfinder(
            args.domain, subfinder_path=args.subfinder_path,
            timeout=args.subfinder_timeout, verbose=args.verbose
        )
        all_subs.update(subfinder_results)

    if not args.skip_sublist3r:
        sublist3r_results = run_sublist3r(
            args.domain, sublist3r_path=args.sublist3r_path,
            timeout=args.sublist3r_timeout, verbose=args.verbose
        )
        all_subs.update(sublist3r_results)

    # Basic cleanup: lowercase, strip stray wildcards/protocol prefixes
    # some tools occasionally include.
    cleaned = set()
    for s in all_subs:
        s = s.strip().lower()
        s = s.replace("https://", "").replace("http://", "")
        s = s.rstrip("/").lstrip("*.")
        if s and args.domain in s:
            cleaned.add(s)

    merged = sorted(cleaned)

    print(f"\n[+] Total UNIQUE subdomains after merging: {len(merged)}")

    all_path = f"{args.output}_all.txt"
    with open(all_path, "w") as f:
        f.write("\n".join(merged))
    print(f"[+] Saved merged list: {all_path}")

    if args.resolve and merged:
        alive = resolve_all(merged, threads=args.threads, timeout=args.resolve_timeout)
        alive_path = f"{args.output}_alive.txt"
        with open(alive_path, "w") as f:
            f.write("\n".join(f"{s} {ip}" for s, ip in alive))
        alive_only_path = f"{args.output}_alive_only.txt"
        with open(alive_only_path, "w") as f:
            f.write("\n".join(s for s, _ in alive))
        print(f"[+] Saved alive (with IP) list : {alive_path}")
        print(f"[+] Saved alive (names only)   : {alive_only_path}")

    print("\n" + "=" * 60)
    print(f"[+] Done. {len(merged)} unique subdomain(s) found for {args.domain}")
    if args.resolve:
        print(f"[+] {len(alive) if merged else 0} confirmed alive")
    print("=" * 60)


if __name__ == "__main__":
    main()
