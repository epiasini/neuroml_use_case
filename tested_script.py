"""This should set up and run a simple simulation where a granule cell
is stimulated with a number of "on" (10Hz) inputs and a number of
"off" (80Hz) inputs. The inputs are "refractory Poisson" spike trains,
generated with a custom LEMS element. Each input is connected to the
GrC with a synapse that comprises an AMPA and an NMDA component. These
synaptic models are also defined as custom LEMS elements. The GrC
model itself is a conductance-based integrate-and-fire (IaFRefCell
NeuroML2 componentType). The definitions of custom LEMS componentTypes
must be loaded from external files. Some of the components used (both
LEMS and NeuroML) are defined by this script, while others are loaded
from external files.

The simulation that should be created should be the same as that
contained in the 'simulation.xml' file in this folder.

The key thing would be to have an import_lems() function that would
read an external file and return an whose attributes represent all the
top-level components and componentTypes defined in the external
file. In particular, attributes associated to componentTypes should be
callable, consisting essentially in constructors for Python
classes. Like in libneuroml, but defined on the fly from the
information in the external file instead than from the schema. In
other words, import_lems() would work in a way analogous to Python's
'import' statement, knowing how to create classes and other objects
from a LEMS/NeuroML file.

"""

import neuroml as nml
from pyneuroml import pynml
from pyneuroml.lems.LEMSSimulation import LEMSSimulation
import lems.api as lems

# set parameters controlling the number of "on" and "off" synaptic
# inputs. We do this to show why it is convenient to generate the
# simulation procedurally, rather than writing by hand the LEMS code.
n_inputs_ON = 2
n_inputs_OFF = 2

# load NeuroML components, LEMS components and LEMS componentTypes from external files
spike_generator_file_name = "lemsDefinitions/spikeGenerators.xml"
spike_generator_doc = pynml.read_lems_file(spike_generator_file_name)

###spike_recorder_file_name = "lemsDefinitions/spikeRecorder.xml"
###spike_recorder_doc = pynml.read_lems_file(spike_recorder_file_name)

iaf_nml2_file_name = "lemsDefinitions/IaF_GrC.nml"
IaF_GrC_doc = pynml.read_neuroml2_file(iaf_nml2_file_name)

ampa_syn_filename="lemsDefinitions/RothmanMFToGrCAMPA.xml"
nmda_syn_filename="lemsDefinitions/RothmanMFToGrCNMDA.xml"
RothmanMFToGrCAMPA_doc = pynml.read_lems_file(ampa_syn_filename)
RothmanMFToGrCNMDA_doc = pynml.read_lems_file(nmda_syn_filename)


# define some components from the componentTypes we just loaded
####spike_recorder = spike_recorder_doc.spikeRecorder(id="spikeRecorder")

spike_generator_ref_poisson_type = spike_generator_doc.component_types['spikeGeneratorRefPoisson']
lems_instances_doc = lems.Model()

spike_generator_on = lems.Component("mossySpikerON", 
                                    spike_generator_ref_poisson_type.name)
                                                      
spike_generator_on.set_parameter("minimumISI", "2 ms")
spike_generator_on.set_parameter("averageRate", "80 Hz")
lems_instances_doc.add(spike_generator_on)
'''
spike_generator_off = lems.Component("mossySpikerOFF", 
                                     spike_generator_ref_poisson_type.name)
                                                      
spike_generator_off.set_parameter("minimumISI", "2 ms")
spike_generator_off.set_parameter("averageRate", "80 Hz")
lems_instances_doc.add(spike_generator_off)
'''

# rename some components for convenience
IaF_GrC = IaF_GrC_doc.iaf_ref_cells[0] # note that here IaF_GrC_doc.IaF_GrC is
                              # already a component, not a
                              # componentType, so it doesn't need to
                              # be instantiated.
                              
RothmanMFToGrCAMPA = RothmanMFToGrCAMPA_doc.components['RothmanMFToGrCAMPA'].id
RothmanMFToGrCNMDA = RothmanMFToGrCNMDA_doc.components['RothmanMFToGrCNMDA'].id

