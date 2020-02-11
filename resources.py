from wikidata_connector import WikidataConnector

# Fixed Constants
OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama',
                        'best performance by an actress in a motion picture - drama',
                        'best performance by an actor in a motion picture - drama',
                        'best motion picture - comedy or musical',
                        'best performance by an actress in a motion picture - comedy or musical',
                        'best performance by an actor in a motion picture - comedy or musical',
                        'best animated feature film', 'best foreign language film',
                        'best performance by an actress in a supporting role in a motion picture',
                        'best performance by an actor in a supporting role in a motion picture',
                        'best director - motion picture', 'best screenplay - motion picture',
                        'best original score - motion picture', 'best original song - motion picture',
                        'best television series - drama',
                        'best performance by an actress in a television series - drama',
                        'best performance by an actor in a television series - drama',
                        'best television series - comedy or musical',
                        'best performance by an actress in a television series - comedy or musical',
                        'best performance by an actor in a television series - comedy or musical',
                        'best mini-series or motion picture made for television',
                        'best performance by an actress in a mini-series or motion picture made for television',
                        'best performance by an actor in a mini-series or motion picture made for television',
                        'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television',
                        'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy',
                        'best performance by an actress in a motion picture - drama',
                        'best performance by an actor in a motion picture - drama',
                        'best performance by an actress in a motion picture - musical or comedy',
                        'best performance by an actor in a motion picture - musical or comedy',
                        'best performance by an actress in a supporting role in any motion picture',
                        'best performance by an actor in a supporting role in any motion picture',
                        'best director - motion picture', 'best screenplay - motion picture',
                        'best motion picture - animated', 'best motion picture - foreign language',
                        'best original score - motion picture', 'best original song - motion picture',
                        'best television series - drama', 'best television series - musical or comedy',
                        'best television limited series or motion picture made for television',
                        'best performance by an actress in a limited series or a motion picture made for television',
                        'best performance by an actor in a limited series or a motion picture made for television',
                        'best performance by an actress in a television series - drama',
                        'best performance by an actor in a television series - drama',
                        'best performance by an actress in a television series - musical or comedy',
                        'best performance by an actor in a television series - musical or comedy',
                        'best performance by an actress in a supporting role in a series, limited series or motion picture made for television',
                        'best performance by an actor in a supporting role in a series, limited series or motion picture made for television',
                        'cecil b. demille award']

EXTERNAL_SOURCES = {'actors': 'actorLabel', 'films': 'filmLabel', 'directors': 'directorLabel', 'series': 'seriesLabel', 'actresses':'actorLabel'}
MOMENT_TYPES = ["fun|laugh|hilarious|surprise", "win|winner|victory", "awkward|horror|pain|delicate", "sad|bitter|heartbroken|unhappy"]
HOST_WORDS = "hosting"
#Words for filtering
NOMINEE_WORDS = "nominee|nomination|nominated|nominees|nominations|nominate|introduce|introduced|introducing|vote|voting|voter|voted|candidate|hope|hoping|hopeful"
PRESENTER_WORDS = "presents|presenting|presented|presentation|presenter|presenters|presentations|announce|announces|announced"
BEST_DRESS = "beautiful|pretty|awesome|wonderful|stunning|nice|elegant|alluring|dazzling|fascinating|favorite"
WORST_DRESS = "worst|ugly|awful|grisly|grotesque|unattractive|disgusting|distasteful|horrid"
DRESS = "dress|wardrobe|costume|attire|robe"
SNUB = "did not win|didn't win"
MOMENTS = "moment"
STOPWORDS = ["an", "in", "a", "for", "by", "-", "or"]

data = {}

years = []

wikidata = WikidataConnector()
