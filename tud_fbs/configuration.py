#!/usr/bin/env false
import datetime
import re

import jinja2
import yaml


class FbsConfig():
    # TODO: replace by string, so that we to not have to read data from filesystem over and over again
    __tuple_re = re.compile(r"\s*\((?P<posx>[0-9]+)\s*,\s*(?P<posy>[0-9]+)\s*\)")
    def __init__(self, thesis_config='../thesis.yml', base_config='../config.yml'):
        with open(thesis_config) as thesis_fh:
            self.data = yaml.load(thesis_fh, Loader=yaml.FullLoader)

        with open(base_config) as thesis_fh:
            self.config = yaml.load(thesis_fh, Loader=yaml.FullLoader)

        self.append_degree_info()
        self.append_dates()

    def append_degree_info(self):
        self.data['thesis']['studies'] = self.config['degrees'][self.data['thesis']['degree']]['studies']
        self.data['thesis']['type'] = self.config['degrees'][self.data['thesis']['degree']]['type']

    def append_dates(self):
        # compute dates
        weeks = self.config['degrees'][self.data['thesis']['degree']]['duration']
        start = datetime.datetime.strptime(self.data['thesis']['start'], "%Y-%m-%d")
        diff = datetime.timedelta(days=7 * weeks)
        end = start + diff
        self.data['thesis']['start'] = {}
        self.data['thesis']['start']['daymonth'] = start.strftime("%b %d")
        self.data['thesis']['start']['year'] = start.strftime("%y")
        self.data['thesis']['end'] = {}
        self.data['thesis']['end']['daymonth'] = end.strftime("%b %d")
        self.data['thesis']['end']['year'] = end.strftime("%y")

    def get_filling_data(self):
        # little bit of a crapy approach, but who cares it's just a simple script here
        fillme = self.config['degrees'][self.data['thesis']['degree']]['filling']['values']
        for item, value in fillme.items():
            if isinstance(value, str):
                template = jinja2.Template(value)
                fillme[item] = template.render(self.data)
            elif isinstance(value, dict):
                if 'value' in value:
                    template = jinja2.Template(value['value'])
                    try:
                        fillme[item]['value'] = template.render(self.data)
                    except jinja2.exceptions.UndefinedError as e:
                        print(f"Some Value was missing for key: {item} / {value['value']}. Detailed Message follows.")
                        print(e)
                if 'abs' in value:
                    m = self.__tuple_re.match(value['abs'])
                    if m:
                        fillme[item]['abs'] = (int(m.group("posx")), int(m.group("posy")))
                if 'offset' in value:
                    m = self.__tuple_re.match(value['offset'])
                    if m:
                        fillme[item]['offset'] = (int(m.group("posx")), int(m.group("posy")))
            else:
                raise NotImplementedError("Not Implemented.")
        return fillme
