class Spatial:
    def __init__(self):
        self.spatial_str = ""
        self.indent = 0

    def getSpatialStr(self):
        return self.spatial_str

    def addIndent(self, line):
        for i in range(self.indent):
            line = "\t" + line
        return line

    def addNewline(self, line=None):
        if line is None:
            self.spatial_str += "\n"
        else:
            line += "\n"
        return line

    def format(self, line):
        return self.addNewline(self.addIndent(line))

    def loopBody(self, lines):
        for idx, line in enumerate(lines):
            lines[idx] = "\t" + line
        return lines

    def writeBlock(self, lines):
        for line in lines:
            self.spatial_str += self.format(line)
        self.addNewline()

    def incIndentation(self):
        self.indent += 1

    def decIndentation(self):
        self.indent -= 1

    def makeSpatialFile(self, base_dir, app_name):
        with open(base_dir + "/" + app_name + ".scala", "w") as fp:
            fp.write(self.spatial_str)

    def setupImports(self, *args):
        lines = []
        for arg in args:
            lines.append("import " + arg)
        self.writeBlock(lines)

    def setupClass(self, app_name):
        lines = []
        lines.append("@spatial class " + app_name +
                     " extends SpatialTest {")
        self.writeBlock(lines)
        self.incIndentation()

    def setupConstants(self, constants):
        lines = []
        for key, val in constants.items():
            lines.append("val " + key + " = " + str(val))
        self.writeBlock(lines)

    def setupTypes(self, types):
        lines = []
        for key, val in types.items():
            lines.append("type " + key + " = " + str(val))
        self.writeBlock(lines)

    def setupInOutFile(self):
        lines = []
        lines.append("val infile = buildPath(IR.config.genDir," +
                     "\"tungsten\", \"in.csv\")")
        lines.append("val outfile = buildPath(IR.config.genDir," +
                     "\"tungsten\", \"out.csv\")")
        lines.append("createDirectories(dirName(infile))")
        lines.append("val inputs = List.tabulate(N * field) {i => i}")
        lines.append("writeCSVNow(inputs, infile)")
        self.writeBlock(lines)

    def setupStreams(self):
        lines = []
        lines.append("val stream_in  = StreamIn[T]" +
                     "(FileBus[T](infile))")
        lines.append("val stream_out  = StreamOut[Tup2[I32,Bit]]" +
                     "(FileEOFBus[Tup2[I32,Bit]](outfile))")
        self.writeBlock(lines)

    def setupMain(self):
        self.writeBlock(["def main(args: Array[String]): Unit = {"])
        self.incIndentation()
        self.setupInOutFile()
        self.setupStreams()
        self.writeBlock(["Accel {"])
        self.incIndentation()

    def setupMemories(self, mems):
        lines = []
        for key, val in mems.items():
            line = ("val " + key + " = " +
                    val["mem_type"] + "[" +
                    val["data_type"] + "](" +
                    str(val["dims"])[1:-1] + ")")
            if val["mem_type"] == "FileLUT":
                line += "(" + val["path"] + ")"
            lines.append(line)

        self.writeBlock(lines)

    def startStream(self, num_iters, idx):
        self.writeBlock(["Foreach(*) { " +
                        idx + "=>"])

        self.incIndentation()

    def foreach(self, num_iters, par, idx, inner_lines, write=True):
        lines = []
        lines.append("Foreach(0 until " + str(num_iters) + " par " +
                     str(par) + ") { " + str(idx) + " =>")
        lines.extend(self.loopBody(inner_lines))
        lines.append("}")

        if write is True:
            self.writeBlock(lines)
        else:
            return lines

    def reduce(self, type, num_iters, par, idx, out,
               inner_lines,
               reduce_lines,
               write=True):

        lines = []
        lines.append("val " + out + " = Reduce(Reg[" + type + "])(" +
                     str(num_iters) + " par " + str(par) + "){ " + idx + " =>")

        lines.extend(self.loopBody(inner_lines))
        lines.append("}{" + reduce_lines + "}")

        if write is True:
            self.writeBlock(lines)
        else:
            return lines

    def buildReLU(self, out, weights, bias_lut):
        line = out + " = " + "max(" + weights + " + " + bias_lut + ", 0)"
        return [line]

    def buildDNNLayer(self, dict):

        inner_line = dict["weight_lut"] + "(i,j) * " + dict["arg_mem"] + "(j)"

        red = self.reduce(dict["type"], dict["neuron_size"],
                          dict["inner_par"], "j", "w", [inner_line],
                          "_ + _", False)

        red.extend(self.buildReLU(dict["result_mem"] + "(i)", "w",
                                  dict["bias_lut"] + "(i)"))

        self.foreach(dict["num_neurons"], dict["outer_par"], "i", red)

    def chooseMultiClassResult(self, type, num_classes, par, arg_mem, out):

        self.reduce(type, num_classes, par, "i", "maxVal", [arg_mem + "(i)"],
                    "(a,b) => max(a,b)")

        self.reduce("I32", num_classes, par, "i", out,
                    ["mux(" + arg_mem + "(i) == maxVal.value, i, -1)"],
                    "(a,b) => max(a,b)")

    def endStream(self, out, idx):
        self.writeBlock(["stream_out := Tup2(" + out + ".value, " +
                        idx + " == (N-1))"])
        self.decIndentation()
        self.writeBlock(["}"])
        self.decIndentation()

    def closeBraces(self):
        self.writeBlock(["}", "assert(true)"])
        self.decIndentation()
        self.writeBlock(["}"])
        self.decIndentation()
        self.writeBlock(["}"])

