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
    print(f"Y mean: {data['y'].mean():.4f}, std: {data['y'].std():.4f}")
    
    # More aggressive outlier removal using percentiles
    # Remove values beyond 1st and 99th percentiles
    p1 = data['y'].quantile(0.01)
    p99 = data['y'].quantile(0.99)
    
    before_count = len(data)
    data_clean = data[(data['y'] >= p1) & (data['y'] <= p99)]
    after_count = len(data_clean)
    
    print(f"Percentile outlier removal (1st-99th): {before_count} -> {after_count} points (removed {before_count - after_count})")
    print(f"Bounds: [{p1:.4f}, {p99:.4f}]")
    
    # Extract cleaned data
    t = data_clean["x"].to_numpy()
    y = data_clean["y"].to_numpy()
    
    print(f"Final data: {len(y)} points")
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
        damping = -ln_OS / denom
        
        print(f"Debug: ln(OS)={ln_OS:.3f}, damping={damping:.4f}")
        
        # Damping ratio should be between 0 and 1 for underdamped systems
        if damping < 0 or damping > 1:
            print(f"⚠️  Warning: Damping ratio {damping:.4f} is outside typical range [0,1]")
        
        return damping  # Take absolute value to ensure positive
    except ValueError as e:
        print(f"Error in damping calculation: {e}")
        return np.nan
    

def calc_settling(damp, frequency):
    return 4 / (damp * frequency)

def calc_frequency(tp, damping):
    return pi / (tp * math.sqrt(1 - damping**2))




def calc_k1():
    pass


def find_OS(): 
    global y, y_max, y_final, y_init

    y_final = y[-1]
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
    overshoot = (y_max - y_final) / step_size
    
    print(f"Debug: y_init={y_init:.4f}, y_final={y_final:.4f}, y_max={y_max:.4f}")
    print(f"Debug: step_size={step_size:.4f}, overshoot={overshoot:.4f}")
    
    return overshoot


def find_TP(): 
    global t, y, y_init, y_max
    
    # Find the index of the maximum value (first occurrence)
    max_idx = np.argmax(y)
    
    # Return time to peak from the start of measurement
    return t[max_idx] - t[0]

if __name__ == "__main__": 

    init()
    OS = find_OS()
    damp = calc_damping(OS)
    tp = find_TP()
    frequency = calc_frequency(tp, damp)
    settling = calc_settling(damp, frequency)
    
    # Calculate additional characteristics
    # natural_freq = frequency / math.sqrt(1 - damp**2) if damp < 1 else frequency
    # overshoot_percent = OS * 100 if not np.isnan(OS) else np.nan
    
    print("\n" + "="*60)
    print("           STEP RESPONSE CHARACTERISTICS")
    print("="*60)
    
    print(f"\n📊 DATA SUMMARY:")
    print(f"   • Data points analyzed: {len(y)}")
    print(f"   • Initial value (y₀):   {y_init:.4f} rad")
    print(f"   • Final value (y∞):     {y[-1]:.4f} rad")
    print(f"   • Peak value (yₘₐₓ):     {np.max(y):.4f} rad")
    
    print(f"\n⏱️  TIME DOMAIN CHARACTERISTICS:")
    print(f"   • Time to peak (tₚ):     {tp:.1f} ms")
    print(f"   • Settling time (t₅):    {settling:.1f} ms")
    
    print(f"\n📈 OVERSHOOT & DAMPING:")
    print(f"   • Overshoot ratio:       {OS:.3f}")
    # print(f"   • Overshoot percentage:  {overshoot_percent:.1f}%")
    print(f"   • Damping ratio (ζ):     {damp:.4f}")
    
    print(f"\n🔄 FREQUENCY CHARACTERISTICS:")
    # print(f"   • Damped frequency (ωd): {frequency:.6f} rad/ms")
    print(f"   • Natural frequency (ωn): {frequency:.6f} rad/ms")
    
    print(f"\n🎯 SYSTEM CLASSIFICATION:")
    if damp < 0:
        system_type = "⚠️  UNSTABLE (negative damping)"
    elif damp == 0:
        system_type = "🔄 UNDAMPED (oscillatory)"
    elif 0 < damp < 1:
        system_type = "📉 UNDERDAMPED (oscillatory with decay)"
    elif damp == 1:
        system_type = "⚖️  CRITICALLY DAMPED"
    elif damp > 1:
        system_type = "📊 OVERDAMPED"
    else:
        system_type = "❓ UNDEFINED"
    
    print(f"   • System type: {system_type}")
    
    print("\n" + "="*60)
    
    # Raw values for debugging (if needed)
    print(f"\n🔧 RAW VALUES (for debugging):")
    print(f"   OS={OS}")
    print(f"   damp={damp}")
    print(f"   tp={tp}")
    print(f"   frequency={frequency}")
    print(f"   settling={settling}")





