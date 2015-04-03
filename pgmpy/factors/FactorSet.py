#!/usr/bin/env python3
from pgmpy.factors import Factor
from functools import reduce


class FactorSet:
    r"""
    Base class of *Factor Sets*.

    A factor set provides a compact representation of  higher dimensial factor
    :math:`\phi_1\cdot\phi_2\cdots\phi_n`

    For example the factor set corresponding to factor :math:`\phi_1\cdot\phi_2` would be the union of the factors
    :math:`\phi_1` and :math:`\phi_2` i.e. factor set :math:`\vec\phi = \phi_1 \cup \phi_2`.
    """
    def __init__(self, *factors_list):
        """
        Initialize the factor set class.

        Parameters
        ----------
        factors_list: Factor1, Factor2, ....
            All the factors whose product is represented by the factor set

        Examples
        --------
        >>> from pgmpy.factors import FactorSet
        >>> from pgmpy.factors import Factor
        >>> phi1 = Factor(['x1', 'x2', 'x3'], [2, 3, 2], range(12))
        >>> phi2 = Factor(['x3', 'x4', 'x1'], [2, 2, 2], range(8))
        >>> factor_set = FactorSet(phi1, phi2)
        """
        if not all(isinstance(phi, Factor) for phi in factors_list):
            raise TypeError("Input parameters must be all factors")
        self.factors_set = set(factors_list)

    def product(self, *factorsets):
        r"""
        Return the factor sets product with the given factor sets

        Suppose :math:`\vec\phi_1` and :math:`\vec\phi_2` are two factor sets then their product is a another factors
        set :math:`\vec\phi_3 = \vec\phi_1 \cup \vec\phi_2`.

        Parameters
        ----------
        factorsets: FactorSet1, FactorSet2, ..., FactorSetn
            FactorSets to be multiplied

        Examples
        --------
        >>> from pgmpy.factors import FactorSet
        >>> from pgmpy.factors import Factor
        >>> phi1 = Factor(['x1', 'x2', 'x3'], [2, 3, 2], range(12))
        >>> phi2 = Factor(['x3', 'x4', 'x1'], [2, 2, 2], range(8))
        >>> factor_set1 = FactorSet(phi1, phi2)
        >>> phi3 = Factor(['x5', 'x6', 'x7'], [2, 2, 2], range(8))
        >>> phi4 = Factor(['x5', 'x7', 'x8'], [2, 2, 2], range(8))
        >>> factor_set2 = FactorSet(phi3, phi4)
        >>> factor_set2.product(factor_set1)
        """
        return factorset_product(self, *factorsets)

    def divide(self, factorset):
        r"""
        Returns a new factor set instance after division by the factor set

        Division of two factor sets :math:`\frac{\vec\phi_1}{\vec\phi_2}` basically translates to union of all the
        factors present in :math:`\vec\phi_2` and :math:`\frac{1}{\phi_i}` of all the factors present in
        :math:`\vec\phi_2`.

        Parameters
        ----------
        factorset: FactorSet
            The divisor

        Examples
        --------
        >>> from pgmpy.factors import FactorSet
        >>> from pgmpy.factors import Factor
        >>> phi1 = Factor(['x1', 'x2', 'x3'], [2, 3, 2], range(12))
        >>> phi2 = Factor(['x3', 'x4', 'x1'], [2, 2, 2], range(8))
        >>> factor_set1 = FactorSet(phi1, phi2)
        >>> phi3 = Factor(['x5', 'x6', 'x7'], [2, 2, 2], range(8))
        >>> phi4 = Factor(['x5', 'x7', 'x8'], [2, 2, 2], range(8))
        >>> factor_set2 = FactorSet(phi3, phi4)
        >>> factor_set3 = factor_set2.divide(factor_set1)
        """
        return factorset_divide(self, factorset)

    def marginalize(self, variables, inplace=True):
        """
        Marginalizes the factors present in the factor sets with respect to the given variables.

        Parameters
        ----------
        variables: string, list-type
            name of the variable (or variables) to be marginalized

        inplace: boolean
            If inplace=True it will modify the factor set itself, else it would create a new factor set

        Examples
        --------
        >>> from pgmpy.factors import FactorSet
        >>> from pgmpy.factors import Factor
        >>> phi1 = Factor(['x1', 'x2', 'x3'], [2, 3, 2], range(12))
        >>> phi2 = Factor(['x3', 'x4', 'x1'], [2, 2, 2], range(8))
        >>> factor_set1 = FactorSet(phi1, phi2)
        >>> factor_set1.marginalize('x1')
        """
        if not isinstance(variables, (list, set, tuple)):
            variables = [variables]

        factors_to_be_marginalized = set(filter(lambda x: len(set(x.scope()).intersection(variables)) != 0,
                                                self.factors_set))
        if not inplace:
            new_factors_set = self.factors_set - factors_to_be_marginalized

        for factor in factors_to_be_marginalized:
            variables_to_be_marginalized = list(set(factor.scope()).intersection(variables))
            if inplace:
                factor.marginalize(variables_to_be_marginalized, inplace=True)
            else:
                new_factors_set.add(factor.marginalize(variables_to_be_marginalized, inplace=False))

        if not inplace:
            return FactorSet(*new_factors_set)


