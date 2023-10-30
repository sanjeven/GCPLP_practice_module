import pandas as pd
import re
import unicodedata


def has_vulgar_fraction(digits: dict):
	result = False
	for _, value in digits.items():
		if value < 1:
			result = True
			break

	return result

def get_the_string_value_pair(value_digits):
	value_digits_len = len(value_digits) - 1

	ten_multiplier = 10**(value_digits_len - 1) # 10^(n - 1)
	total_sum_product = 0
	full_digit_string = ""

	# Do the maths merge all numbers found
	ten_multiplier = 10**(value_digits_len - 1) # 10^(n - 1)
	total_sum_product = 0
	full_digit_string = ""
	for key, value in value_digits.items():
		if value < 1:
			total_sum_product += value
		else:
			total_sum_product += value*ten_multiplier
			ten_multiplier = ten_multiplier/10
		full_digit_string += key

	return full_digit_string, total_sum_product

def convert_all_vulgar_fractions(string_value):
	result = {}
	value_digits = {}
	for character in string_value:
		# The heart of the solution is here
		try:
			value_digits[character] = unicodedata.numeric(character)
		except:
			# if string has no vulgar fraction i.e 1.25, dont try to parse it
			if not has_vulgar_fraction(value_digits):
				value_digits = {}
				continue
			
			# exclude the vulgar fraction value
			key, value = get_the_string_value_pair(value_digits)
			result[key] = value
			value_digits = {}
		
	# Sometimes the string has the fraction at the end
	if has_vulgar_fraction(value_digits):
		key, value = get_the_string_value_pair(value_digits)
		result[key] = value

	return result

def run(ingredient):
	items_to_repace = convert_all_vulgar_fractions(ingredient)
	for key, value in items_to_repace.items():
		ingredient = ingredient.replace(key, str(value))
	return ingredient

# read in the pre-processed data
recipe_df = pd.read_csv('cleaned_recipes_cuisine.csv')

# replace vulgar fraction to decimal.
#https://stackoverflow.com/a/71738137
recipe_df['ingredients'] = recipe_df['ingredients'].apply(run)

#Allow alphanumeric 
#Allow ,./[]%()

replace_regex = '[^A-Za-z0-9\/\,\.\'\%\[\]\(\) ]+'
recipe_df['ingredients'] = recipe_df['ingredients'].str.replace(replace_regex, '', regex=True)

recipe_df.to_csv('cleaned_recipes_v2.csv', index=False)
