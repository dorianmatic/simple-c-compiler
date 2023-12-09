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