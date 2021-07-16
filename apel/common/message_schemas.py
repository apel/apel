"""A file to store message schemas for JSON based messages"""

import datetime

current_year = datetime.datetime.now().year

GPU_MSG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema", 
    "$id": "http://localhost/schema.json", # [?] Will this schema be made accessible via HTTP? May be difficult using a python object, so unecessary in this state.
    "type": "object",
    "title": "GPU message schema root",
    "description": "This schema defines the basic conditions a GPU message must meet",
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
            "const": "APEL GPU message"
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
            "title": "GPU usage records",
            "description": "The list of records matching GPU record requirements",
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
                        # [?] Values greater than 2000 and not in the future
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
                        "type": "string",
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
                        "description": "The number of GPUs used",
                        "type": "number",
                        "examples": [
                            1.4
                        ]
                    },
                    "Cores": {
                        "$id": "#/properties/UsageRecords/items/properties/Cores",
                        "description": "The number of cores for this GPU type",
                        "type": "integer",
                        "examples": [
                            128
                        ]
                    },
                    "ActiveDuration": {
                        "$id": "#/properties/UsageRecords/items/properties/ActiveDuration",
                        "description": "The recorded time in seconds that accelerators were explicitly active for (NOT IMPLEMENTED)",
                        "type": "integer",
                        "examples": [
                            40
                        ]
                    },
                    "AvailableDuration": {
                        "$id": "#/properties/UsageRecords/items/properties/AvailableDuration",
                        "description": "The wall time in seconds that accelerators were held for"
                        "type": "integer",
                        "examples": [
                            4000
                        ]
                    },
                    "BenchmarkType": {
                        "$id": "#/properties/UsageRecords/items/properties/BenchmarkType",
                        "description": "The identifier for the accelerator benchmark",
                        "type": "string",
                        "examples": [
                            "HEPSPEC"
                        ]
                    },
                    "Benchmark": {
                        "$id": "#/properties/UsageRecords/items/properties/Benchmark",
                        "description": "The benchmark score",
                        "type": "number",
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
                        "description": "",
                        "type": "string",
                        "examples": [
                            "VendorA-ModelA",
                            "VendorA-ModelB"
                        ]
                        # [ ] TODO conditional on type
                    }
                },
                "allOf": [ # Check that models match accelerator type
                    "if": {
                        "properties": {
                            "Model": "GPU"
                        }
                    },
                    "then": {
                        "properties": {
                            "Model": {
                                "enum": [ "gpu-model1", "gpu-model2", "gpu-model3" ] 
                            }
                        }
                    },

                    "if": {
                        "properties": {
                            "Model": "FPGA"
                        }
                    },
                    "then": {
                        "properties": {
                            "Model": {
                                "enum": [ "fpga-model1", "fpga-model2", "fpga-model3" ]
                            }
                        }
                    },

                    "if": {
                        "properties": {
                            "Model": "Other"
                        }
                    },
                    "then": {
                        "properties": {
                            "Model": {
                                "type": "string"
                            }
                        }
                    }
                ]
            }
        }
    }
}
