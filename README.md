# Khata Dalo — Desktop Ledger & POS

A Windows desktop Point-of-Sale & Ledger application for Pakistani retail,
wholesale, and local shops (grocery, sanitary, electric, supermarts).
Built with **Python 3.10+, PyQt6, and SQLite**.

## Design

Modern light theme using this palette throughout (`utils/style.py`):

| Purpose | Hex |
|---|---|
| Primary Blue | `#2563EB` |
| Hover Blue | `#1D4ED8` |
| Accent Blue | `#60A5FA` |
| Light Blue Background | `#EFF6FF` |
| Main Background | `#FFFFFF` |
| Section Background | `#F8FAFC` |
| Text | `#1F2937` |
| Border | `#E2E8F0` |

Every screen opens with a consistent modern header (icon badge + bold title
+ muted subtitle, via `utils/widgets.py:PageHeader`) instead of a plain
bold label. The app icon/logo is a custom flat "ledger book" mark generated
in `assets/icon.ico`, `assets/logo_mark.png`, and `assets/logo_wordmark.png`
— replace these with your own artwork any time.

## Features

- **Top Status Bar** — an always-visible strip above the sidebar/workspace
  showing an Online status pill, current shift/user, a live clock, plus
  the Quick Price Check (F2) and Backup Now actions — this is the
  "Top Status Header" from the original spec, now implemented as its own
  bar rather than folded into a page header.
- **Animated collapsible sidebar** — the Collapse button (and the
  auto-collapse at narrow window widths) now smoothly animates the
  sidebar width instead of snapping instantly.
- **POS Counter (F1)** — barcode-first billing, on-screen numpad, quick
  payment buttons (Cash / EasyPaisa-JazzCash / Bank / Udhar-Khata), editable
  cart lines, checkout with credit-limit checking.
- **Item File & Inventory** — scan-to-populate product form, Urdu name field,
  cost/sale price, stock + minimum stock alert, category, tax %.
- **Category Manager** — English/Urdu category names with default GST %.
- **Customer Udhar Khata**
  - Customer list with balances & credit limits, per-customer ledger,
    credit-limit warning.
  - Recovery entry with a printable slip preview — and it now actually
    **opens WhatsApp** (via a `wa.me` deep link, prefilled with the
    receipt text) right after you record a payment, including a distinct
    "Khata Cleared — Thank You!" message when the balance hits zero. A
    "Resend via WhatsApp" button lets you re-open it if the chat didn't
    launch. See the note on WhatsApp below for why this uses `wa.me`
    instead of a background auto-send.
  - **Remove Customer** — permanently deletes a customer and their entire
    Khata transaction history from the database (confirmation required;
    this cannot be undone).
- **Supplier & Purchase Management** — supplier profiles, purchase invoice
  entry that restocks inventory and updates supplier balances.
- **Barcode Tools & Labels — fully functional** — select one or more
  products with real Code128 barcodes attached, see a live label preview
  (name, price, scannable barcode graphic) rendered right in the app, and
  export a multi-label PDF sheet sized for thermal stickers. Uses
  `python-barcode` + `Pillow` for real scannable graphics; falls back to a
  text-only label automatically if those packages aren't installed.
- **Quick Price Check Terminal (F2)** — full-screen scan-only lookup modal.
- **Dashboard & Analytics** — today's totals, a 7-day sales bar chart (no
  extra chart dependency needed), and Top 50 selling items.
- **Responsive layout** — resizing the window below ~1080px reflows to a
  2-column layout, and below ~800px the sidebar collapses to icon-only and
  tables drop secondary columns.
- **MACLAY OD7100E barcode scanner support** — `utils/scanner_input.py`
  provides a `ScannerLineEdit` that auto-refocuses after every scan (Enter
  key) so scans on the POS counter and Item File screens work without a
  mouse click. Works with any generic USB-HID keyboard-wedge scanner.
