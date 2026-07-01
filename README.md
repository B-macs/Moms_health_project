<<<<<<< HEAD
# Moms_health_project
Moms health project
=======
# Weekly Check-In 🎾

A simple, mobile-friendly Streamlit app for a single athlete to record a
5-question wellness check-in. Every submission is appended as a timestamped
row to a Google Sheet.

This guide assumes no prior experience with Google Cloud or Streamlit. Follow
the steps in order.

---

## 1. Create a Google Cloud project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with the Google account that owns (or will own) the Google Sheet.
3. Click the project dropdown at the top of the page, then **New Project**.
4. Give it a name (e.g. `checkin-app`) and click **Create**.
5. Once created, make sure it's selected in the project dropdown.

## 2. Enable the Google Sheets and Drive APIs

1. In the Cloud Console, use the search bar at the top and search for
   **Google Sheets API**. Open it and click **Enable**.
2. Search for **Google Drive API**. Open it and click **Enable**.
   (The Drive API is required by `gspread` to look up the sheet by ID.)

## 3. Create a service account

A service account is a "robot user" your app logs in as — no interactive
login or password needed.

1. In the Cloud Console search bar, search for **Service Accounts** and open
   that page (under "IAM & Admin").
2. Click **+ Create Service Account**.
3. Give it a name (e.g. `checkin-app-bot`). Click **Create and Continue**.
4. You can skip granting it project roles — click **Continue**, then **Done**.
5. You'll land back on the Service Accounts list. Click on the service
   account you just created.
6. Go to the **Keys** tab, click **Add Key** → **Create new key**.
7. Choose **JSON** and click **Create**. A JSON file will download to your
   computer — this is your credentials file. Keep it private; don't share it
   or commit it to git.
8. Note the service account's email address (looks like
   `checkin-app-bot@your-project-id.iam.gserviceaccount.com`) — you'll need
   it in the next step.

## 4. Create the Google Sheet and share it with the service account

1. Go to [Google Sheets](https://sheets.google.com) and create a new,
   blank spreadsheet (e.g. name it "Weekly Check-In Data").
2. Click **Share** in the top right.
3. Paste in the service account's email address (from step 3.8) and give it
   **Editor** access. Click **Send** (it's fine that it's a robot account,
   not a real person — ignore any warning about that).
4. Copy the Sheet's ID from the browser URL. The URL looks like:
   ```
   https://docs.google.com/spreadsheets/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/edit
   ```
   The ID is the long string between `/d/` and `/edit` — in this example,
   `1AbCdEfGhIjKlMnOpQrStUvWxYz`.

You do not need to add any headers or formatting to the sheet — the app
creates the header row automatically the first time it runs.

## 5. Fill in `secrets.toml`

1. In this project folder, copy the example file:
   - **Mac/Linux:** `cp .streamlit/secrets.toml.example .streamlit/secrets.toml`
   - **Windows (PowerShell):** `Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml`
2. Open `.streamlit/secrets.toml` and open the JSON key file you downloaded
   in step 3.7 side by side.
3. Under `[sheet]`, set `sheet_id` to the Sheet ID from step 4.4.
4. Under `[gcp_service_account]`, copy each value from the JSON file into
   the matching field:
   - `type`, `project_id`, `private_key_id`, `private_key`, `client_email`,
     `client_id`, `auth_uri`, `token_uri`, `auth_provider_x509_cert_url`,
     `client_x509_cert_url`, `universe_domain` all come straight from the
     JSON file's fields of the same name.
   - The `private_key` value is long and contains `\n` characters — copy it
     exactly as it appears in the JSON file, quotes and all.
5. Save the file. **Never commit this file to git** — `.gitignore` already
   excludes it, and the downloaded JSON key file (`*.json`) is excluded too.

## 6. Run the app locally

Open a terminal in this project folder.

**Create and activate a virtual environment:**

- **Mac/Linux:**
  ```bash
  python -m venv venv
  source venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the app:**
```bash
streamlit run app.py
```

A browser tab should open automatically at `http://localhost:8501`. Fill
out the form and click Submit — check your Google Sheet to confirm a new
row was added.

---

## 7. Deploy for free on Streamlit Community Cloud

This lets your mom open the app from a simple URL on her phone, with nothing
to install.

1. Push this project to a **GitHub repository** (it can be private).
   Double check `.streamlit/secrets.toml` and the downloaded JSON key file
   are *not* included (they're covered by `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   GitHub.
3. Click **New app**, choose your repository, branch, and set the main
   file path to `app.py`.
4. Before or after deploying, open the app's **Settings → Secrets** panel
   in the Streamlit Cloud dashboard.
5. Paste the **entire contents** of your local `.streamlit/secrets.toml`
   file into that Secrets text box, then click **Save**. Streamlit Cloud
   uses this the same way your local `secrets.toml` file works — no code
   changes needed.
6. Click **Deploy**. After the build finishes, you'll get a URL like
   `https://your-app-name.streamlit.app`.
7. Send that URL to your mom. On her phone, she can open it in any browser
   and optionally use "Add to Home Screen" so it looks like a regular app
   icon.

### Updating the app later

Any time you push new commits to the connected GitHub branch, Streamlit
Community Cloud automatically redeploys the app. If you ever need to change
a secret, use the same Settings → Secrets panel — no redeploy of code is
needed for secrets-only changes.

---

## Troubleshooting

- **"Sorry, something went wrong saving your check-in"** — this means the
  write to Google Sheets failed. Common causes:
  - The service account email wasn't given **Editor** access to the sheet
    (step 4.3).
  - The Sheets or Drive API isn't enabled on the Google Cloud project
    (step 2).
  - `sheet_id` in secrets doesn't match the sheet's actual ID.
- **App works locally but not when deployed** — double check you pasted the
  full secrets file into the Streamlit Cloud Secrets panel, including the
  `[sheet]` and `[gcp_service_account]` section headers.
>>>>>>> 28b585f (Version 1)
