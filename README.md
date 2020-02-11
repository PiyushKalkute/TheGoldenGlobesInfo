# Natural Langauge Processing on Golden Globes
_by Aditi Badrinath Atreyasa, Shashank Satish Damodaran, Piyush Kalkute

# Github Repository: 

This project aims to use NLP methods to identify the hosts, award names, nominees, winners and presenters for a given award ceremony, which in this case is The "Golden Globes".But the project has been developed in such a way that the strategies can be generalized in order to be applicable to any other award ceremony besides the Golden Globes like the Oscars. Currently this project has been trained on on tweets for the Golden Globes 2013 and 2015. 

The first step involved extracting the award names from scratch. After examining the tweets and award names we identified the underlying syntactic and semantic structure of these categories. We created chunks and parsed them based on these structures. We also observed the award names of other functions and found them to have a similar semantic pattern. For the next tasks like extracting the hosts, award names , nominees,winners and presenters, we did a speciliazed search for each category based on the words that were frequently observed pertaining to a certain category, which greatly narrowed down the search area and reduced the runtime. One of the major challenges was ensuring the correct mapping of presenters, winners and nominees to their actual correct award name, as the name of awards were almost never completely mentioned in the tweets. We also exploits the periodic dependency of the tweets to extract nominees more effectively.

### Goals
Standard Goals:
- Hosts
- Awards
- Winners
- Presenters
- Nominees  

Additional Goals:
- Red Carpet (best/worst)
- Moments (happy/sad/funny/triumph)
- Snub (Who got snubbed?)

### File format:
The datasets (gg2013, gg2015, etc.) are expected to be in .zip program by our program. This was done to avoid using hardcoded file path and OS dependencies for slashes (/, \)

### Executing files:
- Open a command prompt and navigate to the source code directory 
- Make sure your machine is connected to the internet.
- Create a virtual environment (if on MacOS use: python3 -m venv env1)
- Activate it using : source env/bin/activate
- Then install the required packages via: pip install -r requirements.txt
- Run this command on the console : python -m spacy download en
- Also we need the 'punkt' packages from nltk : python3 -m nltk.downloader punkt
- First, run the gg_api.py using the command:  python gg_api.py 2013 
(NOTE: Running this Occasionally throws a “JSONDecodeError: Expects a value”.  While running the SparQL query to fetch data from the Wikipedia database.)
- Possible Solution(s):
    i) Re-run the gg_api.py file and the error disappears
    ii) If the above solution didn’t work, the environment is possibly missing the English language package of spacy. Download spacy’s web-sm-eng package using :python -m spacy download en.
- Running gg_api.py creates 2 different outputs:
    i) .JSON file (results.json): to be directly executed by the auto-grader
    ii) .MD file (results.md): a human-readable form of results of this semantic natural language processing, for easy understanding

- Run the autograder.py for the corresponding year: python autograder.py 2013

### Viewing results:
- The autograder displays performance of the model in regards with the Standard goals.
- For viewing the Additional goals, kindly refer to the 'results.md' file in the repository
