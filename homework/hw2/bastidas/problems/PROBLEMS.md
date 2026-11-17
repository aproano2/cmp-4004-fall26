# Banco de problemas — Duelo 2 (CSP)

40 acertijos de casas en fila, 10 por nivel. Generados por
`code/generate_problems.py` (semillas fijas) y verificados por fuerza bruta
con `code/verify_problems.py`, que no usa el solver ni el parser de los brazos.

| Nivel | Casas | Grupos | Variables | Pistas (rango) |
|---|---|---|---|---|
| L1 | 4 | person | 4 | 2–4 |
| L2 | 4 | person, colour | 8 | 5–8 |
| L3 | 5 | person, colour | 10 | 6–8 |
| L4 | 5 | person, colour, pet | 15 | 9–14 |

## L1-01  (nivel 1, 4 variables, 3 pistas)

```
Four friends -- Ben, Gina, Carla and Mateo -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Gina's house is house 3.
2. Gina's house is somewhere to the left of Carla's house.
3. Mateo's house is not house 1.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Ben=1, Mateo=2, Gina=3, Carla=4

## L1-02  (nivel 1, 4 variables, 2 pistas)

```
Four friends -- Raul, Nora, Hugo and Elena -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Nora's house is house 3.
2. Raul's house is immediately to the left of Elena's house.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Raul=1, Elena=2, Nora=3, Hugo=4

## L1-03  (nivel 1, 4 variables, 4 pistas)

```
Four friends -- Paula, Sara, Lucia and Hugo -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Lucia's house is somewhere to the left of Sara's house.
2. Sara's house is not house 2.
3. Sara's house and Lucia's house are next to each other.
4. Lucia's house is somewhere to the left of Hugo's house.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Paula=1, Lucia=2, Sara=3, Hugo=4

## L1-04  (nivel 1, 4 variables, 3 pistas)

```
Four friends -- Nora, Dev, Sara and Raul -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Nora's house is somewhere to the left of Dev's house.
2. Raul's house is immediately to the left of Nora's house.
3. Sara's house is somewhere to the left of Raul's house.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Sara=1, Raul=2, Nora=3, Dev=4

## L1-05  (nivel 1, 4 variables, 3 pistas)

```
Four friends -- Paula, Mateo, Sara and Nora -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Sara's house and Nora's house are next to each other.
2. Nora's house is not house 4.
3. Mateo's house is immediately to the left of Sara's house.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Mateo=1, Sara=2, Nora=3, Paula=4

## L1-06  (nivel 1, 4 variables, 3 pistas)

```
Four friends -- Lucia, Ben, Hugo and Omar -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Lucia's house is immediately to the left of Hugo's house.
2. Omar's house is somewhere to the left of Hugo's house.
3. Omar's house is immediately to the left of Ben's house.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Omar=1, Ben=2, Lucia=3, Hugo=4

## L1-07  (nivel 1, 4 variables, 3 pistas)

```
Four friends -- Ben, Felix, Jon and Tomas -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Felix's house is house 1.
2. Tomas's house is somewhere to the left of Jon's house.
3. Jon's house is immediately to the left of Ben's house.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Felix=1, Tomas=2, Jon=3, Ben=4

## L1-08  (nivel 1, 4 variables, 3 pistas)

```
Four friends -- Raul, Omar, Kai and Carla -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Carla's house is somewhere to the left of Omar's house.
2. Carla's house is immediately to the left of Raul's house.
3. Omar's house is somewhere to the left of Kai's house.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Carla=1, Raul=2, Omar=3, Kai=4

## L1-09  (nivel 1, 4 variables, 4 pistas)

