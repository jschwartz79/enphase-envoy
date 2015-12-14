from envoy import Envoy
import time

envoy = Envoy('envoy')

print 'Current generation: %s %s' % (envoy.current_generation())
print 'Today\'s generation: %s %s' % (envoy.power_generation_today())
print 'Past week generation: %s %s' % (envoy.power_generation_past_week())
print 'Lifetime generation: %s %s' % (envoy.lifetime_generation())
print 'Number of Microinverters: %s' % envoy.number_of_microinverters()
print 'Number of Microinverters Online: %s' % envoy.number_of_microinverters_online()
print 'Current software version: %s' % envoy.current_software_version()
print 'Software build date: %s' % envoy.software_build_date()
print 'Last cloud connection: %s' % envoy.last_connection_to_website()
