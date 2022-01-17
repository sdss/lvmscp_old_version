# this is the example code of how to use the lvmscp as an API
from lvmscp.module import API as spectrograph_interface


spectrograph_interface.ping()

# setting the linear gage
spectrograph_interface.gage_set("b1")

# setting the readout mode
spectrograph_interface.readout_set("400")
spectrograph_interface.expose(0.0, 1, "bias", "sp1", 1)
spectrograph_interface.readout_set("800")
spectrograph_interface.expose(0.0, 1, "bias", "sp1", 1)

# taking the exposure with hartmann doors
# exptime, number of exposure, image type, spectrograph, binning
spectrograph_interface.hartmann_set("left")
spectrograph_interface.expose(10.0, 1, "arc", "sp1", 1)
spectrograph_interface.hartmann_set("right")
spectrograph_interface.expose(10.0, 1, "arc", "sp1", 1)
spectrograph_interface.hartmann_set("both")
spectrograph_interface.expose(10.0, 1, "arc", "sp1", 1)
