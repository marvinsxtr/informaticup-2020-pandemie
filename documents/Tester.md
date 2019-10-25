# Documentation Tester

## Goal

Test different approaches to eliminate the pandemia as fast as possible by running a simulation.

## Simulation

Each approach implements a method, which gets the json of the current round of a specified seed and returns the answer in json format using a helper method.

This method is then run for the complete games with the seeds 1 to 100.

## Scoring

After each completed simulation for a game, the score is calculated in the following way:

```Code
n := steps until the game ends
p := 1 if the game is won else -1

score(game) = p*n
```

The overall score is now calculated by taking the average of the game simulations with the seeds 1 to 100.
