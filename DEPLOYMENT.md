# Deployment (Get a Live Hosted URL)


## Option A (Recommended): Hugging Face Spaces
This is usually the fastest path to get a public URL.

1. Create a free Hugging Face account.
2. Create a new **Space**:
   - SDK: **Streamlit**
   - Visibility: Public
3. Push this repo to GitHub (or upload files to the Space).
4. In the Space settings, ensure these files exist at the repo root:
   - `app.py` (Streamlit entry)
   - `requirements.txt`
   - `packages.txt` (installs `ffmpeg`)
5. Wait for the build to finish.

Your URL will look like:
`https://huggingface.co/spaces/<username>/<space-name>`

## Option B: Streamlit Community Cloud
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
- On Streamlit Community Cloud you typically **cannot install system packages** like `ffmpeg` (so `packages.txt` is for Hugging Face Spaces, not Streamlit Cloud).
- URL input downloading depends on `yt-dlp` and may fail without `ffmpeg` or for some streaming providers; **uploading a file** in the app is the most reliable.
- For faster demos, use **Max frames** in the app settings.
