import data.H358.data_container
import common.timemg as timemg
import testunion_intersec
import matplotlib.pyplot as plt
import numpy as np
from sympy import Symbol
import matplotlib.mlab as mlab  # probas
import math
from math import *
from scipy.stats import norm
from scipy import integrate
from scipy.linalg import solve
from math import sqrt
# moyenne, variance, ecart type
def moyenne(tableau):
    return sum(tableau, 0.0) / len(tableau)

#La variance est définie comme la moyenne des carrés des écarts à la moyenne
def variance(tableau):
    m=moyenne(tableau)
    return moyenne([(x-m)**2 for x in tableau])

#L'écart-type est défini comme la racine carrée de la variance
def ecartype(tableau):
    return variance(tableau)**0.5
def detect_gaps(epochtimesms: list, values: list):
    delta_values = [values[k + 1] - values[k] for k in range(len(values) - 1)]
    mu = variance(delta_values)
    sigma = ecartype(delta_values)
    print('mu=', mu)
    print('sigma=', sigma)

    A = exp(- (mu / (sqrt(2) * sigma)) ** 2)
    alpha = 0.99 ** 2
    a = -((1 - alpha) ** 2)
    print('a=', a)
    b = 4 * alpha - 2 * (1 + alpha ** 2) * A
    c = 4 * alpha ** 2 + 4 * alpha * A + ((1 + alpha) ** 2) * (A ** 2)
    delta = b ** 2 - (4 * a * c)
    print('delta=', delta)
    x1 = (-b + sqrt(delta)) / (2 * a)
    print('x1=', x1)
    x2 = (-b - sqrt(delta)) / (2 * a)
    print('x2=', x2)
    gaps = list()
    x = x2  # 9900
    print('Ln_x=', math.log(x))
    th = mu - sqrt(2) * sigma * sqrt(math.log(x))
    print('th=', th)
    #print('ln_th=', math.log(th))
    for k in range(1, len(values) - 1):

        if (values[k]>sqrt(th)):#22436

            gaps.append((timemg.epochtimems_to_datetime(epochtimesms[k]), timemg.epochtimems_to_datetime(epochtimesms[k+1])))
    return gaps
if __name__ == '__main__':
    h358 = data.H358.data_container.DataContainer(sample_time=60 * 60, starting_stringdatetime='01/01/2016 0:00:00', ending_stringdatetime='31/01/2016 23:59:00')
    raw_variable_full_names = h358.get_raw_variable_full_names()
    print(raw_variable_full_names)
    selected_variable_full_names = [raw_variable_full_names[4]]#, raw_variable_full_names[4]]
    print(selected_variable_full_names)
    raw_variable_names = list()
    raw_variable_full_name_datetimes = list()
    faulty_intervals = list()
    gaps = list()
    raw_variable_indices = []
    for variable_name in selected_variable_full_names:
        epochtimes_in_ms, values = h358.get_raw_measurements_from_variables(variable_name)
        raw_variable_indices.extend([variable_name for j in range(len(epochtimes_in_ms))])
        raw_variable_full_name_datetimes.extend(timemg.epochtimems_to_datetime(epochtimes_in_ms[k]) for k in range(len(epochtimes_in_ms)))
        time_deltas=[]
        gaps=[]
        time_deltas = [epochtimes_in_ms[j] - epochtimes_in_ms[j - 1] for j in range(1, len(epochtimes_in_ms))]
        gaps.append(detect_gaps(epochtimes_in_ms, time_deltas))
    global_gaps = testunion_intersec.union([gaps])
    print('Global :\n', global_gaps)
    fig, ax = plt.subplots()
    ax.plot(raw_variable_full_name_datetimes, raw_variable_indices, '|k')
    plt.xlabel('datetimes')
    plt.ylabel('time_deltas')
    plt.title('Data gaps')
    ax.grid()
    plt.show()