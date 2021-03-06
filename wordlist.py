from collections import defaultdict

import os
import re
import unicodedata


class WordList(object):
    def __init__(self, lower=False, strip_nonalpha=False, echo=True, min=None, max=None, transforms=[]):
        self._lower = lower
        self._echo = echo
        self._strip_nonalpha = strip_nonalpha
        self._words = set()

        self.sets = defaultdict
        self.min = min
        self.max = max
        self.transforms = transforms

    def _transform(self, word, fns, min=None, max=None):
        if not isinstance(fns, list):
            fns = [fns]

        results = [word]
        for fn in fns:
            results += fn(word)

        print(results)

        return self._add_words(results, min=min, max=max)

    def _add_word(self, word, min=None, max=None):
        word_length = len(word)

        min = min if min else self.min
        max = max if max else self.max

        if min and word_length < min:
            return 0

        if max and word_length > max:
            return 0

        if word not in self._words:
            self._words.add(word)
            return 1

        return 0

    def _add_words(self, words, min=None, max=None):
        count_added = 0
        for word in words:
            count_added += self._add_word(word, min=min, max=max)
        return count_added

    @property
    def words(self):
        return self._words

    def add_file(self, filename, split_further=None, min=None, max=None, reject=[], transforms=[]):
        count_possible = 0
        count_transformed = 0
        count_added = 0
        with open(filename, 'U', encoding='iso-8859-15') as f: # can also try cp437 (so:16528468)
            for row in f:
                if split_further is None:
                    words = [row]
                else:
                    words = row.split(split_further)

                for word in words:

                    word = word.strip('\n').strip('\r')
                    if self._lower:
                        word = word.lower()

                    word = unicodedata.normalize('NFKD', word).encode('ascii','ignore').decode("utf-8")

                    if self._strip_nonalpha:
                        word = re.sub('[^a-zA-Z]', '', word)

                    do_continue = True
                    for fn in reject:
                        if fn(word):
                            do_continue = False

                    if not do_continue:
                        break

                    number_words_transformed = 0
                    number_words_added = self._add_word(word, min=min, max=max)
                    if transforms and number_words_added > 0:
                        number_words_transformed = self._transform(word, transforms, min=min, max=max)

                    count_possible += 1
                    count_transformed += number_words_transformed
                    count_added += number_words_added
        if self._echo:
            print('Dictionary: {}, Possible: {}, Words added: {}, Transformed added: {}, Total: {}'.format(
                os.path.basename(filename), count_possible, count_added, count_transformed, len(self._words)))

    def dict_by_length(self):
        out = defaultdict(set)
        for word in self._words:
            out[len(word)].add(word)
        return out