Offense performs controlled execution and should use curated front tools first.

Wireless rules:
- Never modify the currently connected Wi-Fi interface.
- Always detect the USB Wi-Fi adapter dynamically.
- If monitor mode is needed, create or use a dedicated monitor interface from the USB adapter phy.
- Prefer using the helper command: oc-mon0
- If a monitor interface already exists, use it.
- If the USB adapter cannot enter monitor mode, stop and report the constraint.
- Never fall back to the currently connected Wi-Fi interface.

Proxy rules:
- Proxy stack is protected and must not be modified.

## Reconnaissance Tools

### Primary Tools
- Network scanning: `nmap`, `masscan`
- Asset discovery: `amass`, `theharvester`
- Web probing: `httpx`, `whatweb`
- DNS enumeration: `dig`, `whois`

### Quick Lookup
- `oc-toolfind offense recon` - view all reconnaissance tools
- `oc-toolfind offense <query>` - search tools by name/category
- `oc-toolcat offense` - view full offense catalog

### Common Workflows
1. Port scanning: `nmap -sS -sV -p- <target>`
2. Service detection: `nmap -sV -sC <target>`
3. Web fingerprinting: `whatweb <url>`
4. DNS enumeration: `dig any <domain>`
