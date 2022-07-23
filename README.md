# WynnRecipeOptimizer
wynncraft crafting recipe optimizer

a bit of code i wrote to optimize crafting recipes
i only really planned to use this for personal use but since people wanted the code its provided here in this repository

the code requires an `Ingredients_m.json` file for the ingredient information, i modified mine slightly since there were some odd characters in the original
it also requires `numpy` and `tqdm`

to calculate a recipe you need to change line 314 to the skill and identification you want
you can then run the code through console by using `python crafty.py` or however else you choose

stuff you can change:
| line number | name | description |
| ----------- | ---- | ----------- |
| line 224 | `durabilityModifier` | the maximum durability lost from the base durability when crafting this recipe
| line 226 | `duration` | the maximum duration lost from the base duration when crafting this recipe
| line 228 | `charges` | the maximum charges lost from the base charges when crafting this recipe
| line 256 | `strengthRequirement` | the maximum strength skill points the recipe can use |
| line 258 | `dexterityRequirement` | the maximum dexterity skill points the recipe can use |
| line 260 | `intelligenceRequirement` | the maximum intelligence skill points the recipe can use |
| line 262 | `defenceRequirement` | the maximum defence skill points the recipe can use |
| line 264 | `agilityRequirement` | the maximum agility skill points the recipe can use |
| line 266 | `sum(requirements)` | the total skill points the recipe can use |
| line 271 | `if bonus > best_bonus:` | the way a best recipe is found, change to `<` if you want to find the worst recipe |
| line 285 | `self.removeUselessModifiers(identification)` | this function removes items that dont have at least one positive modifier (obelisk core, parasitic absicssion) |
| line 312 | `extras = []` | this is where you can add extra items, by default when running the code all items that dont have positive modifiers or the selected modifier will be removed, this is a good place to add durability or charge enhancing items (luxroot cuttings, death whistle leaf) |

i eventually plan to add a gui or something so that its more accessible for the end user
