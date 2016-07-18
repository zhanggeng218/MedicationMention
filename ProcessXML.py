#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
# import re
# import codecs
# import json
# from collections import defaultdict


def travelTrough(filename, textname):
    xml_file = open(filename, "r")
    textfile = open(textname, "r").read()
    medications = []
    sentences = []
    doses = []

    for event, elem in ET.iterparse(xml_file, events=("start",)):

        if elem.tag == "{http:///org/apache/ctakes/typesystem/type/textsem.ecore}MedicationMention":
            medications.append([textfile[int(elem.attrib["begin"]):int(elem.attrib["end"])], int(elem.attrib["begin"])])
        elif elem.tag == "{http:///org/apache/ctakes/typesystem/type/textspan.ecore}Sentence":
            sentences.append([int(elem.attrib["begin"]), int(elem.attrib["end"])])
        elif elem.tag == "{http:///org/apache/ctakes/typesystem/type/textsem.ecore}MeasurementAnnotation":
            doses.append([textfile[int(elem.attrib["begin"]):int(elem.attrib["end"])], int(elem.attrib["begin"])])

    xml_file.close()
    return medications, sentences, doses

def findSentenceNumber(sentences, entities):
    sentenceNum_entity_pair = {}
    for entity in entities:
        for sen_ind, sentence in enumerate(sentences):
            if entity[1] >= sentence[0] and entity[1] <= sentence[1]:
                if sen_ind in sentenceNum_entity_pair: sentenceNum_entity_pair[sen_ind].append(entity[0])
                else: sentenceNum_entity_pair[sen_ind] =[entity[0]]

    return sentenceNum_entity_pair

def combineMedicationAndDose(medication_pairs, dose_pairs):
    medication_sentences = set(medication_pairs.keys())
    dose_sentences = set(dose_pairs.keys())

    common = set.intersection(medication_sentences, dose_sentences)
    medications_only = medication_sentences - common
    doses_only = dose_sentences - common


    mentions_medication = []
    mentions_dose = []
    mentions_complete = []
    dlm = "|"
    for sen_num in medications_only:
        mentions_medication.append([dlm.join(medication_pairs[sen_num]), "UN"])

    for sen_num in doses_only:
        mentions_dose.append(["UN", dlm.join(dose_pairs[sen_num])])

    for sen_num in common:
        mentions_complete.append([dlm.join(medication_pairs[sen_num]), dlm.join(dose_pairs[sen_num])])

    return mentions_complete, mentions_medication, mentions_dose




filename = "testout.xml"
textname = "11995"
medications, sentences, doses = travelTrough(filename, textname)

medication_pair = findSentenceNumber(sentences, medications)
doses_pair = findSentenceNumber(sentences, doses)

mentions_all, mentions_medication, mentions_doses = combineMedicationAndDose(medication_pair, doses_pair)

print("Same sentence:")
pprint.pprint(mentions_all)
print("\n")

print("Only drugs:")
pprint.pprint(mentions_medication)
print("\n")

print("Only doses:")
pprint.pprint(mentions_doses)

