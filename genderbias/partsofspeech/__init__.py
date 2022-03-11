#!/usr/bin/env python3

"""
Check for parts of speech that weaken the recommendation

Letters for women are more likely to use adjectives instead of nouns.

Goal: develop code that can read text for the presence of nouns that highlight roles/positions (eg leader, researcher).
If position nouns are absent, return a summary statement that directs the author to consider using nouns to strengthen
the letter. Must differentiate between descriptions that use adjectives, verbs, or weaken the position noun (ie she was
involved in research, she taught instead of she was a researcher/teacher)

"""


import os
import re
import nltk
from genderbias.detector import Detector, Flag, Issue, Report

_dir = os.path.dirname(__file__)



class PartofSpeechDetector(Detector):
    """
    This detector looks for wording that weakens or distances a person from the action or position being described,
    based on literature description of this issue (Trix & Psenka 2003). For example, prepositions following verbs
    ("she was involved in x") tend to weaken the statement, rather than verbs alone ("she did x").

    """


    def get_report(self, doc):
        """
        Generates a report on the text that checks for part of speech use that distances from the action or position.
        Based on tools from bigrams analysis (nltk) and part of speech tagging (upenn treebank).

        These are phrases like "she was involved in research" rather than "she was a researcher" or "she researched x"

        Arguments:
            doc (Document): The document to check

        Returns:
            Report

        """
        report = Report("Parts of Speech")
        text = doc.text()

        word_pairs = list(nltk.bigrams(text))
        word_pos = nltk.pos_tag(text)
        preposition_pairs = []
        for count, item in enumerate(word_pos):
            if item[1][0] == 'V':
                if word_pos[count + 1][1][0] == 'V':
                    if word_pos[count + 2][1] == 'IN':
                        preposition_pairs.append(word_pairs[count][0])
                        preposition_pairs.append(word_pairs[count][1])
        _prep_pairs_regex = "(?:"
        for count, pair in enumerate(preposition_pairs):
            if count < len(preposition_pairs) - 2:
                _prep_pairs_regex = _prep_pairs_regex + preposition_pairs[count] + " " + preposition_pairs[
                    count + 1] + "|"
            else:
                if count == len(preposition_pairs) - 2:
                    _prep_pairs_regex = _prep_pairs_regex + preposition_pairs[count] + " " + preposition_pairs[
                        count + 1] + ")"
        PART_OF_SPEECH_REGEXES = [fr"\s(\w+est[^\.]*{_prep_pairs_regex})"]
        for regex in PART_OF_SPEECH_REGEXES:
            for match in re.finditer(regex, text):
                report.add_flag(
                    Flag(
                        match.span()[0],
                        match.span()[1],
                        Issue(
                            "Part of Speech",
                            "This phrase appears to distance the person from the position/action described.",
                        ),
                    )
                )
        return report
