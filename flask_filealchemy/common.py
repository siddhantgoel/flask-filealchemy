from collections.abc import Mapping, Sequence

from ruamel.yaml import YAML


def _fmt_log(message):
    return 'flask-filealchemy: {}'.format(message)


class LoadError(Exception):
    pass


def parse_yaml_file(file_):
    try:
        with file_.open() as fd:
            data = fd.read()

        values = YAML(typ='safe').load(data)

        if isinstance(values, Sequence):
            for value in values:
                if not isinstance(value, Mapping):
                    raise ValueError()
        elif not isinstance(values, Mapping):
            raise ValueError()
    except IOError:
        raise LoadError(_fmt_log('could not open {}'.format(file_)))
    except ValueError:
        raise LoadError(_fmt_log('{} contains invalid YAML'.format(file_)))
    else:
        return values
