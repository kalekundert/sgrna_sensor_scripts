#!/usr/bin/env python3

import re, contextlib, fcmcmp
import numpy as np, matplotlib.pyplot as plt
import warnings; warnings.simplefilter("error", FutureWarning)
from pprint import pprint

fluorescence_controls = {
        'FITC-A': 'Red-A',
        'Red-A': 'FITC-A', 
}


class AnalyzedWell (fcmcmp.Well):

    def __init__(self, experiment, well, channel=None, normalize_by=None, 
            log_toggle=False, histogram=False, pdf=False, mode=False):

        super().__init__(well.label, well.meta, well.data)

        self.experiment = experiment
        self.channel_override = channel
        self.normalize_by = normalize_by
        self.log_toggle = log_toggle
        self.calc_histogram = histogram
        self.calc_pdf = pdf
        self.calc_mode = mode

        self.measurements = None
        self.log_scale = None
        self.channel = None
        self.control_channel = None
        self.x = self.y = None
        self.loc = None

        self._find_measurements()

    def estimate_distribution(self, axes_or_xlim):
        if isinstance(axes_or_xlim, plt.Axes):
            xlim = axes_or_xlim.get_xlim()
        else:
            xlim = axes_or_xlim

        self._find_distribution(xlim)

    def _find_measurements(self):
        # Pick the channel to display based on what the user asked for, or the 
        # properties of the experiment if nothing was asked for.
        self.channel = pick_channel(self.experiment, self.channel_override)

        # If normalization is requested but no particular channel is given, try 
        # to find a default fluorescent control channel.
        if self.normalize_by is True:
            try: self.control_channel = fluorescence_controls[self.channel]
            except KeyError: raise fcmcmp.UsageError("No internal control for '{}'".format(channel))

        # If no normalization is requested, don't set a control channel.
        elif not self.normalize_by:
            self.control_channel = None

        # If the user manually specifies a channel to normalize with, use it.
        else:
            self.control_channel = self.normalize_by

        # Decide whether or not the data should be presented on a log-axis. 
        self.log_scale = self.channel in fluorescence_controls
        if self.log_toggle:
            self.log_scale = not self.log_scale

        # Save the measurements, from the appropriate channel, with the 
        # appropriate normalization, and on the appropriate scale.
        self.linear_measurements = self.data[self.channel]
        if self.control_channel is not None:
            self.linear_measurements /= self.data[self.control_channel]

        self.measurements = self.linear_measurements
        if self.log_scale:
            self.measurements = np.log10(self.linear_measurements)

    def _find_distribution(self, xlim):
        # Create the x-axis based on the user-specified limits.  The limits 
        # can't be picked automatically because it's important that they be the 
        # same for every plot.
        self.x = np.linspace(*xlim, num=100)

        # Estimate the distribution underlying the measurements.  By default 
        # use a Gaussian kernel density estimate (KDE), or use a histogram if 
        # the user requests it.  A Gaussian KDE gives smoother results, depends 
        # on fewer tunable parameters, and handles the log-scaling better, but 
        # can be significantly slower for large data sets.
        if self.calc_histogram:
            self.y, bins = np.histogram(self.measurements, self.x)
            self.x = (bins[:-1] + bins[1:]) / 2
        else:
            from scipy.stats import gaussian_kde
            kernel = gaussian_kde(self.measurements)
            self.y = kernel.evaluate(self.x)

        # Scale the distribution to make it's area meaningful.  By default, the 
        # area will be proportional to the amount of data.  If the user wants 
        # the data presented as a PDF, the area is set to unity.
        self.y /= np.trapz(self.y, self.x)
        if not self.calc_pdf:
            self.y *= len(self.measurements)

        # Calculate the median or the mode of the data, as requested.
        if self.calc_mode:
            self.loc = self.measurements[np.argmax(self.y)]
        else:
            self.loc = np.median(self.measurements)


class GateLowFluorescence(fcmcmp.GatingStep):

    def __init__(self, threshold=1e3):
        self.threshold = threshold

    def gate(self, experiment, well):
        channel = fluorescence_controls.get(experiment['channel'])
        if channel is not None:
            return well.data[channel] < self.threshold


class RenameRedChannel(fcmcmp.ProcessingStep):
    """
    I use different red channels on different cytometers.  In particular, I use 
    the "PE-Texas Red" channel on the BD LSRII and the "DsRed" channel on the 
    BD FACSAriaII.  To allow my scripts to work on data from either machine, I 
    rename the red channel to "Red".
    """

    def process_well(self, experiment, well):
        if well.meta['$CYT'] == 'FACSAriaII':
            red_channel = 'DsRed-A'
        elif well.meta['$CYT'] == 'LSRII':
            red_channel = 'PE-Texas Red-A'
        else:
            raise ValueError("Unknown cytometer: {}".format(well.meta['$CYT']))

        well.data.rename(columns={red_channel: 'Red-A'}, inplace=True)


