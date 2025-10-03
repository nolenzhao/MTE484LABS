import argparse
import math
import pandas as pd
import numpy as np


parser = argparse.ArgumentParser(description='lab1')
parser.add_argument("--file", help = "data", required = True)
parser.add_argument('-o', help='overshoot ', required=False)
parser.add_argument('-t','--tp', help='Time to first peak', required=False)

args = vars(parser.parse_args())

pi = 3.14159
e = 2.71828



t: np.ndarray
y: np.ndarray
data: pd.DataFrame
y_init: float
y_max: float
y_final: float

def remove_outliers_iqr(data, column='y', factor=1.5):
    """Remove outliers using Interquartile Range (IQR) method"""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - factor * IQR
    upper_bound = Q3 + factor * IQR
    
    before_count = len(data)
    filtered_data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
    after_count = len(filtered_data)
    
    print(f"IQR outlier removal: {before_count} -> {after_count} points (removed {before_count - after_count})")
    print(f"Bounds: [{lower_bound:.4f}, {upper_bound:.4f}]")
    return filtered_data

def remove_outliers_zscore(data, column='y', threshold=3):
    """Remove outliers using Z-score method"""
    z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
    before_count = len(data)
    filtered_data = data[z_scores <= threshold]
    after_count = len(filtered_data)
    
    print(f"Z-score outlier removal: {before_count} -> {after_count} points (removed {before_count - after_count})")
    return filtered_data

def smooth_data(y, window_size=5):
    """Apply moving average smoothing"""
    if window_size <= 1:
        return y
    
    # Pad the data to handle edges
    pad_size = window_size // 2
    y_padded = np.pad(y, pad_size, mode='edge')
    
    # Apply moving average
    smoothed = np.convolve(y_padded, np.ones(window_size)/window_size, mode='same')
    
    # Remove padding
    return smoothed[pad_size:-pad_size]

def init(): 
    global data, t, y, y_init

    data = pd.read_csv(args['file'], header=None, names = ["x", "y"])
    # Remove any rows with NaN values
    data = data.dropna()
    
    print(f"Original data: {len(data)} points")
    print(f"Y range: [{data['y'].min():.4f}, {data['y'].max():.4f}]")
    
    # Use all data - no outlier removal for step response analysis
    t = data["x"].to_numpy()
    y = data["y"].to_numpy()
    
    print(f"Using all {len(y)} data points")
    print(f"Final Y range: [{y.min():.4f}, {y.max():.4f}]")
    
    # Set initial value for overshoot calculation
    y_init = y[10] if len(y) > 10 else y[0]
    print(f"Final Y range: [{y.min():.4f}, {y.max():.4f}]")
    
    # Set initial value for overshoot calculation
    y_init = y[10] if len(y) > 10 else y[0]


def calc_damping(OS): 
    # Check for invalid overshoot values
    if np.isnan(OS) or OS <= 0:
        print(f"Warning: Invalid overshoot value: {OS}")
        return np.nan
    
    try:
        # For overshoot in decimal form (not percentage)
        # The relationship is: OS = exp(-π*ζ/√(1-ζ²))
        # Solving for ζ: ζ = -ln(OS) / √(π² + ln(OS)²)
        ln_OS = math.log(OS)
        denom = math.sqrt(pi**2 + ln_OS**2)
        return  -ln_OS / denom
        
    except ValueError as e:
        print(f"Error in damping calculation: {e}")
        return np.nan
    

def calc_settling(damp, frequency):
    return 4 / (damp * frequency)

def calc_frequency(tp, damping):
    return pi / (tp * math.sqrt(1 - damping**2))


def calc_tau(damp, frequency):
    return 1 / ( 2 *damp * frequency)

def calc_k1(frequency, tau, gain): 
    return (frequency**2 * tau) / gain


def find_OS(): 
    global y, y_max, y_final, y_init

    y_final = y[-1]
    
    # y_max should already be set by find_TP()
    if 'y_max' not in globals() or y_max is None:
        y_max = np.max(y)
    
    # Check for NaN or invalid values
    if np.isnan(y_final) or np.isnan(y_max):
        print(f"Warning: NaN detected - y_final={y_final}, y_max={y_max}")
        return np.nan
    
    # For a step response, overshoot should be calculated relative to the step size
    # Step size is the difference between final and initial values
    step_size = abs(y_final - y_init)
    
    if step_size == 0:
        print(f"Warning: Step size is zero (y_init={y_init}, y_final={y_final})")
        return 0.0
    
    # Correct overshoot calculation: (peak - steady_state) / step_size
    overshoot = ((y_max - y_init) - (step_size)) / step_size
    # overshoot = (y_max - y_final) / step_size
    
    print(f"Debug: y_init={y_init:.4f}, y_final={y_final:.4f}, y_max={y_max:.4f}")
    print(f"Debug: step_size={step_size:.4f}, overshoot={overshoot:.4f}")
    
    return overshoot


def find_TP(): 
    global t, y, y_init, y_max
    
    # Find the index of the maximum value in the raw data
    max_idx = np.argmax(y)
    y_max = y[max_idx]
    
    print(f"Peak detection: max={y_max:.4f} at idx={max_idx}, time={(t[max_idx] - t[0])/1000:.3f}s")
    
    # Return time to peak from the start of measurement
    return (t[max_idx] - t[0]) / 1000 # Convert ms to s

if __name__ == "__main__": 

    kp = 18.0

    init()
    tp = find_TP()  # Call this first to set y_max with smoothed value
    OS = find_OS()  # Now this will use the smoothed y_max
    damp = calc_damping(OS)
    frequency = calc_frequency(tp, damp)
    settling = calc_settling(damp, frequency)
    tau = calc_tau(damp, frequency)
    k1 = calc_k1(frequency, tau, kp)  # Assuming gain
    
    # Calculate additional characteristics
    # natural_freq = frequency / math.sqrt(1 - damp**2) if damp < 1 else frequency
    # overshoot_percent = OS * 100 if not np.isnan(OS) else np.nan
    print("\n")
    
    print(f"{OS=}")
    print(f"{damp=}")
    print(f"{tp=}")
    print(f"{frequency=}")
    print(f"{settling=}")
    print(f"{tau=}")
    print(f"{k1=}")









