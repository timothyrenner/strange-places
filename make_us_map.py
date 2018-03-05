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


def make_map(
    polygons, # Polygon or list of polygons.
    coordinates, # Nx2 numpy array.
    theme="dark",
    point_color="green",
    point_size=1.05,
    plot_title="Strange Places",
    plot_height=12,
    plot_width=16
):
    # Put the polygons into a list if they aren't already in one.
    polygon_list = polygons if isinstance(polygons, list) else [polygons]

    # Obtain the bounds.
    polygon_bounds = cascaded_union(
        [polygon.envelope for polygon in polygons]
    ).bounds

    # Isolate the points in the bounds.
    coordinates_in_bounds = (
        coordinates[:,0] > polygon_bounds[0]
    ) & (
        coordinates[:,0] < polygon_bounds[2]
    ) & (
        coordinates[:,1] > polygon_bounds[1]
    ) & (
        coordinates[:,1] < polygon_bounds[3]
    )

    # Define the projection for the map.
    projection = ccrs.AlbersEqualArea(
        # Centroid of the bounding box of all the polygons.
        central_longitude = (polygon_bounds[0] + polygon_bounds[2])/2,
        central_latitude = (polygon_bounds[1] + polygon_bounds[3])/2
    )

    fig = plt.figure(figsize=(plot_width, plot_height))
    ax = plt.axes(projection=projection)

    # Add each polygon.
    for polygon in polygon_list:
        ax.add_feature(
            cfeature.ShapelyFeature(polygon, ccrs.PlateCarree()),
            linewidth=0.225,
            **polygon_theme(theme)
        )

    # Add the coordinates.
    ax.plot(
        coordinates[:,0],
        coordinates[:,1],
        "o",
        markeredgecolor=COLORS[point_color],
        markeredgewidth=0.3,
        markersize=point_size,
        alpha=1.0,
        transform=ccrs.PlateCarree(),
        **point_theme(theme)
    )

    # Set the extents of the plot.
    ax.set_extent([
        polygon_bounds[0],
        polygon_bounds[2],
        polygon_bounds[1],
        polygon_bounds[3]
    ], ccrs.PlateCarree())

    ax.set_title(plot_title)

    # Make the background of the map transparent.
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)

    return fig,ax


@click.command()
@click.argument('data_file', type=click.File('r'))
@click.option(
    "--output-file", "-o",
    type=str,
    default='strange_places'
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
@click.option(
    "--point-size",
    type=float,
    default=1.05
)
@click.option(
    "--high-quality/--low-quality",
    default=False
)
def main(
    data_file,
    output_file,
    us_shapefile,
    plot_title,
    plot_width,
    plot_height,
    plot_theme,
    point_color,
    point_size,
    high_quality
):

    # Read in the USA data.
    usa_reader = shpreader.Reader(us_shapefile)
    states = [
        state.geometry for state in usa_reader.records()
        if state.attributes['STUSPS'] not in NON_CONUS_STATES
    ]

    # Read the data in and isolate the points to those that fall within the
    # CONUS bounding box.
    strange_places = pd.read_csv(data_file).dropna()

    fig,ax = make_map(
        states,
        strange_places[['longitude','latitude']].values,
        theme=plot_theme,
        point_color=point_color,
        point_size=point_size,
        plot_title=plot_title,
        plot_height=plot_height,
        plot_width=plot_width
    )

    # Save the figure.
    if high_quality:
        fig.savefig(
            "{}.svg".format(output_file),
            transparent=True,
            dpi=1200
        )
    else:
        fig.savefig(
            "{}.png".format(output_file),
            transparent=True,
            dpi=300
        )


if __name__ == "__main__":
    main()