from selenium.webdriver.common.by import By

from pathlib import Path

from SeleniumInstance import SeleniumInstance
from RecipeBook import RecipeBook
# from RecipeBook import RecipeBook

class FileAutomation:    
    def unique_filename(prefix, file_extension):
        index = 1
        while True:
            filename = f"{prefix}_{index}.{file_extension}"
            if not Path(filename).is_file():
                return filename
            index += 1

if __name__ == '__main__':

    #init
    cache_directory = 'SeleniumCache'
    instance1 = SeleniumInstance(cache_directory=cache_directory, options=['--disable-javascript'], base_timeout=10, variance=5)
    instance1.set_page_load_timeout(30)

    output_folder = 'EveryLastBite'
    book1 = RecipeBook(output_folder=output_folder)

    ##Establish root page
    root_page = 'https://www.everylastbite.com/by-diet/specific-carbohydrate-diet/'

    instance1.get(root_page)

    
    
    def recursive_sweep(iteration = 1):
    
        recipe_tiles_container = instance1.find_element(By.CSS_SELECTOR, 'div#content div.archives')
        recipe_tiles = recipe_tiles_container.find_elements(By.TAG_NAME, 'a')
        unsaved_recipe_links = []
        excluded_keywords = ['meal-plan', 'menu']
        for recipe in recipe_tiles:
            if not book1.check_recipe_existence(recipe_title=recipe.text) and not any(keyword in recipe.get_attribute('href') for keyword in excluded_keywords):
                unsaved_recipe_links.append(recipe.get_attribute('href'))
        for unsaved_recipe_link in unsaved_recipe_links:
            
            instance1.get(unsaved_recipe_link)
            #Extract the title on the page
            recipe_title = instance1.find_element(By.TAG_NAME, 'h1').text
            #Extract ingredients for current page
            ingredients_container = instance1.find_element(By.CLASS_NAME, 'wprm-recipe-ingredients')
            ingredients = ingredients_container.find_elements(By.TAG_NAME, 'li')
            ingredients_array = [ingredient.text for ingredient in ingredients]
            #Extract steps to cook
            instruction_container = instance1.find_element(By.CLASS_NAME, 'wprm-recipe-instructions')
            instructions = instruction_container.find_elements(By.TAG_NAME, 'li')
            instructions_array = [instruction.text for instruction in instructions]
            book1.add_recipe(recipe_title=recipe_title, recipe_link=unsaved_recipe_link, ingredients_array=ingredients_array, instructions_array=instructions_array)
            instance1.back()
                
        try:
            next_page = instance1.find_element(By.CSS_SELECTOR, 'a.next').get_attribute('href')
            next_page_bool = True            
        except:
            print('Could not find a next page. Exiting program')
            next_page_bool = False

        if next_page_bool == True:
            print('Moving to next page')
            instance1.get(next_page)
            iteration += 1
            recursive_sweep(iteration)
    recursive_sweep()