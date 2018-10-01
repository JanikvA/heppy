'''Example configuration file for an ee->ZH analysis in the 4 jet channel,
with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from analysis_ee_ZH_had_cfg import * 

'''

import os
import copy
import heppy.framework.config as cfg

from heppy.framework.event import Event
Event.print_patterns=['*jet*', 'bquarks', '*higgs*',
                      '*zed*', '*lep*']

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

# setting the random seed for reproducible results
import heppy.statistics.rrandom as random
random.seed(0xdeadbeef)

# definition of the collider
from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 240.

# input definition
comp = cfg.Component(
    'ee_ZH_Z_Hbb',
    files = [
        'ee_ZH_Hyy_0.root'
    ]
)
selectedComponents = [comp]

# read FCC EDM events from the input root file(s)
# do help(Reader) for more information
from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
)

# the papas simulation and reconstruction sequence
from heppy.test.papas_cfg import papas_sequence, detector
from heppy.test.papas_cfg import papasdisplay as display

# Use a Selector to select leptons from the output of papas simulation.
# Currently, we're treating electrons and muons transparently.
# we could use two different instances for the Selector module
# to get separate collections of electrons and muons
# help(Selector) for more information
from heppy.analyzers.Selector import Selector
def is_photon(ptc):
    return abs(ptc.pdgid())==22

photons = cfg.Analyzer(
    Selector,
    'sel_leptons',
    output = 'photons',
    input_objects = 'rec_particles',
    filter_func = is_photon 
)

# Compute lepton isolation w/r other particles in the event.
# help(IsolationAnalyzer) 
# help(isolation) 
# for more information
from heppy.analyzers.IsolationAnalyzer import IsolationAnalyzer
from heppy.particles.isolation import EtaPhiCircle

iso_photons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'photons',
    particles = 'rec_particles',
    iso_area = EtaPhiCircle(0.4)
)


# Select isolated leptons with a Selector
def is_isolated(lep):
    '''returns true if the particles around the lepton
    in the EtaPhiCircle defined above carry less than 30%
    of the lepton energy.'''
    return lep.iso.sume/lep.e()<0.3  # fairly loose

sel_iso_leptons = cfg.Analyzer(
    Selector,
    'sel_iso_leptons',
    output = 'sel_iso_leptons',
    input_objects = 'leptons',
    filter_func = is_isolated
)


from heppy.analyzers.GenResonanceAnalyzer import GenResonanceAnalyzer
gen_bosons = cfg.Analyzer(
    GenResonanceAnalyzer,
    output='gen_bosons', 
    pdgids=[23, 25],
    statuses=[62],
    # decay_pdgids=[11, 13],
    verbose=False, 
)


# make 4 exclusive jets 
from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
jets = cfg.Analyzer(
    JetClusterizer,
    output = 'jets',
    particles = 'rec_particles',
    fastjet_args = dict( ptmin = 10)  
)

# simple cut flow printout
from heppy.analyzers.examples.hgammagamma.Selection import Selection
selection = cfg.Analyzer(
    Selection,
    reco_ptc='rec_particles',
	higgs="higgs",
	isosum="isosum",
	deta="deta",
	dHtheta="dHtheta",
    selected_photons='selected_photons',
    zed_mass="zed_mass",
    log_level=logging.INFO
)

# Analysis-specific ntuple producer
# please have a look at the ZHTreeProducer class
from heppy.analyzers.examples.hgammagamma.TreeProducer import TreeProducer
tree = cfg.Analyzer(
    TreeProducer,
       particles=[],
    iso_particles=[], 
    jets=[],
    resonances=[('gen_bosons',2)],
    recoPtcs='rec_particles',
	higgs="higgs",
	isosum="isosum",
	deta="deta",
	dHtheta="dHtheta",
    jets1="jets",
    zed_mass="zed_mass",
    selected_photons='selected_photons',
    gen_bosons='gen_bosons'
)

# definition of the sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source,
    papas_sequence, 
	photons,
	iso_photons,
    gen_bosons,
    selection, 
    jets,
    tree,
    display
)

# Specifics to read FCC events 
from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)

