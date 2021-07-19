#!/usr/bin/env python
"""
Prototype of unit test for multiple scattering data
"""

from mantid.simpleapi import (
    ConvertUnits,
    CreateSampleWorkspace,
    EditInstrumentGeometry,
    SetSample,
    MayersSampleCorrection,
    CarpenterSampleCorrection,
    MultipleScatteringCorrection,
)


# prep example data
def make_sample_workspace():
    # Create a fake workspace with TOF data
    sample_ws = CreateSampleWorkspace(Function='Powder Diffraction',
                                      NumBanks=1,
                                      BankPixelWidth=1,
                                      XUnit='TOF',
                                      XMin=1000,
                                      XMax=10000)
    # fake instrument
    EditInstrumentGeometry(sample_ws,
                           PrimaryFlightPath=5.0,
                           SpectrumIDs=[1, 2, 3, 4],
                           L2=[2.0, 2.0, 2.0, 2.0],
                           Polar=[10.0, 90.0, 170.0, 90.0],
                           Azimuthal=[0.0, 0.0, 0.0, 45.0],
                           DetectorIDs=[1, 2, 3, 4],
                           InstrumentName="Instrument")
    return sample_ws


def add_cylinder_sample_to_workspace(
        ws,
        sample_material,
        sample_density,
        height=0.1,  # in meter
        radius=0.1,  # in meter
):
    SetSample(ws,
              Geometry={
                  "Shape": "Cylinder",
                  "Height": height,
                  "Radius": radius,
                  "axis": {
                      "x": 0.0,
                      "y": 1.0,
                      "z": 0.0
                  },
              },
              ChemicalFormula=sample_material,
              SampleNumberDensity=sample_density)
    return ws


# use Mayers correction
def correction_Mayers(sample_ws):
    ConvertUnits(InputWorkspace=sample_ws,
                 OutputWorkspace=sample_ws,
                 Target="TOF",
                 EMode="Elastic")
    return MayersSampleCorrection(sample_ws, MultipleScattering=True)


# use Carpenter correction
def correction_carpenter(sample_ws):
    ConvertUnits(InputWorkspace=sample_ws,
                 OutputWorkspace=sample_ws,
                 Target="Wavelength",
                 EMode="Elastic")
    return CarpenterSampleCorrection(sample_ws)


# use Mutliple scattering correction
def correction_multiple_scattering(sample_ws, unit="Wavelength"):
    ConvertUnits(InputWorkspace=sample_ws,
                 OutputWorkspace=sample_ws,
                 Target=unit,
                 EMode="Elastic")
    return MultipleScatteringCorrection(sample_ws)


if __name__ == "__main__":
    print("running exmaple test")
    # make testing workspace
    ws = make_sample_workspace()
    # add cylinder sample
    ws = add_cylinder_sample_to_workspace(ws, "V", 0.07261, 4e-2, 0.25e-2)

    # use Mayers correction
    mayers_multi = correction_Mayers(ws)

    # use Carpenter correction
    carpenter_multi = correction_carpenter(ws)

    # use Multiple scattering correction
    ms_multi = correction_multiple_scattering(ws)

    # validation
    # -- cast to wavelength
    for me in [ws, mayers_multi, carpenter_multi, ms_multi]:
        ConvertUnits(me, "WaveLength")
    # -- compute difference
