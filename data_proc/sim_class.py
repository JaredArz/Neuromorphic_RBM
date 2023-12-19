import re
import glob
import os
import gzip
import numpy as np


class sim:
    def __init__(self, root = None):
        if root is None:
            return
        self.root = root
        root_glob = glob.glob(f'{root}/*')
        unique_Gccs = set()
        unique_Gdds = set()
        unique_Ndds = set()
        for sub_dir in root_glob:
            pattern_Gdd = re.compile(r'Gdd(\d+(\.\d+)?)')
            pattern_Gcc = re.compile(r'Gcc(\d+(\.\d+)?)')
            pattern_Ndd = re.compile(r'Ndd(\d+(\.\d+)?)')
            unique_Gdds.add((pattern_Gdd.search(sub_dir)).group(1))
            unique_Gccs.add((pattern_Gcc.search(sub_dir)).group(1))
            unique_Ndds.add((pattern_Ndd.search(sub_dir)).group(1))
        self.Gccs = unique_Gccs
        self.Gdds = unique_Gdds
        self.Ndds = unique_Ndds

    def get_interactive(self):
        print("enter path to root of sim")
        root = input()
        self.__init__(root)
        print("Enter Gdd, Gcc, Ndd. Press enter between")
        Gdd = input()
        Gcc = input()
        Ndd = input()
        data = self.get(Gdd,Gcc,Ndd)
        return data

    def get(self, Gdd, Gcc, Ndd):
        if str(Gcc) not in self.Gccs or str(Gdd) not in self.Gdds or str(Ndd) not in self.Ndds:
            raise(AttributeError)

        #FIXME: future pahs wont need strinf
        path_to_get = os.path.join(self.root, f"p_Gdd{Gdd}_Gcc{Gcc}_Ndd{Ndd}_s1.00e+12")
        patterns = {
            "Mean" : r"Mean: (\d+\.\d+)",
            "Stddev" : r"Std. dev: (\d+\.\d+)",
            "High" : r"High: (\d+\.\d+)",
            "Low" : r"Low: (\d+\.\d+)"
        }
        extracted_values = {}
        with open(os.path.join(path_to_get, "device_iterations.txt"), 'r') as f:
            file_contents = f.read()
            file_contents = file_contents.replace('\n', ' ')
            for key, pattern in patterns.items():
                match = re.search(pattern, file_contents)
                value = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
                extracted_values[key] = value

        dir_glob = glob.glob(f"{path_to_get}/*")
        for i,f_path in enumerate(dir_glob):
            if "device_iterations" in f_path or "metadata" in f_path:
                continue
            with gzip.open(f_path, 'rb') as f:
                f_content = f.read()
            with open("temp.npy", 'ab') as f:
                f.write(f_content)
            with open("temp.npy", 'rb') as f:
                all_e = np.load(f)
                all_s = np.load(f)
                #FIXME: will have this data in future
                #energy_usage = np.load(f)
            os.remove("temp.npy")

        data = {
            "sols" : all_s,
            "costs" : all_e,
            #FIXME:
            #"energy" : energy_usage,
            "mean" : extracted_values["Mean"],
            "stddev" : extracted_values["Stddev"],
            "high" : extracted_values["High"],
            "low" : extracted_values["Low"],
        }

        return data


#test = sim("../outputs/RBM_sims_12-13/MaxSat_MTJ_500_14:44:03")
#print(test.Gccs)
#print(test.get(0.0, 0.0, 0.0))
