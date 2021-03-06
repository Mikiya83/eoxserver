# ------------------------------------------------------------------------------
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#
# ------------------------------------------------------------------------------
# Copyright (C) 2017 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ------------------------------------------------------------------------------

from uuid import uuid4
import ast
import _ast
import operator

import numpy as np

from eoxserver.contrib import vrt, gdal, osr


class BrowseGenerationError(Exception):
    pass


class BrowseGenerator(object):
    def __init__(self, footprint_alpha=True, ):
        pass

    def generate(self, product, browse_type, style, out_filename):
        if not product.product_type or \
                not product.product_type == browse_type.product_type:
            raise BrowseGenerationError("Product and browse type don't match")


class FilenameGenerator(object):
    """ Utility class to generate filenames after a certain pattern (template)
        and to keep a list for later cleanup.
    """
    def __init__(self, template, default_extension=None):
        """ Create a new :class:`FilenameGenerator` from a given template
            :param template: the template string used to construct the filenames
                             from. Uses the ``.format()`` style language. Keys
                             are ``index``, ``uuid`` and ``extension``.
        """
        self._template = template
        self._filenames = []
        self._default_extension = default_extension

    def generate(self, extension=None):
        """ Generate and store a new filename using the specified template. An
            optional ``extension`` can be passed, when used in the template.
        """
        filename = self._template.format(
            index=len(self._filenames),
            uuid=uuid4().hex,
            extension=extension or self._default_extension,
        )
        self._filenames.append(filename)
        return filename

    @property
    def filenames(self):
        """ Get a list of all generated filenames.
        """
        return self._filenames


class BandExpressionError(ValueError):
    pass


ALLOWED_NODE_TYPES = (
    _ast.Module,
    _ast.Expr,
    _ast.Load,
    _ast.Name,

    _ast.UnaryOp,
    _ast.BinOp,

    _ast.Mult,
    _ast.Div,
    _ast.Add,
    _ast.Sub,
    _ast.Num,

    _ast.BitAnd,
    _ast.BitOr,
    _ast.BitXor,

    _ast.USub,
)


def parse_expression(band_expression):
    """ Parse and validate the passed band expression
    """
    parsed = ast.parse(band_expression)
    for node in ast.walk(parsed):
        if not isinstance(node, ALLOWED_NODE_TYPES):
            raise BandExpressionError(
                'Invalid expression: %s' % type(node).__name__
            )
    return parsed.body[0].value


def extract_fields(band_expression):
    """ Extract the fields required to generate the output band.
        :param band_expression: the band expression to extract the fields of
        :type band_expression: str
        :return: a list of field names
        :rtype: list
    """
    if isinstance(band_expression, basestring):
        root_expr = parse_expression(band_expression)
    else:
        root_expr = band_expression
    return [
        node.id
        for node in ast.walk(root_expr)
        if isinstance(node, _ast.Name)
    ]


class BrowseCreationInfo(object):
    def __init__(self, filename, env, bands=None):
        self.filename = filename
        self.env = env
        self.bands = bands


# make shortcut: if all relevant bands are in one dataset, we
# will only return that and give the band numbers
def single_file_and_indices(band_expressions, fields_and_coverages):
    band_indices = []
    filenames = set()
    env = None
    for band_expression in band_expressions:
        fields = extract_fields(band_expression)
        if len(fields) != 1:
            return None, None, None

        field = fields[0]

        coverages = fields_and_coverages[field]
        # break early if we are dealing with more than one coverage
        if len(coverages) != 1:
            return None, None, None

        coverage = coverages[0]
        location = coverage.get_location_for_field(field)

        filenames.add(location.path)
        band_indices.append(
            coverage.get_band_index_for_field(field)
        )
        env = location.env

    if len(filenames) == 1:
        return filenames.pop(), env, band_indices

    return None, None, None


def generate_browse(band_expressions, fields_and_coverages,
                    width, height, bbox, crs, generator=None):
    """ Produce a temporary VRT file describing how transformation of the
        coverages to browses.

        :param band_exressions: the band expressions for the various bands
        :param fields_and_coverages: a dictionary mapping the field names to all
                                     coverages with that field
        :param: band_expressiosn: list of strings
        :type fields_and_coverages: dict
        :return: A tuple of the filename of the output file and the generator
                 which was used to generate the filenames.
                 In most cases this is the filename refers to a generated VRT
                 file in very simple cases the file might actually refer to an
                 original file.
        :rtype: tuple
    """
    generator = generator or FilenameGenerator('/vsimem/{uuid}.vrt')

    out_band_filenames = []

    parsed_expressions = [
        parse_expression(band_expression)
        for band_expression in band_expressions
    ]

    is_simple = all(isinstance(expr, _ast.Name) for expr in parsed_expressions)

    if not is_simple:
        return _generate_browse_complex(
            parsed_expressions, fields_and_coverages,
            width, height, bbox, crs, generator
        ), generator, True

    single_filename, env, bands = single_file_and_indices(
        band_expressions, fields_and_coverages
    )

    # for single files, we make a shortcut and just return it and the used
    # bands
    if single_filename:
        return (
            BrowseCreationInfo(single_filename, env, bands),
            generator, False
        )

    # iterate over the input band expressions
    for band_expression in band_expressions:
        fields = extract_fields(band_expression)

        selected_filenames = []

        # iterate over all fields that the output band shall be comprised of
        for field in fields:
            coverages = fields_and_coverages[field]

            # iterate over all coverages for that field to select the single
            # field
            for coverage in coverages:
                location = coverage.get_location_for_field(field)
                orig_filename = location.path
                orig_band_index = coverage.get_band_index_for_field(field)

                # only make a VRT to select the band if band count for the
                # dataset > 1
                if location.field_count == 1:
                    selected_filename = orig_filename
                else:
                    selected_filename = generator.generate()
                    vrt.select_bands(
                        orig_filename, location.env,
                        [orig_band_index], selected_filename
                    )

                selected_filenames.append(selected_filename)

        # if only a single file is required to generate the output band, return
        # it.
        if len(selected_filenames) == 1:
            out_band_filename = selected_filenames[0]

        # otherwise mosaic all the input bands to form a composite image
        else:
            out_band_filename = generator.generate()
            vrt.mosaic(selected_filenames, out_band_filename)

        out_band_filenames.append(out_band_filename)

    # make shortcut here, when we only have one band, just return it
    if len(out_band_filenames) == 1:
        return (
            BrowseCreationInfo(out_band_filenames[0], None), generator, False
        )

    # return the stacked bands as a VRT
    else:
        stacked_filename = generator.generate()
        vrt.stack_bands(out_band_filenames, stacked_filename)
        return (
            BrowseCreationInfo(stacked_filename, None), generator, False
        )


