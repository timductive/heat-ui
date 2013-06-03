heat-ui
=======

Temporary repo to house Heat UI mockups based on requirements gathered. Eventually, implementation of mockups will be submitted for inclusion in Horizon/Openstack dashboard.

To install

install openstack including horizon, python-heatclient and heat

git clone into same folder as horizon
then ln -s ./heat-ui/heat ./horizon/heat

Then, edit your openstack_dashboard settings file:

add ‘heat’ to INSTALLED_APPS tuple;
add ‘heat’ to ‘dashboards’ key in the HORIZON_CONFIG dictionary.
