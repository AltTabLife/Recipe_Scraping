'''
This isn't really meant to be an extensive package. It's mainly just for consistency.
'''

import json, os
from pathlib import Path

class CategoryNotProvided(Exception):
    pass

class RecipeBook:
    '''
    Recipe Book handler that takes an output folder to name it, storing by either category or the first letter of each recipe.

    book = RecipeBook(output_folder, category_sort=True/False)
    
    Methods:
        add_category(category_title, category_href)

        add_recipe(category_title=None recipe_title=None, recipe_link=None, ingredients_array=None, instructions_array=None)

    '''
    #Be sure to have distinguishability between categories and raw recipes
    def __init__(self, output_folder, category_sort = False):
        #init the book
        self.output_folder = Path(output_folder)
        self.category_sort = category_sort
        #Sort by alphabet if no category_sort
        if not self.output_folder.exists() and category_sort == False:
            self.output_folder.mkdir(exist_ok=True)
            for letter in 'abcdefghijklmnopqrstuvwxyz':
                json_filename = f"{letter}_recipes.json"
                json_path = self.output_folder / json_filename
                with json_path.open(mode='w') as json_file:
                    pass
        elif not self.output_folder.exists() and category_sort == True:
            self.output_folder.mkdir(exist_ok = True)
    
    def extract_json(self, json_filename):
        if os.path.getsize(json_filename) <= 2:
            return {}
        else:
            with open(json_filename, 'r') as jf:
                return json.load(jf)

    def check_file_string(self, category_title = None, recipe_title = None):
        '''
        Returns the sanitized Path(output_folder / file_string) for either a category title or a recipe title.

        '''
        if self.category_sort == True:
        
            try:
                #Sanitize to uniform format
                category_words = category_title.split()
                formatted_category = ''.join(word.capitalize for word in category_words)
                
                #create file string
                category_file = self.output_folder / f'{formatted_category}_recipes.json'
                return category_file
            except:
                "Category processing failed"
        elif self.category_sort == False:
                #Sanitize
                for char in recipe_title:
                    if char.isalpha():
                        first_letter = char.lower()
                        recipe_file = self.output_folder / f'{first_letter}_recipes.json'
                        
                        return recipe_file
                    

    def check_recipe_existence(self, category_title = None, recipe_title = None):
        recipe_file = self.check_file_string(recipe_title=recipe_title)

        if self.category_sort == True:
            try:
                if category_title == None:
                    raise CategoryNotProvided("Category title is not provided")
                
                category_file = self.check_file_string(category_title=category_title)

                category_dict = self.extract_json(category_file)
                if recipe_title in category_dict:
                    return True
                else:
                    return False
            except CategoryNotProvided as e:
                print(f'Error: {e}')

        elif self.category_sort == False:
            #If no category sort, check it in the file.
            rf_dict = self.extract_json(recipe_file)

            if recipe_title in rf_dict:
                return True
            else:
                return False

    def add_category(self, category_title, category_href):
        
        category_path = self.check_file_string(category_title=category_title)
        if not category_path.exists():
            file_dict = {
                'links': [category_href]

            }
            with open(category_path, 'w') as category_file:
                category_file.write(json.dumps(file_dict, indent=4))
        elif category_path.exists():
            file_dict = self.extract_json(category_path)
            with open(category_path, 'w+') as category_file:
                file_dict['links'].append(category_href)


    def add_recipe(
        self,
        category_title=None,
        recipe_title=None, 
        recipe_link=None,
        ingredients_array=None,
        instructions_array=None
        ):
        recipe_file = self.check_file_string(recipe_title=recipe_title)

        if self.category_sort == True:
            try:
                if category_title == None:
                    raise CategoryNotProvided("Category title is not provided")
                else:
                    category_file = self.check_file_string(category_title=category_title)

                    recipe_dict = {
                        recipe_title:{
                            'link':recipe_link,
                            'ingredient':ingredients_array,
                            'instructions':instructions_array
                            }
                    }
                    rf_dict = self.extract_json(category_file)

                    if recipe_title in rf_dict:
                        print(f'{recipe_title} found in {recipe_file}')
                        return
                    else:
                        rf_dict.update(recipe_dict)
                        with open(category_file, 'w+') as rf:
                            rf.write(json.dumps(rf_dict, indent=4))
    
            except CategoryNotProvided as e:
                print(f'Error: {e}')

        elif self.category_sort == False:
            #If no category sort, check it in the file.
            rf_dict = self.extract_json(recipe_file)
            recipe_dict = {
                recipe_title:{
                    'link':recipe_link,
                    'ingredient':ingredients_array,
                    'instructions':instructions_array
                    }
            }
            if recipe_title in rf_dict:
                print(f'{recipe_title} found in {recipe_file}')
                return
            else:
                rf_dict.update(recipe_dict)
                with open(recipe_file, 'w') as rf:
                    rf.write(json.dumps(rf_dict, indent=4))