def generateSpatial(model_data, base_dir, num_pkts):
    sp = Spatial()
    lut_dir = base_dir + "/luts"
    num_fields = model_data['input_dim']
    arch = model_data['arch']
    pars = model_data["pars"]

    sp.setupImports("spatial.dsl._", "spatial.lib.ML._",
                    "utils.io.files._",
                    "spatial.lang.{FileBus,FileEOFBus}",
                    "spatial.metadata.bounds._")

    sp.setupClass(model_data["name"])

    sp.setupConstants({"N": num_pkts,
                        "field": num_fields,
                        "project_dir": "s\"" + lut_dir + "\""})
    sp.setupTypes({"T": "Float"})
    sp.setupMain()

    for i in range(len(arch)):
        w_path = "s\"" + lut_dir + "/L" + str(i) + "_NEURON_W_LUT.csv\""
        b_path = "s\"" + lut_dir + "/L" + str(i) + "_NEURON_B_LUT.csv\""
        dim2 = num_fields if i == 0 else arch[i - 1]

        mems = {}
        mems["L" + str(i) + "_res"] = {
                                "mem_type": "SRAM",
                                "data_type": "T",
                                "dims": [arch[i]]}

        mems["L" + str(i) + "_W_LUT"] = {
                                "mem_type": "FileLUT",
                                "data_type": "T",
                                "dims": [arch[i], dim2],
                                "path": w_path}

        mems["L" + str(i) + "_B_LUT"] = {
                                "mem_type": "FileLUT",
                                "data_type": "T",
                                "dims": [arch[i]],
                                "path": b_path}

        sp.setupMemories(mems)

    sp.startStream("N", "p")
    sp.setupMemories({"packet": {
                            "mem_type": "SRAM",
                            "data_type": "T",
                            "dims": [num_fields]}})

    sp.foreach(num_fields, min(16, num_fields), "f",
                ["packet(f) = stream_in.value"])

    for i in range(len(arch)):

        neuron_size = num_fields if i == 0 else arch[i - 1]
        arg_mem = "packet" if i == 0 else ("L" + str(i - 1) + "_res")

        sp.buildDNNLayer({"type": "T",
                            "num_neurons": arch[i],
                            "neuron_size": neuron_size,
                            "arg_mem": arg_mem,
                            "result_mem": "L" + str(i) + "_res",
                            "outer_par": min(pars[i], arch[i]),
                            "inner_par": min(16, neuron_size),
                            "weight_lut": "L" + str(i) + "_W_LUT",
                            "bias_lut": "L" + str(i) + "_B_LUT"})

    last_elem = model_data["output_dim"]
    last_idx = len(arch)-1

    sp.chooseMultiClassResult("T", last_elem, min(16, last_elem),
                                "L" + str(last_idx) + "_res", "decision")

    sp.endStream("decision", "p")
    sp.closeBraces()

    sp.makeSpatialFile(base_dir, model_data["name"])