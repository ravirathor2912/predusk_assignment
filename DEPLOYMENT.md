# Deployment (Get a Live Hosted URL)


## Streamlit Community Cloud
1. Push this repo to GitHub.
2. Go to https://streamlit.io/cloud and connect your GitHub.
3. Deploy app:
   - Repository: your repo
   - Branch: main
   - Main file path: `app.py`
4. Wait for build.

Your URL will look like:
`https://<app-name>-<something>.streamlit.app/`

## Notes / Limits
- Model weights download on first run: The first visitor run may take longer (YOLO weights download).
- The app supports **uploading a file** (recommended for reliability).
- For faster demos, use **Max frames** in the app settings.
