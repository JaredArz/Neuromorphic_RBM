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
        unique_Gdds = set()
        unique_Gccs = set()
        unique_Ndds = set()
        for sub_dir in root_glob:
            pattern_Gdd = re.compile(r'Gdd(\d+(\.\d+)?)')
            pattern_Gcc = re.compile(r'Gcc(\d+(\.\d+)?)')
            pattern_Ndd = re.compile(r'Ndd(\d+(\.\d+)?)')
            unique_Gdds.add((pattern_Gdd.search(sub_dir)).group(1))
            unique_Gccs.add((pattern_Gcc.search(sub_dir)).group(1))
            unique_Ndds.add((pattern_Ndd.search(sub_dir)).group(1))
        self.Gdds = unique_Gdds
        self.Gccs = unique_Gccs
        self.Ndds = unique_Ndds

    def get_Gdds(self):
        return sorted(list(self.Gdds))

    def get_Gccs(self):
        return sorted(list(self.Gccs))

    def get_Ndds(self):
        return sorted(list(self.Ndds))

    def get_data(self, Gdd, Gcc, Ndd):
        if ((str(Gcc) not in self.Gccs) or (str(Gdd) not in self.Gdds) or (str(Ndd) not in self.Ndds)):
            raise(AttributeError)

        path_to_get = os.path.join(self.root, f"p_Gdd{Gdd}_Gcc{Gcc}_Ndd{Ndd}")
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
                energy_usage = np.load(f)
                print(energy_usage)
            os.remove("temp.npy")

        data = {
            "sols" : all_s,
            "costs" : all_e,
            "energy" : energy_usage,
            "mean" : extracted_values["Mean"],
            "stddev" : extracted_values["Stddev"],
            "high" : extracted_values["High"],
            "low" : extracted_values["Low"],
        }

        return data

    def get_interactive(self):
        print("enter path to root of sim")
        root = input()
        self.__init__(root)
        print("Enter Gdd, Gcc, Ndd. Press enter between")
        Gdd = input()
        Gcc = input()
        Ndd = input()
        data = self.get_data(Gdd,Gcc,Ndd)
        return data

    def slice(self, key,entry):
        key_map = {"Gdd": 0,
                   "Gcc": 1,
                   "Ndd": 2}

        if key == "Gdd":
            slice_range = self.Gdds
        elif key == "Gcc":
            slice_range = self.Gccs
        elif key == "Ndd":
            slice_range = self.Ndds
        try:
            length = len(slice_range)
        except(UnboundLocalError):
            raise
        slice_range = sorted(list(slice_range))

        args = [np.zeros(length), np.zeros(length), np.zeros(length)]
        args[ key_map[key] ] = slice_range
        args = np.column_stack(args)

        sliced = []
        for arg in args:
            sliced.append(self.get_data( *arg )[entry])
        sliced = list(np.array(sliced).flatten())

        return sliced

#test = sim("../outputs/RBM_sims_12-19/MaxSat_Memristor_500_15:30:47")
test = sim("../outputs/RBM_sims_12-27/MaxSat_Memristor_10_16:18:40")
data = test.get_data(0.0,0.0,0.0)
print(data["energy"])
