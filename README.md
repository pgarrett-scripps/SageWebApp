# SageWebApp

Web tools for Sage Search Engine

## Apps

1. **sage-input**: Creates config files for Sage Searches.
2. **sage-app**: Handles file uploads, run search, and download zipped results

## What it does

This app lets you:
- Configure Sage search parameters through UI
- Run Sage via online webpage

## Quick start

```bash
# Install
git clone https://github.com/pgarrett-scripps/SageWebApp
cd SageWebApp
pip install -e .

# Run the config generator (app should open automatically, if not it will be availble at localhost:8501)
sage-config

# Run the search tool (app should open automatically, if not it will be availble at localhost:8501)
sage-app
```

## Credits

- Built on [Sage](https://github.com/lazear/sage) search engine
- Frontend using [Streamlit](https://streamlit.io/)
