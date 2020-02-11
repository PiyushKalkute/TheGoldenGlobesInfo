'''Version 0.35'''
import json
import re
import sys
import pandas as pd
from google_images_download import google_images_download

import autograder
import resources
from find_categories import Chunker
from info_extractor import InfoExtractor
from resources import wikidata, EXTERNAL_SOURCES
from tweet_categorizer import TweetCategorizer


# loading actors, films, directors, tv series from Wikipedia (DBPedia) database
# pre_ceremony() is a way to extract useful reference information for better accuracy

def pre_ceremony():

    resources.years.append( int(sys.argv[1]))
    print("Accessing DBPedia.. Loading film data...")
    for key in EXTERNAL_SOURCES:
        if key == "films":
            for year in resources.years:
                wikidata.call_wikidate(key, EXTERNAL_SOURCES[key], str(year - 2), str(year))
                # We've chosen 2 years as a safe margin to accomodate late released movies
                # or early production dates despite releasing in the award consideration year
        else:
            wikidata.call_wikidate(key, EXTERNAL_SOURCES[key])
        print("Done loading DBPedia.. " + key + " ...")
    print("Completed DBPedia Load!\n")

    # Loading the zip files and making .csv file out of them for easy extraction of tokens
    print("Loading Tweets...")
    for year in resources.years:
        try:
            extractor = InfoExtractor()
            extractor.load_save("", year, 300000)
            print("Completed loading tweets for the year" + str(year) + " ...")
        except:
            print("Unable to load tweets for " + str(year) + " ...")
    print("Completed Tweets Loads!\n")
    return



def get_hosts(year):
    hosts = []
    try:
        with open("results.json") as f:
            results = json.load(f)
        hosts = results[year]["Hosts"]
    except:
        print("Couldn't read hosts for " + str(year))
    return hosts


def get_awards(year):
    awards = []
    try:
        with open("results.json") as f:
            results = json.load(f)
        awards = results[year]["Awards"]
    except:
        print("Couldn't read awards for " + str(year))
    return awards


def get_presenters(year):
    awards = resources.OFFICIAL_AWARDS_1315
    if year in [2018, 2019]:
        awards = resources.OFFICIAL_AWARDS_1819
    presenters = {key: [] for key in awards}
    try:
        with open("results.json") as f:
            results = json.load(f)
        for key in awards:
            presenters[key] = results[year][key]["Presenters"]
    except:
        print("Couldn't read presenters for " + str(year))
    return presenters


def get_nominees(year):
    awards = resources.OFFICIAL_AWARDS_1315
    if year in [2018, 2019]:
        awards = resources.OFFICIAL_AWARDS_1819
    nominees = {key: [] for key in awards}
    try:
        with open("results.json") as f:
            results = json.load(f)
        for key in awards:
            nominees[key] = results[year][key]["Nominees"]
    except:
        print("Couldn't read nominees for " + str(year))
    return nominees


def get_winner(year):
    awards = resources.OFFICIAL_AWARDS_1315
    if year in [2018, 2019]:
        awards = resources.OFFICIAL_AWARDS_1819
    winners = {key: [] for key in awards}
    try:
        with open("results.json") as f:
            results = json.load(f)
        for key in awards:
            winners[key] = results[year][key]["Winner"]
    except:
        print("Couldn't read winners for " + str(year))
    return winners


def fuzz_(ident_catg, awards):
    list_ident = ident_catg.split()
    total_len = len(list_ident)

    best_value_percent = 0
    best_value = ''

    for key, value in awards.items():
        value = value.split()
        count = 0
        for each_ in list_ident:
            if each_ in value:
                count += 1

        if count / total_len > best_value_percent:
            best_value_percent = count / total_len
            best_value = key

    if best_value_percent > 0.4:
        return best_value
    else:
        return 'N/a'


