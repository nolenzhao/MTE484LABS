import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_cleaned_data(csv_name):
    # Load original data
    data_original = pd.read_csv(csv_name, header=None, names=["x", "y"])
    data_original = data_original.dropna()
    
    print(f"Original data: {len(data_original)} points")
    print(f"Y range: [{data_original['y'].min():.4f}, {data_original['y'].max():.4f}]")
    
    # Apply the same outlier removal as in param_calc.py
    p1 = data_original['y'].quantile(0.01)
    p99 = data_original['y'].quantile(0.99)
    
    data_cleaned = data_original[(data_original['y'] >= p1) & (data_original['y'] <= p99)]
    
    print(f"Cleaned data: {len(data_cleaned)} points (removed {len(data_original) - len(data_cleaned)})")
    print(f"Outlier bounds: [{p1:.4f}, {p99:.4f}]")
    
    # Create subplot with original and cleaned data
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot original data
    ax1.plot(data_original["x"], data_original["y"], 'b-', alpha=0.7, linewidth=0.5, label='Original data')
    ax1.set_xlabel("Timestamp (ms)")
    ax1.set_ylabel("Motor position (rad)")
    ax1.set_title("Original Data")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Highlight outliers
    outliers = data_original[(data_original['y'] < p1) | (data_original['y'] > p99)]
    if len(outliers) > 0:
        ax1.scatter(outliers["x"], outliers["y"], color='red', s=20, alpha=0.8, label=f'Outliers ({len(outliers)})')
        ax1.legend()
    
    # Plot cleaned data
    ax2.plot(data_cleaned["x"], data_cleaned["y"], 'g-', alpha=0.7, linewidth=0.5, label='Cleaned data')
    ax2.set_xlabel("Timestamp (ms)")
    ax2.set_ylabel("Motor position (rad)")
    ax2.set_title("Cleaned Data (Outliers Removed)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Add statistics as text
    stats_text = f"""Original: {len(data_original)} points
Cleaned: {len(data_cleaned)} points  
Removed: {len(data_original) - len(data_cleaned)} outliers
Y range: [{data_cleaned['y'].min():.4f}, {data_cleaned['y'].max():.4f}]"""
    
    ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig("cleaned_data_plot.png", dpi=150, bbox_inches='tight')
    print(f"Plot saved as 'cleaned_data_plot.png'")
    plt.show()

def plot(csv_name):
    data: pd.DataFrame = pd.read_csv(csv_name, header=None, names = ["x", "y"])
    plt.scatter(data["x"], data["y"])
    plt.xlabel("timestamp (ms)")
    plt.ylabel("motor position (rad)")
    plt.savefig("plot.png")

if __name__ == "__main__":
    # Plot both original and cleaned data
    plot_cleaned_data("lab1e4.csv")
    
    # Original plotting function (uncomment if you want the original plot too)
    # plot("lab1e4.csv")
