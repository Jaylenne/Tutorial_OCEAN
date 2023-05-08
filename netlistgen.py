import numpy as np
import os

def genarray(num_rows, num_cols, dir=".", mode="w", cellname="unit1t1r"):
    with open(f"{dir}/netlist", mode) as f:
        for i in range(num_rows):
            for j in range(num_cols):
                f.write(f"1t1rcell_{i}{j} (te{i} tg{j} bl{j} GND) {cellname} G=G_{i}{j}\n")

def gensource(num_rows, num_cols, dir=".", mode="w"):
    with open(f"{dir}/design/netlist", mode) as f:
        for i in range(num_rows):
            f.write(f"vrow{i} (te{i} GND) vsource type=pwl scale=1 file=\"{dir}/signal/vrow{i}.sgn\"\n")
        for i in range(num_cols):
            f.write(f"vcol{i} (bl{i} GND) vsource type=dc dc=0\n")
            f.write(f"vg{i} (tg{i} GND) vsource type=dc dc=3.3\n")
        f.write("vgnd (GND 0) vsource type=dc dc=0\n")

def writepwl(delay, rise, fall, ontime, xarray, file, mode="a", high=3.3, low=0):
    f = open(file, mode)
    start = 0
    f.write(f"{start} {low}\n")
    for x in xarray:
        f.write(f"{start+delay} {low}\n")
        f.write(f"{start+delay+rise} {x*high}\n")
        f.write(f"{start+delay+rise+ontime} {high*x}\n")
        f.write(f"{start+delay+rise+ontime+fall} {low}\n")
        start = start+delay+rise+ontime+fall

def genVarOcean(filename, weight, gscale=100e-6):
    f = open(filename, "w")
    for i in range(weight.shape[0]):
        for j in range(weight.shape[1]):
            f.write(f"desVar(\"G_{i}{j}\" {weight[i, j]*gscale})\n")
        
def genNetlistConfig(dir):
    with open(f"{dir}/netlistHeader" , "w") as f:
        f.write("simulator lang=spectre\n")
        f.write("global 0\n")

    with open(f"{dir}/netlistFooter", "w") as f:
        f.write("include \"../1t1r.scs\"\n")
    

if __name__ == '__main__':
    size = (5, 8)  # Array size
    vec = np.random.randint(0, 2, size=(5, 8))  # input vector it contains 8 cycles
    weight = np.random.rand(3, 5, 8)  # weight value. It contains 3 sets

    os.mkdir("./design")
    os.mkdir("./ocean")
    os.mkdir("./signal")
    os.mkdir("./results")

    genNetlistConfig("./design")

    with open("./trueResults.data", "w") as f:
        f.write(str(np.exp(np.einsum('ij,nik->njk', vec, weight))))

    genarray(size[0], size[1], dir="./design")  # generte 1T1R Array netlist
    gensource(5, 8, mode="a")  # generate vsource netlist
    for i in range(vec.shape[0]):
        writepwl(10e-9, 0.1e-9, 0.1e-9, 30e-9, vec[i], f"./signal/vrow{i}.sgn", mode="w", high=0.2)  # write pwl signal into pwl file
    for i in range(weight.shape[0]):
        genVarOcean(f"./ocean/desVar{i}.ocn", weight[i])

    