class GateEarlyEvents(fcmcmp.GateEarlyEvents):

    def gate(self, experiment, well):
        if self.throwaway_secs < 0:
            self.throwaway_secs = 2 if well.meta['$CYT'] == 'LSRII' else 0
        return super().gate(experiment, well)


class SharedProcessingSteps:

    def __init__(self):
        self.early_event_gate = None
        self.small_cell_gate = None
        self.low_fluorescence_gate = None

    def process(self, experiments):
        rename_red_channel = RenameRedChannel()
        rename_red_channel(experiments)

        gate_nonpositive_events = fcmcmp.GateNonPositiveEvents()
        gate_nonpositive_events.channels = 'FITC-A', 'Red-A'
        gate_nonpositive_events(experiments)

        gate_early_events = GateEarlyEvents()
        gate_early_events.throwaway_secs = self.early_event_threshold
        gate_early_events(experiments)

        gate_small_cells = fcmcmp.GateSmallCells()
        gate_small_cells.save_size_col = True
        gate_small_cells.threshold = self.small_cell_threshold
        gate_small_cells(experiments)

        gate_low_fluorescence = GateLowFluorescence()
        gate_low_fluorescence.threshold = self.low_fluorescence_threshold
        gate_low_fluorescence(experiments)


class ExperimentPlot:
    """
    Create a grid of shared axes, with one axis for each well in a single 
    experiment.  Provide a few helper functions relating to that grid, such as 
    setting the titles and converting row and column indices into wells and 
    conditions.
    """

    def __init__(self, experiment):
        # Settings configured by the user.
        self.experiment = experiment

        # Internally used plot attributes.
        self.figure = None
        self.axes = None
        self.num_rows = None
        self.num_cols = None

    def plot(self):
        raise NotImplementedError

    def _create_axes(self, square=False):
        """
        Work out how many wells need to be shown.
        
        There will be two rows and as many columns as necessary to show all the 
        wells.  The first row is for the "before" wells and the second row is 
        for the "after" ones.
        """
        num_before = len(self.experiment['wells']['before'])
        num_after = len(self.experiment['wells']['after'])

        self.num_rows = 2
        self.num_cols = max(num_before, num_after)

        # The 'squeeze=False' argument guarantees that the returned axes are 
        # always a 2D array, even if one of the dimensions happens to be 1.

        self.figure, self.axes = plt.subplots(
                self.num_rows, self.num_cols,
                sharex=True, sharey=True, squeeze=False,
        )
        
        # Make the axes square if the user asked for it.  What this really 
        # means is that pixels on the x-axis and the y-axis will have the same 
        # size in axis units.  This relationship is maintained even as the user 
        # zooms in and out.

        if square:
            for ax in self.axes.flat:
                ax.set(adjustable='box-forced', aspect='equal')

    def _set_titles(self):
        """
        Label each plot with the name of the experiment, the condition, and the 
        replicate number.
        """
        self.figure.suptitle(self.experiment['label'], size=14)

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                well = self._get_well(row, col)
                condition = self._get_condition(row)
                title = '{} ({})'.format(well.label, condition)
                self.axes[row, col].set_title(title, size=12)

    def _set_labels(self, x_label, y_label):
        for ax in self.axes[-1,:]:
            ax.set_xlabel(x_label)
        for ax in self.axes[:,0]:
            ax.set_ylabel(y_label)

    def _get_rows_cols(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                yield row, col

    def _get_condition(self, row):
        return ('before', 'after')[row]

    def _get_well(self, row, col):
        return self.experiment['wells'][self._get_condition(row)][col]



def pick_color(experiment):
    """
    Pick a color for the given experiment.

    The return value is a hex string suitable for use with matplotlib.
    """
    # I made this a wrapper function so that I could easily change the color 
    # scheme, if I want to, down the road.
    return pick_ucsf_color(experiment)

def pick_tango_color(experiment):
    """
    Pick a color from the Tango color scheme for the given experiment.

    The Tango color scheme is best known for being the basis of GTK icons, 
    which are used heavily on Linux systems.  The colors are bright, and the 
    scheme includes a few tints of each color.
    """

    white, black = '#ffffff', '#000000'
    grey = '#eeeeec', '#d3d7cf', '#babdb6', '#888a85', '#555753', '#2e3436'
    red =    '#ef2929', '#cc0000', '#a40000'
    orange = '#fcaf3e', '#f57900', '#ce5c00'
    yellow = '#fce94f', '#edd400', '#c4a000'
    green =  '#8ae234', '#73d216', '#4e9a06'
    blue =   '#729fcf', '#3465a4', '#204a87'
    purple = '#ad7fa8', '#75507b', '#5c3566'
    brown =  '#e9b96e', '#c17d11', '#8f5902'

    if experiment['label'].startswith('sgRFP'):
        return red[1]
    elif experiment['label'].startswith('sgGFP'):
        return green[2]
    elif experiment['label'] in ('wt', 'dead', 'null'):
        return grey[4]
    elif experiment['label'].startswith('us('):
        return blue[1]
    elif experiment['label'].startswith('nx('):
        return red[1]
    elif experiment['label'].startswith('cb('):
        return green[1]
    elif experiment['label'].startswith('sh('):
        return orange[1]
    elif experiment['label'].startswith('rb('):
        return purple[1]
    else:
        return brown[2]

def pick_ucsf_color(experiment):
    """
    Pick a color from the official UCSF color scheme for the given experiment.

    The UCSF color scheme is based on primary teal and dark blue colors and is 
    accented by a variety of bright -- but still somewhat subdued -- colors.  
    The scheme includes tints of every color, but not shades.
    """

    navy = ['#002049', '#506380', '#9ba6b6', '#e6e9ed']
    teal = ['#18a3ac', '#5dbfc5', '#a3dade', '#e8f6f7'] 
    olive = ['#90bd31', '#b1d16f', '#d3e4ad', '#f4f8ea'] 
    blue = ['#178ccb', '#5dafdb', '#a2d1ea', '#e8f4fa'] 
    orange = ['#f48024', '#f7a665', '#fbcca7', '#fef2e9'] 
    purple = ['#716fb2', '#9c9ac9', '#c6c5e0', '#f1f1f7'] 
    red = ['#ec1848', '#f25d7f', '#f7a3b6', '#fde8ed'] 
    yellow = ['#ffdd00', '#ffe74d', '#fff199', '#fffce6'] 
    black = ['#000000', '#4d4d4d', '#999999', '#ffffff'] 
    dark_grey = ['#b4b9bf', '#cbced2', '#e1e3e6', '#f8f8f9']
    light_grey = ['#d1d3d3', '#dfe0e0', '#ededee', '#fafbfb'] 

    if experiment['label'].startswith('sgRFP'):
        return red[0]
    elif experiment['label'].startswith('sgGFP'):
        return olive[0]
    elif experiment['label'] in ('wt', 'dead', 'null'):
        return dark_grey[0]
    elif experiment['label'].startswith('us('):
        return blue[0]
    elif experiment['label'].startswith('nx('):
        return red[0]
    elif experiment['label'].startswith('cb('):
        return olive[0]
    elif experiment['label'].startswith('sh('):
        return orange[0]
    elif experiment['label'].startswith('rb('):
        return purple[0]
    else:
        return navy[0]

def pick_style(experiment, condition):
    styles = {
            'before': {
                'color': 'black',
                'dashes': [5,2],
                'linewidth': 1,
                'zorder': 1,
            },
            'after': {
                'color': pick_color(experiment),
                'linestyle': '-',
                'linewidth': 1,
                'zorder': 2,
            },
    }
    return styles[condition]

def pick_channel(experiment, users_choice=None):
    """
    Pick a channel for the given experiment.

    The channel can either be set directly by the user (typically via the 
    command line) or can be inferred from the name of the experiment.  If 
    nothing else is specified, it will default to the "Red-A" channel.
    """
    # If the user manually specified a channel to view, use it.
    if users_choice:
        return users_choice

    # If a particular channel is associated with this experiment, use it.
    if 'channel' in experiment:
        channel = experiment['channel']
        if channel in ('PE-Texas Red-A', 'DsRed-A'):
            return 'Red-A'
        else:
            return channel

    # If a channel can be inferred from the name of the experiment, use it. 
    if 'sgGFP' in experiment['label']:
        return 'FITC-A'
    if 'sgRFP' in experiment['label']:
        return 'Red-A'

    # Default to the red channel, if nothing else is specified.
    return 'Red-A'

def get_duration(experiments):
    min_time = float('inf')
    max_time = -float('inf')

    for experiment in experiments:
        for condition in experiment['wells']:
            for well in experiment['wells'][condition]:
                min_time = min(min_time, min(well.data['Time'] / 100))
                max_time = max(max_time, max(well.data['Time'] / 100))

    return min_time, max_time

@contextlib.contextmanager
def plot_or_savefig(output_path=None, substitution_path=None):
    """
    Either open the plot in the default matplotlib GUI or export the plot to a 
    file, depending on whether or not an output path is given.  If an output 
    path is given and it contains dollar signs ('$'), they will be replaced 
    with the given substitution path.
    """
    import os, sys, matplotlib.pyplot as plt
    from pathlib import Path

    # We have to decide whether or not to fork before plotting anything, 
    # otherwise X11 will complain, and we only want to fork if we'll end up 
    # showing the GUI.  So first we calculate the output path, then we either 
    # fork or don't, then we yield to let the caller plot everything, then we 
    # either display the GUI or save the figure to a file.

    if not output_path and os.fork():
        sys.exit()

    yield

    if output_path and substitution_path:
        output_path = output_path.replace('$', Path(substitution_path).stem)

    if output_path:
        plt.savefig(output_path, dpi=300)
    else:
        plt.gcf().canvas.set_window_title(' '.join(sys.argv))
        plt.show()

