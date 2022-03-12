#!/usr/bin/env python3

"""
Description: Letters for women are less likely to contain superlatives (best, most, top, greatest). If they do contain
superlatives, they usually describe women in the context of emotional terms (eg most compassionate). See "conditional
superlatives" detector for more on gendered superlatives.

Goal: develop code that can read for superlatives. If text lacks superlatives, return a summary statement that directs
author to add superlatives. If superlatives are present, determine if the preceding word is a possessive and if so,
do not count this as a superlative (eg "she does her best" rather than "she is the best").

"""

import os
import re
import nltk
from nltk.corpus import wordnet as wn
from genderbias.detector import Detector, Flag, Issue, Report

_dir = os.path.dirname(__file__)


class RaisesDoubtDetector(Detector):
    """
    This detector looks for superlatives in the text using superlative synsets. If superlatives are present, the
    preceding word is checked, and if it is a possessive, the superlative is not counted (ie 'she does her best' is not
    a superlative).

    """

    def get_report(self, doc):
        """
        Generates a report on the text based on the superlatives used (ie best, most, top, greatest), not including
        possessives (ie "her best"). If no superlatives are used, prompts the user to add superlatives.

        The natural language toolkit wordnet tool is used to access synsets of words with similar uses to look for
        words with similar meanings.

        Arguments:
            doc (Document): The document to check

        Returns:
            Report

        """
        report = Report("Raises Doubt")
        text = doc.text()

        lowercase_text = nltk.Text(word.lower() for word in text)
        word_pos = nltk.pos_tag(text)
        superlatives_in_text = []
        superlatives_synsets = ['better.s.03', 'estimable.s.02', 'adept.s.01', 'incredible.a.01', 'greatest.s.01',
                                'great.s.02', 'excellent.s.01', 'phenomenal.s.02', 'fantastic.s.02', 'ace.s.01',
                                'ever.r.01', 'most.r.01']
        for count, word in enumerate(lowercase_text):
            for synset in superlatives_synsets:
                if word in wn.synset(synset).lemma_names():
                    if word_pos[count - 1][1] != 'PRP$':
                        superlatives_in_text.append(word)
        if len(superlatives_in_text) == 0:
            report.set_summary(
                    "This document contains few or no superlatives "
                    + f"(best, most, greatest, etc) that could increase the strength "
                    + f"of the letter. Consider adding superlatives as appropriate."
            )
        else:
            superlatives_in_text_string = ""
            if len(superlatives_in_text) == 1:
                superlatives_in_text_string = superlatives_in_text[0]
            else:
                if len(superlatives_in_text) == 2:
                    superlatives_in_text_string = superlatives_in_text[0] + " and " + superlatives_in_text[1]
                else:
                    for count, word in enumerate(superlatives_in_text):
                        if count < len(superlatives_in_text) - 1:
                            superlatives_in_text_string = superlatives_in_text_string + word + ", "
                        else:
                            superlatives_in_text_string = superlatives_in_text_string + "and " + word
            report.set_summary(
                "This document contains superlatives that likely increase "
                + f"the strength of the letter, including "
                + superlatives_in_text_string + "."
            )
        return report
