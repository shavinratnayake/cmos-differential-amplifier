import numpy as np
import matplotlib.pyplot as plt

# Load frequency and gain data from NGspice
data = np.loadtxt("results/gain_response.txt")

frequency = data[:, 0]
gain_db = data[:, 1]

# Measured amplifier characteristics
low_freq_gain = 46.96643
bandwidth = 38.36354e6
cutoff_gain = low_freq_gain - 3.0103

# Create the graph
plt.figure(figsize=(9, 5))

plt.semilogx(
    frequency,
    gain_db,
    label="CMOS Differential Amplifier"
)

# Mark the -3 dB bandwidth
plt.axhline(
    cutoff_gain,
    color="red",
    linestyle="--",
    label="-3 dB Gain"
)

plt.axvline(
    bandwidth,
    color="green",
    linestyle="--",
    label="Bandwidth = 38.36 MHz"
)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Voltage Gain (dB)")
plt.title("CMOS Differential Amplifier - AC Frequency Response")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()

# Save graph
plt.savefig("results/gain_response.png", dpi=300)
print("Graph saved to results/gain_response.png")