def factorset_product(*factorsets_list):
    r"""
    Base method used for product of factor sets.

    Suppose :math:`\vec\phi_1` and :math:`\vec\phi_2` are two factor sets then their product is a another factors set
    :math:`\vec\phi_3 = \vec\phi_1 \cup \vec\phi_2`.

    Parameters
    ----------
    factorsets_list: FactorSet1, FactorSet2, ..., FactorSetn
        All the factor sets to be multiplied

    Examples
    --------
    >>> from pgmpy.factors import FactorSet
    >>> from pgmpy.factors import Factor
    >>> from pgmpy.factors import factorset_product
    >>> phi1 = Factor(['x1', 'x2', 'x3'], [2, 3, 2], range(12))
    >>> phi2 = Factor(['x3', 'x4', 'x1'], [2, 2, 2], range(8))
    >>> factor_set1 = FactorSet(phi1, phi2)
    >>> phi3 = Factor(['x5', 'x6', 'x7'], [2, 2, 2], range(8))
    >>> phi4 = Factor(['x5', 'x7', 'x8'], [2, 2, 2], range(8))
    >>> factor_set2 = FactorSet(phi3, phi4)
    >>> factor_set3 = factorset_product(factor_set1, factor_set2)
    """
    if not all(isinstance(factorset, FactorSet) for factorset in factorsets_list):
        raise TypeError("Input parameters must be factor sets")
    return reduce(lambda x, y: FactorSet(*(x.factors_set.union(y.factors_set))), factorsets_list)


def factorset_divide(factorset1, factorset2):
    r"""
    Base method for dividing two factor sets.

    Division of two factor sets :math:`\frac{\vec\phi_1}{\vec\phi_2}` basically translates to union of all the factors
    present in :math:`\vec\phi_2` and :math:`\frac{1}{\phi_i}` of all the factors present in :math:`\vec\phi_2`.

    Parameters
    ----------
    factorset1: FactorSet
        The dividend

    factorset2: FactorSet
        The divisor

    Examples
    --------
    >>> from pgmpy.factors import FactorSet
    >>> from pgmpy.factors import Factor
    >>> from pgmpy.factors import factorset_divide
    >>> phi1 = Factor(['x1', 'x2', 'x3'], [2, 3, 2], range(12))
    >>> phi2 = Factor(['x3', 'x4', 'x1'], [2, 2, 2], range(8))
    >>> factor_set1 = FactorSet(phi1, phi2)
    >>> phi3 = Factor(['x5', 'x6', 'x7'], [2, 2, 2], range(8))
    >>> phi4 = Factor(['x5', 'x7', 'x8'], [2, 2, 2], range(8))
    >>> factor_set2 = FactorSet(phi3, phi4)
    >>> factor_set3 = factorset_divide(factor_set1, factor_set2)
    """
    if not isinstance(factorset1, FactorSet) or not isinstance(factorset2, FactorSet):
        raise TypeError("factorset1 and factorset2 must be factor sets")
    return FactorSet(*factorset1.factors_set.union([x.identity_factor() / x for x in factorset2.factors_set]))
