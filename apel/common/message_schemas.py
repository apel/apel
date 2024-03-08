"""A file to store message schemas for JSON based messages"""

import datetime

current_year = datetime.datetime.now().year

ACCELERATOR_MSG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://localhost/schema.json",
    "type": "object",
    "title": "Accelerator message schema root",
    "description": "This schema defines the basic conditions an accelerator message must meet",
    "required": [
        "Type",
        "Version",
        "UsageRecords"
    ],
    "properties": {
        "Type": {
            "$id": "#/properties/Type",
            "title": "JSON message type",
            "type": "string",
            "const": "APEL-accelerator-message"
        },
        "Version": {
            "$id": "#/properties/Version",
            "title": "JSON message version",
            "type": "string",
            "enum": [
                "0.1"
            ]
        },
        "UsageRecords": {
            "$id": "#/properties/UsageRecords",
            "title": "Accelerator usage records",
            "description": "The list of records matching Accelerator record requirements",
            "type": "array",
            "minItems": 1,
            "maxItems": 1000,
            "items": {
                "$id": "#/properties/UsageRecords/items",
                "type": "object",
                "required": [
                    "MeasurementMonth",
                    "MeasurementYear",
                    "AssociatedRecordType",
                    "AssociatedRecord",
                    "FQAN",
                    "SiteName",
                    "Count",
                    "AvailableDuration",
                    "Type",
                ],
                "properties": {
                    "MeasurementMonth": {
                        "$id": "#/properties/UsageRecords/items/properties/MeasurementMonth",
                        "type": "integer",
                        "enum": [
                            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
                        ]
                    },
                    "MeasurementYear": {
                        "$id": "#/properties/UsageRecords/items/properties/MeasurementYear",
                        "type": "integer",
                        "examples": [
                            2021
                        ],
                        "minimum": 2000,
                        "maximum": current_year
                    },
                    "AssociatedRecordType": {
                        "$id": "#/properties/UsageRecords/items/properties/AssociatedRecordType",
                        "type": "string",
                        "enum": [
                            "cloud",
                            "job"
                        ]
                    },
                    "AssociatedRecord": {
                        "$id": "#/properties/UsageRecords/items/properties/AssociatedRecord",
                        "type": "string",
                        "examples": [
                            "a-fake-vmuuid"
                        ]
                    },
                    "GlobalUserName": {
                        "$id": "#/properties/UsageRecords/items/properties/GlobalUserName",
                        "anyOf": [
                            {"type": "string"},
                            {"type": "null"}
                        ],
                        "examples": [
                            "null",
                            "GlobalUserA"
                        ]
                    },
                    "FQAN": {
                        "$id": "#/properties/UsageRecords/items/properties/FQAN",
                        "type": "string",
                        "examples": [
                            "None",
                            "project1",
                            "/fedcloud.egi.eu/Role=NULL/Capability=NULL"
                        ]
                    },
                    "SiteName": {
                        "$id": "#/properties/UsageRecords/items/properties/SiteName",
                        "type": "string",
                        "examples": [
                            "TEST-SITE"
                        ]
                    },
                    "Count": {
                        "$id": "#/properties/UsageRecords/items/properties/Count",
                        "description": "The number of Accelerators used",
                        "type": "number",
                        "examples": [
                            1.4
                        ]
                    },
                    "Cores": {
                        "$id": "#/properties/UsageRecords/items/properties/Cores",
                        "description": "The number of cores for this Accelerator type",
                        "anyOf": [
                            {"type": "integer"},
                            {"type": "null"}
                        ],
                        "examples": [
                            128
                        ]
                    },
                    "ActiveDuration": {
                        "$id": "#/properties/UsageRecords/items/properties/ActiveDuration",
                        "description": "The recorded time in seconds that accelerators were explicitly active for (NOT IMPLEMENTED)",
                        "anyOf": [
                            {"type": "integer"},
                            {"type": "null"}
                        ],
                        "examples": [
                            40
                        ]
                    },
                    "AvailableDuration": {
                        "$id": "#/properties/UsageRecords/items/properties/AvailableDuration",
                        "description": "The wall time in seconds that accelerators were held for",
                        "type": "integer",
                        "examples": [
                            4000
                        ]
                    },
                    "BenchmarkType": {
                        "$id": "#/properties/UsageRecords/items/properties/BenchmarkType",
                        "description": "The identifier for the accelerator benchmark",
                        "anyOf": [
                            {"type": "string"},
                            {"type": "null"}
                        ],
                        "examples": [
                            "null",
                            "HEPSPEC"
                        ]
                    },
                    "Benchmark": {
                        "$id": "#/properties/UsageRecords/items/properties/Benchmark",
                        "description": "The benchmark score",
                        "anyOf": [
                            {"type": "number"},
                            {"type": "null"}
                        ],
                        "examples": [
                            9000.01
                        ]
                    },
                    "Type": {
                        "$id": "#/properties/UsageRecords/items/properties/Type",
                        "description": "The general descriptor for accelerator",
                        "type": "string",
                        "enum": [
                            "GPU",
                            "FPGA",
                            "Other"
                        ]
                    },
                    "Model": {
                        "$id": "#/properties/UsageRecords/items/properties/Model",
                        "description": "Specific model of accelerator type",
                        "type": "string",
                        "examples": [
                            "VendorA-ModelA",
                            "VendorA-ModelB"
                        ]
                    }
                }
                # We can impose Model restrictions conditional on type using the allOf operator
                # "allOf": [ ]
            }
        }
    }
}

