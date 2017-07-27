def rdkit2amberpdb(mol_pdb_txt):
    """
    Converts a PDB block from openbabel or rdkit like format to  the PDB block in rism pdb format
    :param mol_pdb_txt: pdb block with openbabel  or rdkit like format
    :return: string with a pdb block in rism pdb comparable format
    """
    mol_new_lines = []
    atom_counts = {}
    line_format = '{0[0]}{0[1]:>7}{0[2]:>4}{0[3]:>5}{0[4]:>6}{0[5]: 12.3f}{0[6]: 8.3f}{0[7]: 8.3f}{0[8]:>6}{0[9]:>6}{0[10]:>12}'
    mol_txt_lines = mol_pdb_txt.split('\n')
    for line in mol_txt_lines:
        if line.startswith('HETATM') or line.startswith('ATOM'):
            strings = line.split()
            strings[0] = 'ATOM'
            atom_counts[strings[2]] = atom_counts.get(strings[2], 0) + 1
            strings[2] = strings[2]  # This line differ from calcGeomOBabel.py
            strings[3] = 'MOL'
            strings[5] = float(strings[5])
            strings[6] = float(strings[6])
            strings[7] = float(strings[7])
            new_line = line_format.format(strings)
            mol_new_lines.append(new_line)
    mol_new_lines.extend(['TER', 'END'])
    return '\n'.join(mol_new_lines)
