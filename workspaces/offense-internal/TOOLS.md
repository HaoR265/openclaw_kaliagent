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

## Internal Penetration Tools

### Primary Tools
- AD enumeration: `bloodhound-python`, `enum4linux`
- SMB access: `smbclient`, `impacket-smbclient`
- WinRM access: `evil-winrm`
- Network execution: `netexec`
- LLMNR/NBT-NS poisoning: `responder`

### Advanced Impacket Tools (rare catalog)
- `oc-toolfind command-rare impacket` (secretsdump, psexec, wmiexec, etc.)
- Use with caution - these are powerful internal movement tools

### Quick Lookup
- `oc-toolfind offense ad` - view all AD/Internal tools
- `oc-toolfind command-rare` - view advanced/special tools

### Common Workflows
1. SMB enumeration: `enum4linux -a <target>`
2. Bloodhound collection: `bloodhound-python -d <domain> -u <user> -p <pass> -ns <dc>`
3. Credential dumping: `impacket-secretsdump <domain>/<user>:<pass>@<target>`
