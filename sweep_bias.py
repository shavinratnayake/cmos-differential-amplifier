import subprocess
import re
import numpy as np
import csv
from pathlib import Path

# Bias currents to test (in microamps)
currents = [25, 50, 100, 150, 200]

# Create the results folder if it doesn't exist
results_dir = Path("results")
results_dir.mkdir(exist_ok=True)

# Read the original SPICE circuit
original = Path("diff_amp.cir").read_text()

# Store measurements from each simulation
results = []

# Run a simulation for each bias current
for current in currents:

    print(f"Simulating IBIAS = {current} uA")

    # Replace the bias current in a copy of the circuit
    circuit = re.sub(
        r"\.param IBIAS=\S+",
        f".param IBIAS={current}u",
        original,
        flags=re.IGNORECASE
    )

    # Give each simulation its own output file
    circuit = circuit.replace(
        "results/gain_response.txt",
        f"results/gain_{current}uA.txt"
    )

    # Save the modified circuit as a separate file
    netlist = results_dir / f"bias_{current}uA.cir"
    netlist.write_text(circuit)

    # Run NGspice automatically
    simulation = subprocess.run(
        ["ngspice", "-b", str(netlist)],
        capture_output=True,
        text=True,
        check=True
    )

    # Collect the simulation output
    log = simulation.stdout + simulation.stderr

    # Extract power consumption
    power_match = re.search(
        r"(?m)^power\s*=\s*([+-]?\d+(?:\.\d+)?[eE][+-]?\d+)",
        log
    )

    if not power_match:
        raise RuntimeError(
            f"Could not find power for {current} uA:\n{log}"
        )

    power_w = float(power_match.group(1))

    # Read the frequency response
    data = np.loadtxt(results_dir / f"gain_{current}uA.txt")

    frequency = data[:, 0]
    gain_db = data[:, 1]

    # Find the low-frequency gain
    low_gain_db = gain_db[0]

    # Calculate the -3 dB threshold
    target = low_gain_db - 3.0103

    # Find where gain first drops below the threshold
    crossings = np.where(gain_db <= target)[0]

    if len(crossings) == 0:
        bandwidth_hz = float("nan")

    else:
        i = crossings[0]

        if i == 0:
            bandwidth_hz = frequency[0]

        else:
            # Interpolate between the two surrounding points
            x1, x2 = np.log10(frequency[i-1:i+1])
            y1, y2 = gain_db[i-1:i+1]

            log_bw = x1 + (target-y1)*(x2-x1)/(y2-y1)
            bandwidth_hz = 10**log_bw

    # Save measurements for this bias current
    results.append([
        current,
        round(low_gain_db, 3),
        round(bandwidth_hz / 1e6, 3),
        round(power_w * 1e6, 3)
    ])

# Save all measurements to a CSV file
with open(results_dir / "bias_sweep.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "bias_uA",
        "gain_dB",
        "bandwidth_MHz",
        "power_uW"
    ])

    writer.writerows(results)

# Display results
print("\nBias sweep results:")

for row in results:
    print(row)

print("\nSaved results/bias_sweep.csv")
