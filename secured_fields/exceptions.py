class DatabaseBackendNotSupported(Exception):
    pass


class LookupNotSupported(Exception):
    def __init__(self, field_type_name: str, lookup_name: str):
        super().__init__(f'Lookup `{lookup_name}` for field type `{field_type_name}` is not supported.')
