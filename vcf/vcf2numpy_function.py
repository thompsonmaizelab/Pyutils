import cyvcf2
import numpy

def vcf2numpy(
    filename,
    return_mat = True,
    return_taxa = True,
    return_vrnt_chrgrp = True,
    return_vrnt_phypos = True,
    return_vrnt_name = True
):
    """
    Extract information from a vcf file.

    Parameters
    ----------
    filename : str
        String indicating VCF file name.
    return_mat : bool
        Whether to return the genotype matrix. The genotype matrix is formatted
        as (m x n x p) where m is the number of chromosome phases (2, diploid
        for almost all cases), n is the number of taxa/individuals, p is the
        number of genomic markers/variants.
    return_taxa : bool
        Whether to return the taxa/individual name array.
    return_vrnt_chrgrp : bool
        Whether to return the variant chromosome number array. This is the
        chromosome number the marker/variant is assigned.
    return_vrnt_phypos : bool
        Whether to return the variant chromosome physical position array. This
        is the physical position on the assigned chromosome for the
        marker/variant.
    return_vrnt_name : bool
        Whether to return the variant name array.

    Returns
    -------
    out : dict
        A dictionary containing the desired data types. Possible fields are:
            Field         | Data type     | Description
            --------------|---------------|----------------
            "mat"         | numpy.int8    | genotype matrix
            "taxa"        | numpy.object_ | taxa/individual name array
            "vrnt_chrgrp" | numpy.int64   | variant chromosome number array
            "vrnt_phypos" | numpy.int64   | variant chromosome physical position array
            "vrnt_name"   | numpy.object_ | variant name array
    """
    # make VCF iterator
    vcf = cyvcf2.VCF(fname)

    # extract taxa names from vcf header
    taxa = vcf.samples

    # make empty lists to store extracted values
    mat = []
    vrnt_chrgrp = []
    vrnt_phypos = []
    vrnt_name = []

    # iterate through VCF file and accumulate variants
    for variant in vcf:
        if return_vrnt_chrgrp:
            # append chromosome integer
            vrnt_chrgrp.append(int(variant.CHROM))

        if return_vrnt_phypos:
            # append variant position coordinates
            vrnt_phypos.append(variant.POS)

        if return_vrnt_name:
            # append marker name
            vrnt_name.append(str(variant.ID))

        if return_mat:
            # extract allele states + whether they are phased or not
            phases = numpy.int8(variant.genotypes)

            # append genotype states
            mat.append(phases[:,0:2].copy())

    # construct a dictionary of values
    out_dict = {}

    if return_mat:
        out_dict["mat"] = numpy.int8(mat).transpose(2,1,0)  # convert and transpose genotype matrix
    if return_taxa:
        out_dict["taxa"] = numpy.object_(taxa)              # convert to object array
    if return_vrnt_chrgrp:
        out_dict["vrnt_chrgrp"] = numpy.int64(vrnt_chrgrp)  # convert to int64 array
    if return_vrnt_phypos:
        out_dict["vrnt_phypos"] = numpy.int64(vrnt_phypos)  # convert to int64 array
    if return_vrnt_name:
        out_dict["vrnt_name"] = numpy.object_(vrnt_name)    # convert to object array

    # return output dictionary
    return out_dict
