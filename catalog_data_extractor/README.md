```text
# ======================================================================== #
#                          Catalog Data Extractor                          #
#                 Extraction, cleaning, and processing tools               #
#                           Catalog Dumper (v4.4)                          #
#                     Cleaner & Cross-Reference (v3.8)                     #
#                               Author: Max                                #
# ======================================================================== #

This directory contains sequential tools designed to extract, clean, and cross-reference in-game catalog data using the G-Earth proxy.

### Step 1: Catalog Dumper (`catalog_dumper.py`)
Captures catalog menus, collections, and descriptions via G-Earth as you navigate the in-game shop. It operates in two stages (Names and Descriptions).
*   **How to run:** Requires the G-Earth proxy running and the connection port defined via `-p`.
python catalog_dumper.py -p 9092

### Step 2: Cleaner and Cross-Reference (`cleaner_cross.py`)
Cleans and cross-references data from catalog dumps, allowing you to filter specific menus and keys for the final output.
*   **How to run:**
python cleaner_cross.py
```