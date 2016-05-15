__author__ = 'Elias'
import RPK
import math

zero = [0, 0, 0, 0, 0, 0, 0, 0]
transformations = [[1, 1, 2, 3, 5, -4, 1, -3], [5, -4, 1, -3, 1, 1, 2, 3]]

#min amount of concatenated notes that need to be transformed.
min_length = 4
height = 14

def bestTransformed(int_notes, keyIndex):
    #transformation from -6 to +7
    #add new history to back of the array
    prob_keep_past = [[-100000, -100000, -100000, -100000, -100000, -100000, 0, -100000, -100000, -100000, -100000, -100000, -100000, -100000] for x in range(min_length)]
    prob_keep_current = [-100000 for y in range(height)]
    prob_transform_past = [[[-100000 for y in range(height)] for x in range(min_length)] for z in range(len(transformations))]
    prob_transform_current = [[-100000 for y in range(height)] for z in range(len(transformations))]

    path_end_on_keep_past = [[[] for x in range(height)] for y in range(min_length)]
    path_end_on_keep_current = [[] for x in range(height)]
    path_end_on_transform_past = [[[[] for x in range(height)] for y in range(min_length)] for z in range(len(transformations))]
    path_end_on_transform_current = [[[] for x in range(height)] for z in range(len(transformations))]

    for x in range(len(int_notes)-1):
        present_note = int_notes[x+1]

        #case of keeping original
        for y in range(height):
            last_note = int_notes[x]+y-6
            diff = abs(present_note-last_note)
            new_note = present_note+(zero[(diff+8)%8])
            #extending one that already ended on a keep
            if prob_keep_current[new_note-present_note+6] < prob_keep_past[min_length-1][y]+RPK.proximity_prob_log(new_note, last_note):
                prob_keep_current[new_note-present_note+6] = prob_keep_past[min_length-1][y]+RPK.proximity_prob_log(new_note, last_note)
                copy = list(path_end_on_keep_past[min_length-1][y])
                copy.append(y)
                path_end_on_keep_current[new_note-present_note+6] = copy
            #extending one that ended on a transform
            for z in range(len(transformations)):
                if prob_keep_current[new_note-present_note+6] < prob_transform_past[z][min_length-1][y]+RPK.proximity_prob_log(new_note, last_note):
                    prob_keep_current[new_note-present_note+6] = prob_transform_past[z][min_length-1][y]+RPK.proximity_prob_log(new_note, last_note)
                    copy = list(path_end_on_transform_past[z][min_length-1][y])
                    copy.append(y)
                    path_end_on_keep_current[new_note-present_note+6] = copy

        #case of transform
        if x >= (min_length-1):
            for z in range(len(transformations)):
                #extending one that already ended on the same transform
                for y in range(height):
                    last_note = int_notes[x]+y-6
                    diff = abs(present_note-last_note)
                    new_note = -1
                    if (present_note-last_note <= 0):
                        new_note = present_note+(transformations[z][(diff+8)%8])
                    else:
                        new_note = present_note-(transformations[z][(diff+8)%8])
                    if RPK.note_prob_in_key(new_note, keyIndex) < 0.02:
                        if (RPK.note_prob_in_key(new_note+1, keyIndex) > RPK.note_prob_in_key(new_note-1, keyIndex)):
                            new_note = new_note+1
                        else:
                            new_note = new_note-1
                    if prob_transform_current[z][new_note-present_note+6] < prob_transform_past[z][min_length-1][y]+RPK.proximity_prob_log(new_note, last_note):
                        prob_transform_current[z][new_note-present_note+6] = prob_transform_past[z][min_length-1][y]+RPK.proximity_prob_log(new_note, last_note)
                        copy = list(path_end_on_transform_past[z][min_length-1][y])
                        copy.append(y)
                        path_end_on_transform_current[z][new_note-present_note+6] = copy

                #extending one that ended on another transform
                for q in range(len(transformations)):
                    if q==z:
                        continue
                    start_probs = list(prob_transform_past[q][0])
                    past_paths = [list(path_end_on_transform_past[q][0][x]) for x in range(height)]
                    result = simulate_best_paths(start_probs, transformations[z], min_length, past_paths, x-(min_length-1), keyIndex, int_notes)
                    end_probs = result[0]
                    end_paths = result[1]
                    for y in range(height):
                        if prob_transform_current[z][y] < end_probs[y]:
                            prob_transform_current[z][y] = end_probs[y]
                            path_end_on_transform_current[z][y] = list(end_paths[y])

                #extending one that ended on keep
                start_probs = list(prob_keep_past[0])
                past_paths = [list(path_end_on_keep_past[0][x]) for x in range(height)]
                result = simulate_best_paths(start_probs, transformations[z], min_length, past_paths, x-(min_length-1), keyIndex, int_notes)
                end_probs = result[0]
                end_paths = result[1]
                for y in range(height):
                    if prob_transform_current[z][y] < end_probs[y]:
                        prob_transform_current[z][y] = end_probs[y]
                        path_end_on_transform_current[z][y] = list(end_paths[y])

        #reinitialize arrays
        for y in range(height):
            for q in range(min_length-1):
                prob_keep_past[q][y] = prob_keep_past[q+1][y]
                path_end_on_keep_past[q][y] = path_end_on_keep_past[q+1][y]
                for z in range(len(transformations)):
                    prob_transform_past[z][q][y] = prob_transform_past[z][q+1][y]
                    path_end_on_transform_past[z][q][y] = path_end_on_transform_past[z][q+1][y]
            prob_keep_past[min_length-1][y] = prob_keep_current[y]+RPK.range_prob_log(present_note+y-6)+math.log(RPK.note_prob_in_key(present_note+y-6, keyIndex))
            prob_keep_current[y] = -100000
            for z in range(len(transformations)):
                prob_transform_past[z][min_length-1][y] = prob_transform_current[z][y]+RPK.range_prob_log(present_note+y-6)+math.log(RPK.note_prob_in_key(present_note+y-6, keyIndex))
                prob_transform_current[z][y] = -100000
            path_end_on_keep_past[min_length-1][y] = path_end_on_keep_current[y]
            path_end_on_keep_current[y] = []
            for z in range(len(transformations)):
                path_end_on_transform_past[z][min_length-1][y] = path_end_on_transform_current[z][y]
                path_end_on_transform_current[z][y] = []

    #Return path with max probability
    maxIndexKeep = 0
    for x in range(height):
        if (prob_keep_past[min_length-1][x] > prob_keep_past[min_length-1][maxIndexKeep]):
            maxIndexKeep = x

    maxIndexTransform = 0
    maxIndexTypeTransform = 0
    for z in range(len(transformations)):
        for x in range(height):
            if (prob_transform_past[z][min_length-1][x] > prob_transform_past[maxIndexTypeTransform][min_length-1][maxIndexTransform]):
                maxIndexTransform = x
                maxIndexTypeTransform = z

    best_path = []
    if (prob_keep_past[min_length-1][maxIndexKeep] > prob_transform_past[maxIndexTypeTransform][min_length-1][maxIndexTransform]):
        best_path = list(path_end_on_keep_past[min_length-1][maxIndexKeep])
        best_path.append(maxIndexKeep)
    else:
        best_path = list(path_end_on_transform_past[maxIndexTypeTransform][min_length-1][maxIndexTransform])
        best_path.append(maxIndexTransform)

    new_int_notes = [0 for x in range(len(int_notes))]
    for x in range(len(int_notes)):
        new_int_notes[x] = int_notes[x]+best_path[x]-6
    return new_int_notes

    reversed_list = [0 for x in range(len(int_notes))]
    reversed_list[0] = maxIndex
    for x in range(len(int_notes)-1):
        reversed_list[x+1] = matrix[len(int_notes)-x-2][maxIndex]
        maxIndex = reversed_list[x+1]
    ordered_list = [0 for x in range(len(int_notes))]
    for x in range(len(int_notes)):
        ordered_list[x] = reversed_list[len(int_notes)-x-1]
    new_int_notes = [0 for x in range(len(int_notes))]
    for x in range(len(int_notes)):
        new_int_notes[x] = int_notes[x]+ordered_list[x]-6
    return new_int_notes

