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
    a daughter class of CatalogDBobject) which combines all of the requested data.

    When you call query_columns, a recarray will be returned as in a CatalogDBObject.
    Note, however, that the names of the columns of the recarray will be modified.
    If the first CatalogDBObject in the list of CatalogDBObjects passed to the constructor
    asks for a column named 'col1', that will be mapped to 'catName_col1' where 'catName'
    is the CatalogDBObject's objid member.  'col2' will be mapped to 'catName_col2', etc.
    """


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
        self.columns= []
        for dbo, dbName in zip(self._dbObjectList, self._nameList):
            for row in dbo.columns:
                new_row=[ww for ww in row]
                new_row[0]='%s_%s' % (dbName, row[0])
                self.columns.append(tuple(new_row))


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
                raise RuntimeWarning('WARNING the objid %s ' % dbo.objid \
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
