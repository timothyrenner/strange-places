import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

from shapely.ops import cascaded_union


class AlaskaProjection(ccrs.Projection):
    def __init__(self):
        super().__init__({"proj": "alsk"})


def make_map(
    conus_states,
    alaska,
    hawaii,
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


    conus_bounds = [-124.763068, 24.523096, -66.949895, 49.384358]
    alaska_bounds = [
        -169.716186605,
        51.7040827393,
        -128.6561585288,
        71.425880743
    ]
    hawaii_bounds = [
        -160.8488520731,
        18.864031,
        -154.75766,
        22.6665176143
    ]

    figure = plt.figure(figsize=(plot_width, plot_height))

    conus_projection = ccrs.AlbersEqualArea(
        central_longitude=(conus_bounds[0] + conus_bounds[2]) / 2,
        central_latitude=(conus_bounds[1] + conus_bounds[3]) / 2
    )

    conus_axes = _add_polygons_and_points(
        figure,
        conus_states,
        coordinates,
        conus_bounds,
        conus_projection,
        polygon_face_color=polygon_face_color,
        polygon_edge_color=polygon_edge_color,
        point_size=point_size,
        point_edge_width=point_edge_width,
        point_color=point_color,
        point_face_color=point_face_color
    )

    alaska_projection = ccrs.AlbersEqualArea(
        central_longitude=(alaska_bounds[0] + alaska_bounds[2]) / 2,
        central_latitude=(alaska_bounds[1] + alaska_bounds[3]) / 2
    )
    alaska_axes = _add_polygons_and_points(
        figure,
        [alaska],
        coordinates,
        alaska_bounds,
        alaska_projection,
        subplot_bounds=[0.1, 0.1, 0.25, 0.25],
        polygon_face_color=polygon_face_color,
        polygon_edge_color=polygon_edge_color,
        point_size=point_size,
        point_edge_width=point_edge_width,
        point_color=point_color,
        point_face_color=point_face_color
    )

    hawaii_projection = ccrs.AlbersEqualArea(
        central_longitude=(hawaii_bounds[0] + hawaii_bounds[2]) / 2,
        central_latitude=(hawaii_bounds[1] + hawaii_bounds[3]) / 2
    )
    hawaii_axes = _add_polygons_and_points(
        figure,
        [hawaii],
        coordinates,
        hawaii_bounds,
        hawaii_projection,
        subplot_bounds=[0.325, 0.135, 0.1, 0.1],
        polygon_face_color=polygon_face_color,
        polygon_edge_color=polygon_edge_color,
        point_size=point_size,
        point_edge_width=point_edge_width,
        point_color=point_color,
        point_face_color=point_face_color
    )

    return figure, conus_axes


def _add_polygons_and_points(
    figure,
    polygon_list,
    coordinates,
    polygon_bounds,
    projection,
    subplot_bounds=[0, 0, 1, 1],
    polygon_face_color="black",
    polygon_edge_color="white",
    point_size=1.05,
    point_edge_width=0.3,
    point_color="green",
    point_face_color="white"
):
    axes = figure.add_axes(subplot_bounds, projection=projection)

    axes.add_feature(
        cfeature.ShapelyFeature(polygon_list, ccrs.PlateCarree()),
        linewidth=0.225,
        facecolor=polygon_face_color,
        edgecolor=polygon_edge_color
    )
    
    axes.plot(
        coordinates[:, 0],
        coordinates[:, 1],
        "o",
        markeredgecolor=point_color,
        markerfacecolor=point_face_color,
        markeredgewidth=point_edge_width,
        markersize=point_size,
        alpha=1.0,
        transform=ccrs.PlateCarree()
    )

    axes.set_extent([
        polygon_bounds[0],
        polygon_bounds[2],
        polygon_bounds[1],
        polygon_bounds[3]
    ], ccrs.PlateCarree())

    axes.outline_patch.set_visible(False)
    axes.background_patch.set_visible(False)

    return axes