def main():
    # Reload the csv files from disk and store the data in a dataframe
    results = {}
    all_winners = {}
    categorie_data = {}
    best_catg_time = {}
    clean_awards = {}

    # Reload the wikidata from disk
    people = wikidata.call_wikidate('actors', 'actorLabel')
    people += wikidata.call_wikidate('directors', 'directorLabel')
    people += wikidata.call_wikidate('actresses', 'actorLabel')
    things = wikidata.call_wikidate('series', 'seriesLabel')
    people = [re.sub(r'[^\w\d\s]+', '', person_) for person_ in people]
    things = [re.sub(r'[^\w\d\s]+', '', thing_) for thing_ in things]

    # Load the csv files and clean data
    print("Load Dataframes")
    for year in resources.years:
        try:
            extractor = InfoExtractor()
            print("Start " + str(year) + " ...")
            print("Reading ...")
            extractor.read_dataframe("dirty_gg%s.csv" % year)
            print("Language ...")
            extractor.get_english_tweets("text", "language")
            print("Cleaning ...")
            extractor.clean_dataframe_column("text", "clean_upper")
            print("Lowering ...")
            extractor.make_to_lowercase("clean_upper", "clean_lower")
            print("Dropping ...")
            extractor.convert_time('timestamp_ms')
            extractor.drop_column("user")
            extractor.drop_column("id")
            extractor.drop_column("timestamp_ms")
            extractor.drop_column("language")
            resources.data[year] = extractor.get_dataframe()
            print("Finish " + str(year) + " ...")
            results[year] = {}
        except:
            print("Couldn't load Dataframes for" + str(year))
    print("Done Dataframes\n")

    # We start by finding the awards for each year
    print("Find Awards")
    for year in resources.years:
        # try:
            chunker = Chunker()
            categorie_data[year] = resources.data[year].copy()
            categorie_data[year]['categorie'] = categorie_data[year].apply(chunker.extract_wrapper, axis=1)
            categorie_data[year] = categorie_data[year].loc[categorie_data[year].categorie != 'N/a', :]
            categorie_data[year].reset_index(drop=True, inplace=True)
            categorie_data[year] = categorie_data[year].loc[categorie_data[year].categorie.str.split().map(len) > 3, :]
            best_categories = chunker.pick_categories(categorie_data[year])
            best_categories = chunker.filter_categories(best_categories)
            for i in best_categories:
                if 'actor' in i:
                    i.replace('actor','performance by an actor')
                elif 'actress' in i :
                    i.replace('actress','performance by an actress')
                if 'tv' in i:
                    i.replace('tv','television')
                elif 'picture' in i and 'motion' not in i:
                    i.replace('picture','motion picture')
                if 'series' in i and 'television' not in i:
                    i.replace('series','television series')
            results[year]["Awards"] = best_categories
        # except:
        #     print("Couldn't find awards for " + str(year))
    print("Done Awards\n")

    # Find the point in time when an award took place
    print("Find Times")
    for year in resources.years:
        try:
            if year in [2013, 2015]:
                awards = resources.OFFICIAL_AWARDS_1315
            else:
                awards = resources.OFFICIAL_AWARDS_1819

            info_extract = InfoExtractor()
            for each_award in awards:
                clean_awards[each_award] = info_extract.clean_tweet(each_award)

            categorie_data[year]['real_categorie'] = categorie_data[year]['categorie'].apply(lambda x: fuzz_(x, clean_awards))
            categorie_data[year] = categorie_data[year].loc[categorie_data[year]['real_categorie'] != 'N/a', :]
            categorie_data[year].reset_index(drop=True, inplace=True)

            data_catg = categorie_data[year].groupby(['hour', 'minute', 'real_categorie']).count()['clean_lower'].unstack().reset_index()
            data_catg = data_catg.dropna(how='all', axis=1)

            best_catg_time[year] = {}
            for each_ in list(data_catg.columns):
                if not each_ in ['hour', 'minute']:
                    best_catg_time[year][each_] = []
                    max_idx = data_catg[each_].idxmax()
                    best_catg_time[year][each_].append(
                        (data_catg.iloc[max_idx - 2]['hour'], data_catg.iloc[max_idx - 2]['minute']))
                    best_catg_time[year][each_].append(
                        (data_catg.iloc[max_idx - 1]['hour'], data_catg.iloc[max_idx - 1]['minute']))
                    best_catg_time[year][each_].append(
                        (data_catg.iloc[max_idx]['hour'], data_catg.iloc[max_idx]['minute']))
                    best_catg_time[year][each_].append(
                        (data_catg.iloc[max_idx + 1]['hour'], data_catg.iloc[max_idx + 1]['minute']))
                    best_catg_time[year][each_].append(
                        (data_catg.iloc[max_idx + 2]['hour'], data_catg.iloc[max_idx + 2]['minute']))
        except:
            print("Couldn't find times for " + str(year))
    print("Finished Times for award ceremony\n")

    # We search for the hosts
    print("Searching for Host(s)")
    for year in resources.years:
        try:
            host_categorizer = TweetCategorizer([resources.HOST_WORDS], [], "host_tweet", resources.data[year], 0,resources.data[year].shape[0])
            host_tweets = host_categorizer.get_categorized_tweets()
            hosters = host_categorizer.find_percentage_of_entities(host_tweets, 0.2, people, [])
            results[year]["Hosts"] = hosters[resources.HOST_WORDS]
        except:
            print("Couldn't find Hosts for " + str(year))
    print("Found the Hosts!\n")

    # Search for the winners
    print("Searching for Winners...")
    for year in resources.years:
        try:
            all_winners[year] = []
            awards = resources.OFFICIAL_AWARDS_1315
            if year in [2018, 2019]:
                awards = resources.OFFICIAL_AWARDS_1819
            winner_categorizer = TweetCategorizer(awards, resources.STOPWORDS, "award", resources.data[year], 3,
                                                  resources.data[year].shape[0])
            winner_tweets = winner_categorizer.get_categorized_tweets()
            winners = winner_categorizer.find_list_of_entities(winner_tweets, 1, people,things + wikidata.call_wikidate("films", "filmLabel",str(year - 2),str(year)))
            for key in winners:
                results[year][key] = {}
                if winners[key]:
                    results[year][key]["Winner"] = winners[key][0]
                else:
                    results[year][key]["Winner"] = ""
                all_winners[year].append(winners[key])
        except:
            print("Couldn't find Winners for the year " + str(year))
    print("Found all the Winners!\n")

    # Identifying the presenters for the specified year
    print("Searching for Presenters")
    for year in resources.years:
        try:
            for key, value in best_catg_time[year].items():
                data_new = pd.DataFrame(columns=list(resources.data[year].columns))

                for each_value in value:
                    data_temp = resources.data[year].loc[(resources.data[year].hour == int(each_value[0])), :]
                    data_temp = data_temp.loc[(data_temp.minute == int(each_value[1])), :]
                    data_new = pd.concat([data_new, data_temp])

                presenter_categorizer = TweetCategorizer([resources.PRESENTER_WORDS], [], "presenter_tweet", data_new,
                                                         0,
                                                         data_new.shape[0])
                presenter_tweets = presenter_categorizer.get_categorized_tweets()

                # presenters = find_names(presenter_tweets.clean_upper.tolist(),2,people,all_winners[year],results[year]["Hosts"])
                presenters = presenter_categorizer.find_list_of_entities(presenter_tweets, 3, people, [], people=True)
                presenters = [p for p in presenters[list(presenters.keys())[0]] if
                              (p not in all_winners[year]) and (p not in results[year]["Hosts"])]

                results[year][key]['Presenters'] = presenters[-3:]

            if year in [2013, 2015]:
                awards = resources.OFFICIAL_AWARDS_1315
            else:
                awards = resources.OFFICIAL_AWARDS_1819

            for each_ in awards:
                if not each_ in best_catg_time[year].keys():
                    results[year][each_]['Presenters'] = []
        except:
            print("Couldn't find presenters for " + str(year))
    print("Found the Presenters!\n")

    # Identify the nominees for each year
    print("Looking for Nominees...")
    for year in resources.years:
        try:
            for key, value in best_catg_time[year].items():
                data_new = pd.DataFrame(columns=list(resources.data[year].columns))

                for each_value in value:
                    data_temp = resources.data[year].loc[(resources.data[year].hour == int(each_value[0])), :]
                    data_temp = data_temp.loc[(data_temp.minute == int(each_value[1])), :]
                    data_new = pd.concat([data_new, data_temp])

                nominee_categorizer = TweetCategorizer([resources.NOMINEE_WORDS], [], "nominee_tweet", data_new, 0,
                                                       data_new.shape[0])
                nominee_tweets = nominee_categorizer.get_categorized_tweets()

                # presenters = find_names(presenter_tweets.clean_upper.tolist(),2,people,all_winners[year],results[year]["Hosts"])
                if ('actress' in key.split()):
                    nominees = nominee_categorizer.find_list_of_entities(nominee_tweets, 6,
                                                                         wikidata.call_wikidate('actresses',
                                                                                                'actorLabel'),
                                                                         [], people=True)
                elif ('actor' in key.split()):
                    nominees = nominee_categorizer.find_list_of_entities(nominee_tweets, 6,
                                                                         wikidata.call_wikidate('actors', 'actorLabel'),
                                                                         [],
                                                                         people=True)
                elif ('director' in key.split()):
                    nominees = nominee_categorizer.find_list_of_entities(nominee_tweets, 6,
                                                                         wikidata.call_wikidate('directors',
                                                                                                'actorLabel'),
                                                                         [], people=True)
                else:
                    nominees = nominee_categorizer.find_list_of_entities(nominee_tweets, 6, [],
                                                                         things + wikidata.call_wikidate("films",
                                                                                                         "filmLabel",
                                                                                                         str(year - 2),
                                                                                                         str(year)))

                nominees = [p for p in nominees[list(nominees.keys())[0]] if (p not in all_winners[year]) and (
                        p not in results[year]["Hosts"] and (p not in results[year][key]['Presenters']))]

                results[year][key]['Nominees'] = nominees[-6:]

            if year in [2013, 2015]:
                awards = resources.OFFICIAL_AWARDS_1315
            else:
                awards = resources.OFFICIAL_AWARDS_1819

            for each_ in awards:
                if not each_ in best_catg_time[year].keys():
                    results[year][each_]['Nominees'] = []
        except:
            print("Couldn't find nominees for the year" + str(year))
    print("Found the Nominees!\n")

    # Searching for best and worst dress on the Red Carpet
    print("Looking for every mention of Dresses...")
    for year in resources.years:
        try:
            dress_categorizer = TweetCategorizer([resources.DRESS], [], "dress", resources.data[year], 0,
                                                 resources.data[year].shape[0])
            dress_tweets = dress_categorizer.get_categorized_tweets()

            best_dress_categorizer = TweetCategorizer([resources.BEST_DRESS], [], "best_dress", dress_tweets, 0,
                                                      dress_tweets.shape[0])
            best_dress_tweets = best_dress_categorizer.get_categorized_tweets()
            probs_best = best_dress_categorizer.list_probabilities(best_dress_tweets, 3, people, [], people=True)
            best_dressed = list(probs_best.keys())
            representative_best_tweets = []
            for b in best_dressed:
                for index, row in best_dress_tweets.iterrows():
                    if b in str(row["clean_upper"]):
                        representative_best_tweets.append(str(row["text"]))
                        break

            worst_dress_categorizer = TweetCategorizer([resources.WORST_DRESS], [], "worst_dress", dress_tweets, 0,
                                                       dress_tweets.shape[0])
            worst_dress_tweets = worst_dress_categorizer.get_categorized_tweets()
            probs_worst = worst_dress_categorizer.list_probabilities(worst_dress_tweets, 3, people, [], people=True)
            worst_dressed = list(probs_worst.keys())

            representative_worst_tweets = []
            for w in worst_dressed:
                for index, row in worst_dress_tweets.iterrows():
                    if w in str(row["clean_upper"]):
                        representative_worst_tweets.append(str(row["text"]))
                        break

            results[year]["BestDressed"] = probs_best
            results[year]["WorstDressed"] = probs_worst
            results[year]["BestDressedTweets"] = representative_best_tweets
            results[year]["WorstDressedTweets"] = representative_worst_tweets
        except:
            print("Couldn't find dresses for " + str(year))
    print("Found best and worsed Dressed celebrites\n")

    # Looking for memorable moments from the award ceremony
    print("Finding the most memorable Moments...")
    for year in resources.years:
        try:
            moment_categorizer = TweetCategorizer([resources.MOMENTS], [], "moments", resources.data[year], 0,
                                                  resources.data[year].shape[0])
            moment_tweets = moment_categorizer.get_categorized_tweets()
            link_finder = re.compile(r'\bhttp[^\s ]+\b')
            results[year]["Moments"] = {}
            for type in resources.MOMENT_TYPES:
                type_categorizer = TweetCategorizer([type], [], "jokes", moment_tweets, 0, moment_tweets.shape[0])
                type_tweets = type_categorizer.get_categorized_tweets()
                type_person = type_categorizer.find_list_of_entities(type_tweets, 1, people, [], people=True)[type]
                if len(type_person) > 0:
                    type_person = type_person[0]
                    results[year]["Moments"][type] = {}
                    results[year]["Moments"][type]["Person"] = type_person
                    for index, row in type_tweets.iterrows():
                        if type_person in str(row["clean_upper"]):
                            results[year]["Moments"][type]["Tweet"] = str(row["text"])
                            break
                    http_categorizer = TweetCategorizer(["http"], [], "links", type_tweets, 0, type_tweets.shape[0],
                                                        column="text")
                    http_tweets = http_categorizer.get_categorized_tweets()
                    http_tweets = http_tweets.reset_index(drop=True)
                    links = set()
                    if (len(http_tweets) > 0):
                        results[year]["Moments"][type]["Tweet"] = str(http_tweets["text"][0])
                        for index, row in http_tweets.iterrows():
                            matches = link_finder.findall(str(row["text"]))
                            for m in matches:
                                links.add(m)
                    results[year]["Moments"][type]["Link"] = list(links)[:3]
        except:
            print("Couldn't find moments for the year " + str(year))
    print("Found the best Moments!\n")

    # Finding people who were expected to win, but did not win
    print("Searching for the biggest Snubbed personalities from the show... ")
    for year in resources.years:
        try:
            snub_categorizer = TweetCategorizer([resources.SNUB], ["Golden", "Golden Globes", "Hollywood", "Globe Awards", "Disney","Oscar","Common"],"snub", resources.data[year], 0,resources.data[year].shape[0])
            snub_tweets = snub_categorizer.get_categorized_tweets()

            most_snub_categorizer = TweetCategorizer([resources.SNUB], [], "most_snub", snub_tweets, 0,snub_tweets.shape[0])
            most_snub_tweets = most_snub_categorizer.get_categorized_tweets()
            probs_most_snub = most_snub_categorizer.list_probabilities(most_snub_tweets, 2, people, [], people=True)
            most_snubbed = list(probs_most_snub.keys())
            results[year]["Snubbed"] = probs_most_snub
        except:
            print("Couldn't find snubbed celebs for " + str(year))
    print("Found all interestingly snubbed celebrities\n")

    # Preparing output files

    print("Write Markdown")
    markdown = ""
    for year in resources.years:
        markdown += "# " + str(year) + " Golden Globes\n"
        try:
            markdown += "## Hosts\n"
            for h in results[year]["Hosts"]:
                markdown += " - " + h + "\n"
        except:
            print("Couldn't write markdown hosts for " + str(year))

        try:
            markdown += "## Best Dressed\n"
            i = 1
            best_dressed = list(results[year]["BestDressed"].keys())
            for b in best_dressed:
                markdown += " " + str(i) + ". " + b + " (" + str(results[year]["BestDressed"][b]) + ") " + "\n"
                i += 1
            markdown += "\n"
            for b in best_dressed:
                response = google_images_download.googleimagesdownload()
                search = b + " " + str(year) + " Golden Globes Dress"
                arguments = {"keywords": search, "limit": 1,"format": "jpg", "print_urls": True}
                paths = response.download(arguments)
                print(paths)
                markdown += "<img src='file://" + paths[0][search][0] + "' height=300px alt='" + search + "'>  "
            markdown += "\n"
            markdown += "\n"
            for b in results[year]["BestDressedTweets"]:
                markdown += b + "  \n\n"
            markdown += "\n"
        except:
            print("Couldn't write markdown best dressed for " + str(year))

        try:
            markdown += "## Worst Dressed\n"
            i = 1
            worst_dressed = list(results[year]["WorstDressed"].keys())
            for w in worst_dressed:
                markdown += " " + str(i) + ". " + w + " (" + str(results[year]["WorstDressed"][w]) + ") " + "\n"
                i += 1
            markdown += "\n"
            for w in worst_dressed:
                response = google_images_download.googleimagesdownload()
                search = w + " " + str(year) + " Golden Globes Dress"
                arguments = {"keywords": search, "limit": 1, "print_urls": False}
                paths = response.download(arguments)
                print(paths)
                markdown += "<img src='file://" + paths[search][0] + "' height=300px alt='" + search + "'>  "
            markdown += "\n"
            markdown += "\n"
            for w in results[year]["WorstDressedTweets"]:
                markdown += w + "  \n\n"
            markdown += "\n"
        except:
            print("Couldn't write markdown worst dressed for " + str(year))

        try:
            i=1
            markdown += "## Who got Snubbed?\n"
            most_snubbed = list(results[year]["Snubbed"].keys())

            for b in most_snubbed:
                if len(b.split())>1:
                    markdown += " " + str(i) + ". " + b + " (" + str(results[year]["Snubbed"][b]) + ") " + "\n"
                    i += 1
            markdown += "\n"
            markdown += "\n"
        except:
            print("Couldn't write markdown snubbed for " + str(year))

        try:
            markdown += "#### Awards found\n"
            for a in results[year]["Awards"]:
                markdown += " - " + a + "\n"
        except:
            print("Couldn't write markdown awards for " + str(year))

        try:
            markdown += "## Moments\n"
            for moment in results[year]["Moments"]:
                markdown += "## " + moment.replace("|", " or ") + " moments\n"
                markdown += "##### Person:\n"
                markdown += "- " + results[year]['Moments'][moment]["Person"] + "\n"
                markdown += "##### Tweet:\n"
                markdown += "- " + results[year]['Moments'][moment]["Tweet"] + "\n"
                markdown += "##### Links:\n"
                for link in results[year]['Moments'][moment]["Link"]:
                    markdown += "- " + link + "\n"
                markdown += "\n"
        except:
            print("Couldn't write markdown moments for the year" + str(year))

        try:
            markdown += "## Awards\n"
            if year in [2013, 2015]:
                awards = resources.OFFICIAL_AWARDS_1315
            else:
                awards = resources.OFFICIAL_AWARDS_1819
            for cat in awards:
                markdown += "### " + cat + "\n"
                # Presenters
                markdown += "#####Presenters:\n"
                for a in results[year][cat]['Presenters']:
                    markdown += "- " + a + "\n"
                # Nominees
                markdown += "\n#####Nominees:\n"
                for a in results[year][cat]['Nominees']:
                    markdown += " - " + a + "\n"
                # Winner
                markdown += "\n#####Winner:\n"
                markdown += "- " + results[year][cat]['Winner'] + "\n"
        except:
            print("Couldn't write award results for the year " + str(year))
    print("Completed Markdown!\n")
    print("Please run - python autograder.py ",str(year))

    # Saving the final results as a Markdown (for easy access)
    with open('results.md', 'w') as file:
        file.write(markdown)

    # Saving the final results as JSON file (for autograder)
    with open("results.json", "w") as f:
        json.dump(results, f)

    return


if __name__ == '__main__':
    pre_ceremony()          # pre-ceremony: loads all the reference database and necessary information
    main()                  # has all the functionalities; all functions called from within
