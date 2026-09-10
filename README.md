# Habbo-Scripts
A collection of scripts for automation and data extraction in Habbo Hotel. These tools were originally created to support a Japanese localization project.

## Repository Structure & Tools

### HTTPS Extractor (`https_extractor.py`)
*   Generic utility designed to download files and assets from HTTPS URLs.
*   **Modes:** Single input or batch processing via `urls.txt`.

### Habbo HTTPS Extractor International (`https_extractor_intl.py`)
*   A Habbo-specific version pre-configured with worldwide hotel domains to fetch assets across global servers simultaneously.
*   **Modes:** Single path lookup or batch processing via `paths.txt`.

### Catalog Data Extractor (`catalog_data_extractor/`)
*   A sequential toolset combining **Catalog Dumper** (a G-Earth proxy extension) and **Cleaner and Cross-Reference** to capture, clean, and filter in-game catalog data.

## Dependencies
*   **Python 3.x**.
*   **[G-Earth](https://github.com/sirjonasxx/G-Earth)** *(v1.5.4 or higher)* (required exclusively for running the Catalog Dumper).

## Documentation
Please refer to the individual `README.md` file located inside each subfolder for specific step-by-step workflow instructions and execution commands.
