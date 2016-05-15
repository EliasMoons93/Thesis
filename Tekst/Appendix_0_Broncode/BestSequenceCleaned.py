__author__ = 'Elias'
import RPK
import math

zero = [0, 0, 0, 0, 0, 0, 0, 0]
transformations = [[1, 1, 2, 3, 5, -4, 1, -3],[5, -4, 1, -3, 1, 1, 2, 3]]

def bestTransformed(int_notes, keyIndex):
    #transformation from -6 to +7
    past = [-100, -100, -100, -100, -100, -100, 0, -100, -100, -100, -100, -100, -100, -100]
    current = [-100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100]
    matrix = [[0 for x in range(len(past))] for y in range(len(int_notes))]
    for x in range(len(int_notes)-1):
        present_note = int_notes[x+1]

        #case of keeping original
        for y in range(len(past)):
            last_note = int_notes[x]+y-6
            diff = abs(present_note-last_note)
            new_note = present_note+(zero[(diff+8)%8])
            if current[new_note-present_note+6] < past[y]+RPK.proximity_prob_log(new_note, last_note):
                current[new_note-present_note+6] = past[y]+RPK.proximity_prob_log(new_note, last_note)
                matrix[x][new_note-present_note+6] = y

        #case of transform
        for t in range(len(transformations)):
            for y in range(len(past)):
                last_note = int_notes[x]+y-6
                diff = abs(present_note-last_note)
                new_note = -1;
                if (present_note-last_note <= 0):
                    new_note = present_note+(transformations[t][(diff+8)%8])
                else:
                    new_note = present_note-(transformations[t][(diff+8)%8])
                if RPK.note_prob_in_key(new_note, keyIndex) < 0.02:
                    if (RPK.note_prob_in_key(new_note+1, keyIndex) > RPK.note_prob_in_key(new_note-1, keyIndex)):
                        new_note = new_note+1
                    else:
                        new_note = new_note-1
                if current[new_note-present_note+6] < past[y]+RPK.proximity_prob_log(new_note, last_note):
                    current[new_note-present_note+6] = past[y]+RPK.proximity_prob_log(new_note, last_note)
                    matrix[x][new_note-present_note+6] = y

        #reinitialize arrays
        for y in range(len(past)):
            past[y] = current[y]+RPK.range_prob_log(present_note+y-6)+math.log(RPK.note_prob_in_key(present_note+y-6, keyIndex))
            current[y] = -10000000;

    #look at which endpoint had the most probable path and reconstruct that most probable path
    maxIndex = 0
    for x in range(len(past)):
        if (past[x] > past[maxIndex]):
            maxIndex = x
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

