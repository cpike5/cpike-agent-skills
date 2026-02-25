# Adjacency Templates

Ready-to-use adjacency matrices for common scenarios. Copy-paste these directly into API requests.

## 3-Color Website

**Roles**: Background, Text, Accent

```
     BG   Text  Accent
BG  [ 0    65    45 ]
T   [ 65    0    35 ]
A   [ 45   35     0 ]
```

```json
{
  "num_colors": 3,
  "adjacency": ["0","65","45","65","0","35","45","35","0"],
  "palette": ["-","-","-"]
}
```

## 4-Color Website

**Roles**: Background, Surface, Text, Accent

```
      BG   Surf  Text  Accent
BG  [  0    20    65    50 ]
S   [ 20     0    55    40 ]
T   [ 65    55     0    35 ]
A   [ 50    40    35     0 ]
```

```json
{
  "num_colors": 4,
  "adjacency": ["0","20","65","50","20","0","55","40","65","55","0","35","50","40","35","0"],
  "palette": ["-","-","-","-"]
}
```

## 5-Color SaaS Dashboard

**Roles**: Background, Surface, Text, Primary Action, Secondary Action

```
      BG   Surf  Text  Pri   Sec
BG  [  0    15    60    55    45 ]
S   [ 15     0    50    45    35 ]
T   [ 60    50     0    40    35 ]
P   [ 55    45    40     0    30 ]
S   [ 45    35    35    30     0 ]
```

```json
{
  "num_colors": 5,
  "adjacency": ["0","15","60","55","45","15","0","50","45","35","60","50","0","40","35","55","45","40","0","30","45","35","35","30","0"],
  "palette": ["-","-","-","-","-"]
}
```

## 5-Color Brand

**Roles**: Primary, Secondary, Accent, Light, Dark

```
      Pri   Sec   Acc   Light  Dark
P   [  0    35    45    60     70 ]
S   [ 35     0    30    50     60 ]
A   [ 45    30     0    55     50 ]
L   [ 60    50    55     0     80 ]
D   [ 70    60    50    80      0 ]
```

```json
{
  "num_colors": 5,
  "adjacency": ["0","35","45","60","70","35","0","30","50","60","45","30","0","55","50","60","50","55","0","80","70","60","50","80","0"],
  "palette": ["-","-","-","-","-"]
}
```

## 6-Color Landing Page

**Roles**: Background, Surface, Heading Text, Body Text, Primary CTA, Secondary CTA

> Use `transformer` mode only — diffusion max is 5 colors.

```
       BG   Surf  H-Txt B-Txt  P-CTA S-CTA
BG  [   0    18    65    55     55     40  ]
S   [  18     0    55    45     45     30  ]
HT  [  65    55     0    15     40     35  ]
BT  [  55    45    15     0     35     30  ]
PC  [  55    45    40    35      0     25  ]
SC  [  40    30    35    30     25      0  ]
```

```json
{
  "num_colors": 6,
  "adjacency": ["0","18","65","55","55","40","18","0","55","45","45","30","65","55","0","15","40","35","55","45","15","0","35","30","55","45","40","35","0","25","40","30","35","30","25","0"],
  "palette": ["-","-","-","-","-","-"]
}
```

## 4-Color Dark Mode

**Roles**: Dark Background, Dark Surface, Light Text, Accent

```
      D-BG  D-Surf L-Txt  Accent
DB  [  0     12     60     50  ]
DS  [ 12      0     50     40  ]
LT  [ 60     50      0     35  ]
A   [ 50     40     35      0  ]
```

Note lower BG ↔ Surface adjacency (12) for subtle dark-on-dark layering.

```json
{
  "num_colors": 4,
  "adjacency": ["0","12","60","50","12","0","50","40","60","50","0","35","50","40","35","0"],
  "palette": ["-","-","-","-"]
}
```

## 4-Color Card UI

**Roles**: Card Background, Border/Divider, Content Text, Action Color

```
      Card   Border  Text   Action
C   [  0      15     55     45  ]
B   [ 15       0     45     35  ]
T   [ 55      45      0     30  ]
A   [ 45      35     30      0  ]
```

Low Card ↔ Border adjacency (15) for subtle borders. Moderate Text ↔ Action (30) so actions stand out from body text.

```json
{
  "num_colors": 4,
  "adjacency": ["0","15","55","45","15","0","45","35","55","45","0","30","45","35","30","0"],
  "palette": ["-","-","-","-"]
}
```

## Choosing a Template

| Scenario | Template | Colors |
|----------|----------|--------|
| Simple website or blog | 3-Color Website | 3 |
| Standard web app | 4-Color Website | 4 |
| Dashboard / admin panel | 5-Color SaaS Dashboard | 5 |
| Brand identity system | 5-Color Brand | 5 |
| Marketing / landing page | 6-Color Landing Page | 6 |
| Dark mode UI | 4-Color Dark Mode | 4 |
| Card-based layout | 4-Color Card UI | 4 |
