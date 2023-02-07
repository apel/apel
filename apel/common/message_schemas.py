"""A file to store message schemas for JSON based messages"""

IP_MSG_SCHEMA = {
    "definitions": {

    },
    "$schema": "http: //json-schema.org/draft-07/schema#",
    "$id": "http: //example.com/root.json",
    "type": "object",
    "title": "The Root Schema",
    "required": [],
    "properties": {
        "Type": {
            "$id": "#/properties/Type",
            "type": "string",
            "title": "The Type Schema",
            "const": "APEL Public IP message"
        },
        "Version": {
            "$id": "#/properties/Version",
            "type": "string",
            "title": "The Version Schema",
            "enum": [
                "v0.2"
            ],

        },
        "UsageRecords": {
            "$id": "#/properties/UsageRecords",
            "type": "array",
            "minItems": 1,
            "maxItems": 1000,
            "title": "The UsageRecords Schema",
            "items": {
                "$id": "#/properties/UsageRecords/items",
                "type": "object",
                "title": "The UsageRecord Schema",
                "required": [
                    "MeasurementTime",
                    "SiteName",
                    "CloudType",
                    "LocalUser",
                    "LocalGroup",
                    "GlobalUserName",
                    "FQAN",
                    "IPVersion",
                    "IPCount"
                ],
                "properties": {
                    "MeasurementTime": {
                        "$id": "#/properties/UsageRecords/items/properties/MeasurementTime",
                        "type": "integer",
                        "title": "The MeasurementTime Schema",
                        "examples": [
                            1536070129
                        ]
                    },
                    "SiteName": {
                        "$id": "#/properties/UsageRecords/items/properties/SiteName",
                        "type": "string",
                        "title": "The SiteName Schema",
                        "examples": [
                            "TEST-SITE"
                        ],

                    },
                    "CloudComputeService": {
                        "$id": "#/properties/UsageRecords/items/properties/CloudComputeService",
                        "type": [
                            "string",
                            "null"
                        ],
                        "title": "The CloudComputeService Schema",
                        "examples": [
                            "TEST-CLOUD"
                        ],

                    },
                    "CloudType": {
                        "$id": "#/properties/UsageRecords/items/properties/CloudType",
                        "type": "string",
                        "title": "The CloudType Schema",
                        "examples": [
                            "caso/1.1.0  (OpenStack)",
                            "OpenNebula oneacct-export/0.4.6"
                        ],

                    },
                    "LocalUser": {
                        "$id": "#/properties/UsageRecords/items/properties/LocalUser",
                        "type": "string",
                        "title": "The LocalUser Schema",
                        "examples": [
                            "User1"
                        ],

                    },
                    "LocalGroup": {
                        "$id": "#/properties/UsageRecords/items/properties/LocalGroup",
                        "type": "string",
                        "title": "The LocalGroup Schema",
                        "examples": [
                            "Group1"
                        ],

                    },
                    "GlobalUserName": {
                        "$id": "#/properties/UsageRecords/items/properties/GlobalUserName",
                        "type": "string",
                        "title": "The GlobalUserName Schema",
                        "examples": [
                            "GlobalUser1"
                        ],

                    },
                    "FQAN": {
                        "$id": "#/properties/UsageRecords/items/properties/FQAN",
                        "type": "string",
                        "title": "The FQAN Schema",
                        "examples": [
                            "None",
                            "alice",
                            "/fedcloud.egi.eu/Role=NULL/Capability=NULL"
                        ],

                    },
                    "IPVersion": {
                        "$id": "#/properties/UsageRecords/items/properties/IPVersion",
                        "type": "integer",
                        "enum": [
                            4,
                            6
                        ],
                        "title": "The IPVersion Schema"
                    },
                    "IPCount": {
                        "$id": "#/properties/UsageRecords/items/properties/IPCount",
                        "type": "integer",
                        "minimum": 0,
                        "title": "The IPCount Schema",
                        "examples": [
                            12
                        ]
                    }
                }
            }
        }
    }
}
