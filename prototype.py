import pandas as pd
import re
from collections import Counter
import nltk

#####################
# Peter Norvig Code #
#####################

import peterNorvigSimString

def getPeterNorvig(origIngredient):
  """ Use Peter Norvig Sim String implementation to get suggestion """
  try:
      suggestion = peterNorvigSimString.correction(origIngredient)
  except:
        suggestion = origIngredient
  return suggestion

#################
# SymSpell Code #
#################

from symspellpy import SymSpell, Verbosity
import pkg_resources

sym_spell = SymSpell()
sym_spell.create_dictionary('AdditivesDict.txt')

def getSymSpell(mispell):
  """ Use SymSpell implementation to get suggestion """
  suggestion = sym_spell.lookup_compound(mispell, max_edit_distance=2)[0].term
  return suggestion.upper()

#########################
# Database Editing Code #
#########################

def performReplace(result, ingredients, i, method, output):
  """ Performs replacement and returns True/False if it did or did not """
  sensitivity_multiplier = 0.4
  # Get Levenshtein score to determine if it is worth replacing
  levScore = nltk.edit_distance(result, ingredients[i])
  targetScore = len(result) * sensitivity_multiplier
  # Don't want to replace word if large edits are made (> half the length of ingredient)
  if (levScore < targetScore):
    output.write(f"REPLACED \'{ingredients[i]}\' with \'{result}\' using {method}\n")
    ingredients[i] = result
    return True
  else:
    output.write(f"--- SKIPPED replacing \'{ingredients[i]}\' with \'{result}\'. Had Levenshtein score of: {levScore}, needed below {targetScore}\n")
    return False

def replaceIngredient(df, ingredients_dict, output):
  """ 
  Edits the database using 2 different methods in order according to tool evaluation
  Must satisfy a low enough Levenshtein distance based on ingredient word length
  """
  replaceCounter, foodCounter = 0, 0
  columnSeriesObj = df['ingredients_corrected']

  for ingredients in columnSeriesObj:
    for i in range(len(ingredients)):
      # No need to attempt correction if it is properly spelled
      if (ingredients[i].lower() in ingredients_dict):
        continue
      # Attempt correction using Peter Norving SimString 0.8 first
      peterNorvigSSResult = getPeterNorvig(ingredients[i])
      if (peterNorvigSSResult.lower() in ingredients_dict):
        if (performReplace(peterNorvigSSResult, ingredients, i, 'Peter Norvig SimString', output)):
          replaceCounter += 1
      else:
        # Suggestion not found in additives dictionary so try SymSpell next
        symSpellResult = getSymSpell(ingredients[i])
        if (symSpellResult.lower() in ingredients_dict):
          if (performReplace(symSpellResult, ingredients, i, 'SymSpell', output)):
            replaceCounter += 1

      if (replaceCounter % 500 == 0):
        output.write(f"--- Current changed words are {replaceCounter} ---\n")

    foodCounter += 1
    if (foodCounter % 1000 == 0):
      output.write(f"--- Iterated through {foodCounter} foods ---\n")

  output.write(f"*****\nTotal changed words: {replaceCounter}\n*****")



###############################
# Perform database correction #
###############################

# First, we read in the branded foods CSV and perform pre-processing
df = pd.read_csv('branded_food.csv')
# Drop NA values first
df.dropna(subset=['ingredients'], inplace=True)
# Replace some punctuation with commas
df['ingredients_corrected'] = df.ingredients.map(lambda x: re.sub("[\[\]*:\(\).{};]", ",", x))
df['ingredients_corrected'] = df.ingredients_corrected.map(lambda x: [i.strip() for i in x.split(",")])

# Next we open up the additives dictionary to build our ingredients dictionary
fileDict = open('AdditivesDict.txt', 'r')
ingredients_dict = {}
for ingredient in fileDict.readlines():
  ingredients_dict[ingredient.strip()] = 0

# Create a cleaning output file to keep track of progress
fileOutput = open('cleaningOutput.txt', 'w')

# Go through and edit the database  
replaceIngredient(df, ingredients_dict, fileOutput)

# Output new database to CSV
df.to_csv('new_branded_food.csv', index=False)