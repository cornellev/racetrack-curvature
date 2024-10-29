# Racetrack Curvature

_Jason Klein. Oct. 29, 2024_

Converts lat/long coordinates of the Indy 500 racetrack to the ENU [local tangent plane](https://en.wikipedia.org/wiki/Local_tangent_plane_coordinates) reference frame, which has units of meters. Then numerically computes the curvature at each point and visualizes the result.

![result](result.png)

## Why?

As part of speccing the steering system, Selena wanted to know the minimum radius of a turn on the competition track and asked me if I happened to know. I didn't, but I did remember that the [2023 driver dash I wrote](https://github.com/cornellev/driverdash) had access to a file called `Indy500.json` that had latitude and longitude coordinates of the actual path traveled during competition.

Combined with an ECEF-g to ENU coordinate frame converter I wrote over the summer (currently in a private repo), I was able to convert the geodetic coordinates to a frame with units in meters. I also tried using [pymap3d](https://pypi.org/project/pymap3d/) which has this sort of converter, but it didn't get the units right.

I then compute the curvature by creating an approximating spline, using that to get analytical first and second derivatives of `x` and `y`, and then plugging those into the curvature formula. Computing the maximum curvature and then taking its reciprocal yields the minimum instantaneous turning radius of `26.597254392113534` meters, which agrees with the value I got when zooming into the plot and manually tracing out the [osculating circle](https://en.wikipedia.org/wiki/Osculating_circle) for the regions I expected to have the most curvature.
