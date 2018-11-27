import click
import pandas as pd
import cartopy.io.shapereader as shpreader

from map_utils import make_map

NON_CONUS_STATES = {'VI', 'AK', 'HI', 'PR', 'GU', 'MP', 'AS'}

COLORS = {
    "green": "#1cff2b",
    "blue": "#1c89ff",
    "pink": "#ff42fb",
    "orange": "#ff8c00",
    "red": "#ff007b"
}

@click.command()
@click.argument(
    "data_file",
    type=click.File('r'),
    default="data/processed/bigfoot_sightings.csv"
)
@click.option(
    "--output-file", "-o",
    type=str,
    default="bigfoot_us"
)
@click.option(
    "--us-shapefile",
    type=str,
    default="data/external/cb_2016_us_state_500k.shp"
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
    "--point-size",
    type=float,
    default=2.0
)
@click.option(
    "--point-color",
    type=click.Choice(list(COLORS.keys())),
    default="orange"
)
@click.option(
    "--high-quality/--low-quality",
    default=False
)
def main(
    data_file,
    output_file,
    us_shapefile,
    plot_width,
    plot_height,
    point_size,
    point_color,
    high_quality
):

    # Read in the USA data.
    usa_reader = shpreader.Reader(us_shapefile)

    states = []
    alaska = None
    hawaii = None
    for state in usa_reader.records():
        if state.attributes['STUSPS'] not in NON_CONUS_STATES:
            states.append(state.geometry)
        elif state.attributes['STUSPS'] == 'AK':
            alaska = state.geometry
        elif state.attributes['STUSPS'] == 'HI':
            hawaii = state.geometry

    bigfoot = pd.read_csv(data_file).dropna()

    fig,ax = make_map(
        states,
        alaska,
        hawaii,
        bigfoot[["longitude", "latitude"]].values,
        plot_height=plot_height,
        plot_width=plot_width,
        point_size=point_size,
        point_edge_width=point_size/3,
        point_color=point_color
    )

    ax.set_title("Bigfoot Sightings")

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