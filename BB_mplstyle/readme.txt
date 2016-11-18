Instructions for using a customized style for published documents
http://matplotlib.org/users/style_sheets.html


Import my custom style like this...

>>> import matplotlib.pyplot as plt
>>> style_path = './BB_mplstyle/'
>>> plt.style.use(style_path+'publications.mplstyle')


Import multiple styles...
>>> plt.style.use([style_path+'publications.mplstyle', style_path+'style2.mplstyle'])

For publicaitons, use publication and define the page width and dpi for the figures.

    publications - general font sizes, etc., that should apply to all figures.
    width_x - width of the figures. Trailing number is percent width:
              width_100: full page width
              width_75: three-quaters a page
              width_50: half a page
              width_25: one-quarter a page wide
    dpi_x - the dots per square inch that is saved.
            dpi_high: dpi is 1000, acceptable for line plots
            dpi_medium: dpi is 500, acceptable for plan view and colorfill plots
            dpi_low: dpi is 300, acceptable for photographs
            dpi_web: dpi is 72, acceptable for plots only displayed on the web

Example for using these:
>>> plt.style.use([style_path+'publications.mplstyle',
                   style_path+'width_100.mplstyle',
                   style_path+'dpi_high.mplstyle']
                   )

There are additional default styles that look nice. To see the available styles
type (plt.style.available). They include:
    'seaborn-darkgrid'
    'seaborn-notebook'
    'classic'
    'seaborn-ticks'
    'grayscale'
    'bmh'
    'seaborn-talk'
    'dark_background'
    'ggplot'
    'fivethirtyeight'
    'seaborn-colorblind'
    'seaborn-deep'
    'seaborn-whitegrid'
    'seaborn-bright'
    'seaborn-poster'
    'seaborn-muted'
    'seaborn-paper'
    'seaborn-white'
    'seaborn-pastel'
    'seaborn-dark'
    'seaborn-dark-palette'