```
Four friends -- Felix, Ana, Paula and Carla -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Felix's house is somewhere to the left of Ana's house.
2. Carla's house is not house 3.
3. Ana's house and Carla's house are next to each other.
4. Felix's house and Ana's house are next to each other.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Paula=1, Felix=2, Ana=3, Carla=4

## L1-10  (nivel 1, 4 variables, 3 pistas)

```
Four friends -- Vera, Hugo, Sara and Carla -- live in 4 houses in a row, numbered 1 to 4 from left to right. Each friend lives in a different house.
Clues:
1. Hugo's house and Sara's house are next to each other.
2. Vera's house is somewhere to the left of Carla's house.
3. Hugo's house is immediately to the left of Carla's house.
Give the house number of every friend.
```

**Respuesta correcta (única):**

- person: Vera=1, Sara=2, Hugo=3, Carla=4

## L2-01  (nivel 2, 8 variables, 5 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Tomas, Ana, Lucia, Ben.
Colours: blue, black, white, orange.
Clues:
1. The orange house is somewhere to the left of Tomas's house.
2. Ana lives in the blue house.
3. Tomas's house is immediately to the left of Lucia's house.
4. Lucia does not live in the white house.
5. Ana's house and Lucia's house are next to each other.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Ben=1, Tomas=2, Lucia=3, Ana=4
- colour: orange=1, white=2, black=3, blue=4

## L2-02  (nivel 2, 8 variables, 5 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Ana, Raul, Kai, Dev.
Colours: white, green, purple, red.
Clues:
1. Kai's house is immediately to the left of the white house.
2. The white house is house 3.
3. Dev's house is somewhere to the left of the green house.
4. The green house and the red house are next to each other.
5. Ana's house and the white house are next to each other.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Dev=1, Kai=2, Raul=3, Ana=4
- colour: red=1, green=2, white=3, purple=4

## L2-03  (nivel 2, 8 variables, 6 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Dev, Sara, Hugo, Jon.
Colours: white, black, yellow, red.
Clues:
1. Sara's house and Hugo's house are next to each other.
2. The white house is not house 3.
3. The yellow house is somewhere to the left of Hugo's house.
4. Sara lives in the black house.
5. Dev lives in the red house.
6. Jon's house is not house 1.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Dev=1, Jon=2, Sara=3, Hugo=4
- colour: red=1, yellow=2, black=3, white=4

## L2-04  (nivel 2, 8 variables, 6 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Raul, Ana, Gina, Lucia.
Colours: blue, black, white, orange.
Clues:
1. The white house is immediately to the left of Gina's house.
2. Raul's house and Gina's house are next to each other.
3. Raul's house is somewhere to the left of the blue house.
4. The black house is somewhere to the left of the orange house.
5. Lucia lives in the orange house.
6. Raul's house and the orange house are next to each other.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Ana=1, Lucia=2, Raul=3, Gina=4
- colour: black=1, orange=2, white=3, blue=4

## L2-05  (nivel 2, 8 variables, 8 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Omar, Ana, Carla, Paula.
Colours: yellow, purple, black, orange.
Clues:
1. Paula's house is not house 2.
2. Ana does not live in the purple house.
3. Omar's house is house 3.
4. The purple house is somewhere to the left of the yellow house.
5. The yellow house is not house 2.
6. Omar's house is somewhere to the left of Carla's house.
7. The orange house is not house 4.
8. Ana's house is somewhere to the left of the orange house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Paula=1, Ana=2, Omar=3, Carla=4
- colour: purple=1, black=2, orange=3, yellow=4

## L2-06  (nivel 2, 8 variables, 5 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Sara, Mateo, Carla, Ben.
Colours: black, purple, white, red.
Clues:
1. Carla's house is immediately to the left of Ben's house.
2. The purple house and the red house are next to each other.
3. The black house is immediately to the left of the red house.
4. Sara's house and Ben's house are next to each other.
5. Sara's house and the black house are next to each other.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Carla=1, Ben=2, Sara=3, Mateo=4
- colour: white=1, black=2, red=3, purple=4

## L2-07  (nivel 2, 8 variables, 5 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Gina, Carla, Nora, Lucia.
Colours: green, white, black, blue.
Clues:
1. Carla's house is immediately to the left of the white house.
2. Carla's house is not house 1.
3. Nora's house and the white house are next to each other.
4. Carla's house is somewhere to the left of Gina's house.
5. The green house is immediately to the left of the black house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Lucia=1, Carla=2, Gina=3, Nora=4
- colour: green=1, black=2, white=3, blue=4

## L2-08  (nivel 2, 8 variables, 6 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Elena, Sara, Mateo, Dev.
Colours: red, orange, black, yellow.
Clues:
1. Sara's house is somewhere to the left of Mateo's house.
2. Elena's house is immediately to the left of the red house.
3. The black house is immediately to the left of the yellow house.
4. Elena's house and Dev's house are next to each other.
5. Dev's house is house 4.
6. Elena lives in the yellow house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Sara=1, Mateo=2, Elena=3, Dev=4
- colour: orange=1, black=2, yellow=3, red=4

## L2-09  (nivel 2, 8 variables, 5 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Iris, Felix, Nora, Ben.
Colours: black, blue, green, white.
Clues:
1. Ben's house and the white house are next to each other.
2. Iris's house is immediately to the left of Felix's house.
3. Felix's house is somewhere to the left of Nora's house.
4. The white house is immediately to the left of the green house.
5. Ben lives in the blue house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Ben=1, Iris=2, Felix=3, Nora=4
- colour: blue=1, white=2, green=3, black=4

## L2-10  (nivel 2, 8 variables, 6 pistas)

```
Four houses stand in a row, numbered 1 to 4 from left to right. Each house has a different owner and a different colour.
Owners: Elena, Paula, Omar, Hugo.
Colours: purple, yellow, green, blue.
Clues:
1. The purple house and the yellow house are next to each other.
2. Elena's house and Omar's house are next to each other.
3. The green house is not house 1.
4. The purple house is somewhere to the left of Hugo's house.
5. Elena lives in the green house.
6. Hugo's house is immediately to the left of the blue house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Paula=1, Hugo=2, Omar=3, Elena=4
- colour: purple=1, yellow=2, blue=3, green=4

