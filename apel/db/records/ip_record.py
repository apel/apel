from apel.db.records import Record, InvalidRecordException


class IPRecord(Record):

    def __init__(self):
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
        self._db_fields = self._msg_fields
        # All allowed fields.
        self._all_fields = self._msg_fields
