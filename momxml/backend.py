from momxml.observationspecificationbase import ObservationSpecificationBase
from momxml.observationspecificationbase import indent
from momxml.utilities import lower_case, AutoReprBaseClass

r'''
This module contains the helper classes that contain the miriad
different setting of the correlator. The main class here is
BackendProcessing, which contains pointers to the other classes:
TiedArrayBeams and Stokes, when needed.
'''


class TiedArrayBeams(AutoReprBaseClass):
    r'''
    Description of Tied Array Beam (TAB) settings.

    **Parameters**

    flyseye : bool
        If True, store data streams from each station individually.

    beam_offsets : list of pairs of float
        The offsets of the phase centres of the TABs in $lm$
        coordinates in a SIN projection towards the pointing centre of
        the stations. *Units are unclear to me!*

    nr_tab_rings : int
        Alternatively, one can specify with how many rings one wants
        to tile the beam.
    
    tab_ring_size : float
        Distance between TAB rings. *Units are unclear to me*

    **Examples**
    
    >>> tab = TiedArrayBeams()
    >>> tab
    TiedArrayBeams(nr_tab_rings  = 0,
                   flyseye       = False,
                   beam_offsets  = None,
                   tab_ring_size = 0)
    >>> print(tab.xml())
    <BLANKLINE>
    <tiedArrayBeams>
      <flyseye>false</flyseye>
      <nrTabRings>0</nrTabRings>
      <tabRingSize>0.000000</tabRingSize>
      <tiedArrayBeamList/>
    </tiedArrayBeams>

    >>> tab_fe = TiedArrayBeams(flyseye      = True,
    ...                         beam_offsets = [(0.0, 0.0), (0.1, -0.05)])
    >>> tab_fe
    TiedArrayBeams(nr_tab_rings  = 0,
                   flyseye       = True,
                   beam_offsets  = [(0.0, 0.0), (0.1, -0.05)],
                   tab_ring_size = 0)
    >>> print(tab_fe.xml())
    <BLANKLINE>
    <tiedArrayBeams>
      <flyseye>true</flyseye>
      <nrTabRings>0</nrTabRings>
      <tabRingSize>0.000000</tabRingSize>
      <tiedArrayBeamList>
        <tiedArrayBeam><coherent>true</coherent><angle1>0.000000</angle1><angle2>0.000000</angle2></tiedArrayBeam>
        <tiedArrayBeam><coherent>true</coherent><angle1>0.100000</angle1><angle2>-0.050000</angle2></tiedArrayBeam>
      </tiedArrayBeamList>
    </tiedArrayBeams>
    '''
    def __init__(self, flyseye    = False,
                 beam_offsets     = None,
                 nr_tab_rings     = 0,
                 tab_ring_size    = 0):
        #super(TiedArrayBeams, self).__init__(name   = 'TAB',
        #                                     parent = None, children = None)
        self.flyseye          = flyseye
        self.beam_offsets     = beam_offsets
        self.nr_tab_rings     = nr_tab_rings
        self.tab_ring_size    = tab_ring_size


    def xml(self, project_name = None):
        output = ('''
<tiedArrayBeams>
  <flyseye>%s</flyseye>
  <nrTabRings>%d</nrTabRings>
  <tabRingSize>%f</tabRingSize>''' %
                  (lower_case(self.flyseye),
                   self.nr_tab_rings,
                   self.tab_ring_size))
        if self.beam_offsets and len(self.beam_offsets) > 0:
            output += ('''
  <tiedArrayBeamList>
    %s
  </tiedArrayBeamList>''' %
                       '\n    '.join(
                           ['<tiedArrayBeam><coherent>true</coherent><angle1>%f</angle1><angle2>%f</angle2></tiedArrayBeam>'
        % (angle_1, angle_2)
                            for angle_1, angle_2 in self.beam_offsets]))
        else:
            output += '''
  <tiedArrayBeamList/>'''
        return output+'\n</tiedArrayBeams>'









