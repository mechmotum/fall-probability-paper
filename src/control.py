import os

import numpy as np
from scipy.constants import golden_ratio
import matplotlib.pyplot as plt
from bicycleparameters.parameter_sets import Meijaard2007ParameterSet
from bicycleparameters.bicycle import sort_eigenmodes

from data import bike_with_rider, bike_without_rider
from model import SteerControlModel

SCRIPT_PATH = os.path.realpath(__file__)
SRC_DIR = os.path.dirname(SCRIPT_PATH)
ROOT_DIR = os.path.realpath(os.path.join(SRC_DIR, '..'))
DAT_DIR = os.path.join(ROOT_DIR, 'data')
FIG_DIR = os.path.join(ROOT_DIR, 'figures')
KPH2MPS = 1000.0/3600.0
MPS2KPH = 1.0/KPH2MPS
# NOTE : The theorectical gains (values) are manually chosen for a eye-balled
# best fit of the weave mode for the Teensy set gain (keys).
GAIN_MAP = {8: 3.9, 10: 5.2}

if not os.path.exists(FIG_DIR):
    os.mkdir(FIG_DIR)

par_set_without = Meijaard2007ParameterSet(bike_without_rider, False)
model_without = SteerControlModel(par_set_without)

par_set_with = Meijaard2007ParameterSet(bike_with_rider, True)
model_with = SteerControlModel(par_set_with)

# FIGURE : Geometry and mass distribution
fig, axes = plt.subplots(1, 2, sharey=True, layout='constrained')
fig.set_size_inches((160/25.4, 160/25.4/golden_ratio))
par_set_without.plot_all(ax=axes[0])
par_set_with.plot_all(ax=axes[1])
fig.savefig(os.path.join(FIG_DIR, 'bicycle-with-geometry-mass.png'), dpi=300)

speeds = np.linspace(0.0, 10.0, num=2001)


# control law
def generate_gains(static_gain):
    """
    static_gain : float
        Gain value for use in the controller model.
    """
    vmin, vmin_idx = 1.5, np.argmin(np.abs(speeds - 1.5))
    vmax, vmax_idx = 4.7, np.argmin(np.abs(speeds - 4.7))
    kphidots = -static_gain*(vmax - speeds)
    kphidots[:vmin_idx] = -static_gain*(vmax - vmin)/vmin*speeds[:vmin_idx]
    kphidots[vmax_idx:] = 0.0
    return kphidots


# FIGURE : Plot the roll rate gains versus speed.
def plot_gains_vs_speed():
    fig, ax = plt.subplots(layout='constrained')
    fig.set_size_inches((80/25.4, 80/25.4/golden_ratio))
    ax.plot(speeds, generate_gains(GAIN_MAP[8]),
            label=f"Gain {GAIN_MAP[8]}")
    ax.plot(speeds, generate_gains(GAIN_MAP[10]),
            label=f"Gain {GAIN_MAP[10]}")
    ax.set_ylabel(r'$k_\dot{\phi}$')
    ax.legend()
    fig.savefig(os.path.join(FIG_DIR, 'gains-vs-speed.png'), dpi=300)


plot_gains_vs_speed()


# FIGURE : Compare eigenvalues vs speed for uncontrolled.
def stable_ranges(evals):
    # TODO : This should return the indice after a rise and before a fall. It
    # now always returns the indices after a rise or fall.
    where_stable = np.all(evals.real < 0.0, axis=1)
    padded = np.hstack(([False], where_stable, [False]))
    start_stop_idxs = np.flatnonzero(np.diff(padded))
    return start_stop_idxs.reshape(-1, 2)


def plot_eig(ax, model, teensy_gain, kphidots=0.0, legend=False):
    evals_, evecs_ = sort_eigenmodes(*model.calc_eigen(v=speeds,
                                                       kphidot=kphidots))
    weave_idx, capsize_idx = stable_ranges(evals_)[0]
    weave_speed, capsize_speed = speeds[weave_idx], speeds[capsize_idx]
    msg = 'Weave speed: {:1.2f} [m/s], {:1.1f} [km/h]'
    print(msg.format(weave_speed, weave_speed*MPS2KPH))
    msg = 'Capsize speed: {:1.2f} [m/s], {:1.1f} [km/h]'
    print(msg.format(capsize_speed, capsize_speed*MPS2KPH))
    if teensy_gain == 10 or teensy_gain == 'both':
        ymin, ymax = -6.0, 12.0
        ax.axvline(6.0*KPH2MPS, ymin=ymin, ymax=ymax, color='black',
                   linestyle=':')
    if teensy_gain == 8 or teensy_gain == 'both':
        ymin, ymax = -5, 11.0
        ax.axvline(10.0*KPH2MPS, ymin=ymin, ymax=ymax, color='black',
                   linestyle='-.')
    if legend:
        # NOTE : Fake line to make legend work.
        ax.axvline(40.0*KPH2MPS, ymin=ymin, ymax=ymax, color='black',
                   linestyle=':')
    model.plot_eigenvalue_parts(ax=ax, v=speeds, kphidot=kphidots,
                                hide_zeros=True, colors=['k']*4)
    ax.set_ylim((ymin, ymax))
    if legend:
        # NOTE : Fake points to make legend work.
        ax.plot([40.0, 41.0], [40.0, 41.], color='black', marker='*',
                linestyle='')
        ax.legend(['10 km/h', '6 km/h', 'Stable', 'Imaginary', '_none',
                   '_none', '_none', 'Real', '_none', '_none', '_none',
                   'Identified'],
                  fontsize=8,
                  bbox_to_anchor=(1.6, 0.25),
                  bbox_transform=fig.transFigure,
                  loc='upper center',
                  ncol=6, labelspacing=0.0)
    return ax


