from Atlas import AeroStructural
from openmdao.lib.drivers.api import SLSQPdriver

import time

top = AeroStructural()

#top.add('driver', SLSQPdriver())

start = time.time()
top.run()
end = time.time()

print "Exectution time: {}".format(end - start)

#============= Objective ================

print top.results.Ptot


#====== Constraints ============

# lift >= weight
top.results.Constr1

# structural failure in rotor spar



# break out deformation

#===== Parameters =============
print top.config.Omega


# top.driver.add_objective("-Lat_uniform.k -Lon_uniform.k")
# top.driver.add_parameter(
#     ["Orbit_Initial.altPerigee", "Orbit_Initial.altApogee"],
#     low=500, high=1000)
# top.driver.add_parameter(
#     "config.Omega", low=-180, high=180)

