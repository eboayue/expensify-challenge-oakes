#!/usr/bin/env python3
import sys
import socket

def main():
    with open('/etc/nagios4/webservers.txt') as f:
        servers = [line.strip() for line in f if line.strip()]
    down = []
    for server in servers:
        try:
            socket.create_connection((server, 80), timeout=3).close()
        except:
            down.append(server)
    if len(down) == 0:
        print("OK: All webservers are up.")
        sys.exit(0)
    elif len(down) == 1:
        print(f"WARNING: {down[0]} is down.")
        sys.exit(1)
    else:
        print(f"CRITICAL: All webservers are down.")
        sys.exit(2)

if __name__ == "__main__":
    main()
