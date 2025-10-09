from matplotlib_tools import MetricsPlotter

# -------------------------
# Example usage
# -------------------------
csv_filename: str = "metrics.csv"

# Initialize the plotter
plotter = MetricsPlotter(csv_file=csv_filename, dark_mode=True, verbose=False)

# Static plot
plotter.plot_or_animate_metrics(animate=False, add_timestamp=True)

# Animated plot with all points
plotter.plot_or_animate_metrics(animate=True, interval=1000, add_timestamp=True)

# Animated plot showing last 60 seconds dynamically
plotter.plot_or_animate_metrics(animate=True, interval=1000, time_window=60, add_timestamp=True)
