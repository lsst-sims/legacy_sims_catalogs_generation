import numpy
from collections import OrderedDict
from lsst.sims.catalogs.generation.db import CatalogDBObject

__all__ = ["CompoundCatalogDBObject"]

class CompoundCatalogDBObject(CatalogDBObject):
    """
    This is a class for taking several CatalogDBObjects that are querying
    the same table of the same database for the same rows (but different columns; note
    that the columns can be transformed by the CatalogDBObjects' self.columns member),
    and combining their queries into one.

    You feed the constructor a list of CatalogDBObjects.  The CompoundCatalogDBObject
    verifies that they all do, indeed, query the same table of the same database.  It
    then constructs its own self.columns member (note that CompoundCatalogDBObject is
    a daughter class of CatalogDBObject) which combines all of the requested data.

    When you call query_columns, a recarray will be returned as in a CatalogDBObject.
    Note, however, that the names of the columns of the recarray will be modified.
    If the first CatalogDBObject in the list of CatalogDBObjects passed to the constructor
    asks for a column named 'col1', that will be mapped to 'catName_col1' where 'catName'
    is the CatalogDBObject's objid member.  'col2' will be mapped to 'catName_col2', etc.
    In cases where the CatalogDBObject does not change the name of the column, the column
    will also be returned by its original, un-mangled name.

    In cases where a custom query_columns method must be implemented, this class
    can be sub-classed and the custom method added as a member method.  In that
    case, the _table_restriction member variable should be set to a list of table
    names corresponding to the tables for which this class was designed.  An
    exception will be raised if the user tries to use the CompoundCatalogDBObject
    class to query tables for which it was not written.  _table_restriction defaults
    to None, which means that the class is for use with any table.
    """

    # This member variable is an optional list of tables supported
    # by a specific CompoundCatalogDBObject sub-class.  If
    # _table_restriction==None, then any table is supported
    _table_restriction = None

    def __init__(self, catalogDbObjectList):
        """
        @param [in] catalogDbObjectList is a list of CatalogDBObjects that
        all query the same database table
        """

        self._dbObjectList = catalogDbObjectList
        self._validate_input()

        self._nameList = []
        for ix in range(len(self._dbObjectList)):
            self._nameList.append(self._dbObjectList[ix].objid)

        self._make_columns()
        self._make_dbTypeMap()
        self._make_dbDefaultValues()

        dbo = self._dbObjectList[0]
        self.tableid = dbo.tableid
        self.idColKey = dbo.idColKey
        self.raColName = dbo.raColName
        self.decColName = dbo.decColName
        super(CompoundCatalogDBObject, self).__init__(database=dbo.database, driver=dbo.driver,
                                                      host=dbo.host, port=dbo.port, verbose=dbo.verbose)


    def _make_columns(self):
        """
        Construct the self.columns member by concatenating the self.columns
        from the input CatalogDBObjects and modifying the names of the returned
        columns to identify them with their specific CatalogDBObjects.
        """
        column_names = []
        self.columns= []
        for dbo, dbName in zip(self._dbObjectList, self._nameList):
            for row in dbo.columns:
                new_row=[ww for ww in row]
                new_row[0]=str('%s_%s' % (dbName, row[0]))
                if new_row[1] is None:
                    new_row[1] = row[0]
                self.columns.append(tuple(new_row))
                column_names.append(new_row[0])

                # 25 August 2015
                # This is a modification that needs to be made in order for this
                # class to work with GalaxyTileObj.  The column galaxytileid in
                # GalaxyTileObj is removed from the query by query_columns, but
                # somehow injected back in by the query procedure on fatboy. This
                # leads to confusion if you try to query something like
                # galaxyAgn_galaxytileid.  We deal with that by removing all column
                # names like 'galaxytileid' in query_columns, but leaving 'galaxytileid'
                # un-mangled in self.columns so that self.typeMap knows how to deal
                # with it when it comes back.
                if row[0] not in column_names and (row[1] is None or row[1]==row[0]):
                    self.columns.append(row)
                    column_names.append(row[0])


    def _make_dbTypeMap(self):
        """
        Construct the self.dbTypeMap member by concatenating the self.dbTypeMaps
        from the input CatalogDBObjects.
        """
        self.dbTypeMap = {}
        for dbo in self._dbObjectList:
            for col in dbo.dbTypeMap:
                if col not in self.dbTypeMap:
                    self.dbTypeMap[col] = dbo.dbTypeMap[col]


    def _make_dbDefaultValues(self):
        """
        Construct the self.dbDefaultValues member by concatenating the
        self.dbDefaultValues from the input CatalogDBObjects.
        """
        self.dbDefaultValues = {}
        for dbo, dbName in zip(self._dbObjectList, self._nameList):
            for col in dbo.dbDefaultValues:
                self.dbDefaultValues['%s_%s' % (dbName, col)] = dbo.dbDefaultValues[col]


    def _validate_input(self):
        """
        Verify that the CatalogDBObjects passed to the constructor
        do, indeed, query the same table of the same database.

        Also verify that this class is designed to query the tables
        it is being used on (in cases where a custom query_columns
        has been implemented).
        """
        hostList = []
        databaseList = []
        portList = []
        driverList = []
        tableList = []
        objidList = []
        for dbo in self._dbObjectList:
            if dbo.host not in hostList:
                hostList.append(dbo.host)
            if dbo.database not in databaseList:
                databaseList.append(dbo.database)
            if dbo.port not in portList:
                portList.append(dbo.port)
            if dbo.driver not in driverList:
                driverList.append(dbo.driver)
            if dbo.tableid not in tableList:
                tableList.append(dbo.tableid)

            if dbo.objid not in objidList:
                objidList.append(dbo.objid)
            else:
                raise RuntimeError('WARNING the objid %s ' % dbo.objid \
                                     + 'is duplicated in your list of ' \
                                     + 'CatalogDBObjects\n' \
                                     + 'CompoundCatalogDBObject requires each' \
                                     + ' CatalogDBObject have a unique objid\n')

        acceptable = True
        msg = ''
        if len(hostList)>1:
            acceptable = False
            msg += ' hosts: ' + str(hostList) + '\n'
        if len(databaseList)>1:
            acceptable = False
            msg += ' databases: ' + str(databaseList) + '\n'
        if len(portList)>1:
            acceptable = False
            msg += ' ports: ' + str(portList) + '\n'
        if len(driverList)>1:
            acceptable = False
            msg += ' drivers: ' + str(driverList) + '\n'
        if len(tableList)>1:
            acceptable = False
            msg += ' tables: ' + str(tableList) + '\n'

        if not acceptable:
            raise RuntimeError('The CatalogDBObjects fed to ' \
                               + 'CompoundCatalogDBObject do not all ' \
                               + 'query the same table:\n' \
                               + msg)

        if self._table_restriction is not None:
            if tableList[0] not in self._table_restriction:
                raise RuntimeError("This CompoundCatalogDBObject does not support " \
                                   + "the table '%s' " % tableList[0])
