"""Parameter settings."""


class Parameter(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError(f'`{key}` is not a parameter key.')
        else:

            if key == 'write_to_file.duplicated_name_extension':
                if type(value) != str:
                    raise Exception(
                        '`write_to_file.duplicate` only accepts strings.')
                if value.strip() == '':
                    raise Exception(
                        'Empty string cannot serve as extension.')
                

            if key in ('write_to_file.replace', 'write_to_file.duplicate', 'points.ignore_missing_point'):
                if type(value) != bool:
                    raise Exception(
                        '`write_to_file.duplicate` only accepts True/False.')

            if key == 'write_to_file.duplicate' and value:
                super().__setitem__('write_to_file.replace', False)
                if self['write_to_file.duplicated_name_extension'] == '':
                    super().__setitem__('write_to_file.duplicated_name_extension', 'modified')

            if key == 'write_to_file.replace' and value:
                super().__setitem__('write_to_file.duplicate', False)
            
            if key == 'to_plot.package':
                if value == 'matplotlib':
                    super().__setitem__('to_plot.size', (15, 10))

                elif value == 'plotly':
                    super().__setitem__('to_plot.size', None)
                
                else:
                    raise Exception(
                        '`to_plot.package` only accepts `matplotlib` or `plotly` as parameter.')

            super().__setitem__(key, value)


parameters = Parameter(
    {
        'write_to_file.replace': False,
        'write_to_file.duplicate': False,
        'write_to_file.duplicated_name_extension': 'modified',
        'points.ignore_missing_point': False,
        'to_plot.package': 'matplotlib',
        'to_plot.size': (15, 10)
    }
)
