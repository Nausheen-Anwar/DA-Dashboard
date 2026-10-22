import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

CHARTS = ["Line plot", "Scatter plot", "Bar chart", "Area chart", "Histogram", "Box plot",
          "Violin plot", "Density plot", "Pie chart", "Count plot", "Heatmap (correlation)"]

NEEDS_XY = {"Line plot", "Scatter plot", "Bar chart", "Area chart"}
NEEDS_ONE = {"Histogram", "Box plot", "Violin plot", "Density plot", "Pie chart", "Count plot"}

# House colours, matching the dashboard theme. Any other name is passed to seaborn as-is.
PALETTES = {"teal": ["#0097AC", "#fe7096", "#047edf", "#07cdae", "#f5a25d", "#006E74"]}
INK = "#343a40"


def apply_limits(ax, xlim, ylim):
    if xlim[0] is not None or xlim[1] is not None:
        ax.set_xlim(xlim[0], xlim[1])
    if ylim[0] is not None or ylim[1] is not None:
        ax.set_ylim(ylim[0], ylim[1])


def make_chart(df, kind, x=None, ys=None, col=None, heat_cols=None, title="", xlim=(None, None),
               ylim=(None, None), grid=True, palette="deep", size=(10, 5.5)):
    sns.set_theme(style="whitegrid" if grid else "white", palette=PALETTES.get(palette, palette),
                  rc={"axes.edgecolor": "#D6E7E8", "grid.color": "#E4EFF0", "text.color": INK,
                      "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
    fig, ax = plt.subplots(figsize=size)
    ys = ys or []

    if kind == "Line plot":
        for y in ys:
            sns.lineplot(data=df, x=x, y=y, ax=ax, label=y)
    elif kind == "Scatter plot":
        for y in ys:
            sns.scatterplot(data=df, x=x, y=y, ax=ax, label=y)
    elif kind == "Bar chart":
        if len(df) > 60:
            raise ValueError("Bar chart supports up to 60 rows - narrow the row range.")
        long = df.melt(id_vars=x, value_vars=ys, var_name="series", value_name="value")
        sns.barplot(data=long, x=x, y="value", hue="series" if len(ys) > 1 else None, ax=ax)
        ax.set_ylabel(", ".join(ys))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    elif kind == "Area chart":
        d = df.sort_values(x)
        ax.stackplot(d[x], *[d[y] for y in ys], labels=ys, alpha=.75)
        ax.set_xlabel(x)
    elif kind == "Histogram":
        sns.histplot(data=df, x=col, kde=True, ax=ax)
    elif kind == "Box plot":
        sns.boxplot(data=df, y=col, ax=ax)
    elif kind == "Violin plot":
        sns.violinplot(data=df, y=col, ax=ax)
    elif kind == "Density plot":
        sns.kdeplot(data=df, x=col, fill=True, ax=ax)
    elif kind == "Pie chart":
        counts = df[col].astype(str).value_counts().head(10)
        ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
    elif kind == "Count plot":
        order = df[col].value_counts().head(30).index
        sns.countplot(data=df, x=col, order=order, ax=ax)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    elif kind == "Heatmap (correlation)":
        sns.heatmap(df[heat_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    else:
        raise ValueError("Unknown chart type.")

    if kind not in {"Pie chart", "Heatmap (correlation)"}:
        apply_limits(ax, xlim, ylim)
    if len(ys) > 1 and kind in NEEDS_XY:
        ax.legend()
    elif ax.get_legend() is not None and len(ys) <= 1:
        ax.get_legend().remove()
    if title.strip():
        ax.set_title(title.strip(), fontsize=14, weight="bold", color=INK)
    fig.tight_layout()
    return fig


def fig_bytes(fig, fmt="png") -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=200, bbox_inches="tight")
    return buf.getvalue()


MIME = {"png": "image/png", "pdf": "application/pdf", "svg": "image/svg+xml"}


def density_figure(values, x, normal, kde, column, method, mu, sigma, title=""):
    sns.set_theme(style="whitegrid", rc={"axes.edgecolor": "#D6E7E8", "grid.color": "#E4EFF0"})
    fig, ax = plt.subplots(figsize=(10, 5.5))
    if method in ("Kernel density estimate", "Both"):
        ax.plot(x, kde, lw=2.2, label="KDE", color="#006E74")
        ax.fill_between(x, kde, alpha=.15, color="#0097AC")
    if method in ("Normal distribution PDF", "Both"):
        ax.plot(x, normal, lw=2.2, ls="--", color="#07cdae", label=f"Normal(μ={mu:.3g}, σ={sigma:.3g})")
    ax.set_xlabel(column)
    ax.set_ylabel("Probability density")
    ax.set_title(title.strip(), fontsize=14, weight="bold")
    ax.legend()
    fig.tight_layout()
    return fig
