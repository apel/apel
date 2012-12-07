from apel.db.records import CloudRecord
from unittest import TestCase

class CloudRecordTest(TestCase):
    '''
    Test case for StorageRecord
    '''
    
#    def test_load_from_tuple(self):
#        # full example
#        data = ('host.example.org/sr/87912469269276', 1289293612, 'host.example.org', 'MySite',
#                 'pool-003', 'disk', 'replicated', 42, '/home/projectA', 
#                 'johndoe', 'projectA', '/O=Grid/OU=example.org/CN=John Doe',
#                 'binarydataproject.example.org', '2010-10-11T09:31:40Z', '2010-10-11T09:41:40Z',
#                 14728, 13617)
#        
#        record = StorageRecord()
#        record.load_from_tuple(data)
#        
#        self.assertEquals(record.get_field('RecordId'), 'host.example.org/sr/87912469269276')
#        self.assertEquals(str(record.get_field('CreateTime')), "2010-11-09 09:06:52")
#        self.assertEquals(record.get_field('StorageSystem'), 'host.example.org')
#        self.assertEquals(record.get_field('Site'), 'MySite')
#        self.assertEquals(record.get_field('StorageShare'), 'pool-003')
#        self.assertEquals(record.get_field('StorageMedia'), 'disk')
#        self.assertEquals(record.get_field('StorageClass'), 'replicated')
#        self.assertEquals(record.get_field('FileCount'), 42)
#        self.assertEquals(record.get_field('DirectoryPath'), '/home/projectA')
#        self.assertEquals(record.get_field('LocalUser'), 'johndoe')
#        self.assertEquals(record.get_field('LocalGroup'), 'projectA')
#        self.assertEquals(record.get_field('UserIdentity'), '/O=Grid/OU=example.org/CN=John Doe')
#        self.assertEquals(record.get_field('GroupName'), 'binarydataproject.example.org')
#        self.assertEquals(str(record.get_field('StartTime')), "2010-10-11 09:31:40")
#        self.assertEquals(str(record.get_field('EndTime')), "2010-10-11 09:41:40")
#        self.assertEquals(record.get_field('ResourceCapacityUsed'), 14728)
#        self.assertEquals(record.get_field('LogicalCapacityUsed'), 13617)

    def setUp(self):
        self._msg = '''
RecordId: 2012-12-04 09:15:01+00:00 CESNET vm-0
SiteName: CESNET
ZoneName: EU
MachineName: 'one-0'
LocalUserId: 5
LocalGroupId: 1
GlobalUserName: NULL
FQAN: NULL
Status: completed
StartTime: 1318840264
EndTime: 1318848076
SuspendTime: NULL
TimeZone: CEST
WallDuration: NULL
CpuDuration: NULL
CpuCount: 1
NetworkType: NULL
NetworkInbound: 0
NetworkOutbound: 0
Memory: 512
Disk: NULL
StorageRecordId: NULL
ImageId: 'scilin6'
CloudType: OpenNebula
'''

    def test_load_from_msg(self):
        cr = CloudRecord()
        cr.load_from_msg(self._msg)
        
        
        
    def test_mandatory_fields(self):
        record = CloudRecord()
        record.set_field('RecordId', 'host.example.org/cr/87912469269276')
        record.set_field('SiteName', 'MySite')
        record.set_field('MachineName', 'MyMachine')
        
        try:
            record._check_fields()
        except Exception, e:
            self.fail('_check_fields method failed: %s [%s]' % (str(e), str(type(e))))