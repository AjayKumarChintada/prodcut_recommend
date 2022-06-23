
def update_vector_with_choices(question_num,choice_num):

    question_filters = {
        0: {
            # indexes:  weight battery screensize
            #option number: [[index,replacements]

            0: [[0, 5, 6], [1, 1.75, 1.75]],
            1: [[0, 5, 6], [1.75, 1.2, 2]],
            2: [[0, 5, 6], []]
        },
        ## RAM, Graphic ram, processor speed
        1: {

            0: [[1, 3, -2], [2, 1.75, 2]],
            1: [[1, 3, -2], [1, 1, 1]],
            2: [[1, 3, -2], [1.5, 1.4, 1.5]]


        },
        ## price
        2: {
            0: [[2], [1]],
            1: [[2], [1.5]],
            2: [[2], [2]]

        },
        ## disk size, max memory support
        3: {
            0: [[4, 8], [2, 2]],
            1: [[4, 8],[1, 1]],
            2: [[4, 8], [1.5, 1.5]] 
        }
    }

    return question_filters[question_num][choice_num]
    


