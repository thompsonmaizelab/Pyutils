#!/usr/bin/env python3
import optparse
import numpy
import h5py
import shapefile
import laspy
import os
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def assign_by_shpfile(shpFile, x_record, y_record, x_scale, y_scale, x_offset,
    y_offset, verbose = True):
    # calculate x and y positions
    x_position = (x_record * x_scale) + x_offset
    y_position = (y_record * y_scale) + y_offset

    # list to hold shape IDs associated with the polygon
    shpID = []

    # create a uint32 array to hold integers for assignments to shapes
    shpIX = numpy.empty(len(x_position), dtype='uint32')

    # fill with max integer value; this represents NA (not assigned)
    shpIX.fill(numpy.iinfo('uint32').max)

    # get number of shapes
    nshapes = shpFile.numRecords

    # index counter for shape IDs appended to shpID
    k = 0

    # loop through all shapes
    for j,shp in enumerate(shpFile):
        # if the shape is not a polygon (code == 5), skip it.
        if shp.shape.shapeType != 5:
            print(
                "skipping %s '%s' (%s != 5)" %
                (shp.shape.shapeTypeName, shp.record.id, shp.shape.shapeType)
            )
            continue

        # append the ID associated with the shape
        shpID.append(shp.record.id)

        if verbose:
            print("%.4f%% Process shape %s: %s" % (100*j/nshapes, j, shpID[k]))

        # unpack bounding box for polygon
        bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max = shp.shape.bbox

        ### algorithm:
        ### ray-tracing algorithm to determine if point in polygon is expensive
        ### to reduce compute time, prefilter point using bounding box: O(4n)

        # create mask of points within the bounding box:
        # do this in steps to reduce memory overhead
        mask = x_position >= bbox_x_min
        mask = numpy.logical_and(mask, y_position >= bbox_y_min)
        mask = numpy.logical_and(mask, x_position <= bbox_x_max)
        mask = numpy.logical_and(mask, y_position <= bbox_y_max)

        # get the indicies of points within the bounding box
        nonzero = numpy.flatnonzero(mask)

        # construct a polygon for the shapefile entry
        polygon = Polygon(shp.shape.points)

        # for each index of each point in the bounding box, check if in polygon
        for i in nonzero:
            point = Point(x_position[i], y_position[i])
            # OPTIMIZE: not sure if 'if' statement would be faster...
            # set mask to be equal to if the point is in the polygon
            mask[i] = polygon.contains(point)

        # set shape index assignment to this polygon's index
        shpIX[mask] = k

        # increment k index
        k += 1

    # return both shape IDs and assignments
    return shpID, shpIX

def h5grp_write(h5grp, verbose = True, **kwargs):
    for key, value in kwargs.items():
        if verbose:
            print("Write %s to HDF5" % key)
        h5grp[key] = value

def las2h5(lasfname, h5fname, shpfname = None, shpcut = False,
    x = True, y = True, z = True, red = True, blue = True, green = True,
    verbose = True):
    # open LAS, HDF5, SHP files
    lasFile = laspy.base.Reader(lasfname, mode='r')
    h5File = h5py.File(h5fname, mode='w')
    shpFile = None if shpfname is None else shapefile.Reader(shpfname)

    # get LAS file header
    lasHeader = lasFile.get_header()

    # begin by creating two groups: las and shp for LAS and SHP data
    h5_lasgrp = h5File.create_group("las")
    h5_shpgrp = h5File.create_group("shp")

    # start by making a selection mask (nothing selected by default)
    mask = slice(None)

    # declare variables for shape ID list and shape index array
    shpID = None
    shpIX = None

    # get x and y coordinates
    x_record = lasFile.get_x()
    y_record = lasFile.get_y()

    # get scaling factors and offsets
    x_scale, y_scale, z_scale = lasHeader.get_scale()
    x_offset, y_offset, z_offset = lasHeader.get_offset()

    # gather shape ID list and index array if we have a shapefile
    if shpFile is not None:
        shpID, shpIX = assign_by_shpfile(
            shpFile,
            x_record, y_record, x_scale, y_scale, x_offset, y_offset,
            verbose
        )

    # if we seek to filter by shape, alter the selection mask
    if shpcut:
        max_uint32 = numpy.iinfo('uint32').max  # get max int allowable
        mask = shpIX != max_uint32              # everything != max is good

    # begin writing to HDF5

    # if we want to save x records
    if x:
        h5grp_write(
            h5_lasgrp,
            verbose = verbose,
            x_record = x_record[mask],
            x_scale = x_scale,
            x_offset = x_offset
        )

    # if we want to save y records
    if y:
        h5grp_write(
            h5_lasgrp,
            verbose = verbose,
            y_record = y_record[mask],
            y_scale = y_scale,
            y_offset = y_offset
        )

    # if we want to save z records
    if z:
        h5grp_write(
            h5_lasgrp,
            verbose = verbose,
            z_record = lasFile.get_z()[mask],
            z_scale = z_scale,
            z_offset = z_offset
        )

    # if we want to save red records
    if red:
        h5grp_write(
            h5_lasgrp,
            verbose = verbose,
            r_record = lasFile.get_red()[mask]
        )

    if green:
        h5grp_write(
            h5_lasgrp,
            verbose = verbose,
            g_record = lasFile.get_green()[mask]
        )

    if blue:
        h5grp_write(
            h5_lasgrp,
            verbose = verbose,
            b_record = lasFile.get_blue()[mask]
        )

    if shpFile is not None:
        h5grp_write(
            h5_shpgrp,
            verbose = verbose,
            shpID = numpy.string_(shpID), # force conversion to string array
            shpIX = shpIX[mask]
        )

    # close files
    lasFile.close()
    h5File.close()
    if shpFile is not None:
        shpFile.close()


if __name__ == '__main__':
    # build parser object
    parser = optparse.OptionParser()

    # add options to parser
    parser.add_option(
        "-i", "--inlas",
        dest = "lasfname",
        help = "Mandatory input LAS file name.",
        metavar = "LASFILE"
    )
    parser.add_option(
        "-s", "--shapefile",
        dest = "shpfname",
        help = "Optional input SHP file name. Polygons in SHPFILE will be "\
               "used to group points in the H5 output.",
        metavar = "SHPFILE"
    )
    parser.add_option(
        "-c", "--shapefile-cut",
        dest = "shpcut",
        help = "Use the shapefile to cut out points within the shapefile polygons.",
        action = "store_true"
    )
    parser.add_option(
        "-o", "--outh5",
        dest = "h5fname",
        help = "Mandatory output HDF5 file name.",
        metavar = "H5FILE"
    )
    parser.add_option(
        "-f", "--fields",
        dest = "fields",
        help = "Specify codes for extracting specific LAS fields. \n"\
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

    if not options.lasfname:
        parser.error("LAS file name not given.")
    if not os.path.isfile(options.lasfname):
        parser.error("Input LASFILE does not exist.")
    if not options.h5fname:
        parser.error("H5 file name not given.")
    if not options.fields:
        options.fields = "xyzrgb"

    # read and convert suff
    las2h5(
        options.lasfname,
        options.h5fname,
        shpfname = options.shpfname,
        shpcut = options.shpcut,
        x = 'x' in options.fields,
        y = 'y' in options.fields,
        z = 'z' in options.fields,
        red = 'r' in options.fields,
        green = 'g' in options.fields,
        blue = 'b' in options.fields,
        verbose = options.verbose
    )