# create populations
GrCPop = nml.Population(id="GrCPop",
                        component=IaF_GrC.id,
                        size=1)
    
'''
SpikeRecorderPop = nml.Population(id="SpikeRecorderPop",
                                  component="IaF_GrC",
                                  size=1)'''
                                  
mossySpikersPopON = nml.Population(id=spike_generator_on.id+"Pop",
                                   component=spike_generator_on.id,
                                   size=n_inputs_ON)
'''
mossySpikersPopOFF = nml.Population(id=spike_generator_off.id+"Pop",
                                    component=spike_generator_off.id,
                                    size=n_inputs_OFF)'''
                                    
# create network and add populations
net = nml.Network(id="network")
net_doc = nml.NeuroMLDocument(id=net.id)
net_doc.networks.append(net)
net.populations.append(GrCPop)
####net.populations.append(SpikeRecordersPop)
net.populations.append(mossySpikersPopON)
#net.populations.append(mossySpikersPopOFF)

# set up connections
################for stim_pop in [mossySpikersPopON, mossySpikersPopOFF]:
for stim_pop in [mossySpikersPopON]:
    for k in range(stim_pop.size):
        for synapse in [RothmanMFToGrCAMPA, RothmanMFToGrCNMDA]:
            connection = nml.SynapticConnection(from_="{}[{}]".format(stim_pop.id, k),
                                                synapse=synapse,
                                                to="GrCPop[0]")
            net.synaptic_connections.append(connection)
'''
# set up fake connection for counting spikes
net.append(nml.SynapticConnection(from_="GrCPop[0]",
                                  to="SpikeRecorderPop[0]",
                                  synapse=spikeRecorder.id))
'''



# Write network to file
net_file_name = 'generated_network.net.nml'
pynml.write_neuroml2_file(net_doc, net_file_name)

# Write LEMS instances to file
lems_instances_file_name = 'instances.xml'
pynml.write_lems_file(lems_instances_doc, lems_instances_file_name)



# Create a LEMSSimulation to manage creation of LEMS file
duration = 100  # ms
dt = 0.05  # ms
ls = LEMSSimulation("sim", duration, dt)


# Point to network as target of simulation
ls.assign_simulation_target(net.id)


# Include generated/existing NeuroML2 files
ls.include_neuroml2_file(iaf_nml2_file_name)
ls.include_lems_file(spike_generator_file_name, include_included=False)
ls.include_lems_file(lems_instances_file_name)
ls.include_lems_file(ampa_syn_filename, include_included=False)
ls.include_lems_file(nmda_syn_filename, include_included=False)
###ls.include_lems_file(spike_recorder_file_name)
ls.include_neuroml2_file(net_file_name)


# Specify Displays and Output Files
disp0 = "display_voltages"
ls.create_display(disp0, "Voltages", "-95", "-38")

disp1 = "display_spike_generators"
ls.create_display(disp1, "Spike generators", "-10", "80")

of0 = 'Volts_file'
ls.create_output_file(of0, "v.dat")

quantity = "%s[%i]/v"%(GrCPop.id, 0)
ls.add_line_to_display(disp0, "GrC: Vm", quantity, "1mV", "#66c2a5")
ls.add_column_to_output_file(of0, 'v0', quantity)

quantity = "%s[%i]/tsince"%(mossySpikersPopON.id, 0)
ls.add_line_to_display(disp1, "mossySpikersPopON 0", quantity, "1ms", "#000000")
'''
quantity = "%s[%i]/tsince"%(mossySpikersPopOFF.id, 0)
ls.add_line_to_display(disp1, "mossySpikersPopOFF 0", quantity, "1ms", "#FF0000")
'''

# Save to LEMS XML file
lems_file_name = ls.save_to_file()

# Run with jNeuroML
results1 = pynml.run_lems_with_jneuroml(lems_file_name, nogui=True, load_saved_data=True, plot=True)

'''
# Run with jNeuroML_NEURON
results2 = pynml.run_lems_with_jneuroml_neuron(lems_file_name, nogui=True, load_saved_data=True, plot=True)
'''

