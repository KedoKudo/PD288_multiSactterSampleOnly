#!/usr/bin/env python
"""
Prototype of unit test for multiple scattering data
"""

from mantid.simpleapi import (
    ConvertUnits,
    CreateSampleWorkspace,
    EditInstrumentGeometry,
    Divide,
    SetSample,
    MayersSampleCorrection,
    CalculateCarpenterSampleCorrection,
    CarpenterSampleCorrection,
    PaalmanPingsAbsorptionCorrection,
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


def add_cylinder_sample_to_workspace(ws,
                                     sample_material,
                                     sample_density,
                                     height=0.1,
                                     radius=0.1):
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
    #
    absorption = MayersSampleCorrection(sample_ws, MultipleScattering=False)
    multiplescattering = MayersSampleCorrection(sample_ws,
                                                MultipleScattering=True)
    #
    return absorption, multiplescattering


# use Carpenter correction
def get_carpenter_results(sample_ws, cylinder_radius=0.2):
    ConvertUnits(InputWorkspace=sample_ws,
                 OutputWorkspace=sample_ws,
                 Target="Wavelength",
                 EMode="Elastic")
    corrections = CalculateCarpenterSampleCorrection(
        InputWorkspace=sample_ws, CylinderSampleRadius=cylinder_radius)
    absCorr = corrections.getItem(0)
    absorption = Divide(sample_ws, absCorr)
    multiplescattering = CarpenterSampleCorrection(sample_ws)
    return absorption, multiplescattering


# use Mutliple scattering correction
def get_multiple_scattering_results(sample_ws, unit="Wavelength"):
    ConvertUnits(InputWorkspace=sample_ws,
                 OutputWorkspace=sample_ws,
                 Target=unit,
                 EMode="Elastic")
    #
    absorption = PaalmanPingsAbsorptionCorrection(sample_ws)
    #
    multiplescattering = MultipleScatteringCorrection(sample_ws)
    return absorption, multiplescattering


if __name__ == "__main__":
    print("running exmaple test")