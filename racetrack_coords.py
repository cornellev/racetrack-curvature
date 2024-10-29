import json
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

with open("Indy500.json") as f:
    lat_lon_json = json.load(f)
print("Loaded file.")

# [lat (rad), long (rad), alt (m)]
arr_ecefg = np.zeros((len(lat_lon_json), 3))
for i, lat_lon in enumerate(lat_lon_json):
    # assuming elevation of 730ft = 222.504 m
    arr_ecefg[i] = [
        lat_lon["lat"] * np.pi / 180,
        lat_lon["long"] * np.pi / 180,
        222.504]

ltp_origin = None

# copied from https://github.com/Jklein64/dcgr-ros/blob/666468579b8b61fc7d82d3c808447e71aee1d790/dcgr_map/nodes/gps_mapper#L116
def ecefg_to_enu(x_ecefg) -> np.ndarray:
    """Converts x_ecefg, a location in the Earth-Centered Earth-Fixed coordinate
    frame, into x_enu, a location in the East-North-Up local tangent plane
    coordinate frame.

    See https://archive.psas.pdx.edu/CoordinateSystem/Latitude_to_LocalTangent.pdf
    for derivation.

    Params:
        x_ecefg: Location in the ECEF-g coordinate frame.
    """
    global ltp_origin

    a = 6378137.0
    b = 6356752.3142
    f = (a - b) / a
    e = np.sqrt(f * (2 - f))
    lat, lon, h = x_ecefg
    N = a / np.sqrt(1 - e**2 * np.sin(lat) ** 2)
    # ECEF-g --> ECEF-r
    x_ecefr = np.array(
        [
            (h + N) * np.cos(lat) * np.cos(lon),
            (h + N) * np.cos(lat) * np.sin(lon),
            (h + (1 - e**2) * N) * np.sin(lat),
        ],
        dtype=np.float64,
    )
    # ECEF-r --> LTP
    if ltp_origin is None:
        # local tangent plane uses the first location as the origin and
        # computes all other locations relative to that. This means the first
        # coordinate is aways the origin in the LTP coordinate frame.
        ltp_origin = x_ecefr
        x_enu = np.zeros(3)
    else:
        # fmt: off
        R = np.array([
                [-np.sin(lon),                np.cos(lon),               0],
                [-np.cos(lon) * np.sin(lat), -np.sin(lat) * np.sin(lon), np.cos(lat)],
                [ np.cos(lat) * np.cos(lon),  np.cos(lat) * np.sin(lon), np.sin(lat)]])
        # fmt: on
        x_0 = ltp_origin
        x_enu = R @ (x_ecefr - x_0)
    return x_enu

arr_enu = np.zeros_like(arr_ecefg)
for i in range(arr_ecefg.shape[0]):
    arr_enu[i] = ecefg_to_enu(arr_ecefg[i])
print("Completed conversion.")

x, y = arr_enu[:, :2].T
# not sure why this didn't work for arc length parameterization
# t = np.concatenate([[0], np.cumsum(1/np.linalg.norm(np.diff(arr_enu[:, :2], axis=0), axis=1))])
t = np.arange(0, arr_enu.shape[0]).astype(float)
x_spline = sp.interpolate.UnivariateSpline(t, x, s=5)
y_spline = sp.interpolate.UnivariateSpline(t, y, s=5)
dx, ddx = x_spline.derivative(1), x_spline.derivative(2)
dy, ddy = y_spline.derivative(1), y_spline.derivative(2)
# literal implementation of parametric curvature formula
kappa = np.abs(ddx(t) * dy(t) + dx(t) * ddy(t)) / np.power(dx(t)**2 + dy(t)**2, 1.5)

plt.scatter(x_spline(t), y_spline(t), s=1, c=kappa)
plt.gca().set_aspect('equal')
plt.savefig("result.png")