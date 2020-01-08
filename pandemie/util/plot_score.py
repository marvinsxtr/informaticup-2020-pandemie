"""
This file is a useful to plot the currently used score function.
"""

from numpy import arange
from matplotlib import pyplot as plt
from pandemie.tester.tester import Tester, SCORE_HALVED

def main():
    """
    Plot score functions and open window
    :return: None
    """
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    # create data
    rounds = arange(0, SCORE_HALVED * 2)

    # weight functions are static, no need to create a Tester object
    c1 = Tester.win_weight(rounds)
    c2 = Tester.loss_weight(rounds)

    # plot data
    plt.plot(rounds, c1)
    plt.plot(rounds, c2)

    plt.xlabel("rounds")
    plt.ylabel("score")

    plt.grid()


    # Change spine position and hide top and right ones
    ax1.spines['bottom'].set_position("center")
    ax1.spines['top'].set_color('none')
    ax1.spines['right'].set_color('none')

    ax1.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')

    plt.show()

if __name__ == "__main__":
    main()