ACCELERATOR_SUMMARY_MSG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://localhost/schema.json",
    "type": "object",
    "title": "Accelerator summary message schema root",
    "description": "This schema defines the basic conditions an accelerator summary message must meet",
    "required": [
        "Type",
        "Version",
        "UsageRecords"
    ],
    "properties": {
        "Type": {
            "$id": "#/properties/Type",
            "title": "JSON message type",
            "type": "string",
            "const": "APEL-accelerator-message"
        },
        "Version": {
            "$id": "#/properties/Version",
            "title": "JSON message version",
            "type": "string",
            "enum": [
                "0.1"
            ]
        },
        "UsageRecords": {
            "$id": "#/properties/UsageRecords",
            "title": "Accelerator Summary usage records",
            "description": "The list of records matching Accelerator summary requirements",
            "type": "array",
            "minItems": 1,
            "maxItems": 1000,
            "items": {
                "$id": "#/properties/UsageRecords/items",
                "type": "object",
                "required": [
                    "Month",
                    "Year",
                    "AssociatedRecordType",
                    "SiteName",
                    "Count",
                    "AvailableDuration",
                    "Type",
                    "NumberOfRecords"
                ],
                "properties": {
                    "Month": {
                        "$id": "#/properties/UsageRecords/items/properties/Month",
                        "type": "integer",
                        "enum": [
                            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
                        ]
                    },
                    "Year": {
                        "$id": "#/properties/UsageRecords/items/properties/Year",
                        "type": "integer",
                        "examples": [
                            2021
                        ],
                        "minimum": 2000,
                        "maximum": current_year
                    },
                    "AssociatedRecordType": {
                        "$id": "#/properties/UsageRecords/items/properties/AssociatedRecordType",
                        "type": "string",
                        "enum": [
                            "cloud",
                            "job"
                        ]
                    },
                    "GlobalUserName": {
                        "$id": "#/properties/UsageRecords/items/properties/GlobalUserName",
                        "anyOf": [
                            {"type": "string"},
                            {"type": "null"}
                        ],
                        "examples": [
                            "GlobalUserA"
                        ]
                    },
                    "FQAN": {
                        "$id": "#/properties/UsageRecords/items/properties/FQAN",
                        "type": "string",
                        "examples": [
                            "None",
                            "project1",
                            "/fedcloud.egi.eu/Role=NULL/Capability=NULL"
                        ]
                    },
                    "SiteName": {
                        "$id": "#/properties/UsageRecords/items/properties/SiteName",
                        "type": "string",
                        "examples": [
                            "TEST-SITE"
                        ]
                    },
                    "Count": {
                        "$id": "#/properties/UsageRecords/items/properties/Count",
                        "description": "The number of Accelerators used",
                        "type": "number",
                        "examples": [
                            1.4
                        ]
                    },
                    "Cores": {
                        "$id": "#/properties/UsageRecords/items/properties/Cores",
                        "description": "The number of cores for this Accelerator type",
                        "anyOf": [
                            {"type": "integer"},
                            {"type": "null"}
                        ],
                        "examples": [
                            128
                        ]
                    },
                    "ActiveDuration": {
                        "$id": "#/properties/UsageRecords/items/properties/ActiveDuration",
                        "description": "The recorded time in seconds that accelerators were explicitly active for (NOT IMPLEMENTED)",
                        "anyOf": [
                            {"type": "integer"},
                            {"type": "null"}
                        ],
                        "examples": [
                            40
                        ]
                    },
                    "AvailableDuration": {
                        "$id": "#/properties/UsageRecords/items/properties/AvailableDuration",
                        "description": "The wall time in seconds that accelerators were held for",
                        "type": "integer",
                        "examples": [
                            4000
                        ]
                    },
                    "BenchmarkType": {
                        "$id": "#/properties/UsageRecords/items/properties/BenchmarkType",
                        "description": "The identifier for the accelerator benchmark",
                        "anyOf": [
                            {"type": "string"},
                            {"type": "null"}
                        ],
                        "examples": [
                            "HEPSPEC"
                        ]
                    },
                    "Benchmark": {
                        "$id": "#/properties/UsageRecords/items/properties/Benchmark",
                        "description": "The benchmark score",
                        "anyOf": [
                            {"type": "number"},
                            {"type": "null"}
                        ],
                        "examples": [
                            9000.01
                        ]
                    },
                    "Type": {
                        "$id": "#/properties/UsageRecords/items/properties/Type",
                        "description": "The general descriptor for accelerator",
                        "type": "string",
                        "enum": [
                            "Accelerator",
                            "FPGA",
                            "Other"
                        ]
                    },
                    "Model": {
                        "$id": "#/properties/UsageRecords/items/properties/Model",
                        "description": "Specific model of accelerator type",
                        "type": "string",
                        "examples": [
                            "VendorA-ModelA",
                            "VendorA-ModelB"
                        ]
                    },
                    "NumberOfRecords": {
                        "$id": "#/properties/UsageRecords/items/properties/NumberOfRecords",
                        "description": "Total combined individual records in this summary",
                        "type": "integer",
                        "minimum": 1
                    }
                }
            }
        }
    }
}
