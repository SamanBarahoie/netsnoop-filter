#!/usr/bin/env python3
import psutil
import socket
import argparse
import textwrap

# ———————— Helpers ————————

def is_private_ip(ip: str) -> bool:
    """
    Determine whether the given IP address is in a private range.
    """
    try:
        return ip.startswith("10.") or \
               ip.startswith("172.") or \
               ip.startswith("192.168.") or \
               ip == "127.0.0.1"
    except:
        return False

# ———————— Filter Rules ————————

# Each rule is defined as a tuple: (name, condition function)
# ———————— Filter Rules ————————

# Each rule is defined as a tuple: (name, condition function)
RULES = [
    ("External IP",
     lambda proc, conn, cc: conn.raddr is not None and not is_private_ip(conn.raddr.ip)),
    ("Suspicious Path",
     lambda proc, conn, cc: any(x in proc.exe().lower() for x in ("temp","appdata","roaming"))),
    ("Suspicious Parent",
     lambda proc, conn, cc: psutil.Process(proc.ppid()).name().lower()
                             in ("powershell.exe","cmd.exe","python.exe")),
    ("High Port",
     lambda proc, conn, cc: conn.raddr is not None and conn.raddr.port > 10000),
    ("Local High Port",
     lambda proc, conn, cc: conn.raddr is not None
                             and conn.raddr.ip == "127.0.0.1"
                             and conn.raddr.port > 10000),
    ("Too Many Connections",
     lambda proc, conn, cc: cc.get(conn.pid, 0) > 5),
    ("Close Wait",
     lambda proc, conn, cc: conn.status == "CLOSE_WAIT"),
]

def match_filters(proc, conn, conn_count, enabled_rules):
    """
    Return a list of rule names that match for the given process and connection.
    """
    matched = []
    for idx in enabled_rules:
        name, condition = RULES[idx]
        try:
            if condition(proc, conn, conn_count):
                matched.append(name)
        except Exception:
            pass
    return matched

# ———————— Core Logic ————————

def gather_connections():
    """
    Retrieve all inet connections and count ESTABLISHED connections per PID.
    """
    conns = psutil.net_connections(kind='inet')
    conn_count = {}
    for c in conns:
        if c.pid and c.status == "ESTABLISHED":
            conn_count[c.pid] = conn_count.get(c.pid, 0) + 1
    return conns, conn_count

def filter_and_list(enabled_rules):
    """
    Apply the enabled filter rules and return a list of matching entries.
    """
    conns, conn_count = gather_connections()
    results = []
    for c in conns:
        if not c.pid or c.status != "ESTABLISHED":
            continue
        try:
            proc = psutil.Process(c.pid)
        except psutil.NoSuchProcess:
            continue
        matched = match_filters(proc, c, conn_count, enabled_rules)
        if matched:
            results.append((proc, c, matched))
    # sort by number of matched rules descending
    results.sort(key=lambda x: len(x[2]), reverse=True)
    return results

def print_header():
    print("=" * 80)
    print(" Index │ PID   │ Process           │ Local                │ Remote               │ Matched Filters")
    print("-" * 80)

def print_connection(idx, proc, conn, matched):
    l = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
    r = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
    print(f" {idx:<5} │ {proc.pid:<5} │ {proc.name():<17} │ {l:<20} │ {r:<20} │ {', '.join(matched)}")

def interactive_detail(proc, conn):
    """
    Display detailed information about a specific process and its connections.
    """
    print("\n" + "-" * 40)
    print(f"PID: {proc.pid}  Name: {proc.name()}")
    try:
        print(f"Executable: {proc.exe()}")
    except psutil.AccessDenied:
        print("Executable: [Access Denied]")
    print(f"Command Line: {' '.join(proc.cmdline())}")
    print(f"Connection Status: {conn.status}")
    print(f"Open Files: {len(proc.open_files())}")
    print("All Connections for this PID:")
    for c2 in psutil.net_connections(kind='inet'):
        if c2.pid == proc.pid:
            addr = f"{c2.laddr} → {c2.raddr}"
            print(f"  - {addr} [{c2.status}]")
    print("-" * 40 + "\n")

# ———————— Command-Line Interface ————————

def main():
    parser = argparse.ArgumentParser(
        prog="netsnoop-filter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            netsnoop-filter:
            Filter and list network connections matching user-selected rules.
            You can enable or disable specific rules before viewing results.
        """))
    parser.add_argument(
        "-r", "--rules", type=int, nargs="+", default=list(range(len(RULES))),
        help="Indices of rules to apply (e.g. -r 0 3 5).")
    args = parser.parse_args()

    print_header()
    results = filter_and_list(args.rules)
    for i, (proc, conn, matched) in enumerate(results, 1):
        print_connection(i, proc, conn, matched)

    if not results:
        print("\nNo connections matched the selected filters.")
        return

    choice = input("\nEnter an index to view details (or press Enter to exit): ")
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(results):
            proc, conn, _ = results[idx]
            interactive_detail(proc, conn)

if __name__ == "__main__":
    main()
