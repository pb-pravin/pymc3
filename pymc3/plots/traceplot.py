import matplotlib.pyplot as plt
import numpy as np

from .artists import histplot_op, kdeplot_op
from .utils import identity_transform, get_default_varnames, get_axis, make_2d


def traceplot(trace, varnames=None, transform=identity_transform, figsize=None, lines=None,
              combined=False, plot_transformed=False, grid=False, alpha=0.35, priors=None,
              prior_alpha=1, prior_style='--', ax=None):
    """Plot samples histograms and values.

    Parameters
    ----------

    trace : result of MCMC run
    varnames : list of variable names
        Variables to be plotted, if None all variable are plotted
    transform : callable
        Function to transform data (defaults to identity)
    figsize : figure size tuple
        If None, size is (12, num of variables * 2) inch
    lines : dict
        Dictionary of variable name / value  to be overplotted as vertical
        lines to the posteriors and horizontal lines on sample values
        e.g. mean of posteriors, true values of a simulation.
        If an array of values, line colors are matched to posterior colors.
        Otherwise, a default red line
    combined : bool
        Flag for combining multiple chains into a single chain. If False
        (default), chains will be plotted separately.
    plot_transformed : bool
        Flag for plotting automatically transformed variables in addition to
        original variables (defaults to False).
    grid : bool
        Flag for adding gridlines to histogram. Defaults to True.
    alpha : float
        Alpha value for plot line. Defaults to 0.35.
    priors : iterable of PyMC distributions
        PyMC prior distribution(s) to be plotted alongside posterior. Defaults
        to None (no prior plots).
    prior_alpha : float
        Alpha value for prior plot. Defaults to 1.
    prior_style : str
        Line style for prior plot. Defaults to '--' (dashed line).
    ax : axes
        Matplotlib axes. Accepts an array of axes, e.g.:

        >>> fig, axs = plt.subplots(3, 2) # 3 RVs
        >>> pymc3.traceplot(trace, ax=axs)

        Creates own axes by default.

    Returns
    -------

    ax : matplotlib axes

    """
    if varnames is None:
        varnames = get_default_varnames(trace, plot_transformed)

    if figsize is None:
        figsize = (12, len(varnames) * 2)

    ax = get_axis(ax, len(varnames), 2, squeeze=False, figsize=figsize)

    for i, v in enumerate(varnames):
        if priors is not None:
            prior = priors[i]
        else:
            prior = None
        for d in trace.get_values(v, combine=combined, squeeze=False):
            d = np.squeeze(transform(d))
            d = make_2d(d)
            if d.dtype.kind == 'i':
                hist_objs = histplot_op(ax[i, 0], d, alpha=alpha)
                colors = [h[-1][0].get_facecolor() for h in hist_objs]
            else:
                artists = kdeplot_op(ax[i, 0], d, prior, prior_alpha, prior_style)[0]
                colors = [a[0].get_color() for a in artists]
            ax[i, 0].set_title(str(v))
            ax[i, 0].grid(grid)
            ax[i, 1].set_title(str(v))
            ax[i, 1].plot(d, alpha=alpha)

            ax[i, 0].set_ylabel("Frequency")
            ax[i, 1].set_ylabel("Sample value")

            if lines:
                try:
                    if isinstance(lines[v], (float, int)):
                        line_values, colors = [lines[v]], ['r']
                    else:
                        line_values = np.atleast_1d(lines[v]).ravel()
                        if len(colors) != len(line_values):
                            raise AssertionError("An incorrect number of lines was specified for "
                                                 "'{}'. Expected an iterable of length {} or to "
                                                 " a scalar".format(v, len(colors)))
                    for c, l in zip(colors, line_values):
                        ax[i, 0].axvline(x=l, color=c, lw=1.5, alpha=0.75)
                        ax[i, 1].axhline(y=l, color=c,
                                         lw=1.5, alpha=alpha)
                except KeyError:
                    pass
        ax[i, 0].set_ylim(ymin=0)
    plt.tight_layout()
    return ax
