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

## Wireless Tools

### Monitoring Setup
- `oc-mon0` - create monitor interface on USB Wi-Fi adapter
- Check current interface: `iw dev` or `ip link show`

### Wireless Assessment Tools
- `oc-toolfind command-rare wireless` (aircrack-ng suite)
- `oc-toolfind command-rare network` (ettercap for network interception)

### General Offense Tools (when needed)
- Recon: `oc-toolfind offense recon`
- Passwords: `oc-toolfind offense passwords` (for cracking captured hashes)
