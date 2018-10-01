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
Collider.SQRTS = 365.
jet_correction = False

#local input
#comp = cfg.Component(
#    'ee_VBF',
#    files = [
#        'ee_VBF_0.root'
#    ]
#)
#selectedComponents = [comp]

# input definition for batch
import glob
ZH = cfg.Component(
    'ZH',
    files = glob.glob('/afs/cern.ch/work/j/jvonahne/public/VBF365GeVSamples/ZH500k/*.root')
    )   
ZH.splitFactor = len(ZH.files)

VBF = cfg.Component(
    'VBF',
    files = glob.glob('/afs/cern.ch/work/j/jvonahne/public/VBF365GeVSamples/VBF100k/*.root')
    )   
VBF.splitFactor = len(VBF.files)

ZZ = cfg.Component(
    'ZZ',
    files = glob.glob('/afs/cern.ch/work/j/jvonahne/public/VBF365GeVSamples/ZZ500k/*.root')
    )   
ZZ.splitFactor = len(ZZ.files)

WW = cfg.Component(
    'WW',
    files = glob.glob('/afs/cern.ch/work/j/jvonahne/public/VBF365GeVSamples/WW500k/*.root')
    )   
WW.splitFactor = len(WW.files)

qqbar = cfg.Component(
    'qqbar',
    files = glob.glob('/afs/cern.ch/work/j/jvonahne/public/VBF365GeVSamples/ffbar2M/*.root')
    )   
qqbar.splitFactor = len(qqbar.files)

selectedComponents = [ZH]



# read FCC EDM events from the input root file(s)
# do help(Reader) for more information
from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
)

# the papas simulation and reconstruction sequence
from heppy.papas.detectors.CLIC import clic
from heppy.papas.detectors.CMS import cms
detector = clic


from heppy.test.papas_cfg import papas, pfreconstruct, papas_sequence
from heppy.test.papas_cfg import papasdisplaycompare as display 

papas.detector = detector    
display.detector = detector
pfreconstruct.detector = detector


# compute the missing 4-momentum
from heppy.analyzers.RecoilBuilder import RecoilBuilder
missing_energy = cfg.Analyzer(
    RecoilBuilder,
    instance_label = 'missing_energy',
    output = 'missing_energy',
    sqrts = Collider.SQRTS,
    to_remove = 'jets'
) 


# make 4 exclusive jets 
from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
jets = cfg.Analyzer(
    JetClusterizer,
    output = 'jets',
    particles = 'rec_particles',
    fastjet_args = dict( njets = 2)  
)

# make 4 gen jets with stable gen particles
genjets = cfg.Analyzer(
    JetClusterizer,
    output = 'genjets',
    particles = 'gen_particles_stable',
    fastjet_args = dict( njets = 2)  
)

# select b quarks for jet to parton matching
from heppy.test.btag_parametrized_cfg import btag_parametrized, btag
# reconstruction of the H and Z resonances.
# for now, use for the Higgs the two b jets with the mass closest to mH
# the other 2 jets are used for the Z.
# implement a chi2? 
from heppy.analyzers.examples.hbb_Emiss.ZHReconstruction import ZHReconstruction
zhreco = cfg.Analyzer(
    ZHReconstruction,
    output_higgs='higgs',
    output_zed='zed', 
    input_jets='rescaled_bjets'
)

# simple cut flow printout
#from heppy.analyzers.examples.hbb_Emiss.Selection import Selection
#selection = cfg.Analyzer(
#    Selection,
#    input_jets='rescaled_bjets', 
#    log_level=logging.INFO
#)

from heppy.analyzers.examples.hbb_Emiss.Selection import Selection
selection = cfg.Analyzer(
    Selection,
    input_jets='jets',
    misenergy ='missing_energy',
    cutlife ='cut_life',
    alpha='alpha',
    beta='beta',
    pLges='pLges',
    pTges='pTges',
    det='det',
    emratio='emratio',
    mvis='mvis',
ctracks='ctracks',
cross='cross',
    log_level=logging.INFO
)

# Analysis-specific ntuple producer
# please have a look at the ZHTreeProducer class
#from heppy.analyzers.examples.hbb_Emiss.TreeProducer import TreeProducer
#tree = cfg.Analyzer(
#    TreeProducer,
#    misenergy = 'missing_energy', 
#    jets='rescaled_jets',
#    higgs='higgs',
#    zed='zed',
#    leptons='sel_iso_leptons'
#)

from heppy.analyzers.GenResonanceAnalyzer import GenResonanceAnalyzer
gen_bosons = cfg.Analyzer(
    GenResonanceAnalyzer,
    output='gen_bosons', 
    pdgids=[23, 25],
    statuses=[62],
    # decay_pdgids=[11, 13],
    verbose=False, 
)

from heppy.analyzers.examples.hbb_Emiss.TreeProducerWithGenB import TreeProducer
tree = cfg.Analyzer(
    TreeProducer,
       particles=[],
    iso_particles=[], 
    jets=[],
    resonances=[('gen_bosons',2)],
    misenergy = 'missing_energy',
    jets1='jets',
    scaledjets='rescaled_bjets',
    genjets='genjets',
    higgs='higgs',
    zed='zed',
    scalingfac='scalingfactor',
    scalingfac2='scalingfactor2',
    alpha='alpha',
    beta='beta',
    pLges='pLges',
    pTges='pTges',
    emratio='emratio',
    mvis='mvis',
    ctracks='ctracks',
    cross='cross',
    gen_particles='gen_particles',
    gen_bosons='gen_bosons'
)

#from heppy.analyzers.examples.hbb_Emiss.TreeProducer350 import TreeProducer
#tree = cfg.Analyzer(
#    TreeProducer,
#    misenergy = 'missing_energy',
#    jets='jets',
#    scaledjets='rescaled_bjets',
#    genjets='genjets',
#    higgs='higgs',
#    zed='zed',
#    scalingfac='scalingfactor',
#    scalingfac2='scalingfactor2',
#    alpha='alpha',
#    beta='beta',
#    pLges='pLges',
#    pTges='pTges',
#    emratio='emratio',
#    mvis='mvis',
#    ctracks='ctracks',
#    cross='cross',
#    gen_particles='gen_particles',
#)

from heppy.analyzers.examples.hbb_Emiss.Bjetscaling import Bjetscaling
bjetscaling = cfg.Analyzer(
    Bjetscaling,
    output_jets='rescaled_bjets',
    input_jets='jets',
    sqrts=Collider.SQRTS,
    misenergy = 'missing_energy',
    det = 'det',
    scalingfac='scalingfactor',
    scalingfac2='scalingfactor2'
)



if jet_correction:
    from heppy.analyzers.JetEnergyCorrector import JetEnergyCorrector
    jets_cor = cfg.Analyzer(
        JetEnergyCorrector,
        input_jets='jets',
        detector=detector 
    )   
    jets = cfg.Sequence(jets, jets_cor)



# definition of the sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source,
    papas_sequence, 
    gen_bosons,
    jets,
    missing_energy, 
    bjetscaling,
    genjets, 
    btag_parametrized,
    selection, 
    zhreco, 
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

