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

## Web Application Tools

### Primary Tools
- SQL injection: `sqlmap`
- Directory brute force: `ffuf`, `gobuster`
- Web fingerprinting: `whatweb`, `nikto`
- WordPress assessment: `wpscan`
- Manual testing: `curl`, `burpsuite`

### Quick Lookup
- `oc-toolfind offense web` - view all web testing tools
- `oc-toolfind offense <query>` - search tools by name/category

### Common Workflows
1. SQL injection: `sqlmap -u "<url>" --batch --level=3 --risk=2`
2. Directory discovery: `ffuf -u <url>/FUZZ -w wordlist.txt`
3. WordPress scan: `wpscan --url <url> --enumerate vp,vt,u`
4. Manual request: `curl -v "<url>" -H "Custom-Header: value"`
