import os

from bayes_opt import BayesianOptimization, JSONLogger
from bayes_opt.event import Events

import pandemie.tester as tst  # We cannot use import from due to circular imports

from pandemie.util import block_print, enable_print, to_camel_case, operations


def weighted_final_strategy(**weights):
    """
    This function executes the final strategy with the given weights for optimization purposes
    :return: None
    """
    print(weights)

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

    # Set the weight bounds for each measure
    p_bounds = {op: (minimum, maximum) for op in operations.OPERATIONS}

    # Initialize the optimizer
    optimizer = BayesianOptimization(
        f=weighted_final_strategy,
        pbounds=p_bounds,
        random_state=1,
    )

    # Log progress
    number_of_logs = len(os.listdir("./logs"))
    logger = JSONLogger(path="./logs/bayes_log_{0}.json".format(number_of_logs))
    optimizer.subscribe(Events.OPTMIZATION_STEP, logger)

    optimizer.probe(
        params={
            "end_round": 1.0,
            "put_under_quarantine": 1.6,
            "close_airport": 1.5,
            "close_connection": 1.4,
            "develop_vaccine": 2.0,
            "deploy_vaccine": 1.8,
            "develop_medication": 1.9,
            "deploy_medication": 1.7,

            "exert_influence": 1.0,
            "call_elections": 1.1,
            "apply_hygienic_measures": 1.3,
            "launch_campaign": 1.2
        },
        lazy=True,
    )

    optimizer.probe(
        params={
            "apply_hygienic_measures": 0.8,
            "call_elections": 1.2,
            "close_airport": 0.8,
            "close_connection": 1.2,
            "deploy_medication": 0.8,
            "deploy_vaccine": 1.2,
            "develop_medication": 0.8,
            "develop_vaccine": 0.8,
            "end_round": 1.2,
            "exert_influence": 0.8,
            "launch_campaign": 1.2,
            "put_under_quarantine": 1.2
        },
        lazy=True,
    )

    # Start optimizer
    optimizer.maximize(
        init_points=5,
        n_iter=100,
    )

    print(optimizer.max)
    return optimizer.max
