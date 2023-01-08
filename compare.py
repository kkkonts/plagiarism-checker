import ast
import argparse
from typing import List, Tuple

class LevenshteinDistance:
    def __init__(self, s1: str, s2: str):
        self.s1 = s1
        self.s2 = s2

    def distance(self) -> int:
        len1, len2 = len(self.s1), len(self.s2)
        if len1 == 0 or len2 == 0:
            return max(len1, len2)
        else:
            prev = [i for i in range(len1 + 1)]  # previous row in matrix
            for i in range(1, len2 + 1):
                d = [0] * (len1 + 1)  # current row in matrix
                d[0] = i
                for j in range(1, len1 + 1):
                    if self.s1[j - 1] == self.s2[i - 1]:
                        d[j] = prev[j - 1]
                    else:
                        d[j] = 1 + min(d[j - 1], prev[j - 1], prev[j])
                prev = d
            return prev[-1]

    def accuracy(self) -> float:
        return (len(self.s1) - self.distance()) / len(self.s1)

class Normalizer:
     def normalise(s) -> str:
        tree = ast.parse(s)
        for node in ast.walk(tree):
            if type(node).__name__ == 'Expr':
                node.value = ast.Constant(value='docstring') 
            if type(node).__name__ == 'FunctionDef':
                node.returns = None 
            if type(node).__name__ == 'arg':
                node.annotation = [] 
        s = ast.unparse(tree)
        return s

class ParseFiles:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input', type=str)
        parser.add_argument('output', type=str)
        args = parser.parse_args()
        self.input = args.input
        self.output = args.output
    
    def get_paths(self) -> Tuple[str, str]:
        return tuple([self.input, self.output])

    def read_lines(path: str) -> List[str]:
        with open(path, 'r') as f:
            return f.readlines()

    def read_file(path: str) -> str:
        with open(path, 'r') as f:
            return f.read()

    def write_to_file(path, s: str) -> None:
        with open(path, 'w') as f:
            f.writelines(s)
        

class Application:
    def __init__(self):
        pass

    def run(self): 
        inp_f, out_f = ParseFiles().get_paths()
        plagiarism = ""

        for line in ParseFiles.read_lines(inp_f):
            path1, path2 = line.split()
            f1, f2 = ParseFiles.read_file(path1), ParseFiles.read_file(path2)
            f1, f2 = Normalizer.normalise(f1), Normalizer.normalise(f2)
            plagiarism += str(LevenshteinDistance(f1, f2).accuracy()) + "\n"

        ParseFiles.write_to_file(out_f, plagiarism)


def main() -> None:
    Application().run()
    

if __name__ == '__main__':
    main()