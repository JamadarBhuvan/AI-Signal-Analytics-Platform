import numpy as np
import pandas as pd

# Number of samples
N = 1000

# Sampling frequency
fs = 1000

# Time axis
t = np.arange(N) / fs

# Create signal
signal = (
    2*np.sin(2*np.pi*10*t) +      # 10 Hz
    1*np.sin(2*np.pi*80*t) +      # 80 Hz
    0.5*np.random.randn(N)        # Noise
)

# Save to CSV
df = pd.DataFrame({"Signal": signal})

df.to_csv("sample_signal.csv", index=False)

print("sample_signal.csv created successfully!")