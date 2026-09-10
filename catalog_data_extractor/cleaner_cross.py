# cleaner_cross.py
# ======================================================================
# Cleaner and Cross-Reference.
# Cleans and cross-references data from catalog dumps.
# Version: 3.8
# Author: Max
# ======================================================================

import json
import os

# Color Definition ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

print("=" * 50)
print(f"{BOLD}Cleaner and Cross-Reference{RESET} | Version: 3.8 | Author: Max")
print("=" * 50)

if not os.path.exists("catalog_tree.json"):
    print(f"{BOLD}{RED}[ERROR]{RESET} Required file 'catalog_tree.json' not found in the execution folder.")
    exit(1)

with open("catalog_tree.json", "r", encoding="utf-8") as f:
    tree_data = json.load(f)

pages = {}
if os.path.exists("catalog_pages.json"):
    with open("catalog_pages.json", "r", encoding="utf-8") as f:
        pages = json.load(f)
else:
    print(f"{BOLD}{BLUE}[INFO]{RESET} 'catalog_pages.json' not found. Cross-referencing for 'texts' will be skipped.")

flat_nodes = {}
def flatten(node):
    if isinstance(node, dict):
        p_id = node.get("pageId")
        if p_id is not None:
            flat_nodes[str(p_id)] = node
        for child in node.get("children", []):
            flatten(child)

flatten(tree_data)
for k, v in tree_data.items():
    if isinstance(v, dict):
        p_id = v.get("pageId")
        if p_id is not None:
            flat_nodes[str(p_id)] = v

def fix(s):
    if not isinstance(s, str) or not s:
        return s
    try:
        return s.encode("iso-8859-1").decode("utf-8")
    except:
        return s

menus = tree_data.get("children", [])
menu_map = {}
print(f"\n{BOLD}Available Menus:{RESET}")
for i, m in enumerate(menus, 1):
    name = fix(m.get("localization") or m.get("pageName", str(m.get("pageId"))))
    menu_map[name.lower()] = m
    print(f"{MAGENTA}{i}.{RESET} {name}")
print(f"{MAGENTA}{len(menus) + 1}.{RESET} All")

ans_menu = input(f"\n{BOLD}Enter the desired Menus separated by comma (or All): {RESET}").strip().lower()

selected_menus = menus if ans_menu == "all" or not ans_menu else []
if ans_menu != "all" and ans_menu:
    for item in [x.strip() for x in ans_menu.split(",")]:
        found = False
        if item.isdigit():
            idx = int(item) - 1
            if 0 <= idx < len(menus):
                m = menus[idx]
                if m not in selected_menus:
                    selected_menus.append(m)
                found = True
        else:
            for k, m in menu_map.items():
                if item in k or k in item:
                    if m not in selected_menus:
                        selected_menus.append(m)
                    found = True
        if not found:
            print(f"{BOLD}{YELLOW}[WARNING]{RESET} Menu '{item}' not found.")

available_vars = ["visible", "icon", "pageId", "pageName", "localization", "offerIds", "childrenIds", "texts"]
print(f"\n{BOLD}Available Variables:{RESET}")
for i, var in enumerate(available_vars, 1):
    print(f"{MAGENTA}{i}.{RESET} {var}")
print(f"{MAGENTA}{len(available_vars) + 1}.{RESET} All")

ans_vars = input(f"\n{BOLD}Enter the desired Variables separated by comma (or All): {RESET}").strip().lower()

selected_vars = available_vars if ans_vars == "all" or not ans_vars else []
if ans_vars != "all" and ans_vars:
    for item in [x.strip() for x in ans_vars.split(",")]:
        found = False
        if item.isdigit():
            idx = int(item) - 1
            if 0 <= idx < len(available_vars):
                v = available_vars[idx]
                if v not in selected_vars:
                    selected_vars.append(v)
                found = True
        else:
            for v in available_vars:
                if item in v.lower() or v.lower() in item:
                    if v not in selected_vars:
                        selected_vars.append(v)
                    found = True
        if not found:
            print(f"{BOLD}{YELLOW}[WARNING]{RESET} Variable '{item}' not found.")

valid_ids = set()
def collect_ids(node):
    if isinstance(node, dict):
        p_id = node.get("pageId")
        if p_id is not None:
            valid_ids.add(str(p_id))
        for child in node.get("children", []):
            collect_ids(child)

for m in selected_menus:
    collect_ids(m)

merged = {}
for pid, info in flat_nodes.items():
    if pid in valid_ids:
        node_data = {}
        for var in selected_vars:
            if var == "texts":
                p_data = pages.get(pid, [])
                if isinstance(p_data, dict):
                    t_list = p_data.get("texts", [])
                elif isinstance(p_data, list):
                    t_list = p_data
                else:
                    t_list = []
                node_data["texts"] = [fix(t) for t in t_list if t]
            elif var in info:
                val = info[var]
                if isinstance(val, str):
                    node_data[var] = fix(val)
                else:
                    node_data[var] = val
        merged[pid] = node_data

with open("catalog_complete.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"\n{BOLD}{GREEN}[SUCCESS]{RESET} {BOLD}catalog_complete.json{RESET} generated with {len(merged)} pages!")