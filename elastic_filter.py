
q2_options = {
    "0": {
        "text": "gaming and media development",
        "change":
         {
             "index": [1, 3, -2],
                "value": [2, 1.75, 2]
         }
    },
    "1": {
        "text": "office and general business purpose",
        "change": {
            "index": [1, 3, -2],
            #if no graphis its 0
            "value": [1, 1, 1]
        }
    },
    "2": {
        "text": "student usage/design and development",
        "change": {
            "index": [1, 3, -2],
            "value": [1.5, 1.4, 1.5]
        }
    },

}
questions_updations = {
    1: {
        # indexes:  weight battery screensize
        #option number: [[index,replacements]

        0: [[0, 5, 6], [1, 1.75, 1.75]],
        1: [[0, 5, 6], [1.75, 1.2, 2]],
        2: [[0, 5, 6], []]
    },
    2: {

        0: [[1, 3, -2], [2, 1.75, 2]],
        1: [[1, 3, -2], [1, 1, 1]],
        2: [[1, 3, -2],[1.5, 1.4, 1.5]]


    }
}
