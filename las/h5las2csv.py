#!/usr/bin/env python3
import optparse
import numpy
import h5py
import os

def h5las2csv(h5fname, csvfname, delimiter = ',', header = True,
    x = True, y = True, z = True, red = True, blue = True, green = True,
    verbose = True):
    # read files
    h5File = h5py.File(h5fname, mode='r')
    csvFile = open(csvfname, mode='w')

    # declare header variables
    header = ''
    header_tuple = filter(None, (
        "x" if x else None,
        "y" if y else None,
        "z" if z else None,
        "red" if red else None,
        "green" if green else None,
        "blue" if blue else None
    ))

    # build header string
    add_delim = False
    for e in header_tuple:
        if not add_delim:
            header += e
            add_delim = True
            continue
        header += delimiter
        header += e

    # retrieve 
    lasKeys = list(h5File['las'].keys())



if __name__ == '__main__':
    # build parser object
    parser = optparse.OptionParser()

    # add options to parser
    parser.add_option(
        "-i", "--inh5",
        dest = "h5fname",
        help = "Mandatory input HDF5 file name.",
        metavar = "H5FILE"
    )
    parser.add_option(
        "-o", "--outcsv",
        dest = "csvfname",
        help = "Mandatory output CSV file name.",
        metavar = "CSVFILE"
    )
    parser.add_option(
        "-f", "--fields",
        dest = "fields",
        help = "Specify codes for extracting specific HDF5 fields. \n"\
               "Codes: \n"\
               " x -> X position \n"\
               " y -> Y position \n"\
               " z -> Z position \n"\
               " r -> Red value \n"\
               " g -> Green value \n"\
               " b -> Blue value \n"\
               "Default is: xyzrgb",
        metavar = "STR"
    )
    parser.add_option(
        "-v", "--verbose",
        dest = "verbose",
        help = "Process data verbosely.",
        action = "store_true"
    )

    # actually pare the arguments
    options, args = parser.parse_args()

    if not options.h5fname:
        parser.error("HDF5 file name not given.")
    if not os.path.isfile(options.h5fname):
        parser.error("Input H5FILE does not exist.")
    if not options.csvfname:
        parser.error("CSV file name not given.")
    if not options.fields:
        options.fields = "xyzrgb"
