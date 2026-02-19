# Contributing to Fiznum

Thank you for wanting to share your Python code! Follow the steps below to submit your contribution.

## How to Contribute

### 1. Fork the Repository

Click the **Fork** button at the top-right of this page to create your own copy of the repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/<your-username>/Fiznum.git
cd Fiznum
```

### 3. Create a Folder for Your Submission

Place your Python file(s) inside the `submissions/` directory, in a subfolder named after you or your project:

```
submissions/
└── your_username/
    └── your_script.py
```

For example:

```
submissions/
└── adam/
    └── fizzbuzz.py
```

### 4. Write Your Python Code

- Use **Python 3.6+** syntax.
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines.
- Add a short docstring or comment at the top of your file describing what it does.
- Keep each file focused on a single script or solution.

### 5. Commit and Push

```bash
git add submissions/your_username/your_script.py
git commit -m "Add your_script.py by your_username"
git push origin main
```

### 6. Open a Pull Request

Go to the original repository on GitHub and click **New Pull Request**. Select your fork and branch, then submit.

## Code Style

All submitted Python code is automatically checked with [flake8](https://flake8.pycqa.org/). Your pull request will fail CI if there are linting errors. You can check locally before submitting:

```bash
pip install flake8
flake8 submissions/your_username/your_script.py
```

## What to Submit

- Python scripts or programs
- Solutions to coding challenges (e.g., FizzBuzz, Fibonacci, sorting algorithms)
- Useful utilities or tools written in Python
- Anything you find interesting and worth sharing!

## Code of Conduct

- Be respectful and constructive in pull request reviews.
- Do not submit malicious, harmful, or offensive code.
- Keep submissions original or properly attributed.
