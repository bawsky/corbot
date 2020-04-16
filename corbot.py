# Reference: https://matthewkudija.com/blog/2019/01/15/state-maps/
# Data Source: https://www.worldometers.info/coronavirus/country/us/

import requests
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib as mpl
import pandas as pd
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader


class Corbot():
    def __init__(self):
        self.edge_color = 'black'
        self.projection_type = ccrs.LambertConformal()
        self.title = 'TotalCases'
        self.attr = 'name'
        self.df = None
        self.color_map = mpl.cm.Blues
        self.shape_name = 'admin_1_states_provinces_lakes_shp'
        self.save_filename = 'Corbot-USA-TotalCases.png'

    def get_data(self):
        url = 'https://www.worldometers.info/coronavirus/country/us/'

        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        res = requests.get(url, headers=header)

        df_init = pd.read_html(res.text, index_col=0)[0]

        # arbitrary limit to exclude non-states from source table
        self.df = df_init.head(62)

    def process_data(self):
        max_val = self.df[self.title].max()
        min_val = self.df[self.title].min()

        self.norm_color = colors.LogNorm(vmin=min_val, vmax=max_val)

    def plot(self):
        ax = plt.axes([0, 0, 1, 1], projection=self.projection_type)
        ax.background_patch.set_visible(False)
        ax.outline_patch.set_visible(False)
        ax.set_extent([-100, -160, 20, 100], ccrs.Geodetic())

        shape_filename = shpreader.natural_earth(
            resolution='110m', category='cultural', name=self.shape_name)

        reader = shpreader.Reader(shape_filename)
        states = reader.records()

        for state in states:
            name = state.attributes[self.attr]

            try:
                color = self.color_map(self.norm_color(
                    self.df.loc[state.attributes[self.attr]][self.title]))

                ax.add_geometries(
                    state.geometry, ccrs.PlateCarree(),
                    facecolor=color,
                    label=state.attributes[self.attr],
                    edgecolor=self.edge_color,
                    linewidth=.05)
            except LookupError:
                print('Could not find \'{}\' in data frame.'.format(name))

        plt.savefig(
            self.save_filename,
            bbox_inches='tight', pad_inches=0.2, dpi=300)


def main():
    corbot = Corbot()
    corbot.get_data()
    corbot.process_data()
    corbot.plot()


if __name__ == '__main__':
    main()
