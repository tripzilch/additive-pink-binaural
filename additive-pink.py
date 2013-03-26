#
# uncomment if you don't use `IPython --pylab` and `%run -i`
#
# from pylab import *
#

tau = 2*pi
sr = 44100.0

print '''Sampling rate is %f Hz.
this value is used for both generation and playback. you can change it by
setting the sr variable to another number, before generation and playback.
changing sr after generation will do the expected thing to playback.''' % sr

def sinewave(f, phi, L):
    '''Returns L samples of a sinewave of frequency f (Hz) and phase phi.'''
    res = arange(phi, phi + L)
    res *= (f * tau / sr)
    res = sin(res)
    return res

def beep(freq_phase_amp, L):
    '''Additive synthesis of sinewaves.

    freq_phase_amp -- a numpy array with a row for each sinewave, and
    frequency, phase and amplitude in each column.
    L -- length in samples.
    '''
    res = zeros(L)
    for f, p, a in freq_phase_amp:
        res += a * sinewave(f, p, L)

    return res

def pink(N=100, lo=50, hi=15000, exponent=1.0):
    '''Calculates frequency, phase and amplitude information for a pink noise approximation.

    N -- number of frequencies.
    lo, hi -- frequency band range in Hz.
    exponent -- pink noise generally has a power spectral density of 1/f, this can however be
    generalized to different exponents. for instance, Brownian noise has a power spectral density
    of 1/f^2.
    '''
    # frequency rand[lo,hi], phase rand[0,2pi]
    fpa = rand(N, 2) * c_[(hi - lo), tau] + c_[lo, 0]
    # amplitude = 1 / frequency
    fpa = c_[fpa, 1 / (fpa[:, 0] ** exponent)]
    return fpa

# ----------------------------- playback and sample format functions ---------
import pygame
def pplay_sound(ar, normalize=0.25):
    '''play the array as a wave through pygame, normalized to a level.'''

    pygame.mixer.quit()
    if ar.ndim == 1:
        pygame.mixer.init(frequency=int(sr), size=-16, channels=1)
    elif ar.ndim == 2 and ar.shape[1] == 2:
        pygame.mixer.init(frequency=int(sr), size=-16, channels=2)
    else:
        print "ERR: array must be 1D (mono) or 2D with shape(x, 2)"
        return

    sound = pygame.sndarray.make_sound(wav_float_to_int16(ar, normalize))
    channel = sound.play()
    return channel

def wav_float_to_int16(ar, normalize = 0.25):
    res = ar
    res *= (32767 * normalize) / max(abs(ar.min()), abs(ar.max()))
    return res.astype('int16')

# ----------------------------------------------------------------------------

# I used the following lines of code to generate binaural_pink_10hz.wav (later converted to FLAC with Audacity)

sr = 11025.0

# left channel, 250 sinewaves between 150..4000Hz
pink_fpa_L = pink(N=250, lo=150,hi=4000)
# generate 5 minutes of audio for left channel
print 'generating left channel ...'
beep11kL = beep(pink_fpa_L, sr * 5 * 60)
# pplay_sound(beep11k)
# pygame.mixer.quit()

# right channel has same freqs +10Hz 
pink_fpa_R = pink_fpa_L + c_[10,0,0]
# generate 5 minutes of audio for right channel
print 'generating right channel ...'
beep11kR=beep(pink_fpa_R, sr * 5 * 60) 

print '... done! combining channels and writing to file ...'

# combine
beep11k = column_stack((beep11kL,beep11kR))
# pplay_sound(beep11k)

# write to file
from scipy.io import wavfile
wavfile.write(r'd:\dump\pink_binaural_10Hz.wav', sr, wav_float_to_int16(beep11k))
