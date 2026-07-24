# Getting Started (from zero)

This walks through everything needed to get this project onto your computer, running, and pushed to your own GitHub account. Written assuming you have never used Git or GitHub before.

## 1. Install Python

Check if you already have it:

```         
python3 --version
```

If that fails, download Python 3.11+ from [python.org/downloads](https://www.python.org/downloads/) and install it (on Windows, tick "Add python.exe to PATH" during install).

## 2. Install Git

Check if you already have it:

```         
git --version
```

If not installed, download from [git-scm.com/downloads](https://git-scm.com/downloads). Defaults are fine during install.

Then set your identity (one time only):

```         
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## 3. Install an editor (optional but recommended)

[VS Code](https://code.visualstudio.com/) is free and works well with Python. Install it, then install the "Python" extension from the Extensions panel (icon on the left sidebar).

## 4. Create a GitHub account

Go to [github.com](https://github.com/) and sign up if you haven't already.

## 5. Create a new repository on GitHub

1.  Click the **+** icon (top right) → **New repository**.
2.  Name it `ipaas-portfolio`.
3.  Leave it **public** (so it shows up on your profile).
4.  Do **not** initialize with a README, .gitignore, or license — this project already has those.
5.  Click **Create repository**. GitHub will show you a page with setup commands — keep that tab open.

## 6. Put this project under Git and push it

Open a terminal in the `ipaas-portfolio` folder (in VS Code: **Terminal → New Terminal**), then run:

```         
cd path/to/ipaas-portfolio
git init
git add .
git commit -m "Initial commit: iPaaS portfolio with webhook, data collector, and connector engine demos"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ipaas-portfolio.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your actual GitHub username (shown on the setup page from step 5).

If GitHub asks you to log in, follow its prompt — for pushing from the command line it will usually ask you to authenticate via browser or a personal access token.

## 7. Check it worked

Refresh your GitHub repo page in the browser. You should see all the folders (`01-webhook-basics`, `02-data-collector`, `03-mini-connector-engine`) and files.

## 8. Running each demo

Each subfolder has its own README with exact run instructions. General pattern for all of them:

```         
cd 01-webhook-basics
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 receiver.py             # then, in a second terminal (with venv activated), python3 sender.py
```

## Making changes later

Any time you edit files and want to save the update to GitHub:

```         
git add .
git commit -m "Describe what you changed"
git push
```
