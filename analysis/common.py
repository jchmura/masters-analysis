from pathlib import Path


def find_data_dir():
    cur_dir = Path('.').resolve()
    data_dir = _find_data_in_dir(cur_dir)
    return data_dir


def get_data_path(name):
    data_dir = find_data_dir()
    data_path = data_dir / name
    if not data_path.exists():
        raise IOError('No data file named {}'.format(name))
    return str(data_path)


def _find_data_in_dir(path):
    for child in path.iterdir():
        if child.is_dir() and child.name == 'data' and _has_root_files(child):
            return child
    parent = path.parent
    if parent != Path.home():
        return _find_data_in_dir(parent)


def _has_root_files(path):
    for child in path.iterdir():
        if child.is_file() and child.name.endswith('.root'):
            return True
    return False
