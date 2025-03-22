# MPXJ Integration for CSCSC AI Agent

This commit integrates MPXJ (Microsoft Project Exchange) library with the CSCSC AI Agent, providing enhanced project file format conversions and analysis capabilities.

## Added Features

- **MPXJ Wrapper Module**: Created `mpxj_wrapper.py` to provide a Python interface for interacting with the MPXJ library
- **MPXJ API Router**: Developed `mpxj_router.py` with endpoints for file uploads, conversions, and data analysis
- **Web UI for Project File Conversion**: Added a complete user interface for uploading, converting, and analyzing project files
- **Format Detection**: Implemented automatic detection of project file formats
- **Project Data Analysis**: Added functionality to extract and analyze tasks, resources, critical path, and other project data
- **Integration with Main Application**: Updated `main.py` to include MPXJ endpoints

## Technical Details

- Added necessary dependencies to `requirements.txt` (mpxj, jpype1, typing-extensions)
- Created responsive UI with drag-and-drop file upload capabilities
- Implemented data visualization for project metrics and resource allocation
- Added RESTful API endpoints for programmatic access to MPXJ functionality
- Updated README.md with comprehensive MPXJ documentation

## Supported File Formats

- Microsoft Project: .mpp, .mpx, .xml
- Primavera P6: .xer, .pmxml
- Asta Powerproject: .pp
- And many more formats for project file interchange
