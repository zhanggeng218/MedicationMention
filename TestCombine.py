# for developing functions combining same drug mentions
from PickEntities import *

def catEntities(xmlfname, txtfname):
    textfile = open(txtfname, "r").read()
    medications, sentences, doses = travelTrough(xmlfname, txtfname)

    addSentenceNumber_new(sentences, medications, doses)

    combinedentities = combinedEntities(medications, doses)


    # pprint.pprint(combinedentities)

    newentities = {}
    entity_keys = list(combinedentities.keys())
    entity_keys.sort()
    sz = len(entity_keys)

    # determine if there is a need to close the parentheses
    need_to_close = False
    # determine if the the two are the same
    previous_same = False
    previous_ind = 0
    # keep track of the position covered
    covered_position = 0

    for i in range(sz):
        cur_type = combinedentities[entity_keys[i]]["type"]
        cur_beg = combinedentities[entity_keys[i]]["beg"]
        cur_end = combinedentities[entity_keys[i]]["end"]


        if i < sz - 1:
            next_type = combinedentities[entity_keys[i + 1]]["type"]
            next_beg = combinedentities[entity_keys[i + 1]]["beg"]
            next_end = combinedentities[entity_keys[i + 1]]["end"]
            if cur_type == "medication" and next_type == "medication" and (next_beg - cur_end) < 4:

                # regex for determining if two adjacent medications are the same
                seperated_medication = re.compile(r'[^ (]',re.IGNORECASE)
                m = seperated_medication.search(textfile[cur_end : next_beg])

                # regex for determining if there is a left parentheses between two medications
                contains_left_parentheses = re.compile(r'\(')
                m1 = contains_left_parentheses.search(textfile[cur_end : next_beg])

                contains_right_parentheses = re.compile(r'\)')

                # if the same medications, combine them
                # TODO: also see if there is need to close any parentheses
                if m == None:
                    # if the previous two are also the same, no need to create a new entry in newentities
                    # only do the combining
                    if previous_same:
                        # for closing parentheses
                        if m1 != None:
                            m2 = contains_right_parentheses.search(textfile[newentities[previous_ind]['beg'] : ])
                            end = m2.start() + newentities[previous_ind]['beg'] + 1
                        else:
                            m3 = contains_left_parentheses.search(textfile[cur_end : ])
                            m4 = contains_right_parentheses.search(textfile[cur_end : ])
                            if (m3 == None and m4 != None) or (m4 != None and m4 != None and m3.start() > m4.start()):
                                end = m4.start() + cur_end + 1
                                pprint.pprint(textfile[newentities[previous_ind]['beg'] : end])
                            else:
                                end = next_end

                        newentities[previous_ind]['content'] = textfile[newentities[previous_ind]['beg'] : end]
                        newentities[previous_ind]['end'] = end
                        covered_position = end

                    else:
                        # for closing parentheses
                        if m1 != None:
                            m2 = contains_right_parentheses.search(textfile[cur_beg : ])
                            end = m2.start() + cur_beg + 1
                        else:
                            end = next_end

                        newentities[cur_beg] = combinedentities[cur_beg]
                        newentities[cur_beg]['content'] = textfile[cur_beg : end]
                        newentities[cur_beg]['end'] = end
                        previous_same = True
                        previous_ind = cur_beg
                        covered_position = end

                # if not the same, add the entity to newentities, set previous_same to False
                else:
                    if cur_beg >= covered_position:
                        newentities[cur_beg] = combinedentities[cur_beg]
                        covered_position = cur_end
                    previous_same = False
            else:
                if cur_beg >= covered_position:
                    newentities[cur_beg] = combinedentities[cur_beg]
                    covered_position = cur_end
                previous_same = False
        elif cur_beg >= covered_position and not previous_same:
            newentities[cur_beg] = combinedentities[cur_beg]


filename = "../Resources/MedicationMention/XML_Files/n_241468.xml"
textname = "../Resources/MedicationMention/Original_Files/n_241468"
catEntities(filename, textname)