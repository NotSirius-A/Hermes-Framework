class BaseField():
    """
    Base class for fields intended to be used with SQL databases
    """

    priority = 0

    def __init__(self, use_to_identify: bool=False, *args, **kwargs) -> None:

        if self.priority == None:
            raise NotImplementedError("`priority` attribute must be specified when creating new field class")
        elif not isinstance(self.priority, int):
            raise TypeError(f"`priority` attribute must be an int, not '{self.priority}'")


        if isinstance(use_to_identify, bool):
            self.use_to_identify = use_to_identify
        else:
            raise TypeError(f"`use_to_identify` argument must be a bool, not '{use_to_identify}'")


        self.str_representation = None

    def can_use_for_identification(self) -> bool:
        return self.use_to_identify

    def create_str_representation(self) -> str:
        """
        Create and return a string representation of the field
        """

        raise NotImplementedError()

    def get_field_as_string(self) -> str:
        """
        Returns str representation of the field so that it can be directly injected into SQL queries
        for example when creating tables

        Gives something like "name INTEGER NOT_NULL"
        """

        self.str_representation = self.create_str_representation()
        return self.str_representation

    def set_priority(self, priority: int=None):
        self.priority = int(priority)

    def get_priority(self) -> int:
        return self.priority

class SQLiteField(BaseField):
    data_type = None

    def __init__(self, name: str=None, null: bool=False, primary_key: bool=False, attrs: list=[], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if self.data_type == None:
            raise NotImplementedError("`data_type` attribute must be specified when creating new field class")
        elif not isinstance(self.data_type, str):
            raise TypeError(f"`data_type` attribute must be a string, not '{self.data_type}'")


        if isinstance(name, str):
            self.name = name
        else:
            raise TypeError(f"`name` argument must be a str, not '{name}'")


        if isinstance(null, bool):
            self.null = null
        else:
            raise TypeError(f"`null` argument must be a bool, not '{null}'")


        if isinstance(primary_key, bool):
            self.primary_key = primary_key
            if primary_key:
                self.priority += 1
        else:
            raise TypeError(f"`primary_key` argument must be a bool, not '{null}'")

        if len(attrs) == 0:
            self.attrs = attrs

        elif isinstance(attrs, list) and len(attrs) != 0:
            is_list_of_strings = all([isinstance(attr, str) for attr in attrs])
            if is_list_of_strings:
                self.attrs = attrs
                
        else:
            raise TypeError("`attrs` argument must be a list of string")


    def create_str_representation(self) -> str:

        rv = f"{self.name} {self.data_type}"

        if not self.null and not self.primary_key:
            rv += " NOT NULL "

        if self.primary_key:
            rv += " PRIMARY KEY AUTOINCREMENT "

        for attribute in self.attrs:
            rv += f" {attribute}"

        return rv


class IntegerFieldSQLite(SQLiteField):
    data_type = "INTEGER"

class TextFieldSQLite(SQLiteField):
    data_type = "TEXT"

class BoolFieldSQLite(SQLiteField):
    data_type = "BOOL"

class ConstraintField(BaseField):
    priority = -1

    def __init__(self, constraint: str=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if isinstance(constraint, str):
            self.constraint = constraint
        else:
            raise TypeError(f"`constrain` argument must be a str, not '{constraint}'")

    def create_str_representation(self) -> str:
        return self.constraint
