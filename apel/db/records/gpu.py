"""This file contains the GPURecord class."""
from apel.common import parse_fqan
from apel.db.records import Record, InvalidRecordException


class GPURecord(Record):
    """Class to represent one GPU record."""
    def __init__(self):
        """Provide the necessary lists containing message information."""
        Record.__init__(self)

        # Fields which are required by the message format.
        self._mandatory_fields = [
            "MeasurementMonth",
            "MeasurementYear",
            "AssociatedRecordType",
            "AssociatedRecord",
            "FQAN",
            "SiteName",
            "Count",
            "AvailableDuration",
            "Type",
        ]

        # This list allows us to specify the order of lines when we construct
        # records.
        self._msg_fields = [
            "MeasurementMonth", 
            "MeasurementYear", 
            "AssociatedRecordType",
            "AssociatedRecord", 
            "GlobalUserName",
            "FQAN",
            "SiteName", 
            "Count",
            "Cores",
            "ActiveDuration",
            "AvailableDuration", 
            "BenchmarkType",
            "Benchmark", 
            "Type",
            "Model",
        ]

        self._int_fields = [
            "MeasurementMonth",
            "MeasurementYear",
            "Cores",
            "ActiveDuration",
            "AvailableDuration"
        ]

        self._float_fields = [
            "Count",
            "Benchmark"
        ]

        # This list specifies the information that goes in the database.
        self._db_fields = ( self._msg_fields )

        # All allowed fields.
        self._all_fields = self._db_fields

    def _check_fields(self):
        """
        Add extra checks to those made in every record.

        Also populates fields that are extracted from other fields.
        """
        # First, call the parent's version.
        Record._check_fields(self)

        # [?] TODO Do we care about assigning VOx to GPU?

        ### Extract the relevant information from the user fqan.
        ### Keep the fqan itself as other methods in the class use it.
        #role, group, vo = parse_fqan(self._record_content['FQAN'])
        #self._record_content['VORole'] = role
        #self._record_content['VOGroup'] = group
        #self._record_content['VO'] = vo

        # [?] TODO Check logic GlobalUserName, SiteName, FQAN
        # [?] TODO Check Type, Model, Cores
        # [?] TODO Check Benchmark, AssociatedRecord