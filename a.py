a= [
    {
        "_id": {
            "$oid": "62e0f4dd000c06f5041978fd"
        },
        "max_value": 3.6,
        "min_value": 0.553,
        "filter": "weight",
        "data_type": "Number"
    },
    {
        "_id": {
            "$oid": "62e0f4dd000c06f5041978fe"
        },
        "max_value": 16.0,
        "min_value": 1.0,
        "filter": "ram",
        "data_type": "Number"
    },
    {
        "_id": {
            "$oid": "62e0f4dd000c06f5041978ff"
        },
        "max_value": 194999.0,
        "min_value": 14490.0,
        "filter": "price",
        "data_type": "Number"
    },
    {
        "_id": {
            "$oid": "62e0f4dd000c06f504197900"
        },
        "max_value": 8.0,
        "min_value": 0.0,
        "filter": "graphics",
        "data_type": "Boolean"
    },
    {
        "_id": {
            "$oid": "62e0f4dd000c06f504197901"
        },
        "max_value": 2048.0,
        "min_value": 16.0,
        "filter": "disk",
        "data_type": "Number"
    },
    {
        "_id": {
            "$oid": "62e0f4dd000c06f504197902"
        },
        "max_value": 17.0,
        "min_value": 1.5,
        "filter": "battery",
        "data_type": "Number"
    },
    {
        "_id": {
            "$oid": "62e0f4dd000c06f504197903"
        },
        "max_value": 17.79527559055118,
        "min_value": 10.5,
        "filter": "display",
        "data_type": "Number"
    },
    {
        "_id": {
            "$oid": "62e0f4dd000c06f504197904"
        },
        "max_value": 4.7,
        "min_value": 1.0,
        "filter": "processor",
        "data_type": "Number"
    },
    {
        "_id": {
            "$oid": "62e0f4dd000c06f504197905"
        },
        "max_value": 64.0,
        "min_value": 4.0,
        "filter": "max_memory",
        "data_type": "Number"
    },
    {
        "_id": {
            "$oid": "62e0f4dd000c06f504197906"
        },
        "filter": "brand",
        "values": [
            "ASUS",
            "AVITA",
            "Acer",
            "Dell",
            "Fujitsu",
            "HP",
            "Honor",
            "Infinix",
            "Lenovo",
            "MI",
            "MSI",
            "Microsoft",
            "Redmi"
        ],
        "data_type": "Enum"
    }
]

for i in a:
    a.remove( i['_id'])
    print(i)



