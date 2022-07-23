import json
import numpy as np
import itertools
from tqdm import tqdm

f = False
t = True
adjs = {'left': {0: [f, f, #adjacencies
                     f, f,
                     f, f],
                 1: [t, f,
                     f, f,
                     f, f],
                 2: [f, f,
                     f, f,
                     f, f],
                 3: [f, f,
                     t, f,
                     f, f],
                 4: [f, f,
                     f, f,
                     f, f],
                 5: [f, f,
                     f, f,
                     t, f]},
        'right': {0: [f, t,
                      f, f,
                      f, f],
                  1: [f, f,
                      f, f,
                      f, f],
                  2: [f, f,
                      f, t,
                      f, f],
                  3: [f, f,
                      f, f,
                      f, f],
                  4: [f, f,
                      f, f,
                      f, t],
                  5: [f, f,
                      f, f,
                      f, f]},
        'above': {0: [f, f,
                      f, f,
                      f, f],
                  1: [f, f,
                      f, f,
                      f, f],
                  2: [t, f,
                      f, f,
                      f, f],
                  3: [f, t,
                      f, f,
                      f, f],
                  4: [t, f,
                      t, f,
                      f, f],
                  5: [f, t,
                      f, t,
                      f, f]},
        'under': {0: [f, f,
                      t, f,
                      t, f],
                  1: [f, f,
                      f, t,
                      f, t],
                  2: [f, f,
                      f, f,
                      t, f],
                  3: [f, f,
                      f, f,
                      f, t],
                  4: [f, f,
                      f, f,
                      f, f],
                  5: [f, f,
                      f, f,
                      f, f]},
        'touching': {0: [f, t,
                         t, f,
                         f, f],
                     1: [t, f,
                         f, t,
                         f, f],
                     2: [t, f,
                         f, t,
                         t, f],
                     3: [f, t,
                         t, f,
                         f, t],
                     4: [f, f,
                         t, f,
                         f, t],
                     5: [f, f,
                         f, t,
                         t, f]},
        'notTouching': {0: [f, f,
                             f, t,
                             t, t],
                         1: [f, f,
                             t, f,
                             t, t],
                         2: [f, t,
                             f, f,
                             f, t],
                         3: [t, f,
                             f, f,
                             t, f],
                         4: [t, t,
                             f, t,
                             f, f],
                         5: [t, t,
                             t, f,
                             f, f]}}

class Ingredient: #holds an ingredient and its stats
    def __init__(self, item):
        self.name = item['name'] #str
        self.tier = item['tier'] #int
        self.level = item['level'] #int
        self.skills = item['skills'] #arr(str)
        self.identifications = item['identifications'] #dict(str:dict(str:int))
        self.itemOnlyIDs = item['itemOnlyIDs'] #dict(str:int)
        self.consumableOnlyIDs = item['consumableOnlyIDs'] #dict(str:int)
        self.ingredientPositionModifiers = item['ingredientPositionModifiers'] #dict(str:int)

    def isSkill(self, skill): #checks for a skill
        return True if skill in self.skills else False

    def isIdentification(self, identification): #checks for an identification
        return True if identification in self.identifications else False

    def isModifier(self): #checks for a modifier
        return True if any(modifier != 0 for modifier in self.ingredientPositionModifiers.values()) else False

