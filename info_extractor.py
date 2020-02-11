import glob
import os
import re
import warnings
import zipfile

import nltk
import pandas as pd
import spacy


class InfoExtractor:

    def __init__(self):

        self.z = u'\u007a'
        self.Z = u'\u005a'
        self.a = u'\u0061'
        self.A = u'\u0041'
        self.space = u'\u0020'

        self.stopwords = ['.org', 'aahh', 'aarrgghh', 'abt', 'ftl', 'ftw', 'fu', 'fuck', 'fucks', 'gtfo', 'gtg', 'haa',
                          'hah', 'hahah', 'haha', 'hahaha', 'hahahaha', 'hehe', 'heh', 'hehehe', 'hi', 'hihi', 'hihihi',
                          'http', 'https', 'huge', 'huh', 'huhu', 'huhuhu', 'idk', 'iirc', 'im', 'imho', 'imo', 'ini',
                          'irl', 'ish', 'isn', 'isnt', 'j/k', 'jk', 'jus', 'just', 'justwit', 'juz', 'kinda', 'kthx',
                          'kthxbai', 'kyou', 'laa', 'laaa', 'lah', 'lanuch', 'leavg', 'leh', 'lol', 'lols', 'ltd',
                          'mph', 'mrt', 'msg', 'msgs', 'muahahahahaha', 'nb', 'neways', 'ni', 'nice', 'pls', 'plz',
                          'plzz', 'psd', 'pte', 'pwm', 'pwned', 'qfmft', 'qft', 'tis', 'tm', 'tmr', 'tyty', 'tyvm',
                          'um', 'umm', 'viv', 'vn', 'vote', 'voted', 'w00t', 'wa', 'wadever', 'wah', 'wasn', 'wasnt',
                          'wassup', 'wat', 'watcha', 'wateva', 'watever', 'watnot', 'wats', 'wayy', 'wb', 'weren',
                          'werent', 'whaha', 'wham', 'whammy', 'whaow', 'whatcha', 'whatev', 'whateva', 'whatevar',
                          'whatever', 'whatnot', 'whats', 'whatsoever', 'whatz', 'whee', 'whenz', 'whey', 'whore',
                          'whores', 'whoring', 'wo', 'woah', 'woh', 'wooohooo', 'woot', 'wow', 'wrt', 'wtb', 'wtf',
                          'wth', 'wts', 'wtt', 'www', 'xs', 'ya', 'yaah', 'yah', 'yahh', 'yahoocurrency', 'yall', 'yar',
                          'yay', 'yea', 'yeah', 'yeahh', 'yeh', 'yhoo', 'ymmv', 'young', 'youre', 'yr', 'yum', 'yummy',
                          'yumyum', 'yw', 'zomg', 'zz', 'zzz', 'loz', 'lor', 'loh', 'tsk', 'meh', 'lmao', 'wanna',
                          'doesn', 'liao', 'didn', 'didnt', 'omg', 'ohh', 'ohgod', 'hoh', 'hoo', 'bye', 'byee', 'byeee',
                          'byeeee', 'lmaolmao', 'yeahhh', 'yeahhhh', 'yeahhhhh', 'yup', 'yupp', 'hahahahahahaha',
                          'hahahahahah', 'hahhaha', 'wooohoooo', 'wahaha', 'haah', '2moro', 'veh', 'noo', 'nooo',
                          'noooo', 'hahas', 'ooooo', 'ahahaha', 'ahahahahah', 'tomolow', 'accent', 'accented',
                          'accents', 'acne', 'ads', 'afaik', 'aft', 'ago', 'ahead', 'ain', 'aint', 'aircon', 'alot',
                          'am', 'annoy', 'annoyed', 'annoys', 'anycase', 'anymore', 'app', 'apparently', 'apps', 'argh',
                          'ass', 'asses', 'awesome', 'babeh', 'bad', 'bai', 'based', 'bcos', 'bcoz', 'bday', 'bit',
                          'biz', 'blah', 'bleh', 'bless', 'blessed', 'blk', 'blogcatalog', 'bro', 'bros', 'btw', 'byee',
                          'com', 'congrats', 'contd', 'conv', 'cos', 'cost', 'costs', 'couldn', 'couldnt', 'cove',
                          'coves', 'coz', 'crap', 'cum', 'curnews', 'curr', 'cuz', 'dat', 'de', 'diff', 'dis', 'doc',
                          'doesn', 'doesnt', 'don', 'AAWWW', 'dont', 'dr', 'dreamt', 'drs', 'due', 'dun', 'dunno',
                          'duper', 'eh', 'ehh', 'emo', 'emos', 'eng', 'esp', 'fadein', 'ffs', 'fml', 'frm', 'fwah',
                          'g2g', 'gajshost', 'gd', 'geez', 'gg', 'gigs', 'gtfo.1', 'gtg.1', 'hasn', 'hasnt', 'hav',
                          'haven', 'havent', 'hee', 'hello', 'hey', 'hmm', 'ho', 'hohoho', 'lotsa', 'lotta', 'luv',
                          'ly', 'macdailynews', 'nite', 'nom', 'noscript', 'nvr', 'nw', 'ohayo', 'omfg', 'omfgwtf',
                          'omgwtfbbq', 'omw', 'org', 'pf', 'pic', 'pm', 'pmsing', 'ppl', 'pre', 'pro', 'rawr', 'rawrr',
                          'rofl', 'roflmao', 'rss', 'rt', 'sec', 'secs', 'seem', 'seemed', 'seems', 'sgreinfo', 'shd',
                          'shit', 'shits', 'shitz', 'shld', 'shouldn', 'shouldnt', 'shudder', 'sq', 'sqft', 'sqm',
                          'srsly', 'stfu', 'stks', 'su', 'suck', 'sucked', 'sucks', 'suckz', 'sux', 'swf', 'tart',
                          'tat', 'tgif', 'thanky', 'thk', 'thks', 'tht', 'tired', 'hahahahahahahahaha', 'hahahahaha',
                          'hahahahah', 'zzzzz', 'hahahahha', 'lolololol', 'lololol', 'lolol', 'lol', 'dude', 'hmmm',
                          'humm', 'tumblr', 'kkkk', 'fk', 'yayyyyyy', 'fffffffuuuuuuuuuuuu', 'zzzz', 'noooooooooo',
                          'hahahhaha', 'woohoo', 'lalalalalalala', 'lala', 'lalala', 'lalalala', 'whahahaahahahahahah',
                          'hahahahahahahahahahaha', 'ahhh', 'RT', 'rt', 'gif', 'amp', '.com', '.ly', '.net', ]

        self.sub_links = re.compile(r'http(s)?\:\/\/[\w\.\d]*\b')
        self.sub_hashtag = re.compile(r'#\w*')
        self.sub_tags = re.compile(r'@[^ ]*\b')
        self.sub_numbers = re.compile(r'\b\d+\b')
        self.sub_punctuation = re.compile(r'[^\w\d\s]+')
        self.sub_splitter = re.compile("([a-z])([A-Z])")
        self.sub_spaces = re.compile(r'\s+')

        self.stopwords_dict = {lang: set(nltk.corpus.stopwords.words(lang)) for lang in nltk.corpus.stopwords.fileids()}
        self.nlp = spacy.load('en_core_web_sm')
        self.data = None

    def load_data(self, path, year):
        # Load the specified zip file and put the data into a dataframe
        allFiles = glob.glob(path + "*.zip")
        for file in allFiles:
            zip_file = zipfile.ZipFile(file)
            file_info = zip_file.infolist()
            if str(year) in os.path.basename(file_info[0].filename):
                self.data = pd.read_json(zip_file.open(file_info[0].filename))
                return
        raise ValueError("There is no tweet resources for " + str(year))

    def clean_tweet(self, tweet):
        # Remove all links hashtags and other things that are not words
        tweet = str(tweet)
        tweet = self.sub_links.sub(' ', tweet)
        tweet = self.sub_hashtag.sub('', tweet)
        tweet = self.sub_tags.sub('', tweet)
        tweet = self.sub_numbers.sub('', tweet)
        tweet = self.sub_punctuation.sub(' ', tweet)
        tweet = self.sub_splitter.sub(r'\1 \2', tweet)
        tweet = self.sub_spaces.sub(' ', tweet)
        tweet = tweet.lstrip(' ')
        tweet = ''.join(c for c in tweet if self.check_emoji(c))

        list_no_stopwords = [i for i in tweet.split() if i.lower() not in self.stopwords]

        tweet = ' '.join(list_no_stopwords)
        tweet = tweet.replace('tv', 'telvision')
        tweet = tweet.replace('mini-series', 'mini series')
        tweet = tweet.replace('miniseries', 'mini series')
        return tweet

    def check_emoji(self, c):
        # Checks if the given character is a letter or space
        if (c <= self.z and c >= self.a) or (c <= self.Z and c >= self.A) or c == self.space:
            return True
        return False

    def clean_dataframe_column(self, to_clean, new_col):
        # Clean the specified column and return the whole dataframe
        self.data[new_col] = self.data[to_clean].apply(lambda x: self.clean_tweet(x))
        self.data = self.data.loc[(self.data[new_col] != '') | (self.data[new_col] != None), :]

    def save_dataframe(self, file):
        # Save the dataframe on disk
        self.data.to_csv(file, index=False)

    def read_dataframe(self, file):
        # Read a dataframe from disk
        self.data = pd.read_csv(file)

    def drop_column(self, column):
        # Drops the specified column of the given dataframe
        self.data = self.data.drop([column], axis=1)

    def convert_time(self, to_convert):
        # Convert the specified columns timestamp to hour and time
        self.data[to_convert] = pd.to_datetime(self.data[to_convert])
        self.data["hour"] = self.data[to_convert].apply(lambda x: x.hour)
        self.data["minute"] = self.data[to_convert].apply(lambda x: x.minute)

    def get_dataframe(self):
        # Returns the processed dataframe
        return self.data

    def count_words_per_tweet(self, to_count):
        # Count the words in the spciefied column and safe it to a new column
        self.data[to_count + "_wordcount"] = self.data[to_count].apply(lambda x: len(x.split()))
        self.data = self.data.loc[self.data[to_count + "_wordcount"] > 1, :]

    def load_save(self, path, year, limit):
        self.load_data(path, year)
        self.data = self.data.sample(frac=1).reset_index(drop=True)[:limit]
        self.data.to_csv('dirty_gg{}.csv'.format(year))

    def get_language(self, text):
        # Detects language based on # of stop words for particular language
        text = str(text).lower()
        words_ = set(nltk.wordpunct_tokenize(text.lower()))
        return self.is_english(words_)

    def is_english(self, words_):
        # Checks if the given words belong to the english language or not
        lang = \
            max(((lang, len(words_ & stopwords)) for lang, stopwords in self.stopwords_dict.items()),
                key=lambda x: x[1])[0]
        if lang == 'english' or lang == 'arabic':
            return True
        return False

    def get_english_tweets(self, src_column, dest_column):
        # Creates new column that indicates if tweet is english or not
        self.data[dest_column] = self.data[src_column].apply(lambda x: self.get_language(x))
        self.data = self.data.loc[(self.data.language == True)]
        self.data.reset_index(drop=True, inplace=True)

    def make_to_lowercase(self, src_column, dest_column):
        # Converts the given column to lowercase
        self.data[dest_column] = self.data[src_column].apply(lambda text: text.lower())


warnings.filterwarnings('ignore')
