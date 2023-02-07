"""This file contains the IPRecord class."""
from apel.common import parse_fqan_db_safe
from apel.db.records import Record, InvalidRecordException


class IPRecord(Record):
    """Class to represent one IP record."""
    def __init__(self):
        """Provide the necessary lists containing message information."""
        Record.__init__(self)
        # Fields which are required by the message format.
        self._mandatory_fields = [
            "MeasurementTime", "SiteName", "CloudType", "LocalUser",
            "LocalGroup", "GlobalUserName", "FQAN", "IPVersion", "IPCount"
        ]

        # This list allows us to specify the order of lines when we construct
        # records.
        self._msg_fields = [
            "MeasurementTime", "SiteName", "CloudComputeService", "CloudType",
            "LocalUser", "LocalGroup", "GlobalUserName", "FQAN", "IPVersion",
            "IPCount"
        ]

        # Fields which will have an integer stored in them
        self._int_fields = ["IPVersion", "IPCount"]

        self._datetime_fields = ["MeasurementTime"]

        # This list specifies the information that goes in the database.
        self._db_fields = (
            self._msg_fields[:1] +
            ["MeasurementMonth", "MeasurementYear"] +
            self._msg_fields[1:8] +
            ['VO', 'VOGroup', 'VORole'] +
            self._msg_fields[8:]
        )

        # All allowed fields.
        self._all_fields = self._db_fields

    def _check_fields(self):
        """
        Add extra checks to those made in every record.

        Also populates fields that are extracted from other fields.
        """
        # First, call the parent's version.
        Record._check_fields(self)

        # Extract the relevant information from the user fqan.
        # Keep the fqan itself as other methods in the class use it.
        role, group, vo = parse_fqan_db_safe(self._record_content['FQAN'])
        self._record_content['VORole'] = role
        self._record_content['VOGroup'] = group
        self._record_content['VO'] = vo

        # Set the MeasurementMonth and MeasurementYear.
        measurement_month = self._record_content['MeasurementTime'].month
        measurement_year = self._record_content['MeasurementTime'].year
        self._record_content['MeasurementMonth'] = measurement_month
        self._record_content['MeasurementYear'] = measurement_year