class Pouch: #holds ingredients
    def __init__(self, path): #loads from json
        f = open('Ingredients_m.json', 'r')
        data = json.load(f)
        f.close()
        self.ingredients = {item['name']:Ingredient(item) for item in data['data']}
        cat_skills = []
        cat_identifications = []
        for name, ingredient in self.ingredients.items():
            cat_skills += ingredient.skills
            cat_identifications += ingredient.identifications
        self.all_skills = list(np.unique(cat_skills)) #list of all skills
        self.all_identifications = list(np.unique(cat_identifications)) #list of all identifications
        self.identification_item = None #best identification item

    def addIngredient(self, ingredient): #add ingredient
        self.ingredients[ingredient.name] = ingredient

    def getIngredients(self): #returns list of ingredients
        return list(self.ingredients.items())

    def getIngredientNames(self): #returns list of ingredient names
        return list(self.ingredients.keys())

    def useSkill(self, skill): #removes all ingredients withoutg iven skill
        if skill not in self.all_skills:
            return False
        for name, ingredient in self.getIngredients():
            if not ingredient.isSkill(skill):
                del self.ingredients[name]

    def useIdentification(self, identification): #removes all ingredients without given identification
        if identification not in self.all_identifications:
            return False
        for name, ingredient in self.getIngredients():
            if not (ingredient.isIdentification(identification) or ingredient.isModifier()):
                del self.ingredients[name]

    def heuristic(self, identification_range): #determine what the value of an item is
        minimum = identification_range['minimum']
        maximum = identification_range['maximum']
        return maximum
    
    def maxIdentification(self, identification): #finds ingredient with max identification
        best_name = None
        best_value = 0
        for name, ingredient in self.getIngredients():
            if ingredient.identifications.get(identification) == None:
                continue
            value = self.heuristic(ingredient.identifications[identification]) #heuristic
            if value > best_value: #better
                if best_name != None:
                    del self.ingredients[best_name] #delete old
                best_name = name
                best_value = value
            else: #worse
                del self.ingredients[name] #delete current
        self.identification_item = best_name

    def removeUselessModifiers(self, identification): #removes ingredients with useless modifiers
        for name, ingredient in self.getIngredients():
            if all(modifier <= 0 for modifier in ingredient.ingredientPositionModifiers.values()) and not ingredient.isIdentification(identification):
                del self.ingredients[name]

    def craft(self, identification): #crafts best item
        ingredients = self.getIngredientNames()
        ingredient_sets = list(itertools.product(ingredients, repeat=6)) #sets of 6 ingredients
        sets = len(ingredient_sets)

        best_bonus = -1
        best_ingredient_set = None
        for ingredient_set in tqdm(ingredient_sets, total=sets): #iterate through sets
            #if self.identification_item not in ingredient_set: #no identification item, no need to continue
            #    continue
            ok = False
            for ingredient in ingredient_set:
                if pouch.ingredients[ingredient].isIdentification(identification):
                    ok = True
            if not ok:
                continue
            durabilityModifier = 0
            duration = 0
            charges = 0
            for ingredient in ingredient_set: #iterate through ingredients
                durabilityModifier += pouch.ingredients[ingredient].itemOnlyIDs['durabilityModifier']
                duration += pouch.ingredients[ingredient].consumableOnlyIDs['duration']
                charges += pouch.ingredients[ingredient].consumableOnlyIDs['charges']
            #if durabilityModifier < -650: #too low dura
            #    continue
            #if duration < -600: #too low duration
            #    continue
            #if charges < 0: #too few charges
            #    continue
            identification_efficiency = [[0, 100], [0, 100], #[identification, efficiency] per slot
                                         [0, 100], [0, 100],
                                         [0, 100], [0, 100]]
            for ingredient_num, ingredient in enumerate(ingredient_set): #iterate through ingredients
                if pouch.ingredients[ingredient].identifications.get(identification) != None:
                    identification_efficiency[ingredient_num][0] += self.heuristic(pouch.ingredients[ingredient].identifications[identification]) #apply identification
                for slot in range(6): #apply ingredient efficiency to all slots
                    identification_efficiency[slot][1] += adjs['left'][ingredient_num][slot] * pouch.ingredients[ingredient].ingredientPositionModifiers['left']
                    identification_efficiency[slot][1] += adjs['right'][ingredient_num][slot] * pouch.ingredients[ingredient].ingredientPositionModifiers['right']
                    identification_efficiency[slot][1] += adjs['above'][ingredient_num][slot] * pouch.ingredients[ingredient].ingredientPositionModifiers['above']
                    identification_efficiency[slot][1] += adjs['under'][ingredient_num][slot] * pouch.ingredients[ingredient].ingredientPositionModifiers['under']
                    identification_efficiency[slot][1] += adjs['touching'][ingredient_num][slot] * pouch.ingredients[ingredient].ingredientPositionModifiers['touching']
                    identification_efficiency[slot][1] += adjs['notTouching'][ingredient_num][slot] * pouch.ingredients[ingredient].ingredientPositionModifiers['notTouching']

            strengthRequirement = 0
            dexterityRequirement = 0
            intelligenceRequirement = 0
            defenceRequirement = 0
            agilityRequirement = 0
            for ingredient_num, ingredient in enumerate(ingredient_set): #test skill funny business (off by one?)
                strengthRequirement += np.floor(pouch.ingredients[ingredient].itemOnlyIDs['strengthRequirement'] * identification_efficiency[ingredient_num][1] / 100)
                dexterityRequirement += np.floor(pouch.ingredients[ingredient].itemOnlyIDs['dexterityRequirement'] * identification_efficiency[ingredient_num][1] / 100)
                intelligenceRequirement += np.floor(pouch.ingredients[ingredient].itemOnlyIDs['intelligenceRequirement'] * identification_efficiency[ingredient_num][1] / 100)
                defenceRequirement += np.floor(pouch.ingredients[ingredient].itemOnlyIDs['defenceRequirement'] * identification_efficiency[ingredient_num][1] / 100)
                agilityRequirement += np.floor(pouch.ingredients[ingredient].itemOnlyIDs['agilityRequirement'] * identification_efficiency[ingredient_num][1] / 100)
            requirements = [strengthRequirement, dexterityRequirement, intelligenceRequirement, defenceRequirement, agilityRequirement]
            #if strengthRequirement > 108:
            #    continue
            #if dexterityRequirement > 108:
            #    continue
            #if intelligenceRequirement > 108:
            #    continue
            #if defenceRequirement > 108:
            #    continue
            #if agilityRequirement > 108:
            #    continue
            #if sum(requirements) > 214:
            #    continue
            
            bonus = sum([np.floor(identification * (efficiency / 100)) for (identification, efficiency) in identification_efficiency]) #calculate bonus
            #use np.floor (fix?) here because individual slots round first before applying to total
            if bonus > best_bonus: #update best bonus
                best_bonus = bonus
                best_ingredient_set = ingredient_set
                best_requirements = requirements
        return (best_bonus, best_ingredient_set, best_requirements)

    def choose(self, skill, identification): #cleans pouch to only given parameters
        if skill not in self.all_skills:
            raise ValueError(f'Skill \'{skill}\' not in valid skills:\n{self.all_skills}.')
        if identification not in self.all_identifications:
            raise ValueError(f'Identification \'{identification}\' not in valid identifications:\n{self.all_identifications}.')
        self.useSkill(skill)
        self.useIdentification(identification)
        self.maxIdentification(identification) #this removes stuff that isnt the best ingredient, use extras if you want stuff added back
        self.removeUselessModifiers(identification) #this removes stuff like obelisk core and parasitic abscission

    def go(self, skill, identification, add=[]): #runs the whole thing
        self.choose(skill, identification)
        for ingredient in add:
            self.addIngredient(ingredient)
        print(self.ingredients.keys())
        out = self.craft(identification)
        return out

