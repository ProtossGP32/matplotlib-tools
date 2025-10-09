"""
Matplotlib Tools Package.

Provides utilities for creating styled static
and animated plots from CSV metrics.

Submodules
----------
- plot_styler: Contains the PlotStyler class for configuring
               Matplotlib styles and saving figures with metadata.
- metrics_plotter: Contains the MetricsPlotter class for
                   generating static and animated metric plots from CSV files.

Public Classes
--------------
- PlotStyler: Applies consistent styling to plots and handles
              saving figures with metadata.
- MetricsPlotter: Generates static or animated plots for CSV metric data,
                  with optional dark mode and time windowing.
"""
from __future__ import annotations

from .metrics_plotter import MetricsPlotter
from .plot_styler import PlotStyler

__all__ = ["PlotStyler", "MetricsPlotter"]