## L3-01  (nivel 3, 10 variables, 6 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Jon, Omar, Elena, Lucia, Hugo.
Colours: white, green, black, orange, yellow.
Clues:
1. Elena lives in the white house.
2. Omar's house and Hugo's house are next to each other.
3. The green house is immediately to the left of the white house.
4. Omar lives in the yellow house.
5. The orange house is somewhere to the left of the yellow house.
6. Hugo's house is immediately to the left of Lucia's house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Jon=1, Omar=2, Hugo=3, Lucia=4, Elena=5
- colour: orange=1, yellow=2, black=3, green=4, white=5

## L3-02  (nivel 3, 10 variables, 6 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Gina, Mateo, Ana, Ben, Tomas.
Colours: purple, black, red, orange, blue.
Clues:
1. Mateo's house and the orange house are next to each other.
2. The red house is somewhere to the left of Ana's house.
3. Gina's house is immediately to the left of Ana's house.
4. The black house is immediately to the left of the red house.
5. The blue house is immediately to the left of the purple house.
6. The black house is immediately to the left of Tomas's house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Ben=1, Mateo=2, Tomas=3, Gina=4, Ana=5
- colour: orange=1, black=2, red=3, blue=4, purple=5

## L3-03  (nivel 3, 10 variables, 7 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Sara, Omar, Hugo, Iris, Ben.
Colours: red, green, orange, purple, white.
Clues:
1. Hugo's house is immediately to the left of Ben's house.
2. The purple house is somewhere to the left of Ben's house.
3. The white house is somewhere to the left of Omar's house.
4. Omar's house is somewhere to the left of Iris's house.
5. The green house is immediately to the left of Sara's house.
6. Ben's house and the green house are next to each other.
7. The orange house is not house 5.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Hugo=1, Ben=2, Omar=3, Sara=4, Iris=5
- colour: purple=1, white=2, green=3, orange=4, red=5

## L3-04  (nivel 3, 10 variables, 7 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Paula, Vera, Gina, Carla, Ana.
Colours: blue, red, white, green, orange.
Clues:
1. Ana's house is somewhere to the left of Paula's house.
2. Carla lives in the blue house.
3. Gina's house and Carla's house are next to each other.
4. Paula's house and Carla's house are next to each other.
5. The orange house is not house 2.
6. The green house is somewhere to the left of Ana's house.
7. Paula's house is somewhere to the left of the white house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Vera=1, Ana=2, Paula=3, Carla=4, Gina=5
- colour: green=1, red=2, orange=3, blue=4, white=5

## L3-05  (nivel 3, 10 variables, 8 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Ben, Mateo, Kai, Paula, Gina.
Colours: blue, purple, black, red, green.
Clues:
1. Paula's house is somewhere to the left of Kai's house.
2. The black house and the green house are next to each other.
3. Mateo's house is immediately to the left of the black house.
4. Ben's house and the blue house are next to each other.
5. Paula's house is not house 2.
6. The red house is somewhere to the left of the black house.
7. Kai's house is somewhere to the left of Ben's house.
8. Gina's house is house 4.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Paula=1, Mateo=2, Kai=3, Gina=4, Ben=5
- colour: red=1, green=2, black=3, blue=4, purple=5

