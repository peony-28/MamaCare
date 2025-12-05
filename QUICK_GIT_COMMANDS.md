# Quick Git Commands for Deployment

## Force Add ML Models

Since `.pkl` files are in `.gitignore`, use the `-f` flag:

```bash
git add -f ml_models/*.pkl
git commit -m "Add ML models"
```

## Or Update .gitignore First

I've commented out the `.pkl` ignore line in `.gitignore`. Now you can use:

```bash
git add ml_models/*.pkl
git commit -m "Add ML models"
```

## Complete Deployment Commit

```bash
# Add everything
git add .

# Commit
git commit -m "Ready for deployment"

# Push to GitHub (after creating repo)
git remote add origin https://github.com/yourusername/mamacare.git
git branch -M main
git push -u origin main
```

