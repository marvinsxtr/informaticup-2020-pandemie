# Documentation Tester

## Goal

Test different approaches to eliminate the pandemia as fast as possible by running a simulation.

## Simulation

Each approach implements a method, which gets the json of the current round of a specified seed and returns the answer in json format using a helper method.

This method is then run for the complete games with the seeds 1 to 100.

## Scoring

After each completed simulation of a game, the score is calculated as a linear score from "short and lost" to "short and won" by mapping it to a [-1,1] intervall using a sigmoid function

The overall score is now calculated by taking the average of the game simulations with the seeds 1 to 100.
