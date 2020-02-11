import itertools

import nltk
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import words


class Chunker:

    def __init__(self):
        self.word_dict = dict.fromkeys(words.words(), 1)
        self.stop_words = set(stopwords.words('english'))

    def extract_chunks(self, text_string, chunker):
        try:
            # Get grammatical functions of words
            tagged_sents = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text_string))

            # Make chunks from the sentences, using grammar. Output in IOB.
            all_chunks = list(itertools.chain.from_iterable(
                nltk.chunk.tree2conlltags(chunker.parse(tagged_sent)) for tagged_sent in tagged_sents))

            # Join phrases based on IOB syntax.
            candidates = [' '.join(w[0] for w in group) for key, group in
                          itertools.groupby(all_chunks, lambda l: l[2] != 'O') if key]

            if candidates != []:
                candidates[0] = ' '.join([w for w in word_tokenize(candidates[0]) if w in self.word_dict])
                return candidates[0]
            else:
                return 'N/a'

        except:
              return 'N/a'

    def extract_noun_pattern(self, series):
        chunker = nltk.RegexpParser("""Chunk: {<NN.?><NN.?|VB.?><NN.?>+}""")
        text_string = series['clean_lower']
        return self.extract_chunks(text_string, chunker)

    def extract_adjective_pattern(self,series):
        chunker = nltk.RegexpParser("""Chunk: {<JJ.?|RB.?><JJ.?|NN.?|VB.?><NN.?><JJ.?|NN.?>?<CC.?|NN.?>?<JJ.?|NN.?>?}""")
        text_string = series['clean_lower']
        return self.extract_chunks(text_string, chunker)

    def extract_adverb_pattern(self, series):
        chunker = nltk.RegexpParser(
            """Chunk: {<RB.?> <NN.?> <IN>? <DT>? <CC>? <NN.?>+ <IN>? <DT>? <VB.?>? <NN.?|JJ.?> <NN.?>+ <CC>? <JJ>? <IN>? <DT>? <NN.?>? <VB.?>? <IN>? <NN.?>?}""")
        text_string = series['clean_lower']
        # text_string = text_string.lower()

        return self.extract_chunks(text_string, chunker)

    def extract_wrapper(self, series):
        try:
            text_string = series['clean_lower']

            if not 'best' in text_string.split():
                return 'N/a'

            wrap1 = self.extract_adverb_pattern(series)
            if wrap1 != 'N/a':
                return wrap1

            wrap2 = self.extract_adjective_pattern(series)
            if wrap2 != 'N/a':
                return wrap2

            return 'N/a'  # self.extract_noun_pattern(series)

        except:
            return 'N/a'

    def filter_categories(self, top_categories):
        try:
            for each_categorie in top_categories:
                list_copy = top_categories.copy()
                list_copy.remove(each_categorie)

                for copy_categorie in list_copy:
                    if (each_categorie in copy_categorie) or (copy_categorie.split()[0] != 'best'):
                        top_categories.remove(copy_categorie)
            return top_categories

        except:
          return top_categories

    def pick_categories(self, data):
        try:

            catg_data = pd.DataFrame(data.categorie.value_counts())
            catg_data.reset_index(inplace=True)
            sum_ = catg_data.categorie.sum()

            catg_data['percent'] = catg_data.categorie.apply(lambda x: (x / sum_) * 100)
            catg_data = catg_data.loc[catg_data.percent > 0.65, :]
            return catg_data['index'].tolist()

        except:
           return data['categorie'].tolist()