- **SQLite database** (`khatadalo.db`) with the requested schema:
  `users, products, categories, customers, sales_header, sales_items,
  khata_transactions` (plus `suppliers`, `purchases`, `purchase_items` to
  support the supplier module).
- **End-of-Day backup** — `db.backup_database()` copies a date-stamped `.db`
  file into `/backups`; it also runs once automatically on app startup, and
  there's a "💾 Backup Now" button in the top status bar for a manual
  backup any time.

## About the WhatsApp send

There's no way to *silently, automatically* deliver a WhatsApp message from
a desktop app without a paid, Meta-approved WhatsApp Business API sender
(Cloud API or a provider like Twilio) — that requires business
verification and credentials this project can't set up for you. What Khata
Dalo does instead (`utils/whatsapp_sender.py`) is open a `wa.me` deep link
with the receipt text already typed into the chat box — the desktop
WhatsApp app opens (or web.whatsapp.com if it's not installed) and the
shopkeeper just taps Send. This is why the recovery slip previously only
showed text in-app and nothing opened — that trigger was missing and is
now wired into `record_recovery()` in `ui/customer_khata.py`. If you later
get access to the official Cloud API, swap the body of
`send_whatsapp_message()` for a real API call — every call site stays the
same.

## Getting started (development)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py
```

First login seed: **admin / admin123** (a `users` table exists for future
login-screen wiring; the current build launches straight into the POS for
speed — see "Next steps" below).

## Building the Windows .exe

Run `build.bat` on a Windows machine with Python 3.10+ on PATH:

```bat
build.bat
```

This creates a virtual environment, installs `requirements.txt` (version
ranges, not hard pins — so pip picks whatever build is compatible with
your installed Python), and runs PyInstaller:

```bat
pyinstaller --name "KhataDalo" --onefile --windowed ^
    --icon "assets\icon.ico" --add-data "assets;assets" ^
    --hidden-import "PyQt6.sip" main.py
```

The finished single executable lands at `dist\KhataDalo.exe`. Copy that
file (plus, if you want it pre-seeded, `khatadalo.db`) anywhere on the
target PC — no Python install needed there.

> If `pip install` complains about no compatible PyInstaller/PyQt6 version
> for your Python, it usually means your Python is very new or very old.
> Khata Dalo targets Python 3.10–3.13; if you're on something outside that
> range, install a 3.11 or 3.12 build from python.org and re-run `build.bat`.

## Suggested next steps

- Add a login screen using the existing `users` table and `role` column
  (admin vs cashier permissions), and reflect the logged-in user in the
  top status bar's "Shift" pill (currently hard-coded to "Admin").
- Wire an actual thermal receipt printer (ESC/POS via `python-escpos`) into
  the POS checkout success path.
- Add refund/void flows against `sales_header.status`.
- Swap in a real WhatsApp Business API sender once you have one (see above).

## Project structure

```
KhataDalo/
├── main.py                  # entry point
├── db.py                    # SQLite schema, connection, backup
├── build.bat                # Windows PyInstaller build script
├── requirements.txt
├── assets/
│   ├── icon.ico              # app icon
│   ├── logo_mark.png         # standalone logo mark
│   └── logo_wordmark.png     # logo + "Khata Dalo" wordmark
├── utils/
│   ├── scanner_input.py     # MACLAY OD7100E-optimized QLineEdit
│   ├── style.py              # theme / QSS (new blue palette)
│   ├── widgets.py            # PageHeader / SectionCard shared components
│   └── whatsapp_sender.py    # wa.me deep-link WhatsApp sender
└── ui/
    ├── main_window.py        # sidebar + top status bar + responsive shell
    ├── pos_counter.py        # F1 POS Counter
    ├── item_file.py          # Item File & Inventory
    ├── category_manager.py
    ├── customer_khata.py     # Udhar Khata ledger + delete + WhatsApp
    ├── supplier_purchase.py
    ├── barcode_tools.py      # functional label generator + live preview
    ├── price_check.py        # F2 Quick Price Check modal
    └── dashboard.py           # analytics
```
