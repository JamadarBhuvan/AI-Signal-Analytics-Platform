from datetime import datetime
report_data = {}
from flask import send_file
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import plotly.graph_objects as go
from scipy.signal import butter, filtfilt
import os
from scipy.fft import fft, fftfreq
import plotly.express as px
from flask import Flask, render_template, request

import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt



# -------------------------------
# Butterworth Filter Functions
# -------------------------------

def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low')
    return filtfilt(b, a, data)


def butter_highpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high')
    return filtfilt(b, a, data)


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist

    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

app = Flask(__name__)

# Folder paths
UPLOAD_FOLDER = "uploads"
GRAPH_FOLDER = "static/plots"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GRAPH_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        file = request.files["file"]

        if file:

            # Save uploaded CSV
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # Read CSV
            df = pd.read_csv(filepath)

            # First column as signal
            

            signal = df.iloc[:, 0]
            signal_array = signal.to_numpy(dtype=float)
            print("Signal Length:", len(signal_array))


            filter_type = request.form.get("filter_type")
            
            fs = float(request.form.get("sampling_frequency", 1000))
            filter_order = int(request.form.get("filter_order", 5))
            cutoff = float(request.form.get("cutoff_frequency", 50))

            low_cutoff = float(request.form.get("low_cutoff", 20))
            high_cutoff = float(request.form.get("high_cutoff", 100))

            
            print("Selected Filter:", filter_type)
            filtered_signal = signal_array.copy()

            nyquist = fs / 2
            # Filter order validation
            if filter_order < 1:
                return "Error: Filter order must be at least 1."
            
            # Low Pass / High Pass validation
            if filter_type in ["lowpass", "highpass"]:
                if cutoff >= nyquist:
                    return f"Error: Cutoff frequency must be less than Nyquist Frequency ({nyquist} Hz)."
                # Band Pass validation
                if filter_type == "bandpass":
                    if low_cutoff >= high_cutoff:
                        return "Error: Low cutoff must be smaller than High cutoff."
                    if high_cutoff >= nyquist:
                        return f"Error: High cutoff frequency must be less than Nyquist Frequency ({nyquist} Hz)."
            

            


            if len(signal_array) <= 18:
                filtered_signal = signal_array
            else:
                if filter_type == "lowpass":
                    
                    filtered_signal = butter_lowpass_filter(
                        signal_array,
                        cutoff,
                        fs,
                        filter_order
                        )
                elif filter_type == "highpass":
                    
                    filtered_signal = butter_highpass_filter(
                        signal_array,
                        cutoff,
                        fs,
                        filter_order
                        )
                elif filter_type == "bandpass":
                    

                    filtered_signal = butter_bandpass_filter(
                        signal_array,
                        low_cutoff,high_cutoff,fs,filter_order
                        )
                else:
                    filtered_signal = signal_array

            


            
            

            


            # Number of samples
            
            
            
            # Number of samples
            
            
            N = len(filtered_signal)

            # Sampling interval (assumed 1 second b/w sample)
            
            T = 1.0 / fs

            # Perform FFT
            
            fft_values = fft(filtered_signal)

            # Frequency bins
            frequencies = fftfreq(N, T)

            # Magnitude
            magnitude = abs(fft_values)
            
            
            # Keep only positive frequencies
            positive_freqs = frequencies[:N // 2]
            positive_magnitude = magnitude[:N // 2]
            
            
            peak_index = np.argmax(positive_magnitude[1:]) + 1
            peak_frequency = positive_freqs[peak_index]
            peak_magnitude = positive_magnitude[peak_index]
            
            
            print("Peak Frequency:", peak_frequency)
            print("Peak Magnitude:", peak_magnitude)

            


            # -----------------------------
            # Signal Statistics
            # -----------------------------
            mean_value = np.mean(filtered_signal)
            max_value = np.max(filtered_signal)
            min_value = np.min(filtered_signal)
            std_value = np.std(filtered_signal)
            rms_value = np.sqrt(np.mean(filtered_signal ** 2))
            peak_to_peak = np.max(filtered_signal) - np.min(filtered_signal)
            variance = np.var(filtered_signal)
            median = np.median(filtered_signal)
            energy = np.sum(filtered_signal ** 2)
            power = energy / len(filtered_signal)
            variance_value = np.var(filtered_signal)
            order = int(request.form["filter_order"])

            # -----------------------------
            # Plot Signal
            # -----------------------------
            plt.figure(figsize=(10, 4))

            plt.plot(filtered_signal)
            plt.title("Signal Plot")

            plt.xlabel("Sample Number")

            plt.ylabel("Amplitude")

            plt.grid(True)

            graph_filename = "signal_plot.png"

            graph_path = os.path.join(GRAPH_FOLDER, graph_filename)

            plt.savefig(graph_path)

            plt.close()
            
            plt.figure(figsize=(8,4))
            plt.plot(frequencies[:N//2], magnitude[:N//2])
            plt.title("Frequency Spectrum (FFT)")
            plt.xlabel("Frequency (Hz)")
            plt.ylabel("Magnitude")
            plt.grid(True)

            
            

            fft_path = os.path.join("static", "images", "fft_plot.png")
            
            os.makedirs("static/images", exist_ok=True)
            plt.savefig(fft_path)
            plt.close()

            print(graph_path)
            print(os.path.exists(graph_path))


            # -----------------------------
            # # Interactive Plotly Graph
            # # -----------------------------
            fig = go.Figure()

            # Original Signal

            fig.add_trace(
                 go.Scatter(
                      x=np.arange(len(signal)),
                      y=signal,
                      mode="lines",
                      name="Original Signal"
                      )
                      
                      )
            


             # Filtered Signal
            fig.add_trace(
                 go.Scatter(
                      x=np.arange(len(filtered_signal)),
                      y=filtered_signal,
                      mode="lines",
                      name="Filtered Signal"
                      )
                      )
            

            fig.update_layout(
                 title="Original vs Filtered Signal",
                 xaxis_title="Samples",
                 yaxis_title="Amplitude",
                 template="plotly_white"
                 )
            plot_html = fig.to_html(full_html=False)
            print("Plot HTML generated:", plot_html[:100])


            # -----------------------------
            # FFT Analysis
            # -----------------------------

            

            

            
            N = len(filtered_signal)
            fft_values = fft(filtered_signal)
            T = 1.0

            frequencies = fftfreq(N, T)

            positive_freq = frequencies[:N // 2]

            positive_fft = np.abs(fft_values[:N // 2])

            fft_fig = px.line(
                  x=positive_freq,
                  y=positive_fft,
                  labels={
                        "x": "Frequency",
                        "y": "Magnitude"
                        },
                        title="Frequency Spectrum (FFT)"
                        )
            fft_fig.update_layout(
                  template="plotly_white"
                  )
            fft_html = fft_fig.to_html(full_html=False)


            

            report_data.clear()
            report_data.update({
                "mean": round(mean_value, 2),
                "maximum": round(max_value, 2),
                "minimum": round(min_value, 2),
                "rms": round(rms_value, 2),
                "std": round(std_value, 2),
                "variance": round(variance, 2),
                "energy": round(energy, 2),
                "power": round(power, 2),
                "peak_frequency": round(peak_frequency, 2),
                "peak_magnitude": round(peak_magnitude, 2),
                "filter_type": filter_type,
                "sampling_frequency": fs,
                "filter_order": order,
                "cutoff_frequency": cutoff,
                "filename": file.filename,
                "number_of_samples": len(signal_array),
                "generated_on": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                })
            print(report_data)

            return render_template(
                "result.html",
                filename=file.filename,
                table=df.head().to_html(
                    classes="table table-striped table-hover table-bordered",
                    index=False
                    ),
                    graph="plots/" + graph_filename,
                    mean=round(mean_value, 2),
                    maximum=round(max_value, 2),
                    minimum=round(min_value, 2),
                    std=round(std_value, 2),
                    rms=round(rms_value, 2),

                    peak_to_peak=round(peak_to_peak, 2),
                    variance=round(variance, 2),
                    median=round(median, 2),
                    energy=round(energy, 2),
                    power=round(power, 2),
                    plot_html=plot_html,
                    fft_html=fft_html,
                    
                    peak_frequency=round(peak_frequency, 2),
                    peak_magnitude=round(peak_magnitude, 2)
                    
                    )

    return render_template("index.html")



@app.route("/download_report")
def download_report():

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("AI Signal Analytics Platform", styles["Title"]))
    story.append(Paragraph("<br/>", styles["BodyText"]))
    story.append(Paragraph("<b>File Information</b>", styles["Heading2"]))
    story.append(
        Paragraph(
            f"<b>Filename:</b> {report_data['filename']}",
            styles["BodyText"]
            )
            )
    story.append(
        Paragraph(
            f"<b>Date & Time:</b> {report_data['generated_on']}",
            styles["BodyText"]
            )
            )
    story.append(
        Paragraph(
            f"<b>Number of Samples:</b> {report_data['number_of_samples']}",
            styles["BodyText"]
            )
            )
    story.append(Paragraph("<br/>", styles["BodyText"]))
    story.append(Paragraph("<b>Signal Statistics</b>", styles["Heading2"]))
    story.append(Paragraph(f"<b>Mean:</b> {report_data['mean']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Maximum:</b> {report_data['maximum']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Minimum:</b> {report_data['minimum']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>RMS:</b> {report_data['rms']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Standard Deviation:</b> {report_data['std']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Variance:</b> {report_data['variance']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Energy:</b> {report_data['energy']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Power:</b> {report_data['power']}", styles["BodyText"]))
    story.append(Paragraph("<br/>", styles["BodyText"]))
    story.append(Paragraph("<b>FFT Analysis</b>", styles["Heading2"]))
    story.append(Paragraph(f"<b>Peak Frequency:</b> {report_data['peak_frequency']} Hz", styles["BodyText"]))
    story.append(Paragraph(f"<b>Peak Magnitude:</b> {report_data['peak_magnitude']}", styles["BodyText"]))
    story.append(Paragraph("<br/>", styles["BodyText"]))
    story.append(Paragraph("<b>Filtering Information</b>", styles["Heading2"]))
    story.append(Paragraph(f"<b>Filter Type:</b> {report_data['filter_type']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Sampling Frequency:</b> {report_data['sampling_frequency']} Hz", styles["BodyText"]))
    story.append(Paragraph(f"<b>Filter Order:</b> {report_data['filter_order']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Cutoff Frequency:</b> {report_data['cutoff_frequency']}", styles["BodyText"]))


    story.append(Paragraph("<br/>", styles["BodyText"]))
    story.append(Paragraph("<b>Signal Plot</b>", styles["Heading2"]))
    
    signal_image = Image(os.path.join(GRAPH_FOLDER, "signal_plot.png"))
    signal_image.drawWidth = 450
    signal_image.drawHeight = 180
    story.append(signal_image)

    print(os.path.join(GRAPH_FOLDER, "signal_plot.png"))
    print(os.path.exists(os.path.join(GRAPH_FOLDER, "signal_plot.png")))

    story.append(Paragraph("<br/>", styles["BodyText"]))
    story.append(Paragraph("<b>FFT Plot</b>", styles["Heading2"]))
    fft_image = Image("static/images/fft_plot.png")
    fft_image.drawWidth = 450
    fft_image.drawHeight = 225
    story.append(fft_image)

    doc.build(story)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Signal_Report.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)