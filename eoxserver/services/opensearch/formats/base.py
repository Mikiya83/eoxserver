# ------------------------------------------------------------------------------
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#
# ------------------------------------------------------------------------------
# Copyright (C) 2015 EOX IT Services GmbH
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


import uuid

from django.http import QueryDict
from lxml.builder import ElementMaker
from django.core.urlresolvers import reverse

from eoxserver.contrib import ogr, vsi
from eoxserver.core.util.timetools import isoformat
from eoxserver.core.util.xmltools import NameSpace, NameSpaceMap
from eoxserver.resources.coverages import models
from eoxserver.services.gml.v32.encoders import GML32Encoder


class BaseOGRResultFormat(object):
    """ Base ckass for result formats using OGR for encoding the records.
    """
    abstract = True

    driver_name = None
    extension = None

    def encode(self, request, collection_id, queryset, search_context):
        """ Encode a query set as an OGR datasource and retrieve its contents.
        """
        # create a datasource and its fields
        driver = self.get_driver()
        filename = self.get_filename()
        ds = self.create_datasource(driver, filename)
        layer = self.create_layer(ds)
        self.create_fields(layer)
        definition = layer.GetLayerDefn()

        # encode the objects
        for eo_object in queryset:
            feature = self.create_feature(layer, definition)
            self.set_feature_values(feature, eo_object)
            layer.CreateFeature(feature)

        # close datasource and read contents
        ds.Destroy()

        with vsi.open(filename) as f:
            content = f.read()

        # perform cleanup and return content + mimetype
        self.cleanup(driver, ds, filename)
        return content

    def get_driver(self):
        """ Get the OGR driver.
        """
        return ogr.GetDriverByName(self.driver_name)

    def get_filename(self):
        """ Get the filename for the temporary file.
        """
        return "/vsimem/%s%s" % (uuid.uuid4().hex, self.extension)

    def create_datasource(self, driver, filename):
        """ Create the OGR DataSource. This needs to be overriden in formats
            that require certain creation options.
        """
        return driver.CreateDataSource(filename)

    def create_layer(self, datasource):
        """ Create the layer in the DataSource.
        """
        return datasource.CreateLayer("layer", geom_type=ogr.wkbMultiPolygon)

    def create_fields(self, layer):
        """ Create the field definitions of the layer. By default, it contains
            definitions of the `id`, `begin_time` and `end_time` fields. For
            certain formats, this needs to be overridden.
        """
        layer.CreateField(ogr.FieldDefn("id", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("begin_time", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("end_time", ogr.OFTString))

    def create_feature(self, layer, definition):
        """ Create a feature from the given definition.
        """
        return ogr.Feature(definition)

    def set_feature_values(self, feature, eo_object):
        """ Set the values and the geometry of the feature. This needs to be
            inline with the :meth:`create_fields` method.
        """
        feature.SetGeometry(
            ogr.CreateGeometryFromWkb(str(eo_object.footprint.wkb))
        )
        feature.SetField("id", eo_object.identifier.encode("utf-8"))
        feature.SetField("begin_time", isoformat(eo_object.begin_time))
        feature.SetField("end_time", isoformat(eo_object.end_time))

    def cleanup(self, driver, datasource, filename):
        """ Perform any necessary cleanup steps, like removing the temporary
            file.
        """
        driver.DeleteDataSource(filename)


ns_atom = NameSpace("http://www.w3.org/2005/Atom", "atom")
ns_opensearch = NameSpace("http://a9.com/-/spec/opensearch/1.1/", "opensearch")
ns_dc = NameSpace("http://purl.org/dc/elements/1.1/", "dc")
ns_georss = NameSpace("http://www.georss.org/georss", "georss")
ns_media = NameSpace("http://search.yahoo.com/mrss/", "media")
ns_owc = NameSpace("http://www.opengis.net/owc/1.0", "owc")

nsmap = NameSpaceMap(ns_atom, ns_dc, ns_georss, ns_media, ns_owc)

ATOM = ElementMaker(namespace=ns_atom.uri)
OS = ElementMaker(namespace=ns_opensearch.uri)
DC = ElementMaker(namespace=ns_dc.uri, nsmap=nsmap)
GEORSS = ElementMaker(namespace=ns_georss.uri, nsmap=nsmap)
MEDIA = ElementMaker(namespace=ns_media.uri, nsmap=nsmap)
OWC = ElementMaker(namespace=ns_owc.uri, nsmap=nsmap)


class BaseFeedResultFormat(object):
    """ Abstract base component for feed result formats like RSS and atom. Adds
    functionality to encode the paging mechanisms by using ``atom:link``s.
    """
    abstract = True

    def encode_feed_links(self, request, search_context):
        sc = search_context
        qdict = QueryDict(request.GET.urlencode(), mutable=True)
        qdict.pop("startIndex", None)
        links = [
            ATOM("link",
                rel="search", type="application/opensearchdescription+xml",
                href=request.build_absolute_uri(
                    reverse("opensearch:description")
                )
            ),
            ATOM("link",
                rel="self", type=self.mimetype, href=request.build_absolute_uri()
            ),
            ATOM("link",
                rel="first", type=self.mimetype,
                href="%s?%s" % (
                    request.build_absolute_uri(request.path),
                    qdict.urlencode()
                )
            )
        ]

        # add link to last page
        qdict["startIndex"] = str(sc.page_count * (sc.page_size or sc.count))
        links.append(
            ATOM("link",
                rel="last", type=self.mimetype,
                href="%s?%s" % (
                    request.build_absolute_uri(request.path),
                    qdict.urlencode()
                )
            )
        )

        # if not already on the first page, include link to previous page
        if sc.current_page != 0:
            qdict["startIndex"] = str(max(0, sc.start_index - sc.page_size))
            links.append(
                ATOM("link",
                    rel="previous", type=self.mimetype,
                    href="%s?%s" % (
                        request.build_absolute_uri(request.path),
                        qdict.urlencode()
                    )
                )
            )

        # if not already on the last page, include link to next page
        if sc.start_index + sc.count < sc.total_count:
            qdict["startIndex"] = str(sc.start_index + sc.count)
            links.append(
                ATOM("link",
                    rel="next", type=self.mimetype,
                    href="%s?%s" % (
                        request.build_absolute_uri(request.path),
                        qdict.urlencode()
                    )
                )
            )
        return links

    def encode_opensearch_elements(self, search_context):
        return [
            OS("totalResults", str(search_context.total_count)),
            OS("startIndex", str(search_context.start_index or 0)),
            OS("itemsPerPage", str(search_context.count)),
            OS("Query", role="request", **dict(
                ("{%s}%s" % (search_context.namespaces[prefix], name), value)
                for prefix, params in search_context.parameters.items()
                for name, value in params.items()
            ))
        ]

    def encode_item_links(self, request, collection_id, item):
        links = []
        if isinstance(item, models.Collection):
            # add link to opensearch collection search
            links.append(
                ATOM("link",
                    rel="search", href=self._create_self_link(
                        request, collection_id, item
                    )
                )
            )
            # TODO: link to WMS (GetCapabilities)

        if isinstance(item, models.Product):
            footprint = item.footprint
            if footprint:

                links.append(
                    ATOM("link", rel="enclosure",
                        href=self._create_dseo_download_link(item)
                    )
                )

                wms_get_capabilities = request.build_absolute_uri(
                    "%s?service=WMS&version=1.3.0&request=GetCapabilities"
                )

                wms_small = self._create_map_link(request, item, 100)
                wms_large = self._create_map_link(request, item, 500)

                # media RSS style links
                links.extend([
                    # "Browse" image
                    MEDIA("content",
                        MEDIA("category", "QUICKLOOK"),
                        url=wms_large
                    ),
                    # "Thumbnail" image
                    MEDIA("content",
                        MEDIA("category", "THUMBNAIL"),
                        url=wms_small
                    ),
                ])

                links.extend([
                    OWC("offering",
                        OWC("operation",
                            code="GetCapabilities", method="GET",
                            type="application/xml", href=wms_get_capabilities
                        ),
                        OWC("operation",
                            code="GetMap", method="GET",
                            type="image/png", href=wms_large
                        ),
                        code="http://www.opengis.net/spec/owc-atom/1.0/req/wms",
                    ),
                ])

                wcs_offering = OWC("offering",
                    OWC("operation",
                        code="GetCapabilities", method="GET",
                        type="application/xml", href=request.build_absolute_uri(
                            "%s?service=WCS&version=2.0.1"
                            "&request=GetCapabilities"
                        )
                    ),
                    code="http://www.opengis.net/spec/owc-atom/1.0/req/wcs",
                )
                for coverage in item.coverages.all():
                    wcs_offering.extend(self.encode_coverage_offerings(
                        request, coverage
                    ))

                links.append(wcs_offering)

        if isinstance(item, models.Coverage):
            # add a link for a Describe and GetCoverage request for
            # metadata and data download

            wcs_get_capabilities = request.build_absolute_uri(
                "%s?service=WCS&version=2.0.1&request=GetCapabilities"
            )

            links.extend([
                ATOM("link", rel="enclosure",
                    href=self._create_coverage_link(
                        request, coverage
                    )
                ),
                ATOM("link", rel="via",
                    href=self._create_coverage_description_link(
                        request, coverage
                    )
                ),
                # "Browse" image
                # ATOM("link", rel="icon", href=wms_large),
            ])

            # OWC offerings for WCS
            links.extend([
                OWC("offering",
                    OWC("operation",
                        code="GetCapabilities", method="GET",
                        type="application/xml", href=wcs_get_capabilities
                    ),
                    *self.encode_coverage_offerings(request, item),
                    **{
                        "code": "http://www.opengis.net/spec/owc-atom/1.0/req/wcs"
                    }
                )
            ])
        return links

    def encode_summary(self, request, collection_id, item):
        pass

    def encode_coverage_offerings(self, request, coverage):
        return [
            OWC("operation",
                code="DescribeCoverage", method="GET",
                type="application/xml",
                href=self._create_coverage_description_link(request, coverage)
            ),
            OWC("operation",
                code="GetCoverage", method="GET",
                type="image/tiff", href=self._create_coverage_link(
                    request, coverage
                )
            )
        ]

    def encode_spatio_temporal(self, item):
        entries = []
        if item.footprint:
            extent = item.footprint.extent
            entries.append(
                GEORSS("box",
                    "%f %f %f %f" % (extent[1], extent[0], extent[3], extent[2])
                )
            )
            entries.append(
                GEORSS("where",
                    GML32Encoder().encode_multi_surface(
                        item.footprint, item.identifier
                    )
                )
            )

        begin_time = item.begin_time
        end_time = item.end_time
        if begin_time and end_time:
            if begin_time != end_time:
                entries.append(
                    DC("date", "%s/%s" % (
                        isoformat(begin_time), isoformat(end_time)
                    ))
                )
            else:
                entries.append(DC("date", isoformat(begin_time)))

        return entries

    def _create_map_link(self, request, item, size):
        footprint = item.footprint
        minx, miny, maxx, maxy = footprint.extent

        fx = 1.0
        fy = 1.0

        if (maxx - minx) > (maxy - miny):
            fy = (maxy - miny) / (maxx - minx)
        else:
            fx = (maxx - minx) / (maxy - miny)

        return request.build_absolute_uri(
            "%s?service=WMS&version=1.3.0&request=GetMap"
            "&layers=%s&format=image/png&TRANSPARENT=true"
            "&width=%d&height=%d&CRS=EPSG:4326&STYLES="
            "&BBOX=%f,%f,%f,%f"
            "" % (
                reverse("ows"), item.identifier,
                int(size * fx), int(size * fy),
                miny, minx, maxy, maxx
            )
        )

    def _create_coverage_link(self, request, coverage):
        return request.build_absolute_uri(
            "%s?service=WCS&version=2.0.1&request=GetCoverage"
            "&coverageId=%s" % (reverse("ows"), coverage.identifier)
        )

    def _create_coverage_description_link(self, request, coverage):
        return request.build_absolute_uri(
            "%s?service=WCS&version=2.0.1&request=DescribeCoverage"
            "&coverageId=%s" % (reverse("ows"), coverage.identifier)
        )

    def _create_eo_coverage_set_description(self, request, eo_object):
        return request.build_absolute_uri(
            "%s?service=WCS&version=2.0.1&request=DescribeEOCoverageSet"
            "&eoId=%s" % (reverse("ows"), eo_object.identifier)
        )

    def _create_self_link(self, request, collection_id, item, format=None):
        if collection_id is None:

            return "%s?uid=%s" % (
                request.build_absolute_uri(
                    reverse("opensearch:search", kwargs={
                        "format_name": format if format else self.name
                    })
                ), item.identifier
            )

        return "%s?uid=%s" % (
            request.build_absolute_uri(
                reverse("opensearch:collection:search", kwargs={
                    "collection_id": collection_id,
                    "format_name": format if format else self.name
                })
            ), item.identifier
        )

    def _create_dseo_download_link(self, request, product):
        return request.build_absolute_uri(
            "%s?service=DSEO&version=1.0.0&request=GetProduct&ProductURI%s" % (
                reverse("ows"), product.identifier
            )
        )
