# Technology Stack

**Analysis Date:** 2026-04-12

## Languages

**Primary:**
- Python - All code is Python-based

## Runtime

**Environment:**
- Python 3.x

**Package Manager:**
- pip (implied)
- Lockfile: Not present

## Frameworks

**Core:**
- tkinter - Built-in Python GUI framework for desktop applications

**Data Processing:**
- numpy - Numerical computing (random, linalg modules)
- pyproj - Coordinate reference system transformations

**Geospatial:**
- pyshp - Shapefile reading/writing (imported as `shapefile`)
- folium - Interactive web mapping with OpenStreetMap

## Key Dependencies

**Critical:**
- pyproj - Core requirement for all coordinate system transformations (EPSG code handling, CRS projections)
- numpy - Used for random point generation and linear algebra operations in `vector_2026.py`

**Infrastructure:**
- pyshp - Required for Shapefile format support
- folium - Required for OpenStreetMap visualization

## Configuration

**Environment:**
- No environment variables required
- Configuration via function parameters and user dialogs

**Build:**
- No build system - runs as Python modules

## Platform Requirements

**Development:**
- Python 3.x with standard library (tkinter, json, os, random, math, ast, webbrowser)
- pip package installation (pyproj, numpy, pyshp, folium)

**Production:**
- Desktop environment (tkinter requires graphical interface)
- Web browser (for folium map output)

---

*Stack analysis: 2026-04-12*