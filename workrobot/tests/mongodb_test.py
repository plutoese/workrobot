# coding = UTF-8

import unittest
from libs.imexport.class_mongodb import MongoDB, MonDatabase, MonCollection


class TestCalculate(unittest.TestCase):
    def setUp(self):
        mongo = MongoDB(conn_str='mongodb://plutoese:z1Yh29@139.196.189.191:3717/')
        mdb = MonDatabase(mongodb=mongo, database_name='region')
        self.mcollection = MonCollection(database=mdb, collection_name='cities')

    def test_connect_mongodb(self):
        self.assertEqual(2, len(list(self.mcollection.find())))

if __name__ == '__main__':
    unittest.main()