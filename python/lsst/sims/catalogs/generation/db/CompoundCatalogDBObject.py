import numpy
from collections import OrderedDict
from lsst.sims.catalogs.generation.db import CatalogDBObject

__all__ = ["CompoundCatalogDBObject"]

class CompoundCatalogDBObject(CatalogDBObject):


    def __init__(self, catalogDbObjectList):
        """
        @param [in] catalogDbObjectList is a list of CatalogDBObjects that
        all query the same database table
        """

        self._dbObjectList = catalogDbObjectList
        self._validate_input()

        self._nameList = []
        for ix in range(len(self._dbObjectList)):
            self._nameList.append('db_%d' % ix)

        self._make_columns()

        dbo = self._dbObjectList[0]
        self.tableid = dbo.tableid
        self.idColKey = dbo.idColKey
        self.raColName = dbo.raColName
        self.decColName = dbo.decColName
        super(CompoundCatalogDBObject, self).__init__(database=dbo.database, driver=dbo.driver,
                                                      host=dbo.host, port=dbo.port, verbose=dbo.verbose)


    def _make_columns():
        self.columns= []
        for dbo, dbName in zip(self._dbObjectList, self._nameList):
            for row in dbo.columns:
                new_row=[ww for ww in row]
                new_row[0]='%s_%s' % dbName,row[0]
                self.columns.append(tuple(new_row))


    def _validate_input(self):
        hostList = []
        databaseList = []
        portList = []
        driverList = []
        tableList = []
        for dbo in self._dbObjectList:
            if dbo.host not in hostList:
                hostList.append(dbo.host)
            if dbo.database not in databaseList:
                databaseList.append(dbo.database)
            if dbo.port not in portList:
                portList.append(dbo.port)
            if dbo.driver not in driverList:
                driverList.append(dbo.driver)
            if dbo.table not in tableList:
                tableList.append(dbo.table)

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
