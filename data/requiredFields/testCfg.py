from configobj import ConfigObj
config = ConfigObj("requiredSchemaFields.dat")
#
print config['TRIM']

