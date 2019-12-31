import os

from bayes_opt import BayesianOptimization, JSONLogger
from bayes_opt.event import Events

from pandemie.util import block_print, enable_print, to_camel_case
from pandemie.tester import Tester


# TODO: add pydoc
def weighted_final_strategy(put_under_quarantine_weight, develop_medication_weight, deploy_medication_weight):
    weights = (put_under_quarantine_weight, develop_medication_weight, deploy_medication_weight)

    name = "final"
    _module = __import__("pandemie.tester.strategies." + name, fromlist=to_camel_case(name))
    final_strategy = getattr(_module, to_camel_case(name))

    block_print()
    tester = Tester(final_strategy(silent=True, visualize=False, weights=weights), random_seed=False)
    score = tester.evaluate(thread_count=20)
    enable_print()

    win_rate = (tester.amount_wins / tester.amount_runs)
    return win_rate  # add score when usable


def bayesian_optimization():
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

    number_of_logs = os.listdir("./logs")
    logger = JSONLogger(path="./logs/bayes_log_{0}.json".format(number_of_logs))
    optimizer.subscribe(Events.OPTMIZATION_STEP, logger)

    optimizer.maximize(
        init_points=5,
        n_iter=100,
    )