def _generate_browse_complex(parsed_expressions, fields_and_coverages,
                             width, height, bbox, crs, generator):
    o_x = bbox[0]
    o_y = bbox[3]
    res_x = (bbox[2] - bbox[0]) / width
    res_y = -(bbox[3] - bbox[1]) / height
    tiff_driver = gdal.GetDriverByName('GTiff')

    field_names = set()
    for parsed_expression in parsed_expressions:
        field_names |= set(extract_fields(parsed_expression))

    fields_and_datasets = {}
    for field_name in field_names:
        coverages = fields_and_coverages[field_name]

        selected_filenames = []

        # iterate over all coverages for that field to select the single
        # field
        for coverage in coverages:
            location = coverage.get_location_for_field(field_name)
            orig_filename = location.path
            orig_band_index = coverage.get_band_index_for_field(field_name)

            # only make a VRT to select the band if band count for the
            # dataset > 1
            if location.field_count == 1:
                selected_filename = orig_filename
            else:
                selected_filename = generator.generate()
                vrt.select_bands(
                    orig_filename, location.env,
                    [orig_band_index], selected_filename
                )

            selected_filenames.append(selected_filename)

        # if only a single file is required to generate the output band, return
        # it.
        if len(selected_filenames) == 1:
            out_field_filename = selected_filenames[0]
            out_field_dataset = gdal.OpenShared(out_field_filename)

        # otherwise mosaic all the input bands to form a composite image
        else:
            out_field_filename = generator.generate()
            out_field_dataset = vrt.mosaic(
                selected_filenames, out_field_filename
            )

        warped_out_field_dataset = tiff_driver.Create(
            generator.generate('tif'), width, height, 1,
            # out_field_dataset.GetRasterBand(1).DataType,
            gdal.GDT_Float32,
            options=[
                "TILED=YES",
                "COMPRESS=PACKBITS"
            ]
        )

        warped_out_field_dataset.SetGeoTransform([o_x, res_x, 0, o_y, 0, res_y])
        warped_out_field_dataset.SetProjection(osr.SpatialReference(crs).wkt)
        gdal.ReprojectImage(out_field_dataset, warped_out_field_dataset)

        fields_and_datasets[field_name] = warped_out_field_dataset.GetRasterBand(1).ReadAsArray()

    out_filename = generator.generate('tif')
    tiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = tiff_driver.Create(
        out_filename,
        width, height, len(parsed_expressions),
        gdal.GDT_Float32,
        options=[
            "TILED=YES",
            "COMPRESS=PACKBITS"
        ]
    )
    out_ds.SetGeoTransform([o_x, res_x, 0, o_y, 0, res_y])
    out_ds.SetProjection(osr.SpatialReference(crs).wkt)

    for band_index, parsed_expression in enumerate(parsed_expressions, start=1):
        with np.errstate(divide='ignore',invalid='ignore'):
            out_data = _evaluate_expression(
                parsed_expression, fields_and_datasets, generator
            )

        if isinstance(out_data, (int, float)):
            out_data = np.full((height, width), out_data)

        out_band = out_ds.GetRasterBand(band_index)
        out_band.WriteArray(out_data)

    return BrowseCreationInfo(out_filename, None)

operator_map = {
    _ast.Add: operator.add,
    _ast.Sub: operator.sub,
    _ast.Div: operator.truediv,
    _ast.Mult: operator.mul,
}


def _evaluate_expression(expr, fields_and_datasets, generator):
    if isinstance(expr, _ast.Name):
        return fields_and_datasets[expr.id] # .GetRasterBand(1).ReadAsArray()

    elif isinstance(expr, _ast.BinOp):
        left_data = _evaluate_expression(
            expr.left, fields_and_datasets, generator
        )

        right_data = _evaluate_expression(
            expr.right, fields_and_datasets, generator
        )

        op = operator_map[type(expr.op)]
        return op(left_data, right_data)

    elif isinstance(expr, _ast.Num):
        return expr.n