## L3-06  (nivel 3, 10 variables, 8 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Raul, Dev, Jon, Vera, Kai.
Colours: yellow, orange, black, white, green.
Clues:
1. The orange house is somewhere to the left of the white house.
2. Jon lives in the orange house.
3. Dev's house and the yellow house are next to each other.
4. The white house is somewhere to the left of the yellow house.
5. Jon's house is not house 1.
6. The yellow house is somewhere to the left of the green house.
7. The yellow house is somewhere to the left of Raul's house.
8. Kai lives in the yellow house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Vera=1, Jon=2, Dev=3, Kai=4, Raul=5
- colour: black=1, orange=2, white=3, yellow=4, green=5

## L3-07  (nivel 3, 10 variables, 7 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Lucia, Mateo, Raul, Paula, Nora.
Colours: yellow, orange, red, green, purple.
Clues:
1. Nora's house and the red house are next to each other.
2. The red house is house 5.
3. The yellow house is somewhere to the left of Nora's house.
4. Nora's house is immediately to the left of Lucia's house.
5. The green house is somewhere to the left of Paula's house.
6. The green house is immediately to the left of Mateo's house.
7. Mateo's house is immediately to the left of the orange house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Raul=1, Mateo=2, Paula=3, Nora=4, Lucia=5
- colour: green=1, yellow=2, orange=3, purple=4, red=5

## L3-08  (nivel 3, 10 variables, 7 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Iris, Paula, Ana, Felix, Nora.
Colours: blue, red, white, green, orange.
Clues:
1. Paula's house and Felix's house are next to each other.
2. Ana's house and the green house are next to each other.
3. The white house is immediately to the left of the blue house.
4. The red house is somewhere to the left of Ana's house.
5. Iris's house is immediately to the left of Felix's house.
6. The blue house is not house 2.
7. Iris lives in the white house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Nora=1, Iris=2, Felix=3, Paula=4, Ana=5
- colour: red=1, white=2, blue=3, green=4, orange=5

## L3-09  (nivel 3, 10 variables, 6 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Omar, Tomas, Kai, Dev, Mateo.
Colours: white, orange, yellow, red, green.
Clues:
1. The red house is somewhere to the left of Dev's house.
2. Tomas lives in the green house.
3. The green house is somewhere to the left of the orange house.
4. Omar lives in the orange house.
5. The yellow house is immediately to the left of Mateo's house.
6. Dev's house is immediately to the left of Tomas's house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Kai=1, Mateo=2, Dev=3, Tomas=4, Omar=5
- colour: yellow=1, red=2, white=3, green=4, orange=5

