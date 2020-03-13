#!/usr/bin/env python3
import optparse
import numpy
import h5py
import os

def h5las2csv(h5fname, csvfname, delimiter = ',', header = True,
    x = True, y = True, z = True, red = True, green = True, blue = True,
    verbose = True):
    # read files
    h5File = h5py.File(h5fname, mode='r')
    csvFile = open(csvfname, mode='w')

    # make a dictionary for data
    data_dict = {}

    # retrieve keys in las, shp
    lasKeys = list(h5File['las'].keys())
    shpKeys = list(h5File['shp'].keys())

    # selectively retrieve data

    if x and (('x_record' in lasKeys) and ('x_scale' in lasKeys) and ('x_offset' in lasKeys)):
        if verbose:
            print("Extract X data.")
        # extract keys
        x_record = h5File.get('las/x_record')[()]
        x_scale = h5File.get('las/x_scale')[()]
        x_offset = h5File.get('las/x_offset')[()]

        # calculate positions
        x_position = (x_record * x_scale) + x_offset

        # store values in dict
        data_dict['x_position'] = x_position

    if y and (('y_record' in lasKeys) and ('y_scale' in lasKeys) and ('y_offset' in lasKeys)):
        if verbose:
            print("Extract Y data.")
        # extract keys
        y_record = h5File.get('las/y_record')[()]
        y_scale = h5File.get('las/y_scale')[()]
        y_offset = h5File.get('las/y_offset')[()]

        # calculate positions
        y_position = (y_record * y_scale) + y_offset

        # store values in dict
        data_dict['y_position'] = y_position

    if z and (('z_record' in lasKeys) and ('z_scale' in lasKeys) and ('z_offset' in lasKeys)):
        if verbose:
            print("Extract Z data.")
        # extract keys
        z_record = h5File.get('las/z_record')[()]
        z_scale = h5File.get('las/z_scale')[()]
        z_offset = h5File.get('las/z_offset')[()]

        # calculate positions
        z_position = (z_record * z_scale) + z_offset

        # store values in dict
        data_dict['z_position'] = z_position

    if red and ('r_record' in lasKeys):
        if verbose:
            print("Extract R data.")
        # extract keys
        r_record = h5File.get('las/r_record')[()]

        # store values in dict
        data_dict['r_record'] = r_record

    if green and ('g_record' in lasKeys):
        if verbose:
            print("Extract G data.")
        # extract keys
        g_record = h5File.get('las/g_record')[()]

        # store values in dict
        data_dict['g_record'] = g_record

    if blue and ('b_record' in lasKeys):
        if verbose:
            print("Extract B data.")
        # extract keys
        b_record = h5File.get('las/b_record')[()]

        # store values in dict
        data_dict['b_record'] = b_record

    if ('shpIX' in shpKeys) and ('shpID' in shpKeys):
        if verbose:
            print("Extract shp data.")
        # extract keys
        shpIX = h5File.get('shp/shpIX')[()]
        shpID = h5File.get('shp/shpID')[()]

        # store values in dict
        max_uint32 = numpy.iinfo('uint32').max
        data_dict['shpIX'] = shpIX
        data_dict['shpID'] = [
            shpID[i].decode('UTF-8') if i < max_uint32 else 'NA' for i in shpIX
        ]


    # build header and format strings and get data types
    header_str = ''
    fmt_str = ''
    add_delim = False
    for e in data_dict.keys():
        if not add_delim:
            header_str += e
            fmt_str += '%s'
            add_delim = True
            continue
        header_str += delimiter
        header_str += e
        fmt_str += delimiter
        fmt_str += '%s'
    header_str += '\n'
    fmt_str += '\n'

    if header:
        csvFile.write(header_str)

    for t in zip(*tuple(data_dict.values())):
        csvFile.write(fmt_str % t)

    h5File.close()
    csvFile.close()

    # arr_name = list(data_dict.keys())
    # arr_fmt = [arr.dtype.str for arr in data_dict.values()]
    #
    # print(arr_fmt)
    #
    # arr_dtype = dict(names = arr_name, formats = arr_fmt)
    #
    # print(arr_dtype)
    #
    # outarray = numpy.array(
    #     list(data_dict.values()),
    #     dtype = arr_dtype
    # )
    #
    # print(outarray)
    #
    # numpy.savetxt(csvFile, outarray.T, delimiter = delimiter, header = header)



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
        "-d", "--delimiter",
        dest = "delimiter",
        help = "Specify a custom delimiter for the CSV.",
        metavar = "STR"
    )
    parser.add_option(
        "--header",
        dest = "header",
        help = "Add header to CSV.",
        action = "store_true"
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
    if not options.delimiter:
        options.delimiter = ','

    h5las2csv(
        options.h5fname,
        options.csvfname,
        delimiter = options.delimiter,
        header = options.header,
        x = 'x' in options.fields,
        y = 'y' in options.fields,
        z = 'z' in options.fields,
        red = 'r' in options.fields,
        green = 'g' in options.fields,
        blue = 'b' in options.fields,
        verbose = options.verbose
    )
