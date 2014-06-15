#-------------------------------------------------------------------------------
#
# WPS 1.0 execute response XML encoder
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#          Martin Paces <martin.paces@eox.at>
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

from django.utils.timezone import now
from eoxserver.core.util.timetools import isoformat
from eoxserver.services.ows.wps.v10.util import WPS

from eoxserver.services.ows.wps.parameters import (
    Parameter, LiteralData, ComplexData, BoundingBoxData,
    fix_parameter,
)

from .process_description import encode_process_brief
from .parameters import (
    encode_input_exec, encode_output_exec, encode_output_def
)
from .base import WPS10BaseXMLEncoder

from eoxserver.services.ows.wps.exceptions import InvalidOutputValueException

#-------------------------------------------------------------------------------

class WPS10ExecuteResponseXMLEncoder(WPS10BaseXMLEncoder):

    content_type = "application/xml"

    @staticmethod
    def encode_response(process, results, resp_form, inputs, raw_inputs):
        """Encode execute response (SUCCESS) including the output data."""
        status = WPS("ProcessSucceded")
        elem = _encode_common_response(process, status, inputs, raw_inputs, resp_form)

        outputs = []
        for result, prm, req in results.itervalues():
            outputs.append(_encode_output(result, prm, req))
        elem.append(WPS("ProcessOutputs", *outputs))

        return elem

    #@staticmethod
    #def encode_failure()

    #@staticmethod
    #def encode_progress()

    #@staticmethod
    #def encode_accepted()

#-------------------------------------------------------------------------------

def _encode_common_response(process, status_elem, inputs, raw_inputs, resp_doc):
    """Encode common execute response part shared by all specific responses."""
    elem = WPS("ExecuteResponse",
        encode_process_brief(process),
        WPS("Status", status_elem, creationTime=isoformat(now()))
    )

    if resp_doc.lineage:
        inputs_data = []
        for id_, prm in process.inputs:
            prm = fix_parameter(id_, prm)
            data = inputs.get(id_)
            rawinp = raw_inputs.get(prm.identifier)
            if rawinp is not None:
                inputs_data.append(_encode_input(data, prm, rawinp))
        elem.append(WPS("DataInputs", *inputs_data))

        outputs_def = []
        for id_, prm in process.outputs:
            prm = fix_parameter(id_, prm)
            outdef = resp_doc.get(prm.identifier)
            if outdef is not None:
                outputs_def.append(encode_output_def(outdef))
        elem.append(WPS("OutputDefinitions", *outputs_def))

    return elem

def _encode_input(data, prm, raw):
    elem = encode_input_exec(raw)
    if isinstance(prm, LiteralData):
        elem.append(WPS("Data", _encode_literal(data, prm, raw)))
    elif isinstance(prm, BoundingBoxData):
        elem.append(WPS("Data", _encode_bbox(data, prm, raw)))
    elif isinstance(prm, ComplexData):
        elem.append(WPS("Data", _encode_complex(data, prm, raw)))
    return elem

def _encode_output(data, prm, req):
    elem = encode_output_exec(Parameter(prm.identifier,
                        req.title or prm.title, req.abstract or prm.abstract))
    if isinstance(prm, LiteralData):
        elem.append(WPS("Data", _encode_literal(data, prm, req)))
    elif isinstance(prm, BoundingBoxData):
        elem.append(WPS("Data", _encode_bbox(data, prm, req)))
    elif isinstance(prm, ComplexData):
        elem.append(WPS("Data", _encode_complex(data, prm, req)))
    return elem

#def _encode_reference(ref):
#    pass

def _encode_literal(data, prm, req):
    attrib = {'dataType': prm.dtype.name}
    uom = req.uom or prm.default_uom
    if prm.uoms:
        attrib['uom'] = uom
    try:
        encoded_data = prm.encode(data, uom)
    except (ValueError, TypeError) as exc:
        raise InvalidOutputValueException(prm.identifier, exc)
    return WPS("LiteralData", encoded_data, **attrib)

def _encode_bbox(data, prm, req):
    #TODO: proper output encoding
    return WPS("BoundingBoxData")

def _encode_complex(data, prm, req):
    #TODO: proper output encoding
    return WPS("ComplexData")

