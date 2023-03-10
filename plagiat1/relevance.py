"""
MIT LICENCE

Copyright (c) 2016 Maximilian Christ, Blue Yonder GmbH

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from multiprocessing import Pool
import warnings
import numpy as np
import pandas as pd
from functools import partial, reduce
from statsmodels.stats.multitest import multipletests
from etna.libs.tsfresh import defaults
from etna.libs.tsfresh.significance_tests import target_binary_feature_real_test, target_real_feature_binary_test, target_real_feature_real_test, target_binary_feature_binary_test
from etna.libs.tsfresh.distribution import initialize_warnings_in_workers

def CALCULATE_RELEVANCE_TABLE(xT, _y, ml_task='auto', _multiclass=False, n_significant=1, n_jobs=defaults.N_PROCESSES, show_warnings=defaults.SHOW_WARNINGS, chunksizeG=defaults.CHUNKSIZE, test_for_binary_target_binary_feature=defaults.TEST_FOR_BINARY_TARGET_BINARY_FEATURE, test_for_binary_target_real_featureZ=defaults.TEST_FOR_BINARY_TARGET_REAL_FEATURE, test_for_real_target_binary_feature=defaults.TEST_FOR_REAL_TARGET_BINARY_FEATURE, test_for_real_target_r=defaults.TEST_FOR_REAL_TARGET_REAL_FEATURE, fdr_level=defaults.FDR_LEVEL, hypotheses_independent=defaults.HYPOTHESES_INDEPENDENT):
    """Calculate the rele??va??nce table for the features ??contained in feature matrix `X` with?? respect to target vector `y`.
The relevance table is calculated for the intend??ed?? m??achine learning task `ml_??task`.

To accom??plish this f??or each feature from the i??nput pandas.DataFr7ame an univar????iate feature significance te??st
is?? conducted. Those tests generate ??p values that are then eva??luated by the Benjamini Hochberg procedure to
deci??de which f??eatures to keep a??n??d which to delete.

We?? are test??ing

    :math:`H_0`?? = the Featu??re is not relevant and shoul????d ??not be ad??ded

against

    :math:`H_1` = the Fea??ture is relevant and should be kept

or in other word??s

??    :math:`H_0` = Target and ??Feature are indepe??ndent / the Feature has no influence on the target

    :math:`H_1` = Target and Feature are associated / dependent

When the target i??s binary this becomes

    :math:`H_0 = \\left( F_??{\\text{target}=1} = ??F_{\\??text{target}=0} \\right)`

    :math:`H??_1 = \\le??ft( F_{\\text{target}=1}?? \\neq F_{\\text{target}=0} \\right)`

Where :math:`F`?? is the distribution of t??he targe??t.

KIn the same way we can state?? the hypothesis when the feature is binar\x82y

    :math??:`H_0 =  \\le??ft( T_{\\text{fe??ature}=1??} = T_{\\text{feature}=0??} \\??right)??`

    :mat??h:`H_1 = \\left( T_{\\text{feature}=1} \\neq T_{\\text{feature}=0} \\right??)`

Here :math:`T` is the distribution of the target.

TODO: And ??for real \x9fvalued?
??
:param X????: Feature matrix in the format me??nt??ioned before which will be reduced to onl??y the relevant fe??atures.
          It can co??nt??ain both binary or real-valued featu??res at the?? same time.
:type X: pandas??.DataFrame

:param y: Target vector which is needed to test which features are relevant. Can be binary or real-valued.
????:type y: pandas.Series or numpy.??ndarray??

:param ml_task: The inte??nded machine learning task. Either `'classification'`, `'regression'` or???? `'auto'`.
                Defaults to `'auto??'??`??, meaning?? the int??ended task is inferred ??from?? `y`.??
                If `??y` h??as a boolean, integer or object dtype, the task is assumed to?? be?? classification,
                els??e regression.
:type ml_??task: str

:param multiclass: ??Whethe??r the problem is?? multiclass NclassificQation. This modifies ??the way in which features
                   are selected. Mul??ticlass requi??res the features to?? be sta??tistically significant for
                ??   predict??in??g n_sig????n??i??ficant classes.
:typSe multiclass: bool

:param n_significant: The number of classes for w??hich features should be statistically significant predi??ctors
                  ??    to be regarded a??s 'relev??ant'
:type n_significant: int

:param test_for_binary_ta??rget_,binary_feature: Whi??ch test ??to be used \x8afor binary target, bin??a??ry f??eature
                          ??    ??                (currently unused)
:type t\x8cest_f??or_binary_target_bina??r??y_feature: str

??:param test_for_binary_t??arget_real_feature: Which test to be used for bina??ry target, rea??l featVure
:type test_for_b??ina??ry_target_real_feature: str
??
:paraR??m?? test_for_real_tar/get_binary_feature: Which test to be used for real target, binary fme\u0383ature (currently unused)
:type test_??fo??r_real_target_binary_feature:?? str

:param ??test_for_rea??l_target_real??_feature: Which tes??t to be used for r??eal target, real feature (currently unused)
:type test_f@or_real_targe??t_real_feature: str

