# Contribution Guide

This document explains how to collaborate on the Web Scraping project in Python.

---

## Workflow

1. **Create a new branch:**
   ```bash
   git checkout -b feature/<branch-name>
   ```

2. **Make your changes and descriptive commits**
   ```bash
   git add .
   git commit -m "Added bla bla bla"
   ```

3. **Upload your branch to the remote repository**
   ```bash
   git push origin feature/project_webscraper
   ```

4. **Create a PR**
    From your branch to dev

**Summary**

Briefly describe the changes made and their purpose.

---

**Related Issue**


---

**Type**
- [ ] 🐛 Fix — Error correction
- [x] ✨ Feature — New feature
- [ ] 🧹 Refactor — Cleaning or restructuring
- [ ] 🧪 Test — Tests added or modified
- [ ] 📘 Docs — Documentation

---

**How to test**
Run the main module with:
   ```bash
   python src/main.py
   ```