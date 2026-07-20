from __future__ import annotations

import logging
import os
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation

from .plot_styler import PlotStyler


class MetricsPlotter:
    """
    A class to handle static and animated plotting of metrics from a CSV file.
    """

    def __init__(self, csv_file: str, output_dir: str = "plots", dark_mode: bool = False, verbose: bool = True):
        """
        Initialize the MetricsPlotter.

        Parameters
        ----------
        csv_file : str
            Path to the CSV file.
        output_dir : str, optional
            Directory where plots or animations will be saved.
        dark_mode : bool, optional
            Whether to apply dark mode styling.
        verbose : bool, optional
            If False, suppress matplotlib INFO logs.
        """
        self.csv_file = csv_file
        self.output_dir = output_dir
        self.dark_mode = dark_mode
        self.verbose = verbose

        self._load_csv()
        self.styler = PlotStyler(output_dir=output_dir)
        self.styler.apply_style(dark_mode=dark_mode)

        # Handle matplotlib logging
        self._mpl_logger = logging.getLogger("matplotlib")
        self._old_level = self._mpl_logger.level
        if not verbose:
            self._mpl_logger.setLevel(logging.WARNING)

    def _load_csv(self):
        self.df = pd.read_csv(self.csv_file, sep=";")
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], unit="s")
        self.metric_cols = [
            col for col in self.df.columns if col != 'timestamp']

    def _compose_filename(self, base_name: str, suffix: str, add_timestamp: bool = True) -> str:
        """Compose a filename without output_dir, PlotStyler will handle the directory."""
        if self.dark_mode:
            suffix += "_dark_mode"
        if add_timestamp:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            suffix += f"_{ts}"
        return f"{base_name}_{suffix}"

    def plot_or_animate_metrics(self, animate: bool = False, interval: int = 1000, time_window: int | None = None, add_timestamp: bool = True):
        """
        Create static or animated plot of metrics.

        Parameters
        ----------
        animate : bool, optional
            Whether to create an animated plot. Default is False.
        interval : int, optional
            Interval in milliseconds for animation frames. Default 1000.
        time_window : int or None, optional
            If specified, only the last `time_window` seconds are displayed in animation.
        add_timestamp : bool, optional
            If True, append timestamp to output filenames.
        """
        base_name = os.path.splitext(os.path.basename(self.csv_file))[0]

        if not animate:
            self._plot_static(base_name, add_timestamp)
            return

        self._plot_animated(base_name, interval, time_window, add_timestamp)

        self._mpl_logger.setLevel(self._old_level)
        if matplotlib.is_interactive():
            plt.show()

    def _plot_static(self, base_name: str, add_timestamp: bool):
        fig, ax = plt.subplots()
        markers = ["o", "s", "^", "D", "v", "x", "*", "+"]
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        for i, col in enumerate(self.metric_cols):
            ax.plot(self.df['timestamp'], self.df[col], marker=markers[i % len(
                markers)], color=colors[i % len(colors)], label=col)

        ax.set_title("Metrics Over Time")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(True, which="both", linestyle="--", alpha=0.3)
        fig.autofmt_xdate()

        filename = self._compose_filename(base_name, "plot", add_timestamp)
        self.styler.save_plot(filename, fig=fig, add_timestamp=False)
        if matplotlib.is_interactive():
            plt.show()

    def _plot_animated(self, base_name: str, interval: int, time_window: int | None, add_timestamp: bool):
        fig, ax = plt.subplots()
        lines = []
        markers = ["o", "s", "^", "D", "v", "x", "*", "+"]
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        for i, col in enumerate(self.metric_cols):
            line, = ax.plot([], [], marker=markers[i % len(markers)],
                            color=colors[i % len(colors)], label=col)
            lines.append(line)

        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Value")
        ax.set_title("Animated Metrics Over Time")
        ax.legend()
        ax.grid(True, which="both", linestyle="--", alpha=0.3)
        fig.autofmt_xdate()

        def animate_frame(frame):
            current_data = self.df.iloc[:frame+1]
            for i, col in enumerate(self.metric_cols):
                lines[i].set_data(current_data['timestamp'], current_data[col])

            if time_window is not None:
                end_time = current_data['timestamp'].iloc[-1]
                start_time = end_time - pd.Timedelta(seconds=time_window)
                ax.set_xlim(start_time, end_time)
                visible_data = current_data[current_data['timestamp']
                                            >= start_time]
                ymin = visible_data[self.metric_cols].min().min() - 1
                ymax = visible_data[self.metric_cols].max().max() + 1
                ax.set_ylim(ymin, ymax)
            else:
                ax.set_xlim(self.df['timestamp'].min(),
                            self.df['timestamp'].max())
                ax.set_ylim(self.df[self.metric_cols].min().min(
                ) - 1, self.df[self.metric_cols].max().max() + 1)
            return lines

        suffix = "animated" if time_window is None else f"animated_window_{time_window}s"
        filename = self._compose_filename(base_name, suffix, add_timestamp)
        output_path = os.path.join(self.output_dir, f"{filename}.gif")

        # Temporarily suppress matplotlib logs during animation save
        old_level = self._mpl_logger.level
        if not self.verbose:
            self._mpl_logger.setLevel(logging.WARNING)

        ani = FuncAnimation(fig, animate_frame, frames=len(
            self.df), interval=interval, blit=False, repeat=False)
        ani.save(output_path, writer="pillow", fps=1000//interval)
        print(f"✅ Plot saved: {output_path}")

        self._mpl_logger.setLevel(old_level)
        if matplotlib.is_interactive():
            plt.show()
