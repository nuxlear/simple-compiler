# Simple Compiler

Simple compiler program with given grammar.

Use **LL(1) Parser** for parsing, and use **Sethi-Ullman algorithm** for register allocation. 

## Dependencies
- Python == 3.7

## Usage

```shell
python main.py [INPUT_FILE]
```

## Result Example
### Input file
- Compile  `input_code.txt`
```text
func () {
    int a;
    int b;
    int c;
    int dd;
    a = 3;
    b = 2;
    IF a < b THEN { c = 1; } ELSE { c = 2; }
    dd = a+c;
}
```

### Command
- Run program as below
```shell
$ python main.py input_code.txt

The number of register used: 2
```

### Result files
- `input_code.symbol`
```text
Scope: 0
	Symbol: func (type: FUNCTION)
Scope: 1
	Symbol: a (type: INT) [addr: 1000]
	Symbol: b (type: INT) [addr: 1004]
	Symbol: c (type: INT) [addr: 1008]
	Symbol: dd (type: INT) [addr: 1012]
```

- `input_code.code`
```text
BEGIN	func
LD	R0, 3
ST	R0, (1000)
LD	R0, 2
ST	R0, (1004)
LD	R0, (1000)
LD	R1, (1004)
LT	R0, R0, R1
JUMPF	R0, ELSE0
LD	R0, 1
ST	R0, (1008)
JUMP	END0
ELSE0:
LD	R0, 2
ST	R0, (1008)
END0:
LD	R0, (1000)
LD	R1, (1008)
ADD	R0, R0, R1
ST	R0, (1012)
EXIT:
END	func
```

## Contributor
- [Junwon Hwang](https://github.com/nuxlear)
- [Yujung Shin](https://github.com/input0)
- [Jaeyeon Kim](https://github.com/JLake310)