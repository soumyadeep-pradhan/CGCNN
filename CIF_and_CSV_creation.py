from mp_api.client import MPRester
from pymatgen.core import Composition

from pymatgen.ext.matproj import MPRester
from pymatgen.io.cif import CifWriter

import os
import pandas as pd

api_key = "1oCZOPAFrvxwXD5QlNiaTIo9gQmPB9Ll" # API KEY of Materials Project

with MPRester(api_key) as mpr:
    docs = mpr.materials.summary.search(
        elements=["O"],
        fields=["material_id","formation_energy_per_atom","formula_pretty","elements","energy_above_hull","nelements","structure"]
    )
print(len(docs)) # No of Oxides obtained from Materials Project using API query

dict = [{"material_id":doc.material_id.replace('mp-',''),"forumula_pretty":doc.formula_pretty,"formation_energy_per_atom":doc.formation_energy_per_atom,  "energy_above_hull":doc.energy_above_hull} for doc in docs]
df = pd.DataFrame(dict)
df.to_csv('all_oxides_with_o2_no_hull_criteria.csv', index = False)

docs = [doc for doc in docs if doc.nelements != 1]
print(len(docs)) # No of oxides after removal of O2

dict = [{"material_id":doc.material_id.replace('mp-',''),"forumula_pretty":doc.formula_pretty,"formation_energy_per_atom":doc.formation_energy_per_atom,  "energy_above_hull":doc.energy_above_hull} for doc in docs]
df = pd.DataFrame(dict)

df.to_csv('all_oxides_without_o2_no_hull_criteria.csv', index = False)


excluded_elements = ["H", "C", "N", "P", "S", "Se", "F", "Cl", "Br", "I", "At", "Te", "Po", "He", "Ne", "Ar", "Kr", "Xe", "Rn", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "B", "Fl", "Mc", "Lv", "Ts", "Og"]

material_id_with_mp = []
material_id = []
formation_energy = []
formula_pretty=[]
energy_above_hull=[]
excluded_docs=[]

for doc in docs:
    elements_in_doc = [doc.elements[i].value for i in range(len(doc.elements))]
    num_of_atoms = Composition(doc.formula_pretty).num_atoms
    if len(set(elements_in_doc).intersection(excluded_elements)) == 0  and (num_of_atoms*doc.energy_above_hull <= 0.0257):
            material_id_with_mp.append(str(doc.material_id))
            material_id.append(str(doc.material_id.replace('mp-', '')))
            formation_energy.append(doc.formation_energy_per_atom)
            formula_pretty.append(doc.formula_pretty)
            energy_above_hull.append(doc.energy_above_hull)
            excluded_docs.append(doc)

data = {'material_id': material_id, 'formation_energy': formation_energy,'formula_pretty': formula_pretty,'energy_above_hull':energy_above_hull}

df = pd.DataFrame(data)

df.to_csv('filtered_oxides.csv', index=False)
df.drop(columns=['formula_pretty','energy_above_hull'], inplace=True)

df.to_csv('id_prop.csv', index=False,header=False) # csv format required for cgcnn without any header


output_dir = 'data' # all cifs will be stored in the 'data' folder
os.makedirs(output_dir, exist_ok=True) # to create the 'd'ata' folder unless it is already there

for doc in excluded_docs:
    try:
        cif_writer = CifWriter(doc.structure)
        file_name = doc.material_id.replace("mp-", "")
        output_file = os.path.join(output_dir, f"{file_name}.cif")
        cif_writer.write_file(output_file)  
    except Exception as e:
        print(f"Error retrieving CIF for {doc.material_id}: {e}")
