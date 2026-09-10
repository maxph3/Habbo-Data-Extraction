# catalog_dumper.py
# ======================================================================
# Catalog Dumper.
# Captures catalog menus, collections and descriptions via G-Earth.
# Version: 4.4
# Author: Max
# ======================================================================

import sys
import os
import json
import threading
from g_python.gextension import Extension
from g_python.hmessage import Direction

# Color Definition ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

extension_info = {
    "title": "Catalog Dumper",
    "description": "Captures catalog menus, collections and descriptions via G-Earth",
    "version": "4.4",
    "author": "Max"
}
ext = Extension(extension_info, sys.argv)

CATALOG_INDEX_HEADER = 3312
CATALOG_PAGE_HEADER = 2833

TREE_FILE = "catalog_tree.json"
PAGES_FILE = "catalog_pages.json"

want_collections = None
click_count = 0


def ask_yes_no(question):
    while True:
        answer = input(f"{question} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print(f"{BOLD}{BLUE}[INFO]{RESET}Invalid option. Please type y or n.")


def stop_script():
    sys.stdout.flush()
    os._exit(0)


def listen_for_manual_stop():
    input()
    print(f"\n{BOLD}{MAGENTA}[CHECK]{RESET} {click_count} collection description(s) captured and saved to '{PAGES_FILE}'.")
    print(f"{BOLD}{BLUE}[INFO]{RESET} Closing the script.")
    stop_script()


def parse_node(p):
    node = {
        "visible": p.read_bool(),
        "icon": p.read_int(),
        "pageId": p.read_int(),
        "pageName": p.read_string(encoding="utf-8"),
        "localization": p.read_string(encoding="utf-8"),
    }
    total_offers = p.read_int()
    node["offerIds"] = [p.read_int() for _ in range(total_offers)]
    total_children = p.read_int()
    node["children"] = [parse_node(p) for _ in range(total_children)]
    return node


def merge_node(node, out):
    out[str(node["pageId"])] = {
        "visible": node["visible"],
        "icon": node["icon"],
        "pageId": node["pageId"],
        "pageName": node["pageName"],
        "localization": node["localization"],
        "offerIds": node["offerIds"],
        "childrenIds": [c["pageId"] for c in node["children"]],
    }
    for c in node["children"]:
        merge_node(c, out)


def on_catalog_index(message):
    global want_collections

    p = message.packet
    tree = parse_node(p)
    p.read_bool()
    p.read_string(encoding="utf-8")

    existing = {}
    if os.path.exists(TREE_FILE):
        with open(TREE_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)

    merge_node(tree, existing)

    with open(TREE_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"{BOLD}{GREEN}[SUCCESS]{RESET} Catalog index captured — {len(existing)} pages registered in total")

    message.is_blocked = False

    if want_collections is None:
        want_collections = ask_yes_no("Do you want to extract Collection descriptions by clicking?")
        if want_collections:
            print(f"{BOLD}{BLUE}[INFO]{RESET} Click on the collections whose descriptions you want to extract in-game.")
            print(f"Press {BOLD}ENTER{RESET} at any time to {BOLD}stop{RESET} and finish extraction.")
            threading.Thread(target=listen_for_manual_stop, daemon=True).start()
        else:
            print(f"{BOLD}{MAGENTA}[CHECK]{RESET} Menu names and categories extracted successfully — {len(existing)} pages saved to '{TREE_FILE}'.")
            print(f"{BOLD}{BLUE}[INFO]{RESET} Nothing else to capture. Closing the script.")
            stop_script()


def on_catalog_page(message):
    global click_count

    p = message.packet
    page_id = p.read_int()
    _ = p.read_string(encoding="utf-8")
    layout_code = p.read_string(encoding="utf-8")
    total_images = p.read_int()
    images = [p.read_string(encoding="utf-8") for _ in range(total_images)]
    total_texts = p.read_int()
    texts = [p.read_string(encoding="utf-8") for _ in range(total_texts)]

    message.is_blocked = False

    if not want_collections:
        return

    pages = {}
    if os.path.exists(PAGES_FILE):
        with open(PAGES_FILE, "r", encoding="utf-8") as f:
            pages = json.load(f)
    pages[str(page_id)] = {"layoutCode": layout_code, "images": images, "texts": texts}
    with open(PAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    click_count += 1
    print(f"{BOLD}{GREEN}[SUCCESS]{RESET} Collection description captured (click {click_count}): page {page_id} ({layout_code})")


ext.intercept(Direction.TO_CLIENT, on_catalog_index, CATALOG_INDEX_HEADER)
ext.intercept(Direction.TO_CLIENT, on_catalog_page, CATALOG_PAGE_HEADER)

print("=" * 50)
print(f"{BOLD}Catalog Dumper{RESET} | Version: 4.4 | Author: Max")
print("=" * 50)
print(f"{BOLD}{YELLOW}[WARNING]{RESET} Do not open the Shop before running this script — the catalog packet is only loaded once per login.")
print(f"{BOLD}{BLUE}[INFO]{RESET} Script running, waiting for Catalog to open...")

ext.start()