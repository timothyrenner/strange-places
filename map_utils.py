import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

from shapely.ops import cascaded_union

def make_map(
    polygons,
    coordinates,
    plot_height=12,
    plot_width=12,
    polygon_face_color="black",
    polygon_edge_color="white",
    point_size=1.05,
    point_edge_width=0.3,
    point_color="green",
    point_face_color="white"
):
    polygon_list = polygons if isinstance(polygons, list) else [polygons]

    polygon_bounds = cascaded_union([
        polygon.envelope for polygon in polygon_list
    ]).bounds

    coordinates_in_bounds = (
        coordinates[:,0] > polygon_bounds[0]
    ) & (
        coordinates[:,0] < polygon_bounds[2]
    ) & (
        coordinates[:,1] > polygon_bounds[1]
    ) & (
        coordinates[:,1] < polygon_bounds[3]
    )

    projection = ccrs.AlbersEqualArea(
        central_longitude = (polygon_bounds[0] + polygon_bounds[2]) / 2,
        central_latitude = (polygon_bounds[1] + polygon_bounds[3]) / 2
    )

    fig = plt.figure(figsize=(plot_width, plot_height))
    ax = plt.axes(projection=projection)

    ax.add_feature(
        cfeature.ShapelyFeature(polygon_list, ccrs.PlateCarree()),
        linewidth=0.225,
        facecolor=polygon_face_color,
        edgecolor=polygon_edge_color
    )

    ax.plot(
        coordinates[:,0],
        coordinates[:,1],
        "o",
        markeredgecolor=point_color,
        markerfacecolor=point_face_color,
        markeredgewidth=point_edge_width,
        markersize=point_size,
        alpha=1.0,
        transform=ccrs.PlateCarree(),
    )

    ax.set_extent([
        polygon_bounds[0],
        polygon_bounds[2],
        polygon_bounds[1],
        polygon_bounds[3]
    ], ccrs.PlateCarree())

    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)

    return fig, ax
