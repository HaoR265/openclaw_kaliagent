Command does analysis and delegation.
Command must not absorb execution tasks that belong to offense.
Never instruct anyone to modify the currently connected Wi-Fi interface.
Any wireless monitor-mode action must use the USB Wi-Fi adapter only.
If the USB adapter cannot enter monitor mode, stop and report the constraint.
Proxy stack is protected and must not be modified.

## Tool Discovery (for delegation planning)

### Offense Tools Catalog
- Recon: `oc-toolfind offense recon` (nmap, masscan, amass, theharvester, httpx, whatweb, whois, dig)
- Web: `oc-toolfind offense web` (sqlmap, burpsuite, ffuf, gobuster, nikto, wpscan, curl, wfuzz)
- AD: `oc-toolfind offense ad` (bloodhound-python, enum4linux, evil-winrm, netexec, responder, impacket suite)
- Reverse: `oc-toolfind offense reverse` (radare2, gdb, binwalk, strings, readelf, objdump)
- Passwords: `oc-toolfind offense passwords` (john, hashcat, hydra, cewl, crunch)

### Defense Tools Catalog
- Surface: `oc-toolfind defense surface` (nmap, httpx, whatweb, whois, dig, theharvester)
- Directory: `oc-toolfind defense directory` (ldapsearch, smbclient, enum4linux, impacket tools)
- Evidence: `oc-toolfind defense evidence` (strings, readelf, objdump, binwalk)

### Special Commands
- `oc-toolfind command-rare` (john-extractors, impacket-rare, wireless-special, etc.)
- `oc-toolcat offense|defense|command-rare` (view full catalog)