## L3-10  (nivel 3, 10 variables, 8 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner and a different colour.
Owners: Sara, Lucia, Tomas, Raul, Ben.
Colours: green, yellow, orange, black, white.
Clues:
1. The black house is somewhere to the left of Sara's house.
2. Raul's house is immediately to the left of the yellow house.
3. The yellow house is not house 2.
4. Raul lives in the orange house.
5. Lucia's house is immediately to the left of Ben's house.
6. Tomas's house is somewhere to the left of the green house.
7. The orange house is somewhere to the left of Lucia's house.
8. Lucia's house is immediately to the left of the black house.
Give the house number of every owner and every colour.
```

**Respuesta correcta (única):**

- person: Tomas=1, Raul=2, Lucia=3, Ben=4, Sara=5
- colour: white=1, orange=2, yellow=3, black=4, green=5

## L4-01  (nivel 4, 15 variables, 9 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Nora, Elena, Vera, Gina, Paula.
Colours: purple, black, orange, yellow, blue.
Pets: horse, rabbit, bird, hamster, fish.
Clues:
1. Vera's house is somewhere to the left of the house with the hamster.
2. The horse lives in the blue house.
3. The house with the bird is immediately to the left of Elena's house.
4. Vera's house is immediately to the left of the blue house.
5. The house with the rabbit is somewhere to the left of the purple house.
6. Nora lives in the orange house.
7. The house with the rabbit is immediately to the left of Paula's house.
8. Gina's house is immediately to the left of the black house.
9. Gina's house is immediately to the left of Paula's house.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Gina=1, Paula=2, Vera=3, Elena=4, Nora=5
- colour: yellow=1, black=2, purple=3, blue=4, orange=5
- pet: rabbit=1, fish=2, bird=3, horse=4, hamster=5

## L4-02  (nivel 4, 15 variables, 11 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Nora, Omar, Carla, Ana, Hugo.
Colours: red, purple, black, green, yellow.
Pets: cat, rabbit, fish, dog, horse.
Clues:
1. The black house is immediately to the left of Carla's house.
2. Carla lives in the red house.
3. Carla owns the cat.
4. The purple house and the house with the cat are next to each other.
5. Omar's house is somewhere to the left of the house with the cat.
6. Hugo's house is not house 2.
7. The green house is somewhere to the left of the yellow house.
8. The house with the rabbit is somewhere to the left of the house with the dog.
9. Ana's house is somewhere to the left of the house with the fish.
10. The red house and the house with the rabbit are next to each other.
11. Hugo's house is somewhere to the left of Omar's house.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Hugo=1, Omar=2, Carla=3, Ana=4, Nora=5
- colour: green=1, black=2, red=3, purple=4, yellow=5
- pet: horse=1, rabbit=2, cat=3, dog=4, fish=5

## L4-03  (nivel 4, 15 variables, 9 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Hugo, Vera, Elena, Ben, Dev.
Colours: white, yellow, red, blue, green.
Pets: dog, turtle, fish, cat, bird.
Clues:
1. Vera's house and the red house are next to each other.
2. Ben lives in the yellow house.
3. Hugo's house is somewhere to the left of Dev's house.
4. The turtle lives in the blue house.
5. The house with the turtle is somewhere to the left of the house with the dog.
6. The white house is somewhere to the left of the house with the turtle.
7. The fish lives in the white house.
8. Dev owns the fish.
9. Elena's house is somewhere to the left of the house with the bird.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Hugo=1, Dev=2, Vera=3, Elena=4, Ben=5
- colour: green=1, white=2, blue=3, red=4, yellow=5
- pet: cat=1, fish=2, turtle=3, dog=4, bird=5

## L4-04  (nivel 4, 15 variables, 11 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Paula, Lucia, Vera, Raul, Ben.
Colours: orange, red, yellow, purple, black.
Pets: bird, dog, hamster, turtle, fish.
Clues:
1. The yellow house is somewhere to the left of the house with the hamster.
2. The fish lives in the red house.
3. The red house is immediately to the left of the house with the turtle.
4. Lucia's house is immediately to the left of Vera's house.
5. Lucia's house and the house with the turtle are next to each other.
6. Lucia's house is immediately to the left of the yellow house.
7. The dog does not live in the purple house.
8. Ben's house is immediately to the left of Lucia's house.
9. Raul does not live in the black house.
10. The house with the fish is somewhere to the left of the black house.
11. The purple house is somewhere to the left of Ben's house.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Raul=1, Ben=2, Lucia=3, Vera=4, Paula=5
- colour: purple=1, orange=2, red=3, yellow=4, black=5
- pet: bird=1, dog=2, fish=3, turtle=4, hamster=5

## L4-05  (nivel 4, 15 variables, 11 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Hugo, Tomas, Dev, Elena, Jon.
Colours: red, white, orange, purple, blue.
Pets: horse, turtle, dog, fish, cat.
Clues:
1. The purple house is immediately to the left of the house with the horse.
2. Elena's house is immediately to the left of the white house.
3. Tomas lives in the blue house.
4. Elena does not own the turtle.
5. The red house is immediately to the left of Dev's house.
6. The orange house is somewhere to the left of the blue house.
7. The purple house is somewhere to the left of Hugo's house.
8. The house with the horse and the house with the fish are next to each other.
9. The white house is somewhere to the left of the house with the dog.
10. The fish does not live in the purple house.
11. The red house is somewhere to the left of Jon's house.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Elena=1, Dev=2, Jon=3, Hugo=4, Tomas=5
- colour: red=1, white=2, purple=3, orange=4, blue=5
- pet: cat=1, turtle=2, dog=3, horse=4, fish=5

## L4-06  (nivel 4, 15 variables, 12 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Raul, Hugo, Kai, Elena, Carla.
Colours: red, orange, yellow, blue, green.
Pets: hamster, horse, bird, rabbit, turtle.
Clues:
1. Hugo's house and the green house are next to each other.
2. The house with the hamster is immediately to the left of the house with the rabbit.
3. Raul does not own the turtle.
4. The green house is somewhere to the left of Kai's house.
5. The house with the bird is somewhere to the left of Carla's house.
6. Raul's house is immediately to the left of Elena's house.
7. Kai's house and the yellow house are next to each other.
8. The green house and the house with the rabbit are next to each other.
9. Carla does not live in the orange house.
10. The red house is somewhere to the left of the house with the bird.
11. Hugo's house is somewhere to the left of the house with the horse.
12. The horse does not live in the yellow house.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Hugo=1, Raul=2, Elena=3, Kai=4, Carla=5
- colour: red=1, green=2, yellow=3, orange=4, blue=5
- pet: turtle=1, hamster=2, rabbit=3, bird=4, horse=5

## L4-07  (nivel 4, 15 variables, 10 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Felix, Iris, Elena, Vera, Mateo.
Colours: red, orange, yellow, white, blue.
Pets: fish, turtle, bird, horse, cat.
Clues:
1. The house with the turtle is immediately to the left of the orange house.
2. Felix's house is immediately to the left of Mateo's house.
3. Vera does not live in the red house.
4. Felix's house and Iris's house are next to each other.
5. The house with the bird is somewhere to the left of Elena's house.
6. The red house and the blue house are next to each other.
7. Iris's house and the house with the bird are next to each other.
8. The house with the cat is somewhere to the left of the house with the turtle.
9. The blue house is immediately to the left of the yellow house.
10. The house with the horse is somewhere to the left of Iris's house.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Vera=1, Iris=2, Felix=3, Mateo=4, Elena=5
- colour: white=1, red=2, blue=3, yellow=4, orange=5
- pet: horse=1, cat=2, bird=3, turtle=4, fish=5

## L4-08  (nivel 4, 15 variables, 11 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Raul, Dev, Iris, Kai, Tomas.
Colours: red, black, yellow, orange, white.
Pets: turtle, dog, cat, rabbit, hamster.
Clues:
1. The orange house is somewhere to the left of the house with the dog.
2. The house with the hamster is immediately to the left of the house with the dog.
3. Iris's house is somewhere to the left of the house with the cat.
4. The dog lives in the yellow house.
5. Iris's house is not house 4.
6. The house with the turtle is immediately to the left of Kai's house.
7. Raul's house is somewhere to the left of Iris's house.
8. Iris's house and Tomas's house are next to each other.
9. The white house is somewhere to the left of the black house.
10. Dev owns the hamster.
11. Raul lives in the red house.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Raul=1, Dev=2, Iris=3, Tomas=4, Kai=5
- colour: red=1, orange=2, yellow=3, white=4, black=5
- pet: rabbit=1, hamster=2, dog=3, turtle=4, cat=5

## L4-09  (nivel 4, 15 variables, 14 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Omar, Ana, Tomas, Jon, Carla.
Colours: orange, green, blue, purple, red.
Pets: fish, hamster, dog, horse, turtle.
Clues:
1. Jon does not own the turtle.
2. The red house and the house with the dog are next to each other.
3. Tomas does not live in the purple house.
4. Omar's house and Ana's house are next to each other.
5. Omar's house and the blue house are next to each other.
6. The green house is immediately to the left of the house with the fish.
7. Jon's house is somewhere to the left of Ana's house.
8. Ana's house is somewhere to the left of the house with the fish.
9. Omar's house and the house with the dog are next to each other.
10. The purple house is somewhere to the left of the house with the hamster.
11. Ana's house is somewhere to the left of Omar's house.
12. The blue house and the house with the hamster are next to each other.
13. The house with the dog is somewhere to the left of Carla's house.
14. The house with the hamster is immediately to the left of the orange house.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Jon=1, Tomas=2, Ana=3, Omar=4, Carla=5
- colour: purple=1, red=2, blue=3, green=4, orange=5
- pet: horse=1, turtle=2, dog=3, hamster=4, fish=5

## L4-10  (nivel 4, 15 variables, 11 pistas)

```
Five houses stand in a row, numbered 1 to 5 from left to right. Each house has a different owner, a different colour and a different pet.
Owners: Elena, Iris, Raul, Jon, Ana.
Colours: orange, purple, yellow, blue, black.
Pets: bird, turtle, rabbit, fish, horse.
Clues:
1. Elena's house is somewhere to the left of the house with the turtle.
2. The house with the fish is immediately to the left of Elena's house.
3. The black house and the house with the turtle are next to each other.
4. The house with the horse is somewhere to the left of the yellow house.
5. The rabbit lives in the purple house.
6. Iris's house is somewhere to the left of Elena's house.
7. Raul's house is not house 3.
8. The house with the turtle is somewhere to the left of the yellow house.
9. Raul's house and the purple house are next to each other.
10. The orange house is immediately to the left of the purple house.
11. The orange house is somewhere to the left of Ana's house.
Give the house number of every owner, every colour and every pet.
```

**Respuesta correcta (única):**

- person: Iris=1, Elena=2, Jon=3, Ana=4, Raul=5
- colour: blue=1, black=2, orange=3, purple=4, yellow=5
- pet: fish=1, horse=2, turtle=3, rabbit=4, bird=5
