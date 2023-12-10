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

    #Initialization shit
    cache_directory = 'ElanasPantryCache'
    instance1 = SeleniumInstance(cache_directory=cache_directory, options=['--disable-javascript'], base_timeout=10, variance=5)
    output_folder = 'RecipeBook'
    book1 = RecipeBook(output_folder=output_folder, category_sort=True)


    ##Establish root page
    root_page = 'https://elanaspantry.com/specific-carbohydrate-diet/'

    #Scrape categories from the root page
    instance1.get(root_page)
    category_container = '//*[@id="genesis-content"]/article/div/div[1]/div'
    container_element = instance1.wait_and_extract(('By.XPATH', category_container))
#    container_element = instance1.find_element(By.XPATH, category_container)
    category_tiles = container_element.find_elements(By.CLASS_NAME, 'kt-inside-inner-col')
    
    category_dict = {} #Setup for next section
    for category_tile in category_tiles:
        category_text = category_tile.find_element(By.TAG_NAME, 'h2').text
        category_link = category_tile.find_element(By.TAG_NAME, 'a').get_attribute('href')
        book1.add_category(category_text, category_link)
        category_dict_line = {category_text: category_link}
        category_dict.update(category_dict_line)
    #Shuffle the categories to help escape detection and scrape recipe names
    #FIX. Might help if there was a shuffle statement and not a 1 for 1.
    
#    category_dict = {key: book1.book[key]['link'] for key in book1.book}

    for category_menu_title in category_dict.keys():
        category_menu_link = category_dict[category_menu_title]
        instance1.get(category_menu_link)

        def recursive_scrape(root_page_url):
            #Notate the recipes for the current page
            recipe_tile_container = instance1.wait_and_extract(('By.ID', 'genesis-content'))
#            recipe_tile_container = instance1.find_element(By.ID, 'genesis-content')
            recipe_tiles = recipe_tile_container.find_elements(By.TAG_NAME, 'article')

            ##Clean out ones that already exist
            recipe_links = []
            for recipe in recipe_tiles:
                recipe = recipe.find_element(By.CSS_SELECTOR, 'h2 a')
                if book1.check_recipe_existence(category_title=category_menu_title, recipe_title=recipe.text):
                    continue
                else:
                    recipe_links.append(recipe.get_attribute('href'))

            for unsaved_recipe_link in recipe_links:

                instance1.get(unsaved_recipe_link)

                #Extract the title on the page
                recipe_title = instance1.wait_and_extract(('By.TAG_NAME', 'h1')).text
#                recipe_title = instance1.find_element(By.TAG_NAME, 'h1').text

                #Extract the ingredients on the current page

                ingredients_container = instance1.wait_and_extract(('By.CLASS_NAME', 'wprm-recipe-ingredients'))
#                ingredients_container = instance1.find_element(By.CLASS_NAME, 'wprm-recipe-ingredients')
                ingredients = ingredients_container.find_elements(By.TAG_NAME, 'li')
                ingredients_array = [ingredient.text for ingredient in ingredients]

                #Extract steps to cook
                instruction_container = instance1.wait_and_extract(('By.CLASS_NAME', 'wprm-recipe-instruction-group'))
#                instruction_container = instance1.find_element(By.CLASS_NAME, 'wprm-recipe-instruction-group')
                instructions = instruction_container.find_elements(By.TAG_NAME, 'li')
                instructions_array = [instruction.text for instruction in instructions]

                book1.add_recipe(category_menu_title, recipe_title, unsaved_recipe_link, ingredients_array, instructions_array)

                instance1.back()

            #Recursively loop through the menu pages
            try:
                next_page = instance1.wait_and_extract(('By.CSS_SELECTOR', 'li.pagination-next a'))
#                next_page = instance1.find_element(By.CSS_SELECTOR, 'li.pagination-next a').get_attribute('href')
                print('Moving on to next page in category')
                instance1.get(next_page)
                recursive_scrape(root_page_url=root_page)
            except:
                print('No next page in category found, moving to next category')
                instance1.get(root_page_url)
                instance1.short_wait()
        recursive_scrape(root_page_url=root_page)
