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

## Social Engineering Tools

### Information Gathering
- OSINT collection: `oc-toolfind offense recon` (theharvester, amass, whois)
- Web reconnaissance: `oc-toolfind offense web` (whatweb, nikto, curl)

### Wordlist Generation
- `oc-toolfind offense passwords` (cewl, crunch)
- Cewl for website content scraping
- Crunch for pattern-based wordlist generation

### Quick Lookup
- `oc-toolfind offense <query>` - search offense tools
- `oc-toolfind command-rare <query>` - search special tools

### Note on Social Engineering
Social engineering primarily involves psychological manipulation rather than technical tools. Use:
- Information gathered from recon tools for targeting
- Wordlists for password spraying or credential stuffing
- Open-source intelligence for pretext development
