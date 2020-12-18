# OS_Process_and_Resource_Management
电子科技大学 2020秋 计算机操作系统

实验一：进程与资源管理器

Fall 2020 Operating System Lab project 1

2018040708002 黎骞



## 运行指引

将指令放在` 0.txt `中，运行` main.py `即可。

## 更多测试用例

source: [os-test-shell](https://github.com/502408764/os-test-shell)

### 0

#### 输入

```
cr x 1
cr p 1
cr q 1
cr r 1
to
req R2 1
to
req R3 3
to
req R4 3
to
to
req R3 1
req R4 2
req R2 2
to
de q
to
to
```

#### 输出

```
init x x x x p p q q r r x p q r x x x p x 
```

### 1

#### 输入

```
cr A 1
cr B 1
cr C 1
to
cr D 1
cr E 1
to
cr F 1
req R1 1
req R2 2
to
req R2 1
req R3 3
to
req R4 4
to
req R3 2
to
rel R2 1
to
rel R3 2
to
to
req R3 3
de B
to
to
to
```

#### 输出

```
init A A A B B B C C C C A D D E E B F C C D D E F A A C F A 
```

### 2

#### 输入

```
cr A 1
cr B 1
cr C 1
req R1 1
to
cr D 1
req R2 2
cr E 2
req R2 1
to
to
to
rel R2 1
de B
to
to
```

#### 输出

```
init A A A A B B B E C A D B E C A C 
```

### 3

#### 输入

```
cr A 1
cr B 1
cr C 1
to
cr D 1
cr E 1
cr F 1
to
to
to
req R1 1
req R2 1
to
req R2 1
to
req R3 3
req R4 3
req R4 3
to
req R1 1
cr G 2
req R1 1
de B
req R3 2
cr H 2
cr I 2
to
req R3 3
req R3 2
to
rel R3 1
to
```

#### 输出

```
init A A A B B B B C A D D D E E F F F B C A G D A A H H I H C A A C
```

### 4

#### 输入

```
cr x 1
cr p 1
cr q 1
cr r 1
to
to
to
req R1 1
to
req R2 1
to
req R3 2
to
to
rel R1 1
to
req R3 3
de p
to
```

#### 输出

```
init x x x x p q r r x x p p q r r x p q r
```

### 5

#### 输入

```
cr a 1
cr b 1
cr c 1
cr d 1
to
cr f 1
req R1 1
to
to
to
cr e 2
req R1 1
to
de b
req R1 1
to
to
to
to
to
```

#### 输出

```
init a a a a b b b c d a e f b e c d a c d a
```

### 6

#### 输入

```
cr a 1
cr b 1
to
cr c 1
cr d 1
to
req R1 1
to
to
req R2 2
to
de b
req R3 1
to
```

输出

```
init a a b b b a a c d d b a a a
```

### 7

#### 输入

```
cr z 1
cr x 1
cr c 1
to
req R3 3
cr v 1
to
to
req R3 1
to
req R1 1
to
req R1 1
de x
to
```

#### 输出

```
init z z z x x x c z v x x c v z c
```

### 8

#### 输入

```
cr a 1
cr s 1
to
cr d 1
req R2 2
cr f 1
to
to
req R2 1
to
de s
to
req R2 1
```

#### 输出

```
init a a s s s s a d f s a a a
```

### 9

#### 输入

```
cr x 1
cr y 1
req R2 2
to
cr z 1
cr m 1
req R1 1
to
req R2 2
de x
to
```

#### 输出

```
init x x x y y y y x z init init
```
