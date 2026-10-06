# Meetdonda animated GitHub profile setup

This folder is already personalized for `Meetdonda`. It contains a colorful animated ASCII portrait, a neofetch-style information card, and a live contribution heatmap. The animations are self-contained in SVG files, so they work in GitHub README files without JavaScript.

## 1. Create the special GitHub repository

Open <https://github.com/new> while signed in as `Meetdonda` and create this repository:

- Repository name: `Meetdonda`
- Visibility: **Public**
- Do not add a README, `.gitignore`, or license on GitHub; those files are already included here.

GitHub only displays a profile README when the repository name exactly matches the username.

## 2. Push this prepared folder

Open PowerShell in this folder and run:

```powershell
git init
git add .
git commit -m "Create colorful animated profile README"
git branch -M main
git remote add origin https://github.com/Meetdonda/Meetdonda.git
git push -u origin main
```

Refresh <https://github.com/Meetdonda>. The new README should appear above the pinned repositories.

## 3. Enable daily activity updates

Open the new repository on GitHub:

1. Go to **Settings → Actions → General**.
2. Under **Workflow permissions**, select **Read and write permissions** and save.
3. Go to **Actions → Update profile art → Run workflow**.

After that first run, GitHub Actions refreshes the contribution heatmap every day at 06:17 UTC. No personal access token is needed.

## 4. Change the text or colors later

Edit `config.json`, then rebuild the generated assets:

With Python 3.11 or newer:

```bash
python -m pip install -r scripts/requirements-workflow.txt
python scripts/build.py --skip-portrait
```

Commit and push the changed files afterward.

## 5. Use a different portrait later

Use a well-lit, front-facing photo with a simple background. Keep the photo private if you do not want the original committed to GitHub.

```bash
python -m pip install -r scripts/requirements-portrait.txt
python scripts/prep_photo.py path/to/photo.jpg --output source-prepped.png
python scripts/make_ascii_svg.py source-prepped.png
```

After `profile-ascii.svg` has been generated, delete both the original photo and `source-prepped.png`; the repository only needs the generated SVG. The current prepared folder already follows this pattern and does not contain your original avatar.

If automatic background removal is unnecessary, add `--keep-background` to the `prep_photo.py` command.

## Notes

- GitHub strips scripts and most inline styles from README HTML. Keep all animation inside the SVG files.
- The workflow has `contents: write` permission only; no personal access token is required.
- If organization policy disables workflow write access, enable **Read and write permissions** under repository **Settings → Actions → General → Workflow permissions**.
- Public contribution HTML is not a formal API and GitHub may change its markup. The fetcher fails clearly instead of overwriting the last known good graph with empty data.
