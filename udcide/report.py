import json
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Crime:
    description: str
    sequences: Tuple[str]

    @staticmethod
    def _parseCrime(json_obj):
        description = json_obj['crime']
        parents = list()
        for seq in json_obj['sequence']:
            parents.append(list(seq.keys()).pop())

        return Crime(description, tuple(parents))


@dataclass(frozen=True)
class Report:
    md5: str
    apk_filename: str
    threat_level: str
    crimes: Tuple[Crime]

    @staticmethod
    def parse_report(report_path):
        with open(report_path, 'r') as file:

            json_obj = json.load(file)

            return Report(json_obj.get('md5'),
                          json_obj.get('apk_filename'),
                          json_obj.get('threat_level'),
                          tuple([Crime._parseCrime(crime) for crime in json_obj['crimes']
                                 if crime['confidence'] == '100%'])
                          )