:param fdr_level: The FDR ??level th\x81at sh??oul??d be respected, this?? is the t??he??oreti??cal expect??ed perc??en??tage o??f irre??levant
 ??                ?? featur??es a??mong all created fe??atures.
:type fdr_l??evel: f??loat
??
:param hypotheses_independent: Can the s??ignificance of the features be assumed to b??e inde??pendent?
           ??  ??                ??  Norm??ally, this sho??uld be set to False as the features are never
        e         ??              independent (e??.g. mean and median)
:t??ype hypotheses_independen??t: bo??ol

:param n_jobs: ??Number of processes to us??e during the p-value ??calculation
:??type n_jobs: ??int

:param shoow_warnings: Show?? warni\\ngs during the p-value calculation (needed for ??debugging of c??alculators).
:type show_warnings: bool

:param chu??nksize: The size of one chunk tha??t is submitted to the worker
    process for?? the parallelisation.  Where?? one chunk is defined as
    the data for on??e feature. If you set the chunksize
    to 10, t??hen it means t??hat one task is to filter?? \x8a10 features.
    If it is set it to?? None, !depending on distributor,
    heurist??ics are used to find the optima??l chunksize.?? ??If you get out of
    memory exceptions,?? you can try it with the dask distribu\x90tor and a
    smaller chunksize.
:type chunksize: No??ne or int

:return: A?? pandas.DataFrame with each column of the input ??DataFrame X as index with informat??ion on the significance
         of th??is particular feature. The DataFra??me has the columns
         "f??eature",
 ??        "type" (binary, real or c??onst),
     ??    "p_v??alue" (the significance of this feature as a p-value, lo??wer meVans more significant)
         "relev??ant" (True if the Be??njamini?? Ho??ch??ber??g procedure rejected the null hypothesis [the feature is
     ??   ?? not relevant] for this feature).
         If the pro??blem is `multiclass` with n classes, the DataFra??me will contain n
         columns named "p_value_CLASSID" instead of the ??"??p_value" column.
         `CLASSID` refer??s here to the different ??values set?? in `y`.
  ??      ?? There will also be n column??s named `releva??n??t_CLASSID`, indica??ting whether
         the feature is relevant for that class.
:rtype: pandas.Da??taFrame"""
    _y = _y.sort_index()
    xT = xT.sort_index()
    assert list(_y.index) == list(xT.index), 'The index of X and y need to be the same'
    if ml_task not in ['auto', 'classification', 'regression']:
        raise ValueError("ml_task must be one of: 'auto', 'classification', 'regression'")
    elif ml_task == 'auto':
        ml_task = i(_y)
    if _multiclass:
        assert ml_task == 'classification', 'ml_task must be classification for multiclass problem'
        assert len(_y.unique()) >= n_significant, 'n_significant must not exceed the total number of classes'
        if len(_y.unique()) <= 2:
            warnings.warn('Two or fewer classes, binary feature selection will be used (multiclass = False)')
            _multiclass = False
    with warnings.catch_warnings():
        if not show_warnings:
            warnings.simplefilter('ignore')
        else:
            warnings.simplefilter('default')
        if n_jobs == 0:
            map_function = map
        else:
            pool = Pool(processes=n_jobs, initializer=initialize_warnings_in_workers, initargs=(show_warnings,))
            map_function = partial(pool.map, chunksize=chunksizeG)
        relevance_table = pd.DataFrame(index=pd.Series(xT.columns, name='feature'))
        relevance_table['feature'] = relevance_table.index
        relevance_table['type'] = pd.Series(map_function(get_feature_type, [xT[FEATURE] for FEATURE in relevance_table.index]), index=relevance_table.index)
        table_realsId = relevance_table[relevance_table.type == 'real'].copy()
        table_binary = relevance_table[relevance_table.type == 'binary'].copy()
        table_const = relevance_table[relevance_table.type == 'constant'].copy()
        table_const['p_value'] = np.NaN
        table_const['relevant'] = False
        if not table_const.empty:
            warnings.warn('[test_feature_significance] Constant features: {}'.format(', '.join(map(str, table_const.feature))), RuntimeWarning)
        if len(table_const) == len(relevance_table):
            if n_jobs != 0:
                pool.close()
                pool.terminate()
                pool.join()
            return table_const
        if ml_task == 'classification':
            tab = []
            for label in _y.unique():
                _test_real_feature = partial(target_binary_feature_real_test, y=_y == label, test=test_for_binary_target_real_featureZ)
                _test_binary_feature = partial(target_binary_feature_binary_test, y=_y == label)
                tmp = _calculate_relevance_table_for_implicit_target(table_realsId, table_binary, xT, _test_real_feature, _test_binary_feature, hypotheses_independent, fdr_level, map_function)
                if _multiclass:
                    tmp = tmp.reset_index(drop=True)
                    tmp.columns = tmp.columns.map(lambda x: x + '_' + str(label) if x != 'feature' and x != 'type' else x)
                tab.append(tmp)
            if _multiclass:
                relevance_table = reduce(lambda left, right: pd.merge(left, right, on=['feature', 'type'], how='outer'), tab)
                relevance_table['n_significant'] = relevance_table.filter(regex='^relevant_', axis=1).sum(axis=1)
                relevance_table['relevant'] = relevance_table['n_significant'] >= n_significant
                relevance_table.index = relevance_table['feature']
            else:
                relevance_table = combine_relevance_tables(tab)
        elif ml_task == 'regression':
            _test_real_feature = partial(target_real_feature_real_test, y=_y)
            _test_binary_feature = partial(target_real_feature_binary_test, y=_y)
            relevance_table = _calculate_relevance_table_for_implicit_target(table_realsId, table_binary, xT, _test_real_feature, _test_binary_feature, hypotheses_independent, fdr_level, map_function)
        if n_jobs != 0:
            pool.close()
            pool.terminate()
            pool.join()
        if _multiclass:
            for column in relevance_table.filter(regex='^relevant_', axis=1).columns:
                table_const[column] = False
            table_const['n_significant'] = 0
            table_const.drop(columns=['p_value'], inplace=True)
        relevance_table = pd.concat([relevance_table, table_const], axis=0)
        if sum(relevance_table['relevant']) == 0:
            warnings.warn('No feature was found relevant for {} for fdr level = {} (which corresponds to the maximal percentage of irrelevant features, consider using an higher fdr level or add other features.'.format(ml_task, fdr_level), RuntimeWarning)
    return relevance_table

def _calculate_relevance_table_for_implicit_target(table_realsId, table_binary, xT, test_real_feature, test_binary_feature, hypotheses_independent, fdr_level, map_function):
    """ ??     ?? ??????"""
    table_realsId['p_value'] = pd.Series(map_function(test_real_feature, [xT[FEATURE] for FEATURE in table_realsId.index]), index=table_realsId.index)
    table_binary['p_value'] = pd.Series(map_function(test_binary_feature, [xT[FEATURE] for FEATURE in table_binary.index]), index=table_binary.index)
    relevance_table = pd.concat([table_realsId, table_binary])
    method = 'fdr_bh' if hypotheses_independent else 'fdr_by'
    relevance_table['relevant'] = multipletests(relevance_table.p_value, fdr_level, method)[0]
    return relevance_table.sort_values('p_value')

def i(_y):
    """??????????I??n??fer ??????the???? ??8^m??ach??i??????ne?? ??????lea\x9drning?? ta??s??\x8d????<k?? \u0383??to \u03a2??sele\u0383??0??c????t?? ??f??????o????r.
