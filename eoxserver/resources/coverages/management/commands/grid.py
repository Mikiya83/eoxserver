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

from django.core.management.base import CommandError, BaseCommand
from django.db import transaction

from eoxserver.resources.coverages import models
from eoxserver.resources.coverages.management.commands import (
    CommandOutputMixIn, SubParserMixIn
)


class Command(CommandOutputMixIn, SubParserMixIn, BaseCommand):
    """ Command to manage grids. This command uses sub-commands for the
        specific tasks: create, delete
    """
    def add_arguments(self, parser):
        create_parser = self.add_subparser(parser, 'create')
        delete_parser = self.add_subparser(parser, 'delete')
        list_parser = self.add_subparser(parser, 'list')

        for parser in [create_parser, delete_parser]:
            parser.add_argument(
                'name', nargs=1, help='The grid name'
            )

        create_parser.add_argument(
            'coordinate_reference_system', nargs=1,
            help=(
                'The definition of the coordinate reference system. Either '
                'an integer (the EPSG code), or the URL, WKT or XML definiton.'
            )
        )

        create_parser.add_argument(
            '--name', '--axis-name', '-n', dest='axis_names', default=[],
            action='append',
            help=(
                'The name of one axis. Must be passed at least once and up to '
                'four times.'
            )
        )
        create_parser.add_argument(
            '--type', '--axis-type', '-t', dest='axis_types', default=[],
            action='append',
            choices=[choice[1] for choice in models.Grid.AXIS_TYPES],
            help=(
                'The type of one axis. Must be passed at least once and up to '
                'four times.'
            )
        )
        create_parser.add_argument(
            '--reference-type', '--axis-reference-type', '-r',
            dest='axis_reference_types', default=[],
            action='append',
            choices=[choice[1] for choice in models.Grid.AXIS_REFERENCE_TYPES],
            help=(
                'The reference type of one axis. Must be passed at least once '
                'and up to four times.'
            )
        )
        create_parser.add_argument(
            '--offset', '--axis-offset', '-o', dest='axis_offsets', default=[],
            action='append',
            help=(
                'The offset for one axis. Must be passed at least once and up '
                'to four times.'
            )
        )
        create_parser.add_argument(
            '--replace', action='store_true', default=False,
            help=(
                'Replace the previous grid of the same name.'
            )
        )

        delete_parser.add_argument(
            '--force', '-f', action='store_true', default=False,
        )

    @transaction.atomic
    def handle(self, subcommand, *args, **kwargs):
        """ Dispatch sub-commands: create, delete, list.
        """
        if subcommand == "create":
            self.handle_create(kwargs.pop('name')[0], *args, **kwargs)
        elif subcommand == "delete":
            self.handle_delete(kwargs.pop('name')[0], *args, **kwargs)
        elif subcommand == "list":
            self.handle_list(*args, **kwargs)

    def handle_create(self, name, coordinate_reference_system, **kwargs):
        """ Handle the creation of a new product
        """
        axis_names = kwargs['axis_names']
        axis_types = kwargs['axis_types']
        axis_offsets = kwargs['axis_offsets']

        if not axis_names:
            raise CommandError('Must supply at least one axis definition.')

        if len(axis_types) != len(axis_names):
            raise CommandError(
                'Invalid number of axis-types supplied. Expected %d, got %d.'
                % (len(axis_names), len(axis_types))
            )
        if axis_offsets and len(axis_offsets) != len(axis_names):
            raise CommandError(
                'Invalid number of axis-offsets supplied. Expected %d, got %d.'
                % (len(axis_names), len(axis_offsets))
            )

        if len(axis_names) > 4:
            raise CommandError('Currently only at most four axes are supported.')

        type_name_to_id = dict(
            (name, id_) for id_, name in models.Grid.AXIS_TYPES
        )

        axis_offsets = axis_offsets or [None] * len(axis_types)

        iterator = enumerate(zip(axis_names, axis_types, axis_offsets), start=1)
        definition = {
            'name': name,
            'coordinate_reference_system': coordinate_reference_system[0]
        }
        for i, (axis_name, type_, offset) in iterator:
            definition['axis_%d_name' % i] = axis_name
            definition['axis_%d_type' % i] = type_name_to_id[type_]
            definition['axis_%d_offset' % i] = offset

        if kwargs['replace']:
            try:
                old_grid = models.Grid.objects.get(name=name)
                self.print_msg("Replacing grid '%s'" % name)

                collections = models.Collection.objects.filter(grid=old_grid)
                collections.update(grid=None)

                mosaics = models.Mosaic.objects.filter(grid=old_grid)
                mosaics.update(grid=None)

                coverages = models.Coverage.objects.filter(grid=old_grid)
                coverages.update(grid=None)

                old_grid.delete()

            except models.Grid.DoesNotExist:
                kwargs['replace'] = False

        grid = models.Grid(**definition)
        grid.full_clean()
        grid.save()
        self.print_msg("Successfully %s grid '%s'" % (
            'replaced' if kwargs['replace'] else 'created', name
        ))

        # reset the grid to the new one, when replacing
        if kwargs['replace']:
            collections.update(grid=grid)
            mosaics.update(grid=grid)
            coverages.update(grid=grid)

    def handle_delete(self, name, force, **kwargs):
        """ Handle the deregistration a product
        """
        try:
            grid = models.Grid.objects.get(name=name)
            if force:
                models.Collection.objects.filter(grid=grid).delete()
                models.Mosaic.objects.filter(grid=grid).delete()
                models.Coverage.objects.filter(grid=grid).delete()

            self.print_msg("Successfully deleted grid '%s'" % name)
        except models.Grid.DoesNotExist:
            raise CommandError('No such Grid %r' % name)

    def handle_list(self, **kwargs):
        for grid in models.Grid.objects.all():
            print(str(grid))
