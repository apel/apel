"""A file to store message schemas for JSON based messages"""

GPU_MSG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "The root schema",
    "required": [
        "Type",
        "Version",
        "UsageRecords"
    ],
    "properties": {
        "Type": {
            "$id": "#/properties/Type",
            "type": "string",
            "title": "The Type schema",
            "const": "APEL GPU message"
        },
        "Version": {
            "$id": "#/properties/Version",
            "type": "string",
            "title": "The Version schema",
            "enum": [
                "0.1"
            ]
        },
        "UsageRecords": {
            "$id": "#/properties/UsageRecords",
            "type": "array",
            "minItems": 1,
            "maxItems": 1000,
            "title": "The UsageRecords schema",
            "items": {
                "$id": "#/properties/UsageRecords/items",
                "type": "object",
                "title": "The UsageRecord Schema",
                "required": [
                    "MeasurementMonth",
                    "MeasurementYear",
                    "AssociatedRecordType",
                    "AssociatedRecord",
                    "FQAN",
                    "SiteName",
                    "Count",
                    "Cores",
                    "ActiveDuration"
                ],
                "properties": {
                    "MeasurementMonth": {
                        "$id": "#/properties/UsageRecords/items/properties/MeasurementMonth",
                        "type": "integer",
                        "title": "The MeasurementMonth schema",
                        "enum": [
                            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
                        ]
                    },
                    "MeasurementYear": {
                        "$id": "#/properties/UsageRecords/items/properties/MeasurementYear",
                        "type": "integer",
                        "title": "The MeasurementYear schema",
                        "examples": [
                            2021
                        ]
                    },
                    "AssociatedRecordType": {
                        "$id": "#/properties/UsageRecords/items/properties/AssociatedRecordType",
                        "type": "string",
                        "title": "The AssociatedRecordType schema",
                        "enum": [
                            "cloud",
                        ]
                    },
                    "AssociatedRecord": {
                        "$id": "#/properties/UsageRecords/items/properties/AssociatedRecord",
                        "type": "string",
                        "title": "The AssociatedRecord schema",
                        "examples": [
                            "a-fake-vmuuid"
                        ]
                    },
                    "GlobalUserName": {
                        "$id": "#/properties/UsageRecords/items/properties/GlobalUserName",
                        "type": "string",
                        "title": "The GlobalUserName schema",
                        "examples": [
                            "GlobalUserA"
                        ]
                    },
                    "FQAN": {
                        "$id": "#/properties/UsageRecords/items/properties/FQAN",
                        "type": "string",
                        "title": "The FQAN Schema",
                        "examples": [
                            "None",
                            "project1",
                            "/fedcloud.egi.eu/Role=NULL/Capability=NULL"
                        ]
                    },
                    "SiteName": {
                        "$id": "#/properties/UsageRecords/items/properties/SiteName",
                        "type": "string",
                        "title": "The SiteName Schema",
                        "examples": [
                            "TEST-SITE"
                        ]
                    },
                    "Count": {
                        "$id": "#/properties/UsageRecords/items/properties/Count",
                        "type": "number",
                        "title": "The Count schema",
                        "examples": [
                            1.4
                        ]
                    },
                    "Cores": {
                        "$id": "#/properties/UsageRecords/items/properties/Cores",
                        "type": "integer",
                        "title": "The Cores schema",
                        "examples": [
                            128
                        ]
                    },
                    "ActiveDuration": {
                        "$id": "#/properties/UsageRecords/items/properties/ActiveDuration",
                        "type": "integer",
                        "title": "The ActiveDuration schema",
                        "examples": [
                            40
                        ]
                    },
                    "AvailableDuration": {
                        "$id": "#/properties/UsageRecords/items/properties/AvailableDuration",
                        "type": "integer",
                        "title": "The AvailableDuration schema",
                        "examples": [
                            4000
                        ]
                    },
                    "BenchmarkType": {
                        "$id": "#/properties/UsageRecords/items/properties/BenchmarkType",
                        "type": "string",
                        "title": "The BenchmarkType schema",
                        "examples": [
                            "Some Benchmark"
                        ]
                    },
                    "Benchmark": {
                        "$id": "#/properties/UsageRecords/items/properties/Benchmark",
                        "type": "number",
                        "title": "The Benchmark schema",
                        "examples": [
                            9000.01
                        ]
                    },
                    "Type": {
                        "$id": "#/properties/UsageRecords/items/properties/Type",
                        "type": "string",
                        "title": "The Type schema",
                        "enum": [
                            "GPU",
                            "FPGA",
                            "Other"
                        ]
                    },
                    "Model": {
                        "$id": "#/properties/UsageRecords/items/properties/Model",
                        "type": "string",
                        "title": "The Model schema",
                        "examples": [
                            "VendorA-ModelA",
                            "VendorA-ModelB"
                        ]
                    }
                }
            }
        }    
    }        
}
