#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import os
import re

# import re
# import codecs
# import json
# from collections import defaultdict

# find medications, and doses
# also find sentence with location indices
#
# medications are in a list of:
#   {'beg': 4659, 'end': 4666, 'medword': 'insulin'}
#
# doses are in a list of:
#   {'beg': 1334, 'dose': '4 pound', 'end': 1341}

RELIST = [
          re.compile(r'[-.\d]+ \bunits\b',re.IGNORECASE),
          re.compile(r'[-.\d]+ \btablets\b', re.IGNORECASE),
          re.compile(r'\bsliding scale\b', re.IGNORECASE),
          re.compile(r'[-.\d]+ \btab\b', re.IGNORECASE)
         ]


def travelTrough(filename, textname):
    xml_file = open(filename, "r")
    textfile = open(textname, "r").read()
    medications = []
    sentences = []
    doses = []

    for event, elem in ET.iterparse(xml_file, events=("start",)):

        # if elem.tag == "{http:///org/apache/ctakes/typesystem/type/textsem.ecore}MedicationMention":
        if elem.tag == "org.apache.ctakes.typesystem.type.textsem.MedicationMention":
            meditem = {}
            beg = int(elem.attrib["begin"])
            end = int(elem.attrib["end"])
            medword = textfile[int(elem.attrib["begin"]):int(elem.attrib["end"])]
            meditem["beg"] = beg
            meditem["end"] = end
            meditem["content"] = medword
            meditem["type"] = "medication"
            medications.append(meditem)
        # elif elem.tag == "{http:///org/apache/ctakes/typesystem/type/textspan.ecore}Sentence":
        elif elem.tag == "org.apache.ctakes.typesystem.type.textspan.Sentence":
            sentences.append([int(elem.attrib["begin"]), int(elem.attrib["end"])])
        # elif elem.tag == "{http:///org/apache/ctakes/typesystem/type/textsem.ecore}MeasurementAnnotation":
        elif elem.tag == "org.apache.ctakes.typesystem.type.textsem.MeasurementAnnotation":
            doseitem = {}
            beg = int(elem.attrib["begin"])
            end = int(elem.attrib["end"])
            dose = textfile[int(elem.attrib["begin"]):int(elem.attrib["end"])]
            doseitem["beg"] = beg
            doseitem["end"] = end
            doseitem["content"] = dose
            doseitem["type"] = "dose"
            doses.append(doseitem)

    # find doses missed by cTakes
    findOtherDoses(textfile, doses)

    xml_file.close()
    return medications, sentences, doses

# find doses not detected by cTakes
def findOtherDoses(text, doses):
    for r in RELIST:
        iters = r.finditer(text)
        for iter in iters:
            doseitem = {}
            doseitem["beg"] = iter.span()[0]
            doseitem["end"] = iter.span()[1]
            doseitem["content"] = iter.group()
            doseitem["type"] = "dose"
            doses.append(doseitem)

def addSentenceNumber_new(sentences, entities, *args):
    list_of_entities = [entities]
    for arg in args:
        list_of_entities.append(arg)
    for ents in list_of_entities:
        for entity in ents:
            for sen_ind, sentence in enumerate(sentences):
                if entity["beg"] >= sentence[0] and entity["end"] <= sentence[1]:
                    entity["sen_id"] = sen_ind

# combine the entities input to the function into a dictionary
# the key is the begining postition
def combinedEntities(entities, *args):
    ret_entites = {}
    original_entities = [entities]

    for arg in args: original_entities.append(arg)

    for ents in original_entities:
        for entity in ents:
            ret_entites[entity["beg"]] = entity

    return ret_entites

def findmatch(combinedentities, sentence_threshold):
    already_picked = set()
    matches = {}
    entity_keys = list(combinedentities.keys())
    entity_keys.sort()
    sz = len(entity_keys)

    for i in range(sz):
        ind = entity_keys[i]
        type = combinedentities[ind]["type"]
        sen_id = combinedentities[ind]["sen_id"]

        if type == "medication":

            already_picked.add(ind)
            if i < sz - 1:
                next_ind = entity_keys[i + 1]
                next_type = combinedentities[next_ind]["type"]
                next_sen_id = combinedentities[next_ind]["sen_id"]
                if next_type == "dose" and (next_sen_id - sen_id) <= sentence_threshold:
                    matches[ind] = next_ind
                    already_picked.add(next_ind)
                elif i > 0:
                    prev_ind = entity_keys[i - 1]
                    prev_type = combinedentities[prev_ind]["type"]
                    prev_sen_id = combinedentities[prev_ind]["sen_id"]
                    if (not (prev_ind in already_picked)) and prev_type == "dose" and (sen_id - prev_sen_id) <= sentence_threshold:
                        matches[ind] = prev_ind
                        already_picked.add(prev_ind)
                    else: matches[ind] = -1
                else:
                    matches[ind] = -1
            else:
                prev_ind = entity_keys[i - 1]
                prev_type = combinedentities[prev_ind]["type"]
                prev_sen_id = combinedentities[prev_ind]["sen_id"]
                if (not (prev_ind in already_picked)) and prev_type == "dose" and (sen_id - prev_sen_id) <= sentence_threshold:
                    matches[ind] = prev_ind
                    already_picked.add(prev_ind)
                else: matches[ind] = -1

    return matches

def fillinEntityName(matches, combinedentities):
    output = []
    for key in matches:
        entry = combinedentities[key]["content"] + " | "
        entry += combinedentities[matches[key]]["content"] if matches[key] >= 0 else "UN"
        output.append(entry)
    return output

def processBatchFiles(original_folder_path, XML_folder_path, output_folder_path, out_prefix):
    for fname in os.listdir(XML_folder_path):
        if "n_" in fname:
            xml_name = XML_folder_path + "/" + fname
            ori_name = original_folder_path + "/" + fname.strip(".xml")
            out_name = output_folder_path + "/" + out_prefix + fname.strip(".xml")

            medications, sentences, doses = travelTrough(xml_name, ori_name)
            addSentenceNumber_new(sentences, medications, doses)
            combinedentities = combinedEntities(medications, doses)
            matches = findmatch(combinedentities, sentence_threshold=1)
            output = fillinEntityName(matches, combinedentities)

            o = open(out_name, 'w')
            for item in output:
                o.write(item)
                o.write("\n")
            o.close()

# def catEntities

def debugOneFile(xmlfname, txtfname):
    medications, sentences, doses = travelTrough(xmlfname, txtfname)

    addSentenceNumber_new(sentences, medications, doses)

    combinedentities = combinedEntities(medications, doses)
    matches = findmatch(combinedentities, sentence_threshold=1)
    output = fillinEntityName(matches, combinedentities)
    pprint.pprint(output)



# debug with one file
filename = "./XML_Files/n_241468.xml"
textname = "./Original_Files/n_241468"
debugOneFile(filename, textname)

# process all
# xmlfolder = os.getcwd() + "/XML_Files"
# orifolder = os.getcwd() + "/Original_Files"
# outfolder = os.getcwd() + "/Output_Files"
# out_prefix = "DrugMentions_"
# processBatchFiles(orifolder, xmlfolder, outfolder, out_prefix)

