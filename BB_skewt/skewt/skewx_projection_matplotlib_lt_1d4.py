from numpy import array
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib.ticker import FixedLocator, AutoLocator, ScalarFormatter
import matplotlib.transforms as transforms
import matplotlib.axis as maxis
import matplotlib.artist as artist
from matplotlib.projections import register_projection
from matplotlib.pyplot import rcParams,figure,show,draw
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


# These are the original SkewX classes provided by Ryan May for producing
# the skewx projection. They are identical to those used in the SkewT 
# package for versions < 1.0, and are provided for backwards compatability 
# for matplotlib versions <1.4.

class SkewXTick(maxis.XTick):
    #Copyright (c) 2008 Ryan May
    def draw(self, renderer):
        if not self.get_visible(): 
            return
        renderer.open_group(self.__name__)

        if self.gridOn:
            self.gridline.draw(renderer)
        if self.tick1On:
            self.tick1line.draw(renderer)
        if self.tick2On:
            self.tick2line.draw(renderer)

        if self.label1On:
            self.label1.draw(renderer)
        if self.label2On:
            self.label2.draw(renderer)

        renderer.close_group(self.__name__)

    def set_clip_path(self, clippath, transform=None):
        artist.Artist.set_clip_path(self, clippath, transform)
        self.tick1line.set_clip_path(clippath, transform)
        self.tick2line.set_clip_path(clippath, transform)
        self.gridline.set_clip_path(clippath, transform)
    
    set_clip_path.__doc__ = artist.Artist.set_clip_path.__doc__

class SkewXAxis(maxis.XAxis):
    #Copyright (c) 2008 Ryan May
    def _get_tick(self, major):
        return SkewXTick(self.axes, 0, '', major=major)

    def draw(self, renderer, *args, **kwargs):
        'Draw the axis lines, grid lines, tick lines and labels'
        ticklabelBoxes = []
        ticklabelBoxes2 = []

        if not self.get_visible(): 
            return
        renderer.open_group(__name__)
        interval = self.get_view_interval()
        for tick, loc, label in self.iter_ticks():
            if tick is None: 
                continue
            if transforms.interval_contains(interval, loc):
                tick.set_label1(label)
                tick.set_label2(label)
            tick.update_position(loc)
            tick.draw(renderer)
            if tick.label1On and tick.label1.get_visible():
                extent = tick.label1.get_window_extent(renderer)
                ticklabelBoxes.append(extent)
            if tick.label2On and tick.label2.get_visible():
                extent = tick.label2.get_window_extent(renderer)
                ticklabelBoxes2.append(extent)

        # scale up the axis label box to also find the neighbors, not
        # just the tick labels that actually overlap note we need a
        # *copy* of the axis label box because we don't wan't to scale
        # the actual bbox

        self._update_label_position(ticklabelBoxes, ticklabelBoxes2)

        self.label.draw(renderer)

        self._update_offset_text_position(ticklabelBoxes, ticklabelBoxes2)
        self.offsetText.set_text( self.major.formatter.get_offset() )
        self.offsetText.draw(renderer)

class SkewXAxes(Axes):
    #Copyright (c) 2008 Ryan May
    # The projection must specify a name.  This will be used be the
    # user to select the projection, i.e. ``subplot(111,
    # projection='skewx')``.
    name = 'skewx'

    def _init_axis(self):
        #Taken from Axes and modified to use our modified X-axis
        "move this out of __init__ because non-separable axes don't use it"
        self.xaxis = SkewXAxis(self)
        self.yaxis = maxis.YAxis(self)
        self._update_transScale()

    def draw(self, *args):
        '''
        draw() is overridden here to allow the data transform to be updated
        before calling the Axes.draw() method.  This allows resizes to be
        properly handled without registering callbacks.  The amount of
        work done here is kept to a minimum.
        '''
        self._update_data_transform()
        Axes.draw(self, *args)

    def _update_data_transform(self):
        '''
        This separates out the creating of the data transform so that
        it alone is updated at draw time.
        '''
        # This transforms x in pixel space to be x + the offset in y from
        # the lower left corner - producing an x-axis sloped 45 degrees
        # down, or x-axis grid lines sloped 45 degrees to the right
        self.transProjection.set(transforms.Affine2D(\
                array([[1, 1, -self.bbox.ymin], [0, 1, 0], [0, 0, 1]])))

        # Full data transform
        self.transData.set(self._transDataNonskew + self.transProjection)

    def _set_lim_and_transforms(self):
        """
        This is called once when the plot is created to set up all the
        transforms for the data, text and grids.
        """
        #Get the standard transform setup from the Axes base class
        Axes._set_lim_and_transforms(self)

        #Save the unskewed data transform for our own use when regenerating
        #the data transform. The user might want this as well
        self._transDataNonskew = self.transData

        #Create a wrapper for the data transform, so that any object that
        #grabs this transform will see an updated version when we change it
        self.transData = transforms.TransformWrapper(
            transforms.IdentityTransform())

        #Create a wrapper for the proj. transform, so that any object that
        #grabs this transform will see an updated version when we change it
        self.transProjection = transforms.TransformWrapper(
            transforms.IdentityTransform())
        self._update_data_transform()

    def get_xaxis_transform(self, which='grid'):
        """
        Get the transformation used for drawing x-axis labels, ticks
        and gridlines.  The x-direction is in data coordinates and the
        y-direction is in axis coordinates.

        We override here so that the x-axis gridlines get properly
        transformed for the skewed plot.
        """

        return self._xaxis_transform + self.transProjection

    # Disable panning until we find a way to handle the problem with
    # the projection
    def start_pan(self, x, y, button):
        pass

    def end_pan(self):
        pass

    def drag_pan(self, button, key, x, y):
        pass

