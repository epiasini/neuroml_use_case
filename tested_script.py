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
import numpy as np
import neuroml as nml
from pyneuroml import pynml

# set parameters controlling the number of "on" and "off" synaptic
# inputs. We do this to show why it is convenient to generate the
# simulation procedurally, rather than writing by hand the LEMS code.
n_inputs_ON = 2
n_inputs_OFF = 2

# load NeuroML components, LEMS components and LEMS componentTypes from external files
####spike_generator_doc = nml.import_lems("lemsDefinitions/spikeGenerators.xml")
####spike_recorder_doc = nml.import_lems("lemsDefinitions/spikeRecorder.xml")
IaF_GrC_doc = pynml.read_neuroml2_file("lemsDefinitions/IaF_GrC.nml")
####RothmanMFToGrCAMPA_doc = nml.import_lems("lemsDefinitions/RothmanMFToGrCAMPA.nml")
####RothmanMFToGrCNMDA_doc = nml.import_lems("lemsDefinitions/RothmanMFToGrCNMDA.nml")



# define some components from the componentTypes we just loaded
####spike_recorder = spike_recorder_doc.spikeRecorder(id="spikeRecorder")

####generator_ON = spike_generator_doc.spikeGeneratorRefPoisson(id="mossySpikerON",
########                                                            minimumISI="2 ms",
####                                                           averageRate="80 Hz")
####generator_OFF = spike_generator_doc.spikeGeneratorRefPoisson(id="mossySpikerOFF",
####                                                             minimumISI="2 ms",
####                                                             averageRate="80 Hz")

# rename some components for convenience
IaF_GrC = IaF_GrC_doc.iaf_ref_cells[0] # note that here IaF_GrC_doc.IaF_GrC is
                              # already a component, not a
                              # componentType, so it doesn't need to
                              # be instantiated.
                              
####RothmanMFToGrCAMPA = RothmanMFToGrCAMPA_doc.RothmanMFToGrCAMPA
####RothmanMFToGrCNMDA = RothmanMFToGrCAMPA_doc.RothmanMFToGrCNMDA

# create populations
GrCPop = nml.Population(id="GrCPop",
                        component=IaF_GrC.id,
                        size=1)
    
'''
SpikeRecorderPop = nml.Population(id="SpikeRecorderPop",
                                  component="IaF_GrC",
                                  size=1)
mossySpikersPopON = nml.Population(id="mossySpikersPopON",
                                   component="mossySpikerON",
                                   size=n_inputs_ON)
mossySpikersPopOFF = nml.Population(id="mossySpikersPopOFF",
                                    component="mossySpikerOFF",
                                    size=n_inputs_OFF)'''
# create network and add populations
net = nml.Network(id="network")
net_doc = nml.NeuroMLDocument(id=net.id)
net_doc.networks.append(net)
net.populations.append(GrCPop)
####net.populations.append(SpikeRecordersPop)
####net.populations.append(mossySpikersPopON)
####net.populations.append(mossySpikersPopOFF)
'''
# set up connections
for stim_pop in [mossySpikersPopON, mossySpikersPopOFF]:
    for k in range(stim_pop.size):
        for synapse in [RothmanMFToGrCAMPA, RothmanMFToGrCNMDA]:
            connection = nml.SynapticConnection(from_="{}[{}]".format(stim_pop.id, k),
                                                synapse=synapse,
                                                to="GrCPop[0]")
            net.synaptic_connections.append(connection)
# set up fake connection for counting spikes
net.append(nml.SynapticConnection(from_="GrCPop[0]",
                                  to="SpikeRecorderPop[0]",
                                  synapse=spikeRecorder.id))


# define outputs
plot_1 = nml.Display(id="display1", title="Voltage", timeScale="1ms",
                     xmin="-10", xmax="1010", ymin="-95", ymax="-38")
plot_1.lines.append(nml.Line(id="GrC: Vm", quantity="GrCPop[0]/v",
                             scale="1mV", color="#66c2a5", timeScale="1ms"))
plot_2 = nml.Display(id="display2", title="Spike count", timeScale="1ms",
                     xmin="-10", xmax="1010", ymin="-1", ymax="10")
plot_2.lines.append(nml.Line(id="GrC: Vm",
                             quantity="SpikeRecorderPop[0]/spikeRecorder/spikeCount",
                             scale="1", color="#fc8d62", timeScale="1ms"))
                             
out_file_1 = nml.OutFile(id="of1", fileName="output.txt")
out_file_1.output_columns.append(nml.OutputColumn(id="sc", quantity="SpikeRecorderPop[0]/spikeRecorder/spikeCount"))


# define simulation
simulation = nml.Simulation(id="sim", length="1 s", step="0.01 ms", target=net.id)
simulation.displays.append(plot_1)
simulation.displays.append(plot_2)
simulation.out_files.append(out_file_1)'''

pynml.write_neuroml2_file(net_doc, 'generated_network.net.nml')

# run simulation
####simulation.run(simulator="NEURON") # if exporting to neuron, graphical
                                   # output doesn't necessarily need
                                   # to be implemented.. but output to
                                   # disk is very important.

# load back simulation output
####sim_data = np.loadtxt("output.txt")


# serialise to external xml file all elements needed to run the
# simulation (I suppose this must be implemented anyway to allow for
# code generation or simulation with jlems)
####simulation.serialize("generated_simulation.xml")

