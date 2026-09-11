# https_extractor_habbo_intl.py
# ======================================================================
# Habbo HTTPS Extractor (International).
# Downloads game files across Habbo hotel domains worldwide.
# Version: 1.5
# Author: Max
# ======================================================================

import os
import time
import requests

# Color Definition ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

OUTPUT_DIR = "downloaded_files"
PATHS_FILE = "paths.txt"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

DELAY_SECONDS = 1

# Verify/update this list before publishing.
HABBO_DOMAINS = {
    "1": ("International (habbo.com)", "com", "COM"),
    "2": ("Brazil", "com.br", "BR"),
    "3": ("Germany", "de", "DE"),
    "4": ("Spain", "es", "ES"),
    "5": ("Finland", "fi", "FI"),
    "6": ("France", "fr", "FR"),
    "7": ("Italy", "it", "IT"),
    "8": ("Netherlands", "nl", "NL"),
    "9": ("Turkey", "com.tr", "TR"),
}


def ask_yes_no(question):
    while True:
        answer = input(f"{question} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print(f"{BOLD}{RED}[ERROR]{RESET} Invalid option. Please type y or n.")


def choose_domain():
    print("\nChoose a Habbo hotel:")
    print("0 - All hotels")
    for key, (label, _, _) in HABBO_DOMAINS.items():
        print(f"{key} - {label}")

    while True:
        choice = input("Enter the number: ").strip()
        if choice == "0":
            return [(domain, sigla) for _, domain, sigla in HABBO_DOMAINS.values()]
        if choice in HABBO_DOMAINS:
            _, domain, sigla = HABBO_DOMAINS[choice]
            return [(domain, sigla)]
        print(f"{BOLD}{RED}[ERROR]{RESET} Invalid option, try again.")


def build_url(domain, path):
    return f"https://www.habbo.{domain}/{path.lstrip('/')}"


def ask_single_or_multiple():
    print("\nHow many items do you want to download?")
    print("1 - Just one")
    print("2 - Multiple (loaded from a .txt list, one per line)")

    while True:
        choice = input("Choose an option (1/2): ").strip()
        if choice in ("1", "2"):
            return choice
        print(f"{BOLD}{RED}[ERROR]{RESET} Invalid option. Please type 1 or 2.")


def prepare_list_file(filename, item_label):
    if ask_yes_no(f"Do you want to create the '{filename}' file now?"):
        if not os.path.isfile(filename):
            open(filename, "w", encoding="utf-8").close()
        print(f"{BOLD}{GREEN}[SUCCESS]{RESET} '{filename}' created in the folder where the script was run.")
        print(f"{BOLD}{BLUE}[INFO]{RESET} Paste your {item_label} into it (one per line) and save the file.")

        if not ask_yes_no("Ready to start the script?"):
            print("Okay, run the script again when you're ready.")
            return []

    if not os.path.isfile(filename):
        print(f"{BOLD}{RED}[ERROR]{RESET} '{filename}' not found. Create it manually or run the script again.")
        return []

    with open(filename, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]
    print(f"{BOLD}{GREEN}[SUCCESS]{RESET} {len(items)} entries loaded from '{filename}'")
    return items


def ask_extension():
    ext = input("What extension should the files be saved as? (xml, json, txt, java, hex, ...): ").strip()
    return ext.lstrip(".") or "txt"


def download_file(url, output_dir, extension):
    os.makedirs(output_dir, exist_ok=True)

    print(f"Fetching: {url} ...")
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS)
        response.raise_for_status()

        file_name = url.rstrip("/").split("/")[-1].split("?")[0] or "index"
        file_path = os.path.join(output_dir, f"{file_name}.{extension}")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"{BOLD}{GREEN}[SUCCESS]{RESET} Saved: {file_path}\n")
        return True

    except requests.exceptions.RequestException as e:
        print(f"{BOLD}{RED}[ERROR]{RESET} Could not fetch {url}")
        print(f"Details: {e}\n")
        return False


def download_single(domains, output_dir, extension):
    while True:
        path = input("Enter the folder path (e.g. gamedata/external_variables): ").strip()
        results = [(build_url(domain, path), sigla) for domain, sigla in domains]

        ok_count = sum(download_file(url, output_dir, extension, sigla) for url, sigla in results)
        if ok_count > 0:
            return ok_count
        print(f"{BOLD}{YELLOW}[WARNING]{RESET} That path was broken for the selected hotel(s). Please enter it again.")


def download_files(url_sigla_pairs, output_dir, extension, delay=DELAY_SECONDS):
    print(f"\nStarting download of {len(url_sigla_pairs)} file(s)...\n")
    success = 0
    for i, (url, sigla) in enumerate(url_sigla_pairs):
        if download_file(url, output_dir, extension, sigla):
            success += 1
        else:
            print(f"{BOLD}{YELLOW}[WARNING]{RESET} That URL was broken.")
            if not ask_yes_no("Continue with the remaining downloads?"):
                print(f"{BOLD}{RED}[ERROR]{RESET} Stopping downloads.")
                break

        if i < len(url_sigla_pairs) - 1:
            time.sleep(delay)

    print(f"{BOLD}{GREEN}[SUCCESS]{RESET} Done! {success}/{len(url_sigla_pairs)} file(s) saved in '{output_dir}'.")
    return success


def main():
    print("=" * 50)
    print(f"{BOLD}Habbo HTTPS Extractor (International){RESET} | Version: 1.5 | Author: Max")
    print("=" * 50)

    domains = choose_domain()
    mode = ask_single_or_multiple()
    extension = ask_extension()

    if mode == "1":
        download_single(domains, OUTPUT_DIR, extension)
        return

    paths = prepare_list_file(PATHS_FILE, "folder paths")
    if not paths:
        print(f"{BOLD}{BLUE}[INFO]{RESET} No paths to process. Exiting.")
        return

    url_sigla_pairs = [(build_url(domain, path), sigla) for domain, sigla in domains for path in paths]
    download_files(url_sigla_pairs, OUTPUT_DIR, extension)


if __name__ == "__main__":
    main()
