# Layout Generator
## 📌 Overview
Our project is a Web application that can ingest a JSON or Excel/CSV file to draw a building layout. The output of the app includes both a downloadable LaTeX file containing code to generate the layout and a PDF of the finished drawing. Users are able to further customize individual layouts with a flexible UI. Style settings are controlled in the app, and it is built using Django and Materialize-CSS.

---

## 🚀 Project Setup Guide
Follow these steps to set up the project on your local machine.

### ✅ Step 1: Update Package Lists
Update your system’s package lists before installing dependencies:
```bash
sudo apt-get update
```

### ✅ Step 2: Clone the Repository
Clone the project repository and navigate into the directory:
```bash
git clone https://github.com/SCCapstone/Layout_Generator.git
cd Layout_Generator
```

### ✅ Step 3: Install Python 3.11
Ensure you have Python 3.11 installed:
```bash
sudo apt install python3.11
```

### ✅ Step 4: Install Pipenv
We use Pipenv to manage dependencies. Install and create the virtual environment:
```bash
pip install pipenv
pipenv --python 3.11 install --ignore-pipfile
```

### ✅ Step 5: Activate the Virtual Environment
Enter the Pipenv shell:
```bash
pipenv shell
```

### ✅ Step 6: Install LaTeX Dependencies
Install required LaTeX packages for generating PDFs:
```bash
sudo apt install texlive-luatex texlive-fonts-recommended texlive-fonts-extra dvipng texlive-science poppler-utils
```

### ✅ Step 7: Run the Application
Start the Django development server:
```bash
python manage.py runserver
```
Once running, open your browser and visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 📦 Deployment
The web application is deployed using Railway.

Access it here: [Layout Generator on Railway](https://layoutgenerator.up.railway.app/)

---

## 🧪 Testing Guide
Our project includes unit tests and behavioral tests:
- Unit Tests: `tests/unit_tests.py`
- Behavioral Tests: `tests/behavioral_tests.py`

### 🔧 Testing Tools
We use Selenium and Chromedriver for automated testing.

#### Installation Guides:
- [Selenium Setup on Windows](https://medium.com/@patrick.yoho11/installing-selenium-and-chromedriver-on-windows-e02202ac2b08)
- [Selenium Setup on Mac](https://www.geeksforgeeks.org/how-to-install-selenium-webdriver-on-macos/)
- [Chromedriver Setup](https://chromedriver.chromium.org/getting-started)
- [Download Chromedriver](https://chromedriver.chromium.org/downloads)

⚠ **Ensure Selenium and Chromedriver versions are compatible!**

Install webdriver-manager:
```bash
pip install webdriver-manager
```

### ✅ Running Tests
Run the following commands to execute tests:
```bash
python manage.py test app1.tests.unit_tests
python manage.py test app1.tests.behavioral_tests
```
**Potential Behavioral Test Bug and Fix:**
If you happen to receive an error regarding the '--user-data-dir=selenium' argument, please add the following option to the WebDriver's initialization for each behavioral test...
```bash
options.add_argument('--headless')
```

---

## ✨ Coding Style Guide
We follow the Prettier coding style guide:
🔗 [Prettier.io](https://prettier.io/)

---

## 👥 Authors
| Name | Email | GitHub |
|------|----------------|-----------|
| Duayne Wright | duayne@email.sc.edu | [DuayneWright](https://github.com/DuayneWright) |
| Theodore Villalva | villalvt@email.sc.edu | [theodv](https://github.com/theodv) |
| Mark Johnson | maj32@email.sc.edu | [MarkJ351](https://github.com/MarkJ351) |
| Hayley Tinder | htinder@email.sc.edu | [hktinder](https://github.com/hktinder) |
| Brandon Hucks | bhucks@email.sc.edu | [branhucks](https://github.com/branhucks) |

## 🏦 Previous Contributors
| Name | Email | GitHub |
|------|----------------|-----------|
| Tyler Beetle | tbeetle22@gmail.com | [TBeetle](https://github.com/TBeetle) |
| Joey Missan | jmissan@email.sc.edu | [jmissan](https://github.com/jmissan) |
| Anna Michelitch | acm34@email.sc.edu | [acm34](https://github.com/acm34) |
| Grant Ward | jgward@email.sc.edu | [jgward](https://github.com/jgward) |
| Jordan Fowler | jsfowler@email.sc.edu | [jordansfowler](https://github.com/jordansfowler) |
