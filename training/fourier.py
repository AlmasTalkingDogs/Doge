# Apply Fast Fourier Transform and frequency filtering to every set of
# time points
import numpy as np

def filtered_frequency_domain_data(signal, T=1.0/192.0):
    W = np.fft.fftfreq(int(signal.size/2) + 1, T)
    f_signal = np.abs(np.real(np.fft.rfft(signal)))
    f_signal[W < 7.5] = 0
    f_signal[W > 30] = 0
    f_signal /= max(f_signal)
    return f_signal, W
