'''
Created on 14 Feb 2013

@author: will
'''
import unittest
import decimal
import apel.ldap.query


class Test(unittest.TestCase):


    def test_parse_ce_capability(self):

        nonsense = "hello"
        invalid_ce_cap = "CPUScalingReferenceSI00=value"
        int_ce_cap = "CPUScalingReferenceSI00=53"
        float_ce_cap = "CPUScalingReferenceSI00=53.53"

        if apel.ldap.query.parse_ce_capability(nonsense) is not None:
            self.fail('parse_ce_capability should return None for %s' % nonsense)
        if apel.ldap.query.parse_ce_capability(invalid_ce_cap) is not None:
            self.fail('parse_ce_capability should return None for %s' % invalid_ce_cap)

        dec = decimal.Decimal(53)
        if apel.ldap.query.parse_ce_capability(int_ce_cap) != dec:
            self.fail('parse_ce_capability should return a decimal for %s' % int_ce_cap)
        dec = decimal.Decimal('53.53')
        if apel.ldap.query.parse_ce_capability(float_ce_cap) != dec:
            self.fail('parse_ce_capability should return a decimal for %s' % float_ce_cap)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_parse_ce_capability']
    unittest.main()