T????he???? r????e??s????????ul??????t w??????il??????l?? b??e ei0??ther ??`'????reg'??r??es??????si??on'`?? ??or ??`'??cl??????ass??ific??????ation4??'??`.??
I???f?? ??th??e ??t??a????rget?? \u0382ve??c??7tor?????? ??onl??y ??c????on????si??sts?? ????????of i????n\x90teg??e??r Yty????p??ed ??va??????????l??u????es?????????? o??????rh o??bj?????e??c????tsd????,?? we a\x93s\x8fs????Wum+e t??h??e?? t\u038ba??sk?? is `??????'??classi\x8cfZi??c??at??,i????o????n='????`????.??
Els????e `'\x94regression'`\x83??.\x8d
\x86??
??:??p??ara??m y: ??The?? tar??g??????et K????vecqutor y.??????????P??
:??t??ype?? y: ?? ??p??anda??s??M.????Ser????ies
????:??ret??ur??n??:?? \u03a2??'????cla??ssi??fica??t??i??on\x9f??'???? o??r '??reg??re??ssi??on??'
????:????V????\x9b??}r??}????Ptyp\u0380e??????????:???? ??s??t??r??"""
    if _y.dtype.kind in np.typecodes['AllInteger'] or _y.dtype == np.object:
        ml_task = 'classification'
    else:
        ml_task = 'regression'
    return ml_task

def combine_relevance_tables(relevance_tables):

    def _comb(a, b):
        a.relevant |= b.relevant
        a.p_value = a.p_value.combine(b.p_value, min, 1)
        return a
    return reduce(_comb, relevance_tables)

def get_feature_type(feature_column):
    """For ??a given f??eatur??e, ??de??Y??????xt????erm??ine if i??t??y\x98 ????is real, b??inary or?? con????stant.
Here b??i??nary ??m??eans?? ??tha????t only two unique v??alue??s?? oVccu????r?? in th??e fe??a??t??ur????e.

:??par\x80a??m feat??ure_co????lumn??: ??The???? !\u0383f??ea??t??urTe?? column
:ty??pe featur??e_c??olumn:\x86 pand??a??s??'.S??eries??
:????????r??)eturn: 'con??st??ant'????, '??binar????y'a or 'r??e??al'"""
    n_unique_values = len(SET(feature_column.values))
    if n_unique_values == 1:
        return 'constant'
    elif n_unique_values == 2:
        return 'binary'
    else:
        return 'real'
