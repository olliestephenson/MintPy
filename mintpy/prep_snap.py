#!/usr/bin/env python3
############################################################
# Program is part of MintPy                                #
# Copyright (c) 2013, Zhang Yunjun, Heresh Fattahi         #
# Author: Andre Theron, Zhang Yunjun, Jun 2019             #
# Email: andretheronsa@gmail.com                           #
############################################################


import os
import sys
import argparse
from mintpy.utils import readfile, writefile, utils as ut


SPEED_OF_LIGHT = 299792458  # m / s


##################################################################################################
DESCRIPTION = """
  For each interferogram, coherence or unwrapped .dim product this script will prepare.rsc 
  metadata files for for mintpy based on .dim metadata file.

  The SNAP .dim file should contain all the required sensor / baseline metadata needed.
  The baseline metadata gets written during snap back-geocoding (co-registration).
  prep_snap is run separately for unw/ifg/cor files so needs separate .dim/.data products
  with only the relevant band in each product. Use Band Subset > save BEAM-DIMAP file.

  The file name should be yyyymmdd_yyyymmdd_type_tc.dim where type can be filt/unw/coh.

  The DEM should be prepared by adding an elevation file to a coregestered product - 
  then extract the elevation band only. Use Band Subset > save BEAM-DIMAP file

  Currently only works for geocoded (terrain correction step in SNAP) interferograms.
"""

EXAMPLE = """example:
  prep_snap.py  ../interferograms/*/*/Unw_*.img
  prep_snap.py  ../dem_tc.data/dem*.img
"""

def create_parser():
    parser = argparse.ArgumentParser(description='Prepare attributes file for SNAP products.\n'+DESCRIPTION,
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=EXAMPLE)

    parser.add_argument('file', nargs='+', help='SNAP data file(s) in *.img format.')
    return parser


def cmd_line_parse(iargs=None):
    parser = create_parser()
    inps = parser.parse_args(args=iargs)

    inps.file = ut.get_file_list(inps.file, abspath=True)
    for fname in inps.file:
        if not fname.endswith('.img'):
            raise ValueError('Input data file does NOT end with .img: {}'.format(fname))

    return inps


def write_rsc(atr, rsc_file):
    """Write to rsc file"""
    # grab atr from existing rsc file
    if os.path.isfile(rsc_file):
        atr_orig = readfile.read_roipac_rsc(rsc_file)
    else:
        atr_orig = dict()

    # (over)write to rsc file if input atr has more items
    if not set(atr.items()).issubset(set(atr_orig.items())):
        atr_out = {**atr_orig, **atr}
        print('write metadata to {} '.format(os.path.basename(rsc_file)))
        writefile.write_roipac_rsc(atr_out, out_file=rsc_file)

    return rsc_file


##################################################################################################
def main(iargs=None):
    inps = cmd_line_parse(iargs)

    for img_file in inps.file:
        # read metadata from *.dim file
        # the map info from *.img.hdr file is NOT right, thus, not used.
        dim_file = os.path.dirname(img_file)[:-4] + 'dim'
        atr = readfile.read_snap_dim(dim_file)

        # write metadata dict to *.rsc file
        rsc_file = img_file + '.rsc'
        write_rsc(atr, rsc_file)

    return


##################################################################################################
if __name__ == "__main__":
    main(sys.argv[1:])