#skills
#['ALCHEMISM', 'ARMOURING', 'COOKING', 'JEWELING', 'SCRIBING',
#'TAILORING', 'WEAPONSMITHING', 'WOODWORKING']

#identifications
#['AGILITYPOINTS', 'AIRDAMAGEBONUS', 'AIRDEFENSE', 'ATTACKSPEED', 'DAMAGEBONUS',
#'DAMAGEBONUSRAW', 'DEFENSEPOINTS', 'DEXTERITYPOINTS', 'EARTHDAMAGEBONUS', 'EARTHDEFENSE',
#'EMERALDSTEALING', 'EXPLODING', 'FIREDAMAGEBONUS', 'FIREDEFENSE', 'GATHER_SPEED',
#'GATHER_XP_BONUS', 'HEALTHBONUS', 'HEALTHREGEN', 'HEALTHREGENRAW', 'INTELLIGENCEPOINTS',
#'JUMP_HEIGHT', 'LIFESTEAL', 'LOOTBONUS', 'LOOT_QUALITY', 'MANAREGEN',
#'MANASTEAL', 'POISON', 'REFLECTION', 'SOULPOINTS', 'SPEED',
#'SPELLDAMAGE', 'SPELLDAMAGERAW', 'STAMINA', 'STAMINA_REGEN', 'STRENGTHPOINTS',
#'THORNS', 'THUNDERDAMAGEBONUS', 'THUNDERDEFENSE', 'WATERDAMAGEBONUS', 'WATERDEFENSE',
#'XPBONUS']

pouch = Pouch('Ingredients_m.json')
everything = Pouch('Ingredients_m.json')
extras = []
#extras = [everything.ingredients['Foul Fairy Dust']]
out = pouch.go('WEAPONSMITHING', 'HEALTHREGENRAW', add=extras)
print(out)
