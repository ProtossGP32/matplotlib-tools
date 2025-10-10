"""
PlotStyler module.

Provides the PlotStyler class for configuring Matplotlib styles and saving
plots with metadata, timestamps, and optional dark mode.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib import rcParams
from matplotlib.figure import Figure


class PlotStyler:
    """Utility for applying consistent Matplotlib styles and saving figures."""

    def __init__(
        self,
        base_font: str = "DejaVu Sans",
        base_size: int = 12,
        output_dir: str = "plots",
        author: str = "Data Engineering Team",
        log_level: int = logging.INFO,
    ):
        """
        Initialize a PlotStyler.

        Parameters
        ----------
        base_font : str, optional
            Base font family used across plots.
        base_size : int, optional
            Default font size.
        output_dir : str, optional
            Default directory where plots are saved.
        author : str, optional
            Default author name embedded in saved plot metadata.
        log_level : int, optional
            Logging level for internal messages.
        """
        self.base_font = base_font
        self.base_size = base_size
        self.output_dir = output_dir
        self.author = author

        self.light_colors = [
            "#4C72B0", "#55A868", "#C44E52", "#8172B3",
            "#CCB974", "#64B5CD",
        ]
        self.dark_colors = [
            "#A6CEE3", "#B2DF8A", "#FB9A99", "#CAB2D6",
            "#FFFF99", "#B3DE69",
        ]

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        self.logger = logging.getLogger(__name__)

    def apply_style(self, dark_mode: bool = False) -> None:
        """
        Apply the global Matplotlib style.

        Parameters
        ----------
        dark_mode : bool, optional
            If True, enables dark background theme.
        """
        rcParams.update({
            "font.family": self.base_font,
            "font.size": self.base_size,
            "axes.titlesize": self.base_size + 2,
            "axes.labelsize": self.base_size,
            "legend.fontsize": self.base_size - 1,
            "xtick.labelsize": self.base_size - 1,
            "ytick.labelsize": self.base_size - 1,
            "figure.figsize": (8, 5),
            "figure.autolayout": True,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "grid.linestyle": "--",
            "lines.linewidth": 2.0,
            "lines.markersize": 6,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "legend.frameon": False,
            "savefig.bbox": "tight",
            "savefig.dpi": 300,
        })

        if dark_mode:
            rcParams.update({
                "axes.facecolor": "#222222",
                "figure.facecolor": "#222222",
                "axes.edgecolor": "#AAAAAA",
                "axes.labelcolor": "#FFFFFF",
                "xtick.color": "#FFFFFF",
                "ytick.color": "#FFFFFF",
                "text.color": "#FFFFFF",
                "axes.prop_cycle": cycler(color=self.dark_colors),
            })
        else:
            rcParams.update({
                "axes.facecolor": "#FFFFFF",
                "figure.facecolor": "#FFFFFF",
                "axes.edgecolor": "#333333",
                "axes.labelcolor": "#111111",
                "xtick.color": "#111111",
                "ytick.color": "#111111",
                "text.color": "#111111",
                "axes.prop_cycle": cycler(color=self.light_colors),
            })

    def save_plot(
        self,
        filename: str,
        fig: Figure | None = None,
        add_timestamp: bool = True,
        dpi: int = 300,
        metadata: dict | None = None,
        fmt: str | None = "png",
    ) -> str:
        """
        Save a Matplotlib figure with consistent formatting and metadata.

        Parameters
        ----------
        filename : str
            Base name for the saved file.
        fig : matplotlib.figure.Figure | None, optional
            The figure object to save. If None, uses the current active figure.
        add_timestamp : bool, optional
            Whether to append a timestamp to the filename.
        dpi : int, optional
            Image resolution in dots per inch.
        metadata : dict | None, optional
            Additional metadata to embed in the file.
        fmt : str | None, optional
            Format override (e.g., "png", "pdf", "gif", "eps").

        Returns
        -------
        str
            The full path to the saved file.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        if fmt:
            filename = f"{os.path.splitext(filename)[0]}.{fmt}"

        if add_timestamp:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{os.path.splitext(filename)[0]}_{ts}" \
                       f"{os.path.splitext(filename)[1]}"

        path = os.path.join(self.output_dir, filename)

        base_metadata = {
            "Title": os.path.splitext(filename)[0],
            "Author": self.author,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if metadata:
            base_metadata.update(metadata)

        if fig is None:
            fig = plt.gcf()

        fig.savefig(
            path, dpi=dpi, bbox_inches="tight",
            metadata=base_metadata, format=fmt,
        )
        print(f"✅ Plot saved: {path}")
        return path
