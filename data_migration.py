import Exceptions
import version

def initial_migration(data):
    result = data.copy()
    result["__format_version__"] = 1
    return result

# These functions just have to migrate any format to any newer format.
# Then there will always be a path to the newest format, from any old
# format version.
migration_functions = {
    0 : initial_migration,
}

def migrate_old_data(data):
    while data['__format_version__'] < version.__format_version__:
        if data['__format_version__'] not in migration_functions:
            raise Exceptions.ChaidoError("Unknown file format version '" + str(data['__format_version__']))
        data = migration_functions[data['__format_version__']](data)
    return data

