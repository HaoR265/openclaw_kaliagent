Defense handles observations, evidence, anomalies, and risk interpretation.
Protected internal Wi-Fi: wlan0
External Wi-Fi for wireless mode changes: wlan1
Proxy stack is protected and must not be modified.

## Defense Tools Catalog

### Primary Tools
- Surface assessment: `oc-toolfind defense surface` (nmap, httpx, whatweb, whois, dig, theharvester)
- Directory inspection: `oc-toolfind defense directory` (ldapsearch, smbclient, enum4linux, impacket tools)
- Evidence analysis: `oc-toolfind defense evidence` (strings, readelf, objdump, binwalk)

### Quick Commands
- `oc-toolfind defense <query>` - search defense tools
- `oc-toolcat defense` - view full defense catalog
- `oc-toolfind offense <query>` - reference attack tools (for threat modeling)
