# FoodDataCentralTextCorrection
The main purpose of this tool is to fix spelling mistakes in FoodData Central's Branded Foods database. Prior to this project Cal Poly's Kinesiology Department was manually looking up mistakes in the ingredients list of the database and fixing them. The database has over 300,000 entries and it is impossible to catch and fix all spelling mistakes manually. The tool uses PeterNorvig's spell checker and the SymSpell libary to generate possible corrections.

# Usage
1) Download the files as a zip folder and unzip them to C:\Users\YOURUSERNAME\Desktop\correction-prototype
2) Download the [branded foods database](https://data.nal.usda.gov/dataset/usda-branded-food-products-database) as a csv file from FoodData Central and save it in the same directory as the tool.
3) Open command prompt and type in: 

 - ```cd Desktop```

 - ```cd correction-prototype```

  The path on the command prompt should be: C:\Users\YOURUSERNAME\Desktop\correction-prototype
  
4) Install python 3 by following this [tutorial](https://phoenixnap.com/kb/how-to-install-python-3-windows).
5) Verify your python installation by typing ```python``` in your command prompt. It should look like [this](https://drive.google.com/file/d/17EINfJJ662u4BVEOv0mUANDx8q_GLqis/view).