def create_six_panel():

    data8_fname = 'weave_eigenvalues_from_experiment_gain_8.csv'
    data10_fname = 'weave_eigenvalues_from_experiment_gain_10.csv'
    plot_fname = 'balance-assist-eig-vs-speeds.png'

    fig_six, axes = plt.subplots(3, 2, sharex=True, sharey=True)
    fig_six.subplots_adjust(top=0.85, bottom=0.16, right=0.95, wspace=0.1,
                            hspace=0.1)
    fig_six.set_size_inches((160/25.4, 160/25.4*3/4))

    msg = 'Without rigid rider and balance assist off:'
    print(msg)
    print("-"*len(msg))
    ax = plot_eig(axes[0, 0], model_without, 'both')
    sax = ax.secondary_xaxis('top', functions=(lambda x: x*MPS2KPH,
                                               lambda x: x*KPH2MPS))
    sax.set_xlabel('Speed [km/h]')
    ax.set_title('Without Rigid Rider', fontsize=10)
    ax.set_ylabel('Assist Off\nEig. Comp. [1/s]', fontsize=8)
    ax.set_xlabel('')

    msg = '\nWithout rigid rider and balance assist on:'
    print(msg)
    print("-"*len(msg))
    print('Model gain: {}'.format(GAIN_MAP[8]))
    kphidots = generate_gains(GAIN_MAP[8])
    ax = plot_eig(axes[1, 0], model_without, 8, kphidots=kphidots, legend=True)
    weave_eig = np.loadtxt(os.path.join(DAT_DIR, data8_fname), delimiter=',',
                           skiprows=1)
    ax.plot(weave_eig[:, 0], weave_eig[:, 1], color='black', marker='*',
            linestyle='')
    ax.plot(weave_eig[:, 0], weave_eig[:, 2], color='black', marker='*',
            linestyle='')
    ax.set_ylabel(f'Assist On, $\kappa={GAIN_MAP[8]}$\nEig. Comp. [1/s]',
                  fontsize=8)
    ax.set_xlabel('')

    msg = '\nWithout rigid rider and balance assist on:'
    print(msg)
    print("-"*len(msg))
    print('Model gain: {}'.format(GAIN_MAP[10]))
    kphidots = generate_gains(GAIN_MAP[10])
    ax = plot_eig(axes[2, 0], model_without, 10, kphidots=kphidots)
    weave_eig = np.loadtxt(os.path.join(DAT_DIR, data10_fname), delimiter=',',
                           skiprows=1)
    ax.plot(weave_eig[:, 0], weave_eig[:, 1], color='black', marker='*',
            linestyle='')
    ax.plot(weave_eig[:, 0], weave_eig[:, 2], color='black', marker='*',
            linestyle='')
    ax.set_ylabel(f'Assist On, $\kappa={GAIN_MAP[10]}$\nEig. Comp. [1/s]',
                  fontsize=8)
    ax.set_xlabel('Speed [m/s]')

    msg = '\nWith rigid rider and balance assist off:'
    print(msg)
    print("-"*len(msg))
    ax = plot_eig(axes[0, 1], model_with, 'both')
    sax = ax.secondary_xaxis('top', functions=(lambda x: x*MPS2KPH,
                                               lambda x: x*KPH2MPS))
    sax.set_xlabel('Speed [km/h]')
    ax.set_title('With Rigid Rider', fontsize=10)
    ax.set_ylabel('')
    ax.set_xlabel('')

    msg = '\nWith rigid rider and balance assist on:'
    print(msg)
    print("-"*len(msg))
    print('Model gain: {}'.format(GAIN_MAP[8]))
    kphidots = generate_gains(GAIN_MAP[8])
    ax = plot_eig(axes[1, 1], model_with, 8, kphidots=kphidots)
    ax.set_ylabel('')
    ax.set_xlabel('')

    msg = '\nWith rigid rider and balance assist on:'
    print(msg)
    print("-"*len(msg))
    print('Model gain: {}'.format(GAIN_MAP[10]))
    kphidots = generate_gains(GAIN_MAP[10])
    ax = plot_eig(axes[2, 1], model_with, 10, kphidots=kphidots)
    ax.set_ylabel('')
    ax.set_xlabel('Speed [m/s]')

    fig_six.savefig(os.path.join(FIG_DIR, plot_fname), dpi=300)


create_six_panel()

# FIGURE : Simulate an initial value problem at a low speed under control.
idx = np.argmin(np.abs(speeds - 6.0*KPH2MPS))  # 6 km/h
kphidots = generate_gains(10)
print('kphidot @ 6 km/h:', kphidots[idx])


def controller(t, x):
    K = np.array([[0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, kphidots[idx], 0.0]])
    torques = -K@x
    if np.abs(torques[1]) >= 7.0:
        torques[1] = np.sign(torques[1])*7.0
    return torques


times = np.linspace(0.0, 10.0, num=1001)
x0 = np.deg2rad([10.0, -10.0, 0.0, 0.0])
axes = model_without.plot_simulation(times, x0, input_func=controller,
                                     v=speeds[idx])
axes[0].set_title(r'$v$ = {:1.2f} [m/s]'.format(speeds[idx]))
axes[0].set_ylabel('Torque\n[Nm]')
axes[1].set_ylabel('Angle\n[deg]')
axes[2].set_ylabel('Angular Rate\n[deg/s]')
fig = axes[0].figure
fig.set_size_inches((6.0, 6.0/golden_ratio))
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'pd-simulation.png'), dpi=300)
