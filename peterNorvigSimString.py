import pandas as pd
import re
from collections import Counter
from simstring.feature_extractor.character_ngram import CharacterNgramFeatureExtractor
from simstring.measure.cosine import CosineMeasure
from simstring.database.dict import DictDatabase
from simstring.searcher import Searcher

##########################
# Database cleaning Code #
##########################

def invalid_char_filter(word):
  """ Filter function to detect words that do not fit our list of whitelisted characters """ 
  re1 = re.compile(r"[^A-Z^ ^%^0-9^-]")
  if re1.search(word):
    return False
  else:
    return True

def get_cleaned_ingredients_list(df):
  """ Cleans up dataframe and returns the cleaned ingredients list """
  # Drop NA values first
  df.dropna(subset=['ingredients'], inplace=True)
  # Replace some punctuation with commas
  df['ingredients'] = df.ingredients.map(lambda x: re.sub("[\[\]*:\(\).{};]", ",", x))
  # Turn ingredients list string into list split by commas
  df['ingredients_arr'] = df.ingredients.map(lambda x: [i.strip() for i in x.split(",")])

  # Add all products' ingredients list to a single list
  all_ingredients = []
  df['ingredients_arr'].map(lambda x: all_ingredients.extend(x))
  # Remove any stray empty string values
  all_ingredients_cleaned = [i for i in all_ingredients if i != ''] 
  # Make all ingredients upper case
  all_ingredients_cleaned = [x.upper() for x in all_ingredients_cleaned]

  # Filter out any ingredients that may have random ASCII characters
  all_ingredients_valid_char = list(filter(invalid_char_filter, all_ingredients_cleaned))

  # Further filtering to limit the data based on ingredient length
  # Lengths were determined in another notebook
  max_length = 50
  min_length = 3
  all_ingredients_final = list(filter(lambda x: len(x) <= max_length and len(x) >= min_length, all_ingredients_valid_char))

  return all_ingredients_final

#############################
# Perform database cleaning #
#############################

# Read in branded foods CSV and clean it
df = pd.read_csv('branded_food.csv')
all_ingredients_final = get_cleaned_ingredients_list(df)
# Get a count for all the ingredients to be used by Peter Norvig Implementation 
ingredients_count = Counter(all_ingredients_final)

##############################################
# Peter Norvig SimString Implementation Code #
##############################################

# Populate database with all ingredients
db = DictDatabase(CharacterNgramFeatureExtractor(2))
for ingredient in all_ingredients_final:
  db.add(ingredient)
# Create searcher object to be used by candidates function
searcher = Searcher(db, CosineMeasure())

# Functions

def probability(word, N=sum(ingredients_count.values())): 
  """ 
  Returns the probability of the word appearing in the text 
  Usually, correctly spelled words will have a higher count and therefore probability than their mispellings
  """
  return ingredients_count[word] / N

def candidates(word, searcher):
  """ 
  Obtain a list of candidates using our searcher for a given word
  We found a similarity score of 0.8 yielded gave us the best options
  """
  return searcher.search(word, 0.8)

def correction(word): 
  """ Attempt to perform correction - return suggestion based on best probability """
  word_possibilities = candidates(word)
  if len(word_possibilities) <= 0:
    raise Exception('Unable to perform correction')
  else:
    return max(candidates(word), key=probability)