# Add this package to your existing PyCharm project

1. Extract the ZIP. Open the folder containing retail_pipeline.py, dashboard.py and sql.
2. Copy its contents into your existing online-retail-analysis project root (beside inspect_data.py).
3. Replace requirements.txt and .gitignore with the supplied versions. Keep your .venv, inspect_data.py and original data/raw/Online Retail.xlsx.
4. Open the PyCharm terminal in the project root and run:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python retail_pipeline.py
python -m streamlit run dashboard.py
```

5. When the browser opens, inspect all three dashboard tabs. The first pipeline run may take a minute to read Excel. If the raw data is unchanged, your reports should reproduce the supplied values.
6. Capture a screenshot of each dashboard tab for your own review or later portfolio presentation. Hide personal details in the browser before sharing screenshots.
7. Stop the dashboard using Control+C in the terminal.

## First local Git commit

Run `git status --short` and check that .venv, .idea, the workbook, SQLite and audited row-level CSV are absent. Then stage only the intended project files:

```bash
git add .gitignore requirements.txt inspect_data.py retail_pipeline.py dashboard.py sql docs reports tests README.md
git diff --cached --stat
git commit -m "Build retail analysis pipeline, SQL reports and dashboard"
```

If inspect_data.py does not exist in a fresh clone, omit it from git add. If Git asks for your name/email, use your actual identity or GitHub noreply address; configure only this repository with `git config user.name "YOUR NAME"` and `git config user.email "YOUR EMAIL"`.

## Publish to GitHub

Create an empty repository named online-retail-analysis in your own GitHub account. Do not initialise it with a README if you are pushing this existing project. Copy its HTTPS repository URL. Then:

```bash
git remote -v
```

If there is no origin yet, add your actual repository URL with `git remote add origin YOUR_REPOSITORY_URL`. Then run:

```bash
git push -u origin main
```

Use GitHub's browser or credential-manager authentication when prompted; do not put a token in code, screenshots or the repository URL. If origin already exists, inspect where it points before changing anything. No force push is needed.

## After publishing

Check the README renders, reports/findings.md opens and sql files are present. Suggested repository description: "Online retail sales and customer retention analysis using Python, SQLite and Streamlit." Add topics such as data-analysis, python, sql, streamlit and customer-retention. Local Streamlit is not public hosting; use screenshots until you choose to deploy.
