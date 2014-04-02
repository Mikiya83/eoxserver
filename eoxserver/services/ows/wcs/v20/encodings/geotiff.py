#-------------------------------------------------------------------------------
# $Id$
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2013 EOX IT Services GmbH
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
#-------------------------------------------------------------------------------


from eoxserver.core import Component, implements
from eoxserver.core.decoders import kvp, xml, upper, enum, value_range, boolean
from eoxserver.core.util.xmltools import NameSpace, NameSpaceMap
from eoxserver.services.ows.wcs.interfaces import EncodingExtensionInterface
from eoxserver.services.ows.wcs.v20.util import ns_wcs


class WCS20GeoTIFFEncodingExtension(Component):
    implements(EncodingExtensionInterface)

    def supports(self, frmt, options):
        return frmt.lower() == "image/tiff"

    def get_decoder(self, request):
        if request.method == "GET":
            return WCS20GeoTIFFEncodingExtensionKVPDecoder(request.GET)
        else:
            return WCS20GeoTIFFEncodingExtensionXMLDecoder(request.body)

    def get_encoding_params(self, request):
        decoder = self.get_decoder(request)

        params = {}

        return params


compression_enum = enum(
    ("None", "PackBits", "Huffman", "LZW", "JPEG", "Deflate")
)
predictor_enum = enum(("None", "Horizontal", "FloatingPoint"))
interleave_enum = enum(("Pixel", "Band"))


def parse_multiple_16(raw):
    value = int(raw)
    if value < 0:
        raise ValueError("Value must be a positive integer.")
    elif (raw % 16) != 0:
        raise ValueError("Value must be a multiple of 16.")
    return value


class WCS20GeoTIFFEncodingExtensionKVPDecoder(kvp.Decoder):
    compression = kvp.Parameter("geotiff:compression", num="?", type=compression_enum)
    jpeg_quality = kvp.Parameter("geotiff:jpeg_quality", num="?", type=value_range(1, 100, type=int))
    predictor   = kvp.Parameter("geotiff:predictor", num="?", type=predictor_enum)
    interleave  = kvp.Parameter("geotiff:interleave", num="?", type=interleave_enum)
    tiling      = kvp.Parameter("geotiff:tiling", num="?", type=boolean)
    tileheight  = kvp.Parameter("geotiff:tileheight", num="?", type=parse_multiple_16)
    tilewidth   = kvp.Parameter("geotiff:tilewidth", num="?", type=parse_multiple_16)


class WCS20GeoTIFFEncodingExtensionXMLDecoder(xml.Decoder):
    compression = xml.Parameter("wcs:Extension/geotiff:parameters/geotiff:compression/text()", num="?", type=compression_enum)
    jpeg_quality = xml.Parameter("wcs:Extension/geotiff:parameters/geotiff:jpeg_quality/text()", num="?", type=value_range(1, 100, type=int))
    predictor   = xml.Parameter("wcs:Extension/geotiff:parameters/geotiff:predictor/text()", num="?", type=predictor_enum)
    interleave  = xml.Parameter("wcs:Extension/geotiff:parameters/geotiff:interleave/text()", num="?", type=interleave_enum)
    tiling      = xml.Parameter("wcs:Extension/geotiff:parameters/geotiff:tiling/text()", num="?", type=boolean)
    tileheight  = xml.Parameter("wcs:Extension/geotiff:parameters/geotiff:tileheight/text()", num="?", type=parse_multiple_16)
    tilewidth   = xml.Parameter("wcs:Extension/geotiff:parameters/geotiff:tilewidth/text()", num="?", type=parse_multiple_16)

    namespaces = NameSpaceMap(
        ns_wcs, NameSpace("http://www.opengis.net/gmlcov/geotiff/1.0", "geotiff")
    )
