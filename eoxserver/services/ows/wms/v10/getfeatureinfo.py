#-------------------------------------------------------------------------------
# $Id$
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2011 EOX IT Services GmbH
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

from itertools import chain

from eoxserver.core import Component, env, implements, UniqueExtensionPoint
from eoxserver.core.decoders import kvp, typelist, InvalidParameterException
from eoxserver.resources.coverages import models, crss
from eoxserver.services.subset import Subsets, Trim, Slice
from eoxserver.services.interfaces import (
    OWSServiceHandlerInterface, OWSGetServiceHandlerInterface
)
from eoxserver.services.ows.wms.util import (
    lookup_layers, parse_bbox
)
from eoxserver.services.ows.wms.interfaces import (
    WMSFeatureInfoRendererInterface
)

class WMS10GetFeatureInfoHandler(Component):
    implements(OWSServiceHandlerInterface)
    implements(OWSGetServiceHandlerInterface)

    renderer = UniqueExtensionPoint(WMSFeatureInfoRendererInterface)

    service = "WMS"
    versions = ("1.0", "1.0.0")
    request = "GetFeatureInfo"

    def handle(self, request):
        decoder = WMS10GetFeatureInfoDecoder(request.GET)

        bbox = decoder.bbox
        srs = decoder.srs
        layers = decoder.layers

        if not layers:
            raise InvalidParameterException("No layers specified", "layers")
    
        minx, miny, maxx, maxy = bbox

        subsets = Subsets((
            Trim("x", minx, maxx, srs),
            Trim("y", miny, maxy, srs),
        ))
        
        root_group = lookup_layers(layers, subsets)
        
        return self.renderer.render(
            root_group, request.GET.items()
        )


class WMS10GetFeatureInfoDecoder(kvp.Decoder):
    layers = kvp.Parameter(type=typelist(str, ","), num=1)
    styles = kvp.Parameter(num="?")
    bbox   = kvp.Parameter(type=parse_bbox, num=1)
    srs    = kvp.Parameter(num=1)
    width  = kvp.Parameter(num=1)
    height = kvp.Parameter(num=1)
    format = kvp.Parameter(num=1)