import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_step_response_analysis(csv_name):
    """Plot the cleaned data with step response characteristics highlighted"""
    
    # Load and clean data (same as param_calc.py)
    data_original = pd.read_csv(csv_name, header=None, names=["x", "y"])
    data_original = data_original.dropna()
    
    # Remove outliers
    p1 = data_original['y'].quantile(0.01)
    p99 = data_original['y'].quantile(0.99)
    data_cleaned = data_original[(data_original['y'] >= p1) & (data_original['y'] <= p99)]
    
    t = data_cleaned["x"].to_numpy()
    y = data_cleaned["y"].to_numpy()
    
    # Calculate key parameters
    y_init = y[10] if len(y) > 10 else y[0]
    y_final = y[-1]
    y_max = np.max(y)
    max_idx = np.argmax(y)
    
    # Calculate overshoot and time to peak
    overshoot = (y_max - y_final) / abs(y_final) if y_final != 0 else 0
    time_to_peak = t[max_idx] - t[0]
    
    # Create the plot
    plt.figure(figsize=(14, 8))
    
    # Plot the cleaned data
    plt.plot(t, y, 'b-', linewidth=1, alpha=0.8, label='Cleaned Data')
    
    # Highlight key points
    plt.axhline(y=y_final, color='red', linestyle='--', alpha=0.7, label=f'Final Value: {y_final:.4f}')
    plt.axhline(y=y_max, color='green', linestyle='--', alpha=0.7, label=f'Peak Value: {y_max:.4f}')
    plt.axhline(y=y_init, color='orange', linestyle='--', alpha=0.7, label=f'Initial Value: {y_init:.4f}')
    
    # Mark the peak
    plt.plot(t[max_idx], y_max, 'ro', markersize=8, label=f'Peak at t={t[max_idx]:.0f}')
    
    # Mark settling bounds (±2% of final value)
    settling_upper = y_final * 1.02
    settling_lower = y_final * 0.98
    plt.axhline(y=settling_upper, color='purple', linestyle=':', alpha=0.5, label='±2% Settling Band')
    plt.axhline(y=settling_lower, color='purple', linestyle=':', alpha=0.5)
    
    # Add annotations
    plt.annotate(f'Overshoot: {overshoot:.1f}', 
                xy=(t[max_idx], y_max), xytext=(t[max_idx] + 200, y_max),
                arrowprops=dict(arrowstyle='->', color='red', alpha=0.7),
                fontsize=10, bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    plt.annotate(f'Time to Peak: {time_to_peak:.0f}', 
                xy=(t[max_idx], y_max/2), xytext=(t[max_idx] - 300, y_max/2),
                arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7),
                fontsize=10, bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))
    
    # Formatting
    plt.xlabel("Time (ms)")
    plt.ylabel("Motor Position (rad)")
    plt.title(f"Step Response Analysis - {csv_name}")
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best')
    
    # Add statistics box
    stats_text = f"""Data Points: {len(data_cleaned)}
Outliers Removed: {len(data_original) - len(data_cleaned)}
Overshoot: {overshoot:.2f}
Time to Peak: {time_to_peak:.0f} ms
Initial Value: {y_init:.4f} rad
Final Value: {y_final:.4f} rad
Peak Value: {y_max:.4f} rad"""
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', fontsize=9,
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig("step_response_analysis.png", dpi=150, bbox_inches='tight')
    print(f"Step response analysis saved as 'step_response_analysis.png'")
    
    return {
        'overshoot': overshoot,
        'time_to_peak': time_to_peak,
        'y_init': y_init,
        'y_final': y_final,
        'y_max': y_max,
        'data_points': len(data_cleaned),
        'outliers_removed': len(data_original) - len(data_cleaned)
    }

if __name__ == "__main__":
    results = plot_step_response_analysis("lab1e4.csv")
    print("\nStep Response Characteristics:")
    for key, value in results.items():
        print(f"{key}: {value}")