#return the best paths of given length, only using the tranform given by the array parameter
def simulate_best_paths(start_probs, transform_array, length, start_paths, start_note, keyIndex, int_notes):
    past_probs = list(start_probs)
    current_probs = [-100000 for x in range(height)]
    past_paths = [list(start_paths[x]) for x in range(height)]
    current_paths = [[] for x in range(height)]

    for x in range(length):
        present_note = int_notes[start_note+x+1]

        for y in range(height):
            last_note = int_notes[start_note+x]+y-6
            diff = abs(present_note-last_note)
            new_note = -1
            if (present_note-last_note <= 0):
                new_note = present_note+(transform_array[(diff+8)%8])
            else:
                new_note = present_note-(transform_array[(diff+8)%8])
            if RPK.note_prob_in_key(new_note, keyIndex) < 0.02:
                if (RPK.note_prob_in_key(new_note+1, keyIndex) > RPK.note_prob_in_key(new_note-1, keyIndex)):
                    new_note = new_note+1
                else:
                    new_note = new_note-1
            #replace if better
            if current_probs[new_note-present_note+6] < past_probs[y]+RPK.proximity_prob_log(new_note, last_note):
                current_probs[new_note-present_note+6] = past_probs[y]+RPK.proximity_prob_log(new_note, last_note)
                copy = list(past_paths[y])
                copy.append(y)
                current_paths[new_note-present_note+6] = copy

        for y in range(height):
            past_probs[y] = current_probs[y]+RPK.range_prob_log(present_note+y-6)+math.log(RPK.note_prob_in_key(present_note+y-6, keyIndex))
            current_probs[y] = -100000
            past_paths[y] = current_paths[y]
            current_paths[y] = []

    last_note = int_notes[start_note+length]
    for y in range(height):
        past_probs[y] = past_probs[y]-RPK.range_prob_log(last_note+y-6)-math.log(RPK.note_prob_in_key(last_note+y-6, keyIndex))

    return (past_probs, past_paths)