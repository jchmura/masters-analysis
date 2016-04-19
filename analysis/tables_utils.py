import re
from collections import defaultdict

import tables


class Columns:
    layer_pattern = re.compile(r'(?P<type>[IOT]T)(?P<layer>[\dab])(?P<rest>.+)')

    def __init__(self, file_path, table_name):
        self.file_path = file_path
        self.table_name = table_name
        self.columns = self._get_columns()

    @property
    def tt_layers(self):
        return [column for column in self.columns if column.startswith('TT')]

    @property
    def it_layers(self):
        return [column for column in self.columns if column.startswith('IT')]

    @property
    def ot_layers(self):
        return [column for column in self.columns if column.startswith('OT')]

    @property
    def t_stations_layers(self):
        return self.it_layers + self.ot_layers

    @property
    def layers(self):
        return self.t_stations_layers + self.tt_layers

    @property
    def layer_to_detector(self):
        return self._layer_to_category(self.group_by_detector(self.tt_layers + self.it_layers + self.ot_layers))

    @property
    def layer_to_station(self):
        return self._layer_to_category(self.group_by_station(self.tt_layers + self.it_layers + self.ot_layers))

    @property
    def layer_to_position(self):
        return self._layer_to_category(self.group_by_position(self.tt_layers + self.it_layers + self.ot_layers))

    @property
    def layer_to_subposition(self):
        return self._layer_to_category(self.group_by_subposition(self.tt_layers + self.it_layers + self.ot_layers))

    def group_by_station(self, layers):
        stations = defaultdict(list)
        for layer in layers:
            match = self.layer_pattern.match(layer)
            layer_type = match.group('type')
            layer_number = match.group('layer')
            stations[layer_type + layer_number].append(layer)
        return stations

    @staticmethod
    def group_by_detector(layers):
        detectors = defaultdict(list)
        for layer in layers:
            detector = 'TT' if layer.startswith('TT') else 'T-Station'
            detectors[detector].append(layer)
        return detectors

    def group_by_position(self, layers):
        positions = defaultdict(list)
        for layer in layers:
            match = self.layer_pattern.match(layer)
            layer_number = match.group('layer')
            if layer_number.isdigit():
                positions['T{}'.format(layer_number)].append(layer)
            else:
                positions['TT{}'.format(layer_number)].append(layer)
        return positions

    def group_by_subposition(self, layers):
        positions = defaultdict(list)
        for layer in layers:
            match = self.layer_pattern.match(layer)
            layer_number = match.group('layer')
            rest = match.group('rest')
            if layer_number.isdigit():
                positions['T{}{}'.format(layer_number, rest)].append(layer)
            else:
                positions['TT{}{}'.format(layer_number, rest)].append(layer)
        return positions

    @staticmethod
    def _layer_to_category(grouped):
        layer_to_category = {}
        for category, layers in grouped.items():
            for layer in layers:
                layer_to_category[layer] = category

        return layer_to_category

    def _get_columns(self):
        file = tables.open_file(self.file_path)
        table_name = self.table_name
        if not table_name.startswith('/'):
            table_name = '/{}'.format(table_name)
        table = file.get_node(table_name).table
        blocks = self._get_blocks(table)

        columns = []
        for block in blocks:
            columns += table._v_attrs['{}_kind'.format(block)]

        file.close()

        return list(sorted(columns))

    @staticmethod
    def _get_blocks(table):
        col_objects = table.description._v_colObjects
        blocks = []
        for col in sorted(col_objects.keys()):
            if col != 'index':
                blocks.append(col)

        return blocks


def group_by_type(df):
    tt_ts = (df['is_true_track'] == True) & (df['is_true_seed'] == True)
    gt_ts = (df['is_true_track'] == False) & (df['is_true_seed'] == True)
    gt_gs = (df['is_true_track'] == False) & (df['is_true_seed'] == False)

    df['type'] = ''
    df.loc[tt_ts, 'type'] = 'TT/TS'
    df.loc[gt_ts, 'type'] = 'GT/TS'
    df.loc[gt_gs, 'type'] = 'GT/GS'
