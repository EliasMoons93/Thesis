__author__ = 'Elias'
import math

#probabilities of note functions in major and minor keys
key_major_prob = [0.184, 0.001, 0.155, 0.003, 0.191, 0.109, 0.005, 0.214, 0.001, 0.078, 0.004, 0.055]
key_minor_prob = [0.192, 0.005, 0.149, 0.179, 0.002, 0.144, 0.002, 0.201, 0.038, 0.012, 0.053, 0.022]

#which key, given amount of sharps +7
key_major = [11, 6, 1, 8, 3 ,10 ,5 ,0, 7, 2, 9, 4, 11, 6, 1]
key_minor = [8, 3, 10, 5, 0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10]

#calculat the sum of the probs in a given score
def score_val(score):
    flatscore = score.flat
    keySign = flatscore.getElementsByClass('KeySignature')
    keyIndex = keySign[0].sharps + 7
    #print('Sharps: ' + str(keyIndex))
    notes = flatscore.pitches
    int_notes = [0 for x in range(len(notes))]
    for i in range(len(notes)):
        int_notes[i] = int(pitch_number(notes[i].nameWithOctave))
    return calculate_probability(int_notes, keyIndex)

#calculate the sum of the probs of a series of notes in a given key
def calculate_probability(notes, keyIndex):
    key_maj = key_major[keyIndex]
    major_prob = calculate_prob(notes, key_maj, True)
    key_min = key_minor[keyIndex]
    minor_prob = calculate_prob(notes, key_min, False)
    return math.log(0.88*math.exp(major_prob) + 0.12*math.exp(minor_prob))

#calculate the sum of the probs of a series of notes in a given key and whether it is major or not
def calculate_prob(notes, key, major):
    p = normalized_prob_log_first(notes[0], key, major)
    for i in range(1, len(notes)):
        note = notes[i]
        p += normalized_prob_log(note, key, major,notes[i-1])
    return p

#calculate the log of the normalized probability of a the first note in a given key (no previous note)
def normalized_prob_log_first(note, key, major):
    prob_notes = [0 for x in range(60)]
    total = 0
    for i in range(0, 60):
        p = key_prob(i+38, key, major)*range_prob(i+38)
        prob_notes[i] = p
        total += p
    return math.log(prob_notes[note-38]/total)

#calculate the log of the normalized probability of a given note in a given key, and a previous note
def normalized_prob_log(note, key, major, previous):
    prob_notes = [0 for x in range(60)]
    total = 0
    for i in range(0, 60):
        p = key_prob(i+38, key, major)*range_prob(i+38)*proximity_prob(i+38, previous)
        prob_notes[i] = p
        total += p
    return math.log(prob_notes[note-38]/total)

#calculate the log of the proximity score of a given current note and previous note
def proximity_prob_log(note, previous):
    return math.log(proximity_prob(note, previous))

#calculate the proximity score of a given current note and previous note
def proximity_prob(note, previous):
    return normal_prob(previous, 7.2, note)

#calculate the probability of a given note in a given key
def note_prob_in_key(note, keyIndex):
    key_maj = key_major[keyIndex]
    major_prob = key_prob(note, key_maj, True)
    key_min = key_minor[keyIndex]
    minor_prob = key_prob(note, key_min, False)
    return (0.88*major_prob + 0.12*minor_prob)

#calculate the log of the probability of a given note, key and boolean to  indicate whether the scale is major or minor
def key_prob_log(note, key, major):
    return math.log(key_prob(note, key, major))

#calculate the key probability of a given note, key and boolean to indicate whether the scale is major or minor
def key_prob(note, key, major):
    index = (((note - key + 12) % 12) + 12) % 12
    if (major == True):
        return key_major_prob[index]
    else:
        return key_minor_prob[index]

#calculate the log of the prob of a given note in integer representation
def range_prob_log(note):
    return math.log(range_prob(note))

#calculate the range probability of a given note in integer representation
def range_prob(note):
    p = 0
    for x in range(38, 98):
        p += normal_prob(68, 13.2, x)*normal_prob(x, 29, note)
    return p

#mean mu, variance sigma_sq, value x
def normal_prob (mu, sigma_sq, x):
    return (1/(math.sqrt(sigma_sq*2*math.pi)))*math.exp(-(x-mu)*(x-mu)/(2*sigma_sq))

#integer value of given note in note+octave representation
def pitch_number(pitch):
    octave = pitch[len(pitch)-1:]
    note = pitch[:len(pitch)-1]
    val = (int(octave)+1)*12 + intValue(note)
    return str(val)

#integer values (modulo 12 )of all possible notes
def intValue(name):
    if (name == 'C'):
        return 0
    elif (name == 'C#'):
        return 1
    elif (name == 'D-'):
        return 1
    elif (name == 'D'):
        return 2
    elif (name == 'D#'):
        return 3
    elif (name == 'E-'):
        return 3
    elif (name == 'E'):
        return 4
    elif (name == 'E#'):
        return 5
    elif (name == 'F-'):
        return 4
    elif (name == 'F'):
        return 5
    elif (name == 'F#'):
        return 6
    elif (name == 'G-'):
        return 6
    elif (name == 'G'):
        return 7
    elif (name == 'G#'):
        return 8
    elif (name == 'A-'):
        return 8
    elif (name == 'A'):
        return 9
    elif (name == 'A#'):
         return 10
    elif (name == 'B-'):
         return 10
    elif (name == 'B'):
        return 11
    elif (name == 'B#'):
        return 0
    elif (name == 'C-'):
        return 11
    else:
        return -1