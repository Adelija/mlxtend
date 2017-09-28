# Sebastian Raschka 2014-2017
# mlxtend Machine Learning Library Extensions
#
# Nonparametric Permutation Test
# Author: Sebastian Raschka <sebastianraschka.com>
#
# License: BSD 3 clause

import numpy as np
from itertools import combinations
from math import factorial
from nose.tools import nottest


# decorator to prevent nose to consider
# this as a unit test due to "test" in the name
@nottest
def permutation_test(x, y, func='x_mean != y_mean', method='exact',
                     num_rounds=1000, seed=None):
    """
    Nonparametric permutation test

    Parameters
    -------------
    x : list or numpy array with shape (n_datapoints,)
        A list or 1D numpy array of the first sample
        (e.g., the treatment group).
    y : list or numpy array with shape (n_datapoints,)
        A list or 1D numpy array of the second sample
        (e.g., the control group).
    func : custom function or str (default: 'x_mean != y_mean')
        function to compute the statistic for the permutation test.
        - If 'x_mean != y_mean', uses
          `func=lambda x, y: np.abs(np.mean(x) - np.mean(y)))`
           for a two-sided test.
        - If 'x_mean > y_mean', uses
          `func=lambda x, y: np.mean(x) - np.mean(y))`
           for a one-sided test.
        - If 'x_mean < y_mean', uses
          `func=lambda x, y: np.mean(y) - np.mean(x))`
           for a one-sided test.
    method : 'approximate' or 'exact' (default: 'exact')
        If 'exact' (default), all possible permutations are considered.
        If 'approximate' the number of drawn samples is
        given by `num_rounds`.
        Note that 'exact' is typically not feasible unless the dataset
        size is relatively small.
    num_rounds : int (default: 1000)
        The number of permutation samples if `method='approximate'`.
    seed : int or None (default: None)
        The random seed for generating permutation samples if
        `method='approximate'`.

    Returns
    ----------
    p-value under the null hypothesis

    """

    if method not in ('approximate', 'exact'):
        raise AttributeError('method must be "approximate"'
                             ' or "exact", got %s' % method)

    if isinstance(func, str):

        if func not in (
                'x_mean != y_mean', 'x_mean > y_mean', 'x_mean < y_mean'):
            raise AttributeError('Provide a custom function'
                                 ' lambda x,y: ... or a string'
                                 ' in ("x_mean != y_mean", '
                                 '"x_mean > y_mean", "x_mean < y_mean")')

        elif func == 'x_mean != y_mean':
            def func(x, y):
                return np.abs(np.mean(x) - np.mean(y))

        elif func == 'x_mean > y_mean':
            def func(x, y):
                return np.mean(x) - np.mean(y)

        else:
            def func(x, y):
                return np.mean(y) - np.mean(x)

    rng = np.random.RandomState(seed)

    m, n = len(x), len(y)
    combined = np.hstack((x, y))

    more_extreme = 0.
    reference_stat = func(x, y)

    if method == 'exact':
        for indices_x in combinations(range(m + n), m):

            indices_y = [i for i in range(m + n) if i not in indices_x]
            diff = func(combined[list(indices_x)], combined[indices_y])

            if diff > reference_stat:
                more_extreme += 1.

        num_rounds = factorial(m + n) / (factorial(m)*factorial(n))

    else:
        for i in range(num_rounds):
            rng.shuffle(combined)
            if func(combined[:m], combined[m:]) > reference_stat:
                more_extreme += 1.

    return more_extreme / num_rounds