class Stokes(AutoReprBaseClass):
    r'''
    Describes averaging and storage parameters for beam formed
    observations. This class is not derived from
    ObservationSpecificationBase because it is really only a helper to
    BackendProcessing. Use instances of this class as parameters to
    BackendProcessing for ``coherent_stokes_data`` and
    ``incoherent_stokes_data``.

    **Parameters**
    
    mode : string
        Either 'coherent' or 'incoherent'.

    subbands_per_file : int
        Number of sub bands per output file / storage machine. Use 512
        for low data rates, but decrease as necessary to keep the data
        rate per file (locus node / storage machine) below about 300 MB /
        s.

    number_collapsed_channels : int
        Frequency averaging parameter. Not sure if this is the number
        of output channels, or the number of channels to be
        averaged. If someone knows, let me know. 0 implies no
        averaging.

    stokes_downsampling_steps : int
        Number of time samples to average before writing to
        disk. Default is 1 (no averaging).

    polarizations : string
       Either 'I' or 'IQUV'.

    **Examples**
    
    >>> stk = Stokes(mode = 'coherent', polarizations = 'IQUV',
    ...              stokes_downsampling_steps = 64)
    >>> stk
    Stokes(stokes_downsampling_steps = 64,
           subbands_per_file         = 512,
           polarizations             = 'IQUV',
           mode                      = 'coherent',
           number_collapsed_channels = 0)
    >>> print(stk.xml())
    <subbandsPerFileCS>512</subbandsPerFileCS>
    <numberCollapsedChannelsCS>0</numberCollapsedChannelsCS>
    <stokesDownsamplingStepsCS>64</stokesDownsamplingStepsCS>
    <whichCS>IQUV</whichCS>
    '''

    def __init__(self, mode, subbands_per_file = 512,
                 number_collapsed_channels = 0,
                 stokes_downsampling_steps = 1,
                 polarizations = 'I'):
        self.mode                      = mode
        self.subbands_per_file         = subbands_per_file
        self.number_collapsed_channels = number_collapsed_channels
        self.stokes_downsampling_steps = stokes_downsampling_steps
        self.polarizations             = polarizations
        self.validate()


    def validate(self):
        r'''
        Raises a ValueError for every problem found in the settings.
        '''
        valid_modes         = ['coherent', 'incoherent']
        valid_polarizations = ['I', 'IQUV']
        if self.mode not in valid_modes:
            raise ValueError('mode(%r) not one of %r.' % 
                             (self.mode, valid_modes))
        if self.polarizations not in valid_polarizations:
            raise ValueError('polarizations(%r) not one of %r.' %
                             (self.polarizations, valid_polarizations))
        if type(self.subbands_per_file) != int:
            raise ValueError('subbands_per_file(%r) must be an integer.' %
                             self.subbands_per_file)
        if self.subbands_per_file <= 0 or self.subbands_per_file > 1024:
            raise ValueError('subbands_per_file(%r) not in <0, 1024]' %
                             self.subbands_per_file)
        if type(self.stokes_downsampling_steps) != int:
            raise ValueError('stokes_downsampling_steps(%r) must be an integer.'
                             % self.stokes_downsampling_steps)
        if self.stokes_downsampling_steps <= 0:
            raise ValueError('stokes_downsampling_steps(%r) must be > 0.' %
                             self.stokes_downsampling_steps)
        


    def stokes_suffix(self):
        r'''
        return CS or IS, depending on whether these are coherent or
        incoherent stokes settings.  coherent stokes settings also
        need tied array beams / fly's eye stuff specified. 
        '''
        return self.mode[0].upper()+'S'


    def xml(self, project_name = None):
        r'''
        Produce the xml for the coherent stokes  or incoherent stokes
        settings of the backend.
        '''
        return ('''<subbandsPerFile%(suffix)s>%(subbands_per_file)d</subbandsPerFile%(suffix)s>
<numberCollapsedChannels%(suffix)s>%(number_collapsed_channels)d</numberCollapsedChannels%(suffix)s>
<stokesDownsamplingSteps%(suffix)s>%(stokes_downsampling_steps)d</stokesDownsamplingSteps%(suffix)s>
<which%(suffix)s>%(polarizations)s</which%(suffix)s>''' % 
                {'suffix'                   : self.stokes_suffix(),
                 'subbands_per_file'        : self.subbands_per_file,
                 'number_collapsed_channels': self.number_collapsed_channels,
                 'stokes_downsampling_steps': self.stokes_downsampling_steps,
                 'polarizations'            : self.polarizations})
               








