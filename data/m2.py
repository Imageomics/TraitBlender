# import sklearn.datasets as datasets
# import pandas as pd
# import pywavefront as pwf
import os
import bpy
# d1 = datasets.make_moons(100, noise=0.3)[0]
# d2 = pd.DataFrame(d1, columns = ['A', 'B'])

# print(d2.head())

os.chdir("D:\\uyeda_lab\\Projects\\Evolution Simulator\\Evolution Simulator\\Code\\shinyapp\\EvoSim\\data\\defaults")
bpy.ops.import_scene.obj("suzanne.obj")