import enum


class DatabaseVendor(str, enum.Enum):

    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
