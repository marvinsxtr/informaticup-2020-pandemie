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
    score = tester.evaluate(thread_count=50)
    enable_print()

    win_rate = (tester.amount_wins / tester.amount_runs)
    return score + win_rate


def bayesian_optimization():
    # Bounded region of parameter space
    p_bounds = {'put_under_quarantine_weight': (0.2, 1.8),
               'develop_medication_weight': (0.2, 1.8),
               'deploy_medication_weight': (0.2, 1.8)}

    optimizer = BayesianOptimization(
        f=weighted_final_strategy,
        pbounds=p_bounds,
        random_state=1,
    )

    logger = JSONLogger(path="./logs/bayes_logs.json")
    optimizer.subscribe(Events.OPTMIZATION_STEP, logger)

    optimizer.maximize(
        init_points=5,
        n_iter=50,
    )