class BackendProcessing(AutoReprBaseClass):
    r'''
    BackendProcessing contains all the settings for the correlator and
    beamformer hardware.

    **Parameters**
    
    channels_per_subband : int
        Number of channels per sub band. Default is 64.

    integration_time_seconds : number
        Integration time for correlator observations. Typically 1 or 2
        seconds, but anything from 0.2 to 99 seconds should be
        possible.

    correlated_data : bool
        True if cross-correlation visibilities should be produced.

    filtered_data : bool
        No idea what this means. Default is False.

    beamformed_data : bool
        True if beamformed data is to be produced, such as complex
        voltage, coherent stokes, or incoherent stokes data. If True
        and neither coherent_stokes_data, nor incoherent_stokes_data
        are specified, complex voltages are produced.

    coherent_stokes_data : None or Stokes instance
        Coherent stokes settings.

    incoherent_stokes_data : None or Stokes instance
        Incoherent stokes settings.

    stokes_integrate_channels : bool
        Apply frequency averaging. Default False.

    coherent_dedispersed_channels : bool
        Apply coherent dedispersion? Default False.

    tied_array_beams : None or TiedArrayBeams instance
        Tied array beam settings.

    bypass_pff : bool
        If True, skip the correlator's / beamformer's polyphase filter
        entirely. Useful for high time resolution beamformed
        data. Default: False.

    enable_superterp: bool
        If True, also beamform the superterp stations and treat them
        as a separate large station.

    **Examples**

    >>> bp = BackendProcessing()
    >>> bp
    BackendProcessing(incoherent_stokes_data        = None,
                      stokes_integrate_channels     = False,
                      integration_time_seconds      = 2,
                      filtered_data                 = False,
                      beamformed_data               = False,
                      coherent_stokes_data          = None,
                      channels_per_subband          = 64,
                      correlated_data               = True,
                      tied_array_beams              = TiedArrayBeams(nr_tab_rings  = 0,
                                                                     flyseye       = False,
                                                                     beam_offsets  = None,
                                                                     tab_ring_size = 0),
                      coherent_dedispersed_channels = False,
                      enable_superterp              = False,
                      bypass_pff                    = False)
    >>> print(bp.xml())
    <correlatedData>true</correlatedData>
    <filteredData>false</filteredData>
    <beamformedData>false</beamformedData>
    <coherentStokesData>false</coherentStokesData>
    <incoherentStokesData>false</incoherentStokesData>
    <integrationInterval>2</integrationInterval>
    <channelsPerSubband>64</channelsPerSubband>
    <pencilBeams>
      <flyseye>false</flyseye>
      <pencilBeamList/>
    </pencilBeams>
    <tiedArrayBeams>
      <flyseye>false</flyseye>
      <nrTabRings>0</nrTabRings>
      <tabRingSize>0.000000</tabRingSize>
      <tiedArrayBeamList/>
    </tiedArrayBeams>
    <stokes>
      <integrateChannels>false</integrateChannels>
    </stokes>
    <bypassPff>false</bypassPff>
    <enableSuperterp>false</enableSuperterp>
    <BLANKLINE>

    Here is a Fly's eye example:
    >>> channels_per_subband = 16
    >>> coherent_stokes_data = Stokes('coherent',
    ...                               stokes_downsampling_steps = 128)
    >>> tied_array_beams     = TiedArrayBeams(flyseye      = True,
    ...                                       beam_offsets = None)

    >>> bp_fe = BackendProcessing(
    ...        correlated_data          = False,
    ...        channels_per_subband     = channels_per_subband,
    ...        coherent_stokes_data     = coherent_stokes_data,
    ...        tied_array_beams         = tied_array_beams)
    >>> bp_fe
    BackendProcessing(incoherent_stokes_data        = None,
                      stokes_integrate_channels     = False,
                      integration_time_seconds      = 2,
                      filtered_data                 = False,
                      beamformed_data               = False,
                      coherent_stokes_data          = Stokes(stokes_downsampling_steps = 128,
                                                             subbands_per_file         = 512,
                                                             polarizations             = 'I',
                                                             mode                      = 'coherent',
                                                             number_collapsed_channels = 0),
                      channels_per_subband          = 16,
                      correlated_data               = False,
                      tied_array_beams              = TiedArrayBeams(nr_tab_rings  = 0,
                                                                     flyseye       = True,
                                                                     beam_offsets  = None,
                                                                     tab_ring_size = 0),
                      coherent_dedispersed_channels = False,
                      enable_superterp              = False,
                      bypass_pff                    = False)
    >>> print(bp_fe.xml())
    <correlatedData>false</correlatedData>
    <filteredData>false</filteredData>
    <beamformedData>false</beamformedData>
    <coherentStokesData>true</coherentStokesData>
    <incoherentStokesData>false</incoherentStokesData>
    <channelsPerSubband>16</channelsPerSubband>
    <pencilBeams>
      <flyseye>true</flyseye>
      <pencilBeamList/>
    </pencilBeams>
    <tiedArrayBeams>
      <flyseye>true</flyseye>
      <nrTabRings>0</nrTabRings>
      <tabRingSize>0.000000</tabRingSize>
      <tiedArrayBeamList/>
    </tiedArrayBeams>
    <stokes>
      <integrateChannels>false</integrateChannels>
      <subbandsPerFileCS>512</subbandsPerFileCS>
      <numberCollapsedChannelsCS>0</numberCollapsedChannelsCS>
      <stokesDownsamplingStepsCS>128</stokesDownsamplingStepsCS>
      <whichCS>I</whichCS>
    </stokes>
    <bypassPff>false</bypassPff>
    <enableSuperterp>false</enableSuperterp>
    <BLANKLINE>

    And here for coherent stokes beam forming:
    >>> tied_array_beams     = TiedArrayBeams(flyseye      = False,
    ...                                       beam_offsets = None)
    >>> bp_cs = BackendProcessing(
    ...        correlated_data          = False,
    ...        channels_per_subband     = channels_per_subband,
    ...        coherent_stokes_data     = coherent_stokes_data,
    ...        tied_array_beams         = tied_array_beams)
    >>> bp_cs
    BackendProcessing(incoherent_stokes_data        = None,
                      stokes_integrate_channels     = False,
                      integration_time_seconds      = 2,
                      filtered_data                 = False,
                      beamformed_data               = False,
                      coherent_stokes_data          = Stokes(stokes_downsampling_steps = 128,
                                                             subbands_per_file         = 512,
                                                             polarizations             = 'I',
                                                             mode                      = 'coherent',
                                                             number_collapsed_channels = 0),
                      channels_per_subband          = 16,
                      correlated_data               = False,
                      tied_array_beams              = TiedArrayBeams(nr_tab_rings  = 0,
                                                                     flyseye       = False,
                                                                     beam_offsets  = None,
                                                                     tab_ring_size = 0),
                      coherent_dedispersed_channels = False,
                      enable_superterp              = False,
                      bypass_pff                    = False)
    >>> print(bp_cs.xml())
    <correlatedData>false</correlatedData>
    <filteredData>false</filteredData>
    <beamformedData>false</beamformedData>
    <coherentStokesData>true</coherentStokesData>
    <incoherentStokesData>false</incoherentStokesData>
    <channelsPerSubband>16</channelsPerSubband>
    <pencilBeams>
      <flyseye>false</flyseye>
      <pencilBeamList/>
    </pencilBeams>
    <tiedArrayBeams>
      <flyseye>false</flyseye>
      <nrTabRings>0</nrTabRings>
      <tabRingSize>0.000000</tabRingSize>
      <tiedArrayBeamList/>
    </tiedArrayBeams>
    <stokes>
      <integrateChannels>false</integrateChannels>
      <subbandsPerFileCS>512</subbandsPerFileCS>
      <numberCollapsedChannelsCS>0</numberCollapsedChannelsCS>
      <stokesDownsamplingStepsCS>128</stokesDownsamplingStepsCS>
      <whichCS>I</whichCS>
    </stokes>
    <bypassPff>false</bypassPff>
    <enableSuperterp>false</enableSuperterp>
    <BLANKLINE>
    '''
    def __init__(self,
                 channels_per_subband     = 64,
                 integration_time_seconds = 2,
                 correlated_data          = True,
                 filtered_data            = False,
                 beamformed_data          = False,
                 coherent_stokes_data     = None,
                 incoherent_stokes_data   = None,
                 stokes_integrate_channels = False,
                 coherent_dedispersed_channels = False,
                 tied_array_beams              = None,
                 bypass_pff                    = False,
                 enable_superterp              = False
                 ):
        self.channels_per_subband = channels_per_subband
        self.integration_time_seconds  = int(round(integration_time_seconds))
        self.correlated_data           = correlated_data
        self.filtered_data             = filtered_data
        self.beamformed_data           = beamformed_data
        self.coherent_stokes_data      = coherent_stokes_data
        self.tied_array_beams          = tied_array_beams
        if self.tied_array_beams  is None:
            self.tied_array_beams = TiedArrayBeams()
        self.incoherent_stokes_data    = incoherent_stokes_data
        self.stokes_integrate_channels = stokes_integrate_channels
        self.coherent_dedispersed_channels = coherent_dedispersed_channels
        self.bypass_pff                = bypass_pff
        self.enable_superterp          = enable_superterp


    def need_beam_observation(self):
        r'''
        '''
        return (self.coherent_stokes_data or self.incoherent_stokes_data or 
                self.filtered_data or self.beamformed_data)



    def instrument_name(self):
        r'''
        '''
        if self.need_beam_observation():
            return 'Beam Observation'
        else:
            return 'Interferometer'



    def default_template(self):
        r'''
        '''
        if self.need_beam_observation():
            return 'BeamObservation'
        else:
            return 'Interferometer'
        
            
    def measurement_type(self):
        if self.need_beam_observation():
            return 'lofar:BFMeasurementType'
        else:
            return 'lofar:UVMeasurementType'


    def measurement_attributes(self):
        if self.need_beam_observation():
            return 'bfMeasurementAttributes'
        else:
            return 'uvMeasurementAttributes'


    def xml(self, project_name=None, child_id=None, parent_label=None):
        r'''
        '''
        def lower_case(bool):
            return repr(bool).lower()
            
        incoherent_stokes = self.incoherent_stokes_data is not None
        coherent_stokes = self.coherent_stokes_data is not None
        flyseye = False
        if coherent_stokes:
            flyseye = self.tied_array_beams.flyseye

            
        output = '''<correlatedData>'''+lower_case(self.correlated_data)+'''</correlatedData>
<filteredData>'''+lower_case(self.filtered_data)+'''</filteredData>
<beamformedData>'''+lower_case(self.beamformed_data)+'''</beamformedData>
<coherentStokesData>'''+lower_case(coherent_stokes)+'''</coherentStokesData>
<incoherentStokesData>'''+lower_case(incoherent_stokes)+'''</incoherentStokesData>'''
        if self.correlated_data:
            output += '''
<integrationInterval>'''+str(self.integration_time_seconds)+'''</integrationInterval>'''
        output += '''
<channelsPerSubband>'''+str(self.channels_per_subband)+'''</channelsPerSubband>
<pencilBeams>
  <flyseye>'''+lower_case(flyseye)+'''</flyseye>
  <pencilBeamList/>
</pencilBeams>''' + self.tied_array_beams.xml()+'''
<stokes>
  <integrateChannels>'''+lower_case(self.stokes_integrate_channels)+'''</integrateChannels>'''
        if self.incoherent_stokes_data:
            output += '\n'+indent(self.incoherent_stokes_data.xml(), 2)
        if self.coherent_stokes_data:
            output += '\n'+indent(self.coherent_stokes_data.xml(), 2)

        output += '''
</stokes>
<bypassPff>'''+lower_case(self.bypass_pff)+'''</bypassPff>
<enableSuperterp>'''+lower_case(self.enable_superterp)+'''</enableSuperterp>
'''
        return output