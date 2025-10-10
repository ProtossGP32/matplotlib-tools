"""
Example script demonstrating usage of the MetricsPlotter class.

This example shows how to load metric data from a CSV file and generate both
static and animated visualizations using the MetricsPlotter utility.

Features illustrated in this example:
- Static plotting with optional dark mode styling.
- Animated plots that dynamically update over time.
- Optional time window to display only the most recent data points.
- Automatic timestamping of output filenames.
- Customizable plot titles and axis labels.
- Custom marker styles for metrics.

The resulting plots are saved in the "plots" directory by default.

Parameters
----------
csv_filename : str
    Path to the CSV file containing metric data.
animate : bool, optional
    Whether to generate an animated plot. Default is False.
interval : int, optional
    Frame interval for animations in milliseconds. Default is 1000.
time_window : int or None, optional
    Number of seconds to display for moving window in animated plots.
    If None, shows all data. Default is None.
add_timestamp : bool, optional
    Whether to append a timestamp to the saved filename. Default is True.
title : str, optional
    Plot title. Default is "Metrics Over Time".
xlabel : str, optional
    Label for the X-axis. Default is "Timestamp".
ylabel : str, optional
    Label for the Y-axis. Default is "Metric Value".
marker_styles : list[str], optional
    List of marker styles for each metric. Default is None.
"""
from __future__ import annotations

from matplotlib_tools import MetricsPlotter

csv_filename = "metrics.csv"

# Custom marker styles for metrics
custom_markers = ["o", "s", "^", "D"]

# Initialize the MetricsPlotter with custom markers
plotter = MetricsPlotter(
    csv_file=csv_filename,
    dark_mode=True,
    verbose=False,
    marker_styles=custom_markers,
)

# -------------------------
# Static plot
# -------------------------
plotter.plot_or_animate_metrics(
    animate=False,
    add_timestamp=True,
    title="Static Metrics Over Time",
    xlabel="Timestamp",
    ylabel="Metric Value",
    format="png",
)

# -------------------------
# Animated plot with all points
# -------------------------
plotter.plot_or_animate_metrics(
    animate=True,
    interval=1000,
    add_timestamp=True,
    title="Animated Metrics Over Time",
    xlabel="Timestamp",
    ylabel="Metric Value",
)

# -------------------------
# Animated plot showing last 60 seconds dynamically
# -------------------------
plotter.plot_or_animate_metrics(
    animate=True,
    interval=1000,
    time_window=60,
    add_timestamp=True,
    title="Animated Metrics (Last 60s)",
    xlabel="Timestamp",
    ylabel="Metric Value",
)
