import click
import pandas as pd
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

from shapely.ops import cascaded_union


NON_CONUS_STATES = {'VI', 'AK', 'HI', 'PR', 'GU', 'MP', 'AS'}

COLORS = {
    "green": "#1cff2b",
    "blue": "#1c89ff",
    "pink": "#ff42fb",
    "orange": "#ff8c00",
    "red": "#ff007b"
}

def polygon_theme(theme_name):
    assert theme_name in {"dark", "light"}

    if theme_name == "dark":
        return {
            "facecolor": "black",
            "edgecolor": "white"
        }
    elif theme_name == "light":
        return {
            "facecolor": "lightgray",
            "edgecolor": "black"
        }


def point_theme(theme_name):
    assert theme_name in {"dark", "light"}

    if theme_name == "dark":
        return {
            "markerfacecolor": "white",
        }
    elif theme_name == "light":
        return {
            "markerfacecolor": "black"
        }


@click.command()
@click.argument('data_file', type=click.File('r'))
@click.option(
    "--output-file", "-o",
    type=str,
    default='strange_places.png'
)
@click.option(
    '--us-shapefile',
    type=str,
    default='data/external/cb_2016_us_state_500k.shp'
)
@click.option(
    '--plot-title',
    type=str,
    default="Strange Places"
)
@click.option(
    "--plot-width", "-w",
    type=int,
    default=16
)
@click.option(
    "--plot-height", "-h",
    type=int,
    default=12
)
@click.option(
    "--plot-theme",
    type=click.Choice(["light", "dark"]),
    default="dark"
)
@click.option(
    "--point-color",
    type=click.Choice(list(COLORS.keys())),
    default="green"
)
def main(
    data_file,
    output_file,
    us_shapefile,
    plot_title,
    plot_width,
    plot_height,
    plot_theme,
    point_color
):

    # Read in the USA data.
    usa_reader = shpreader.Reader(us_shapefile)
    states = [
        state for state in usa_reader.records()
        if state.attributes['STUSPS'] not in NON_CONUS_STATES
    ]

    # Merge the states into a single bounding box.
    usa_bounds = cascaded_union(
        [state.geometry.envelope for state in states]
    ).bounds

    # Read the data in and isolate the points to those that fall within the
    # CONUS bounding box.
    strange_places = pd.read_csv(data_file).query(
        "(longitude > @usa_bounds[0]) and "
        "(longitude < @usa_bounds[2]) and "
        "(latitude > @usa_bounds[1]) and "
        "(latitude < @usa_bounds[3])"
    )

    # Prepare a cartopy projection for the plot.
    proj = ccrs.AlbersEqualArea(
        # Centering the projection on the bounding box centroid is close
        # enough for this purpose.
        central_longitude=(usa_bounds[0] + usa_bounds[2])/2,
        central_latitude=(usa_bounds[1] + usa_bounds[3])/2
    )

    fig = plt.figure(figsize=(plot_width,plot_height))
    ax = plt.axes(projection=proj)

    # Now add the states.
    for state in states:
        ax.add_feature(
            cfeature.ShapelyFeature(state.geometry, ccrs.PlateCarree()),
            linewidth=0.225,
            # Extract the theme based on the plot theme arg.
            **polygon_theme(plot_theme)
        )

    # Add the strange places.
    ax.plot(
        strange_places.longitude,
        strange_places.latitude,
        "o",
        markeredgecolor=COLORS[point_color],
        markeredgewidth=0.3,
        markersize=1.05,
        alpha=1.0,
        transform=ccrs.PlateCarree(),
        **point_theme(plot_theme)
    )

    # Now format the plot.
    ax.set_extent([
        usa_bounds[0],
        usa_bounds[2],
        usa_bounds[1],
        usa_bounds[3]
    ], ccrs.PlateCarree())

    ax.set_title(plot_title)

    # Make the background of the map transparent.
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)

    # Save the figure.
    fig.savefig(output_file, transparent=True)


if __name__ == "__main__":
    main()