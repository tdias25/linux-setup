# Mint Setup

Repeatable setup and performance tuning for **Linux Mint 22.x (Cinnamon, x86_64)**, built with [Ansible](https://docs.ansible.com/). It installs the right NVIDIA driver, trims background work, tunes memory and Bluetooth reconnects, and can restore a personal desktop setup.

You don't need to know Ansible to use it. `setup.sh` installs it if needed and runs everything.

## Quick start

```bash
git clone <your-repository-url> mint-setup
cd mint-setup

# See what would change. Nothing is modified.
./setup.sh preview generic

# Apply it. You'll be asked to confirm and for your sudo password.
./setup.sh apply generic

sudo reboot
```

Run only part of it with tags:

```bash
./setup.sh preview legion-5 --tags memory,bluetooth
./setup.sh apply legion-5 --tags kitty,zsh
```

Tags: `base`, `nvidia`, `debloat`, `apps`, `memory`, `services`, `bluetooth`, `battery`, `boot`, `kitty`, `zsh`, `brave`, `desktop`.

## Profiles

| Profile | Use it for |
|---|---|
| `generic` | Any supported Mint machine. Only safe, broadly useful changes. |
| `legion-5` | Lenovo Legion 5 15IMH05H (RTX 2060). Everything below, including personal preferences. |

To make your own, copy `profiles/legion-5.yml` and edit it. Every option and its default is in `config.yml`.

## What it changes

| Area | Change | `generic` | `legion-5` |
|---|---|:---:|:---:|
| Safety | Timeshift restore point before changes, at most once a day | ✓ | ✓ |
| System | Upgrades installed packages | ✓ | ✓ |
| NVIDIA | Installs the recommended driver if an NVIDIA GPU exists, and verifies a module for **every** installed kernel | ✓ | ✓ |
| Memory | zram swap (zstd, 50% of RAM) and matching kernel settings | ✓ | ✓ |
| Boot | Disables network wait and unused services | ✓ | ✓ |
| Bluetooth | Faster LE reconnects, no adapter autosuspend | ✓ | ✓ |
| Apps | Removes unused default apps, with a safety check | | ✓ |
| Battery | Lenovo conservation mode (holds about 60%) | | ✓ |
| GRUB | Wait reduced to 1 second. Press `Esc` at startup for the menu. | | ✓ |
| Brave | Disables Rewards, Wallet, VPN, Leo, News, Tor, Cast and telemetry | | ✓ |
| Desktop | Rofi on `Alt+Space`, kitty on `Super+T`, zsh with Oh My Zsh, `br` + `us-intl` layouts | | ✓ |

## Safety

- **Preview first.** `preview` is Ansible's check mode and doesn't modify the system.
- **Safe to re-run.** Anything already correct is left alone.
- **Existing config is kept.** It never replaces your `.zshrc` or `kitty.conf`, and it won't take over a shortcut already in use.
- **App removal is guarded.** It simulates the removal first and stops if a core package would be affected.
- **Driver changes are guarded.** It won't replace an NVIDIA driver you already have, and it stops if Secure Boot would block an unsigned module.
- **Downloads are pinned.** kitty is verified by SHA-256 and Oh My Zsh is locked to a specific commit.
- **No secrets or personal data.** The repo has no usernames, device addresses or disk IDs.

## Undo

The simplest full rollback is to restore the **Timeshift** snapshot labeled `before mint-setup`.

To revert individual changes:

```bash
# GRUB wait: edit GRUB_TIMEOUT, then
sudo nano /etc/default/grub && sudo update-grub

# Battery conservation
sudo rm /etc/udev/rules.d/90-conservacao-bateria.rules
echo 0 | sudo tee /sys/bus/platform/devices/VPC2004:00/conservation_mode

# Brave policies (then restart Brave)
sudo rm /etc/brave/policies/managed/brave-leve.json

# Memory settings
sudo rm /etc/sysctl.d/90-desempenho.conf && sudo sysctl --system

# Restore the window menu on Alt+Space
gsettings reset org.cinnamon.desktop.keybindings.wm activate-window-menu
```

## Manual steps

These can't or shouldn't be automated:

1. **Icon theme:** download [Modern Office Night Icons](https://www.opendesktop.org/s/Cinnamon/p/2346851) and extract it to `~/.icons`, then re-run with `--tags desktop`. It isn't included because the listing has no stated license.
2. **Brave:** install it from [brave.com/linux](https://brave.com/linux/) before running the `brave` tag.
3. **YouTube codec:** install the enhanced-h264ify extension in Brave and block only **AV1**.
4. **External monitor:** on the Legion 5, HDMI was limited to 85 Hz at 3440x1440. The rear USB-C port with a DisplayPort adapter reached 100 Hz.
5. **After a reboot:** log out and back in once if shortcuts or the default shell haven't updated.

## Notes and decisions

- **Hardware video decoding in Brave is deliberately not enabled.** Ubuntu's `nvidia-vaapi-driver` 0.0.8 failed real decode tests on driver 595, because its EGL mode is broken on drivers 525 and later. Upstream 0.0.18 adds Chromium support but must be built by hand, and the gain was too small to justify it on a laptop that's usually plugged in.
- **The power profile is left manual.** Use `Fn+Q` or `powerprofilesctl set performance`.
- **Bluetooth can't be instant at boot.** It isn't available in the BIOS or GRUB. A USB receiver such as Logi Bolt is the fix if that matters.
- **Fn Lock:** if `Alt+F4` stops working, press `Fn+Esc` on that keyboard.
- **Heat is the main remaining limit on the Legion 5.** The CPU throttled under normal use. With two high-refresh displays the GPU stays at full memory clock. Cleaning the fans and replacing the thermal paste would help more than further software tuning.

## Updating pinned versions

- **kitty:** change `kitty_version` and `kitty_sha256` in `config.yml`. An existing install isn't replaced automatically.
- **Oh My Zsh:** change `ohmyzsh_commit`, or run `omz update` on an installed system.
- **New Mint base:** add its Ubuntu codename to `supported_ubuntu_bases` only after testing it.
