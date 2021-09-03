################################## test de Loi Normale Tronqué   ###########################################
#load libraries
import data.H358.data_container
import common.timemg as timemg
import scipy.stats as stats
import matplotlib.pyplot as plt
import numpy as np
import math
#lower, upper, mu, and sigma are four parameters
lower, upper = 0, math.inf#10000000
#mu, sigma = 0.6, 0.1
mu, sigma = 56385.13, 98256.97
#instantiate an object X using the above four parameters,
X = stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)

#generate 1000 sample data
# samples = X.rvs(1000)
# print('type_samples=', type(samples))
# print('shape_samples=', np.shape(samples))
if __name__ == '__main__':
    h358 = data.H358.data_container.DataContainer(sample_time=60 * 60, starting_stringdatetime='01/01/2016 0:00:00', ending_stringdatetime='31/01/2016 23:59:00')
    raw_variable_full_names = h358.get_raw_variable_full_names()
    selected_variable_full_names = [raw_variable_full_names[4]]
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

        #time_deltas = [epochtimes_in_ms[j] - epochtimes_in_ms[j - 1] for j in range(1, len(epochtimes_in_ms))]
        for k in range(1, len(epochtimes_in_ms)):
            time_delta=epochtimes_in_ms[k] - epochtimes_in_ms[k - 1]
            if time_delta < 2*3600*1000:
                time_deltas.append(epochtimes_in_ms[k] - epochtimes_in_ms[k - 1])

        samples = np.array(time_deltas)
            # compute the PDF of the sample data
        pdf_probs = stats.truncnorm.pdf(samples, (lower - mu) / sigma, (upper - mu) / sigma, mu, sigma)

            # compute the CDF of the sample data
        cdf_probs = stats.truncnorm.cdf(samples, (lower - mu) / sigma, (upper - mu) / sigma, mu, sigma)

            # make a histogram for the samples
        plt.hist(samples, bins=50, alpha=0.3, label='histogram')#, normed=True

            # # plot the PDF curves
        plt.plot(samples[samples.argsort()], pdf_probs[samples.argsort()], linewidth=2.3, label='PDF curve')
            #
            # # plot CDF curve
        #plt.plot(samples[samples.argsort()], cdf_probs[samples.argsort()], linewidth=2.3, label='CDF curve')

            # legend
        plt.legend(loc='best')
        plt.xlabel('datetimes')
        plt.ylabel('time_deltas')
        plt.title('Probability density of the truncated normal distribution')
        plt.show()















