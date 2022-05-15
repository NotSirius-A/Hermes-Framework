from hermes.core.fields import BaseField, SQLiteField

class BaseTable:
    def __init__(self, name: str=None, fields: list=None) -> None:
        
        if isinstance(name, str):
            self.name = name
        else:
            raise TypeError(f"`name` argument must be a str, not '{name}'")


        if isinstance(fields, list):
    
            is_list_of_fields = all([isinstance(field, BaseField) for field in fields])
            if is_list_of_fields:
                self.fields = fields

        elif len(fields) == 0:
            self.fields = fields
        else:
            raise TypeError("`fields` argument must be a list of fields")

    def add_field(self, field):
        if isinstance(field, BaseField):
            self.fields.append(field)
        else:
            raise TypeError("`field` argument must be a field object")

    def get_ordered_fields(self) -> list:
        ordered_fields = sorted(self.fields, key=lambda x: x.get_priority(), reverse=True)

        return ordered_fields

    def get_fields(self) -> list:
        return self.get_ordered_fields()

    def get_identification_fields(self) -> list:
        rv = [field for field in self.get_fields() if field.can_use_for_identification()]
        return rv

    def get_primary_key_field(self) -> SQLiteField:
        rv = [field for field in self.get_fields() if field.primary_key]
        return rv[0]

    def get_fields_by_priority(self, priority: int=None) -> list:
        if isinstance(priority, int):
            self.priority = priority
        else:
            raise TypeError(f"`priority` argument must be an int, not '{priority}'")

        rv = [field for field in self.get_fields() if field.get_priority() == priority]
        return rv

class SimpleTable(BaseTable):
    pass