import os

from bayes_opt import BayesianOptimization, JSONLogger
from bayes_opt.event import Events

import pandemie.tester as tst  # We cannot use import from due to circular imports

from pandemie.util import block_print, enable_print, to_camel_case


def weighted_final_strategy(put_under_quarantine_weight, develop_medication_weight, deploy_medication_weight,
                            close_airport_weight):
    """
    This function executes the final strategy with the given weights for optimization purposes
    :param put_under_quarantine_weight:
    :param develop_medication_weight:
    :param deploy_medication_weight:
    :param close_airport_weight:
    :return:
    """
    # Put weights in a dict
    weights = {
        "put_under_quarantine": put_under_quarantine_weight,
        "close_airport": close_airport_weight,
        "develop_medication": develop_medication_weight,
        "deploy_medication": deploy_medication_weight,
    }

    # Get final strategy
    name = "final"
    _module = __import__("pandemie.tester.strategies." + name, fromlist=to_camel_case(name))
    final_strategy = getattr(_module, to_camel_case(name))

    # Run strategy
    block_print()
    tester = tst.Tester(final_strategy(silent=True, visualize=False, weights=weights))
    score = tester.evaluate(thread_count=20)
    enable_print()

    # Calculate win rate
    win_rate = (tester.amount_wins / tester.amount_runs)
    return win_rate + score


def bayesian_optimization():
    """
    This function uses a bayesian blackbox optimization to improve the final strategy
    :return: Best parameters and score obtained
    """
    # Bounded region of parameter space
    minimum = 0.8
    maximum = 1.2
    p_bounds = {'put_under_quarantine_weight': (minimum, maximum),
                'develop_medication_weight': (minimum, maximum),
                'deploy_medication_weight': (minimum, maximum),
                'close_airport_weight': (minimum, maximum)}

    optimizer = BayesianOptimization(
        f=weighted_final_strategy,
        pbounds=p_bounds,
        random_state=1,
    )

    number_of_logs = len(os.listdir("./logs"))
    logger = JSONLogger(path="./logs/bayes_log_{0}.json".format(number_of_logs))
    optimizer.subscribe(Events.OPTMIZATION_STEP, logger)

    optimizer.maximize(
        init_points=5,
        n_iter=100,
    )

    print(optimizer.max)
    return optimizer.max
