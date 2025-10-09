"""
MetricsPlotter module.

Provides the MetricsPlotter class for generating static and animated
metric plots from CSV files.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter

from .plot_styler import PlotStyler


class MetricsPlotter:
    """A class to handle static and animated plotting from a CSV file."""

    def __init__(
        self,
        csv_file: str,
        output_dir: str = "plots",
        dark_mode: bool = False,
        verbose: bool = True,
        marker_styles: list[str] | None = None,
    ):
        """
        Initialize MetricsPlotter.

        Parameters
        ----------
        csv_file : str
            Path to the CSV file containing metrics.
        output_dir : str, optional
            Directory where plots are saved. Default is 'plots'.
        dark_mode : bool, optional
            Whether to apply dark mode style. Default is False.
        verbose : bool, optional
            If False, suppress matplotlib INFO logs. Default is True.
        marker_styles : list[str] | None, optional
            List of marker styles for each metric.
            Defaults to ['o','s','^','D','v','x','*','+'].
        """
        self.csv_file = csv_file
        self.output_dir = output_dir
        self.dark_mode = dark_mode
        self.verbose = verbose
        self.marker_styles = marker_styles or [
            "o", "s", "^", "D", "v", "x", "*", "+",
        ]

        self.styler = PlotStyler(output_dir=self.output_dir)
        self.styler.apply_style(dark_mode=self.dark_mode)

        if not self.verbose:
            logging.getLogger("matplotlib").setLevel(logging.WARNING)

        self.df = pd.read_csv(self.csv_file, sep=";")
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"], unit="s")
        self.metric_cols = [
            col for col in self.df.columns if col != "timestamp"
        ]

    def plot_or_animate_metrics(
        self,
        animate: bool = False,
        interval: int = 1000,
        time_window: int | None = None,
        add_timestamp: bool = True,
        title: str = "Metrics Over Time",
        xlabel: str = "Timestamp",
        ylabel: str = "Value",
    ) -> None:
        """
        Plot or animate metrics.

        Parameters
        ----------
        animate : bool
            If True, generates an animated plot.
        interval : int
            Frame interval for animation in milliseconds.
        time_window : int or None
            Seconds to display for moving window in animation.
        add_timestamp : bool
            Append timestamp to filenames.
        title : str
            Plot title.
        xlabel : str
            X-axis label.
        ylabel : str
            Y-axis label.
        """
        base_name = os.path.splitext(os.path.basename(self.csv_file))[0]

        if not animate:
            self._plot_static(base_name, add_timestamp, title, xlabel, ylabel)
            return

        self._plot_animated(
            base_name, interval, time_window, add_timestamp,
            title, xlabel, ylabel,
        )

    def _plot_static(
        self,
        base_name: str,
        add_timestamp: bool,
        title: str,
        xlabel: str,
        ylabel: str,
    ) -> None:
        """
        Generate and save a static metrics plot.

        Parameters
        ----------
        base_name : str
            Base filename to use for saving the plot.
        add_timestamp : bool
            If True, append a timestamp to the saved file.
        title : str
            Plot title.
        xlabel : str
            Label for the X-axis.
        ylabel : str
            Label for the Y-axis.
        """
        fig, ax = plt.subplots()
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        for i, col in enumerate(self.metric_cols):
            ax.plot(
                self.df["timestamp"],
                self.df[col],
                marker=self.marker_styles[i % len(self.marker_styles)],
                linestyle="-",
                color=colors[i % len(colors)],
                label=col,
            )

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()

        filename = f"{base_name}_static.png"
        self.styler.save_plot(filename, fig=fig, add_timestamp=add_timestamp)
        if matplotlib.is_interactive():
            plt.show()
        plt.close(fig)

    def _plot_animated(
        self,
        base_name: str,
        interval: int,
        time_window: int | None,
        add_timestamp: bool,
        title: str,
        xlabel: str,
        ylabel: str,
    ) -> None:
        """
        Generate and save an animated metrics plot.

        Parameters
        ----------
        base_name : str
            Base filename to use for saving the animation.
        interval : int
            Frame interval for animation in milliseconds.
        time_window : int | None
            Number of seconds to display for moving window.
            If None, shows all data.
        add_timestamp : bool
            If True, append a timestamp to the saved file.
        title : str
            Plot title.
        xlabel : str
            Label for the X-axis.
        ylabel : str
            Label for the Y-axis.
        """
        fig, ax = plt.subplots()
        lines = []
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        for i, col in enumerate(self.metric_cols):
            line, = ax.plot(
                [],
                [],
                marker=self.marker_styles[i % len(self.marker_styles)],
                linestyle="-",
                color=colors[i % len(colors)],
                label=col,
            )
            lines.append(line)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()

        def init():
            for line in lines:
                line.set_data([], [])
            return lines

        def update(frame: int):
            current_data = self.df.iloc[: frame + 1]

            if time_window:
                end_time = current_data["timestamp"].iloc[-1]
                start_time = end_time - pd.Timedelta(seconds=time_window)
                visible_data = current_data[
                    current_data["timestamp"]
                    >= start_time
                ]
                ax.set_xlim(start_time, end_time)
                ymin = visible_data[self.metric_cols].min().min() - 1
                ymax = visible_data[self.metric_cols].max().max() + 1
                ax.set_ylim(ymin, ymax)
            else:
                visible_data = current_data
                ax.set_xlim(
                    self.df["timestamp"].min(),
                    self.df["timestamp"].max(),
                )
                ax.set_ylim(
                    self.df[self.metric_cols].min().min() - 1,
                    self.df[self.metric_cols].max().max() + 1,
                )

            for i, col in enumerate(self.metric_cols):
                lines[i].set_data(visible_data["timestamp"], visible_data[col])
            return lines

        suffix = "animated"
        if time_window:
            suffix += f"_window_{time_window}s"
        if self.dark_mode:
            suffix += "_dark_mode"
        if add_timestamp:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            suffix += f"_{ts}"

        output_path = os.path.join(
            self.output_dir, f"{base_name}_{suffix}.gif",
        )
        ani = FuncAnimation(
            fig, update, frames=len(self.df),
            init_func=init, blit=False, interval=interval,
        )
        ani.save(output_path, writer=PillowWriter(fps=1000 // interval))
        print(f"✅ Plot saved: {output_path}")
        if matplotlib.is_interactive():
            plt.show()
        plt.close(fig)
