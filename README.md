# NetSnoop Network Monitor

A simple, Python‑based toolset for filtering and inspecting network connections on a host. Includes:

* **netsnoop-filter**: Interactive CLI to list and filter active TCP/UDP connections by user‑selected rules.
* **simple\_server**: Minimal TCP server to generate test connections and observe socket states (e.g., ESTABLISHED, CLOSE\_WAIT).

---

## Requirements

* Python 3.7 or later
* [psutil](https://pypi.org/project/psutil/) (for `netsnoop-filter`)

Install dependencies:

```bash
pip install psutil
```

---

## netsnoop-filter

### Description

`netsnoop-filter` inspects all active network connections, applies a set of filter rules, and presents matching entries. The user can enable or disable specific rules and then interactively view connection details and process information.

### Supported Rules

1. **External IP**
   Match connections whose remote IP is outside private ranges.

2. **Suspicious Path**
   Match processes running from paths containing “temp”, “appdata” or “roaming”.

3. **Suspicious Parent**
   Match processes launched by `powershell.exe`, `cmd.exe` or `python.exe`.

4. **High Port**
   Match connections to remote ports above 10000.

5. **Local High Port**
   Match connections to `127.0.0.1` on ports above 10000.

6. **Too Many Connections**
   Match processes with more than 5 simultaneous ESTABLISHED connections.

7. **Close Wait**
   Match any connection in the `CLOSE_WAIT` state.

### Usage

```bash
python netsnoop-filter.py               # apply all rules
python netsnoop-filter.py -r 0 3 6      # apply only rules 0 (External IP), 3 (High Port), 6 (Close Wait)
```

After the list is printed, enter an index number to view detailed information about that connection.

---

## simple\_server

### Description

`simple_server.py` is a minimal TCP server that listens on a specified port, accepts incoming connections, and holds them open until the client disconnects or a timeout occurs. Use it alongside `netsnoop-filter` to generate and observe test connections.

### Usage

```bash
python simple_server.py
```

The server listens on port `12345` by default. You can modify `HOST` and `PORT` variables at the top of the script as needed.

---

## Testing Workflow

1. Start the server:

   ```bash
   python simple_server.py
   ```

2. In another terminal, run a test client (for example, a simple socket script) to connect to the server.

3. On the host where you ran `simple_server.py`, run:

   ```bash
   python netsnoop-filter.py -r 6
   ```

   to list and inspect any connections in the `CLOSE_WAIT` state.

4. View details when prompted.

---

## License

This project is released under the MIT License. See `LICENSE` for details.
