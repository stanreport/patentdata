# -*- coding: utf-8 -*-
from nltk import word_tokenize, sent_tokenize
from patentdata.models.basemodels import BaseTextSet, BaseTextBlock
from patentdata.models.lib.utils import check_list
import string


class PatentDoc:
    """ Object to model a patent document. """
    def __init__(
            self,
            claimset,
            description=None,
            figures=None,
            title=None,
            classifications=None,
            number=None
    ):
        """ description, claimset and figures are objects as below. """
        self.description = description
        self.claimset = claimset
        self.figures = figures
        self.title = title
        self.classifications = classifications
        self.number = number

    def __repr__(self):
        return (
            "<Patent Document object for {0}, "
            "title: {1} - containing: "
            "description with {2} paragraphs and "
            "claimset with {3} claims; "
            "classifications: {4}"
            ).format(
                self.number,
                self.title,
                self.description.paragraph_count,
                self.claimset.claim_count,
                self.classifications
            )


    @property
    def text(self):
        """  Get text of patent document as string. """
        if self.description:
            desc_text = self.description.text
        else:
            desc_text = ""
        return "\n\n".join([desc_text, self.claimset.text])


    @property
    def unfiltered_counter(self):
        """ Return token counts across claims and description. """
        return (
            self.description.unfiltered_counter +
            self.claimset.unfiltered_counter
        )

    @property
    def character_counter(self):
        """ Return token counts across claims and description. """
        return (
            self.description.character_counter +
            self.claimset.character_counter
        )

    def reading_time(self, reading_rate=100):
        """ Return estimate for time to read. """
        # Words per minute = between 100 and 200
        return len(word_tokenize(self.text)) / reading_rate

    def bag_of_words(
        self, clean_non_words=True, clean_stopwords=True, stem_words=True
    ):
        """ Return tokens from description and claims. """
        joined_bow = self.description.bag_of_words(
            clean_non_words, clean_stopwords, stem_words
            ) + self.claimset.bag_of_words(
            clean_non_words, clean_stopwords, stem_words
            )
        remove_duplicates = list(set(joined_bow))
        return remove_duplicates

    def string2int(self, filter_printable=True):
        """ Convert text of document into a list of integers representing
        its characters.

        If filter_printable is true limit to 98 printable characters."""
        if filter_printable:
            ints = [
                ord(c) if c in string.printable[:-2] else ord(" ")
                for c in self.text
                ]
        else:
            ints = [ord(c) for c in self.text]
        return ints

    def string2printint(self):
        """ Convert a string into a list of integers representing
        its printable characters."""
        char_map = {c: i for i, c in enumerate(string.printable[:-2])}
        return [
            char_map[c] if c in char_map.keys() else char_map[" "]
            for c in self.text
        ]

    @classmethod
    def printint2string(cls, doc_as_ints):
        """ Reconstruct document string from list of integers."""
        char_map = {i: c for i, c in enumerate(string.printable[:-2])}
        return "".join([char_map[i] for i in doc_as_ints])


class Paragraph(BaseTextBlock):
    """ Object to model a paragraph of a patent description. """

    @property
    def sentences(self):
        """ If sentences have not been segmented, segment when accessed. """
        try:
            return self._sentences
        except AttributeError:
            self._sentences = [Sentence(s) for s in sent_tokenize(self.text)]
            return self._sentences


    @property
    def sentence_count(self):
        return len(self.sentences)


class Sentence(BaseTextBlock):
    """ Object to model a sentence of a patent description. """

    pass


class Description(BaseTextSet):
    """ Object to model a patent description. """

    def __init__(self, initial_input):
        """ Initialise object.

        :param initial_input: Set of Paragraph objects, str or list
        of strings
        :type initial_input: list of Paragraph/str or str
        :return: None
        """
        input_list = check_list(initial_input)

        # Need split large string into paragraphs method here

        para_list = []
        for para in input_list:
            if not isinstance(para, Paragraph):
                para_object = Paragraph(para)
            else:
                para_object = para
            para_list.append(para_object)

        super(Description, self).__init__(para_list)

    def __getattr__(self, name):
        if name == "paragraphs":
            return self.units

    def get_paragraph(self, number):
        """ Return paragraph having the passed number. """
        return super(Description, self).get_unit(number)


    def sentence_segment(self):
        """ Segment all paragraphs into sentences. """
        for paragraph in self.units:
            paragraph.sentence_segment()

    @property
    def paragraph_count(self):
        """ Return count of paragraphs. """
        return len(self.units)

    @property
    def sentence_count(self):
        """ Return count of sentences. """
        return sum([p.sentence_count for p in self.units])


class Figures:
    """ Object to model a set of patent figures. """
    pass
