# AI Signal Analytics Platform

A Flask web app for analyzing signals. Upload a CSV file, filter the signal, look at its frequency spectrum, and download a PDF report.

## Screenshots

![Upload page](screenshots/upload.png)
![Result page](screenshots/result.png)

## Features

- Upload a signal as a CSV file
- Choose a filter: low-pass, high-pass or band-pass (Butterworth, zero-phase using `filtfilt`)
- Frequency analysis with FFT (Fast Fourier Transform)
- Static plots (Matplotlib) and interactive charts (Plotly) for the signal and its spectrum
- Download the results as a PDF report (ReportLab)

## Tech Stack

Python, Flask, NumPy, Pandas, SciPy, Matplotlib, Plotly, ReportLab, HTML, CSS, Bootstrap

## Project Structure

```
app.py               Flask app (upload, filtering, FFT, plots, PDF report)
generate_signal.py   Script to generate a sample signal
sample_signal.csv    Sample data to try the app
templates/           HTML pages (index, result)
static/              CSS and generated plots
utils/               Helper code
requirements.txt     Dependencies
```

## Run Locally

```bash
git clone https://github.com/JamadarBhuvan/AI-Signal-Analytics-Platform.git
cd AI-Signal-Analytics-Platform
python -m venv venv
source venv/Scripts/activate    # Windows Git Bash (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 and upload `sample_signal.csv` to try it.

## Author

Bhuvan Jamadar
