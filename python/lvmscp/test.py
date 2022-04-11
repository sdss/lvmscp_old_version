# this is the example code of how to use the lvmscp as an API

from lvmscp.module import API as spectrograph_interface


spectrograph_interface.ping()
spectrograph_interface.lvmnps_ping()
spectrograph_interface.lvmieb_ping()

"""
This is the example code for taking the focus image for the arc lamps
"""

# Turning on the lamp (6 is the Neon lamp)

spectrograph_interface.expose(10.0, 3, "dark", "sp1", 1)

# argon, neon, hgne, Xenon

spectrograph_interface.expose(10.0, 3, "object", "sp1", 1)

spectrograph_interface.expose(10.0, 3, "dark", "sp1", 1)

spectrograph_interface.expose(10.0, 3, "object", "sp1", 1)

# setting the linear gage
# spectrograph_interface.gage_set("z1")

# setting the readout mode
# spectrograph_interface.readout_set("400")

# taking the exposure with hartmann doors
# exptime, number of exposure, image type, spectrograph, binning
# spectrograph_interface.hartmann_set("left")
# spectrograph_interface.expose(10.0, 1, "arc", "sp1", 1)
# spectrograph_interface.hartmann_set("right")
# spectrograph_interface.expose(10.0, 1, "arc", "sp1", 1)
# spectrograph_interface.hartmann_set("both")
# spectrograph_interface.expose(10.0, 1, "arc", "sp1", 1)

# turning off the lamp
# spectrograph_interface.lamp_off("DLI-03", 6)
