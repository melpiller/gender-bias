#!/usr/bin/env python3

"""
Description: Letters for women are more likely to raise doubt

Goal: develop code that can read text for phrases that raise doubt and return a summary statement that directs the
author to review the identified phrases and consider removing them.

"""

import os
import re
import nltk
from nltk.corpus import wordnet as wn
from genderbias.detector import Detector, Flag, Issue, Report

_dir = os.path.dirname(__file__)


class RaisesDoubtDetector(Detector):
    """
    This detector looks for phrases that raise doubt, including negative language, hedges, faint praise,
    and irrelevancies. For more information, see Trix & Psenka 2003 section on Doubt Raisers. These categories
    could be further divided into different detectors, but here they are combined.

    """

    def get_report(self, doc):
        """
        Generates a report on the text that checks for language that raises doubt, including negative language (eg
        "she is not the best candidate"), hedges (eg "she seems to work hard"), faint praise (eg "she performed well
        despite a lack of confidence"), and irrelevancies (eg "she is friends with my wife"). These sections are
        delineated in case it makes more sense to split them into separate detectors.

        The natural language toolkit wordnet tool is used to access synsets of words with similar meanings to target
        the intended meaning of the words."

        Arguments:
            doc (Document): The document to check

        Returns:
            Report

        """
        report = Report("Raises Doubt")
        text = doc.text()

        lowercase_text = nltk.Text(word.lower() for word in text)
        doubt_raising_words = []

        # First we'll look for negative language using syntax sets
        neg_words = wn.synset('not.r.01').lemma_names()
        neg_words_in_text = []
        for x in lowercase_text:
            if x in neg_words:
                neg_words_in_text.append(x)
        for each in neg_words_in_text:
            doubt_raising_words.append(each)

        # Next we'll look at hedges (eg "she seems to be competent" vs "she is competent"
        hedged_words_in_text = []
        hedged_words = wn.synset('look.v.02').lemma_names()
        hedged_plurals = []
        for each in hedged_words:
            hedged_plurals.append(each + 's')
        for a in hedged_plurals:
            hedged_words.append(a)
        for x in lowercase_text:
            if x in hedged_words:
                hedged_words_in_text.append(x)
        for each in hedged_words_in_text:
            doubt_raising_words.append(each)

        # Next we'll look for faint praise. This portion returns words constituting faint praise based on synsets of
        # words outlined by Trix & Psenka.Possible future developments include some consideration of number or ratios
        # of dependent clauses, etc requiring more advanced sentence mapping.
        faint_praise_in_text = []
        faint_praise_synsets = ['average.s.01', 'average.s.02', 'average.s.03', 'average.s.04', 'median.s.01',
                                'lack.n.01']
        for x in lowercase_text:
            for y in faint_praise_synsets:
                if x in wn.synset(y).lemma_names():
                    if x != 'want':
                        faint_praise_in_text.append(x)
        for each in faint_praise_in_text:
            doubt_raising_words.append(each)

        # Next we'll look for irrelevant information, here including religion and spousal relationships. This
        # could be expanded to include other categories of information
        irrelevancies_in_text = []
        irrelevancies_synsets = ['church.n.03', 'religion.n.01', 'religious.s.01', 'wife.n.01', 'spouse.n.01',
                                 'husband.n.01']
        religion_synsets = wn.synset('religion.n.01').hyponyms()
        for synset in religion_synsets:
            to_add = str(synset)[8:-2]
            irrelevancies_synsets.append(to_add)
        for x in lowercase_text:
            for y in irrelevancies_synsets:
                if x in wn.synset(y).lemma_names():
                    if x != 'benedict':
                        irrelevancies_in_text.append(x)
        for each in irrelevancies_in_text:
            doubt_raising_words.append(each)

        _doubt_raisers_regex = "(?:"
        for count, pair in enumerate(doubt_raising_words):
            if count < len(doubt_raising_words) - 1:
                _doubt_raisers_regex = _doubt_raisers_regex + doubt_raising_words[count] + "|"
            else:
                if count == len(doubt_raising_words) - 1:
                    _neg_words_regex = _doubt_raisers_regex + doubt_raising_words[count] + ")"
        DOUBT_RAISERS_REGEXES = [fr"\s(\w+est[^\.]*{_doubt_raisers_regex})"]
        for regex in DOUBT_RAISERS_REGEXES:
            for match in re.finditer(regex, text):
                report.add_flag(
                    Flag(
                        match.span()[0],
                        match.span()[1],
                        Issue(
                            "Raises Doubt",
                            "This phrase appears to raise doubt, either through negative language, hedging, faint "
                            "praise, or irrelevant information. Consider revising to reduce doubt.",
                        ),
                    )
                )
        return report
