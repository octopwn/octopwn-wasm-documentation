# RDP Client

The **RDP Client** speaks the Remote Desktop Protocol (`MS-RDPBCGR` and friends) against Windows hosts. It wraps [`aardwolf`](https://github.com/skelsec/aardwolf) for the protocol stack and renders the remote desktop into an HTML5 canvas inside the session window. Default port `3389`.

The client is GUI-first: the **Screen** tab is the default view on session open and is where you'll spend nearly all your time. The CLI surface is small and mostly oriented around supplementary actions (clipboard, screenshot capture, scripted keystrokes, optional session recording).

---

## Authentication

The RDP client supports three authentication protocols, covering the realistic combinations exposed by Windows RDP servers (modern NLA-protected NTLM/Kerberos and legacy non-NLA password auth).

| `atype`    | Underlying creds | Notes                                                                                                  |
| ---------- | ---------------- | ------------------------------------------------------------------------------------------------------ |
| `NTLM`     | NTLM             | Wrapped inside CredSSP/NLA. Hash and AES-key variants only work if the server has **RestrictedAdminMode** enabled. |
| `KERBEROS` | Kerberos         | Wrapped inside CredSSP/NLA. Hash and AES-key variants only work with **RestrictedAdminMode**; password and ticket-based variants always work. |
| `PLAIN`    | password / none  | Legacy non-NLA RDP. Only works against servers that have NLA disabled.                                  |

### NTLM credentials

| Secret type   | Description                                                          | Example                |
| ------------- | -------------------------------------------------------------------- | ---------------------- |
| `password`    | Cleartext password.                                                  | `username:Pa55w0rd!`   |
| `pwhex`       | Hex-encoded UTF-16LE password (for non-ASCII passwords).             | `username:70617373…`   |
| `nt`          | NT hash. Requires **RestrictedAdminMode** on the server.             | `username:aad3b…`      |
| `rc4`         | RC4 (synonym for NT). Requires **RestrictedAdminMode** on the server. | `username:aad3b…`      |
| `agentproxy`  | Use a remote NTLM signer over the wsnet agent proxy.                 | n/a                    |
| `sspiproxy`   | Use the OS's SSPI session via the wsnet agent proxy (Windows agent). | n/a                    |

### Kerberos credentials

| Secret type     | Description                                                              | Example                              |
| --------------- | ------------------------------------------------------------------------ | ------------------------------------ |
| `password`      | Cleartext password.                                                      | `username:Pa55w0rd!`                 |
| `pwhex`         | Hex-encoded UTF-16LE password.                                           | `username:70617373…`                 |
| `nt` / `rc4`    | NT/RC4 hash. Requires **RestrictedAdminMode** on the server.             | `username:aad3b…`                    |
| `aes128`        | AES128 long-term key. Requires **RestrictedAdminMode** on the server.    | `username:<32-hex>`                  |
| `aes256`        | AES256 long-term key. Requires **RestrictedAdminMode** on the server.    | `username:<64-hex>`                  |
| `keytab`        | Kerberos keytab file in OctoPwn volatile storage.                        | `/browserfs/volatile/admin.keytab`   |
| `keytabb64`     | Base64-encoded keytab inline.                                            | `username:<b64>`                     |
| `ccache`        | MIT ccache file in OctoPwn volatile storage.                             | `/browserfs/volatile/krb5cc.ccache`  |
| `ccacheb64`     | Base64-encoded ccache inline.                                            | `username:<b64>`                     |
| `kirbi`         | `.kirbi` ticket file (Rubeus-style).                                     | `/browserfs/volatile/admin.kirbi`    |
| `kirbib64`      | Base64-encoded `.kirbi` inline.                                          | `username:<b64>`                     |
| `pfxb64`        | Base64-encoded PFX (PKINIT certificate auth).                            | `username:<b64>`                     |

!!! info "About RestrictedAdminMode"
    Standard CredSSP requires the server to receive a usable cleartext password (or the ability to derive one) so that single-sign-on into local resources works. **RestrictedAdminMode** is a Windows feature that allows CredSSP to accept a hash or AES key directly without the cleartext, at the cost of disabling onward SSO from the RDP session. It's controlled by the `DisableRestrictedAdmin` registry value under `HKLM\System\CurrentControlSet\Control\Lsa` (set to `0` to enable, default is disabled on most builds). If RestrictedAdminMode is off, only `password` / `pwhex` (and Kerberos ticket-based credentials) will succeed.

!!! note "PLAIN auth = no NLA"
    Selecting `PLAIN` skips the NLA / CredSSP handshake and falls back to the legacy RDP authentication flow (challenge sent post-connect). Modern Windows servers reject this by default; only servers with NLA explicitly disabled will accept it.

---

## Session window (the GUI experience)

| Tab          | What it is                                                                                                                                                                                                  |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Screen**   | **Default tab.** HTML5 canvas rendering the remote desktop. Mouse and keyboard input are captured by the canvas and forwarded over the RDP virtual channels. A clipboard text field at the side of the canvas lets you push text into the remote clipboard (and receive incoming clipboard data when the remote side copies). |
| **Commands** | Auto-generated visual command runner — one button per entry under `help_groups['COMMANDS']`, with parameter inputs.                                                                                          |
| **Jobs**     | Live table of running operations with PIDs and per-row Stop buttons.                                                                                                                                        |
| **History**  | Scrollable command history with screenshot-output for reporting.                                                                                                                                             |
| **Settings** | Editor for the session parameters (target, atype, timeout, port, etc.).                                                                                                                                      |
| **Debug**    | Raw protobuf inspector — turns red when active, otherwise hidden.                                                                                                                                            |
| **Console**  | Collapsible bottom drawer — same console as the CLI.                                                                                                                                                         |

The Screen tab also offers a resolution selector and a "Record" toggle; both are honoured the next time `login` is invoked.

!!! info "Resolution is fixed at login time"
    The remote desktop resolution is negotiated during the RDP handshake; runtime resize is not implemented. To change resolution, `logout`, pick a new size, and `login` again.

---

## Commands

### CONNECTION

#### login
Establishes the RDP connection, performs CredSSP/NLA authentication, negotiates the desktop resolution, and starts the video pipeline that paints the **Screen** tab. The server's session is **opened**, not joined — using the same credential against an existing logged-in session would create a new one, not attach.

##### Parameters
- **size** *(optional, str, default `1024x768`)*: Desktop resolution as `WIDTHxHEIGHT` (e.g. `1280x800`, `1920x1080`, `1024x768`). The remote side renders at this resolution; runtime resizing is not supported.
- **record** *(optional, bool, default `False`)*: If `True`, write the entire session to an `.mp4` file in OctoPwn's working directory (filename `rdp_record_<random>.mp4`). See [Recording](#recording) below for codec and frame rate details.

#### logout
Disconnects the RDP session. This **does not log the Windows user out** — it just tears down the OctoPwn → server connection. The Windows session remains in its current state (locked or unlocked depending on server policy) and can be re-attached or kicked from the server side.

---

### CLIPBOARD OPERATIONS

The remote clipboard is bridged via the `RDPECLIP` virtual channel — text copied on the remote side is automatically forwarded to the OctoPwn console (and surfaced in the Screen tab's clipboard panel), and OctoPwn can push text back into the remote clipboard for paste operations.

#### paste
Pushes a string into the remote clipboard as Unicode text. The remote side can then paste it with `Ctrl+V` (or whatever paste mechanism applies) — OctoPwn does not synthesize the paste keystroke automatically.

##### Parameters
- **text**: The string to set as the remote clipboard contents.

#### pastefile
Reads a local text file and pushes its contents into the remote clipboard. The path is jailed to OctoPwn's working directory.

##### Parameters
- **filepath**: Local file to read inside OctoPwn's working directory.

---

### RUBBERDUCKY

Two-step interface for replaying [Rubber Ducky](https://docs.hak5.org/hak5-usb-rubber-ducky/) scripts as synthesized keystrokes against the RDP session. The script is replayed using the active session's keyboard layout (looked up via `aardwolf.keyboard.layoutmanager.KeyboardLayoutManager`), so layout-specific characters are mapped correctly.

#### duckyfile
Sets the path of the Rubber Ducky script to use. **This does not execute anything** — it only stores the path for the subsequent `duckyexec` call.

##### Parameters
- **duckyscriptpath**: Path to the Rubber Ducky `.txt` script (e.g. `/browserfs/volatile/payload.txt`).

#### duckyexec
Executes the previously-set Rubber Ducky script against the remote session, dispatching scancodes (or characters, for VNC-dialect targets) at the script's tempo. The remote desktop must be in a state where the keystrokes will be received by the intended window — typically focus an application before invoking.

This command takes no parameters; the script path comes from the most recent `duckyfile` call. If `duckyfile` has not been set, `duckyexec` prints an error and returns.

---

### SCREEN

#### screenshot
Saves a PNG snapshot of the current desktop buffer to OctoPwn's working directory. The filename is auto-generated as `screenshot_<tid>_<host>_<YYYYMMDD>_<HHMMSS>.png`. Useful for capturing a single moment without enabling full session recording.

This command takes no parameters.

---

## Recording

When `login` is called with `record=True`, the client spawns a background task that pulls one frame from the desktop buffer at the configured frame rate and appends it to an `.mp4` file in OctoPwn's working directory.

| Setting        | Default value | Notes                                                                          |
| -------------- | ------------- | ------------------------------------------------------------------------------ |
| Frame rate     | `5` fps       | Hardcoded in `RDPClient.record_fps`.                                           |
| Codec FourCC   | `mp4v`        | Hardcoded in `RDPClient.record_codec`. Compatible with most MP4 players.       |
| Output path    | `/browserfs/volatile/rdp_record_<random>.mp4` | Generated per session; not configurable from the CLI today. |

!!! info "Recording uses `cv2` and `numpy`"
    The recorder uses OpenCV (`cv2.VideoWriter`) and NumPy under the hood. Both are bundled across all distributions (WASM, Enterprise, standalone Python), so recording works everywhere — but on the WASM/browser distribution it is noticeably slower and consumes a meaningful amount of memory while the session is open, since both the codec and the growing output file live in the browser's address space.

!!! info "Files land in browser memory on WASM"
    On the WASM distribution the resulting `.mp4` lives in OctoPwn's volatile storage, which is held in the browser's memory. Download the file out of `/browserfs/volatile/` before closing the tab to avoid losing it.

---

## Limitations

- **No runtime resize.** Resolution is fixed at login. To change it, `logout` and `login` again with a different `size`.
- **No drive / printer / smart-card / audio redirection.** Only video, keyboard, mouse, and clipboard text channels are wired up. Files cannot be transferred over the RDP virtual channels.
- **No bitmap/file clipboard.** Only text (`CF_UNICODETEXT`) is exchanged via the clipboard channel.
- **Recording is CPU- and memory-heavy on WASM.** Recording works across all distributions, but on the WASM/browser build the encoder runs alongside the rest of OctoPwn in the browser's address space — expect slower frame production and growing memory use while the session stays open (see [Recording](#recording)).
- **Recording parameters are not CLI-configurable.** Frame rate (`5` fps) and codec (`mp4v`) are hardcoded; changing them requires editing the source and reloading the session.
- **Hash/key auth requires RestrictedAdminMode.** Standard NLA/CredSSP rejects hash and AES-key auth unless the server explicitly allows it (see the [Authentication](#authentication) note).
- **PLAIN auth requires NLA disabled.** Modern Windows defaults reject non-NLA RDP; PLAIN is for legacy/explicitly-misconfigured targets only.
- **`logout` ≠ Windows logoff.** Tearing down the client does not log the user off the Windows session — it only disconnects.
