# Symble
A simple interpreted programming language made in python that uses symbols for nearly all of it's keywords.

**EXPLANATION** in `docs.txt`

## Examples

Hello world program:
```
  <_ "hello world\n"
```
or
```
  << "hello world"
```
The first one is actually printing the string "hello world" the other is simply returning the string "hello world" which will print `out: hello world `

Printing the numbers from 1 - 100:
```
  @ i 0;
  % 100 { ++ i; <_ i; <_ "\n" }
```

Printing the alphabet:
```
  @@ abc "abcdefghijklmopqrstuvwxyz";
  @ i 0;
  % (# abc) {
      <_ +_ abc:i "\n";
      ++ i
  }
```
