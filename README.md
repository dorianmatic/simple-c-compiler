# ppj-labos
Repository for PPJ laboratory exercises

---
## Lab 1: Lexical analysis

Lexical analyzer generator outputs ```lab1/analizator/LA_data.pkl``` 
Lexical analyzer outputs the lexical units in the provided source code to the standard output.

Running:
1. Run generator with ```python lab1/GLA.py``` and provide language definition.
2. Run analyzer with ```python lab1/analizator/LA.py``` and provide source code.

Running on official test set:
1. Download official test set.
2. Copy ```lab1_teza``` folder into ```lab1/examples```
3. Run tests with ```python lab1/test/integration_tests/lab1_test.py```

---
## Lab 2: Syntax analysis

Syntax analyzer generator outputs ```lab2/analizator/SA_data.pkl```
Syntax analyzer outputs the syntax tree to the standard output.

Running:
1. Run generator with ```python lab2/SLA.py``` and provide syntax definition.
2. Run analyzer with ```python lab2/analizator/SA.py``` and provide source code.

Running on official test set:
1. Download official test set.
2. Copy ```lab2_teza``` folder into ```lab2/examples```
3. Run tests with ```python lab2/test/integration_tests/lab2_test.py```

---
## Lab 3: Semantic analysis

Semantic analyzer receives the generative tree from the syntax analyzer as input. The analyzer then checks the language 
semantic rules and outputs the first semantic error it detects, if no semantic errors are present, the analyzer has no 
output.

**NOTE:** This analyzer verifies the rules for a language that is a subset of the C programming language.

Running:
1. Run generator with ```python lab3/SemantickiAnalizator.py``` and provide generative tree from previous compilation 
step.

Running on official test set:
1. Download official test set
2. Copy ```lab3_teza``` folder into ```lab3/examples```
3. Run tests with ```python lab3/test/integration_tests/lab3_test.py```