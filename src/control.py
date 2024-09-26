import os

from bicycleparameters.parameter_sets import Meijaard2007ParameterSet
from bicycleparameters.bicycle import sort_eigenmodes
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import golden_ratio

from data import bike_with_rider, bike_without_rider
from model import SteerControlModel

SCRIPT_PATH = os.path.realpath(__file__)
SRC_DIR = os.path.dirname(SCRIPT_PATH)
ROOT_DIR = os.path.realpath(os.path.join(SRC_DIR, '..'))
FIG_DIR = os.path.join(ROOT_DIR, 'figures')
KPH2MPS = 1000.0/3600.0
MPS2KPH = 1.0/KPH2MPS

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
vmin, vmin_idx = 1.5, np.argmin(np.abs(speeds - 1.5))
vmax, vmax_idx = 4.7, np.argmin(np.abs(speeds - 4.7))
static_gain = 10.0
kphidots = -static_gain*(vmax - speeds)
kphidots[:vmin_idx] = -static_gain*(vmax - vmin)/vmin*speeds[:vmin_idx]
kphidots[vmax_idx:] = 0.0

# FIGURE : Plot the roll rate gains versus speed.
fig, ax = plt.subplots(layout='constrained')
fig.set_size_inches((80/25.4, 80/25.4/golden_ratio))
ax.plot(speeds, kphidots)
ax.set_ylabel(r'$k_\dot{\phi}$')
fig.savefig(os.path.join(FIG_DIR, 'gains-vs-speed.png'), dpi=300)

# FIGURE : Compare eigenvalues vs speed for uncontrolled.


def stable_ranges(evals):
    # TODO : This should return the indice after a rise and before a fall. It
    # now always returns the indices after a rise or fall.
    where_stable = np.all(evals.real < 0.0, axis=1)
    padded = np.hstack(([False], where_stable, [False]))
    start_stop_idxs = np.flatnonzero(np.diff(padded))
    return start_stop_idxs.reshape(-1, 2)


fig_four, axes = plt.subplots(2, 2, sharex=True, sharey=True,
                              layout='constrained')
fig.set_size_inches((160/25.4, 160/25.4/golden_ratio))


def plot_eig(ax, model, kphidots=0.0):
    evals_, evecs_ = sort_eigenmodes(*model.calc_eigen(v=speeds,
                                                       kphidot=kphidots))
    weave_idx, capsize_idx = stable_ranges(evals_)[0]
    weave_speed, capsize_speed = speeds[weave_idx], speeds[capsize_idx]
    msg = 'Weave speed: {:1.2f} [m/s], {:1.1f} [km/h]'
    print(msg.format(weave_speed, weave_speed*MPS2KPH))
    msg = 'Capsize speed: {:1.2f} [m/s], {:1.1f} [km/h]'
    print(msg.format(capsize_speed, capsize_speed*MPS2KPH))
    ax.axvline(6.0*KPH2MPS, ymin=-10.0, ymax=10.0, color='black', linestyle=':')
    ax.axvline(10.0*KPH2MPS, ymin=-10.0, ymax=10.0, color='black', linestyle='-.')
    model.plot_eigenvalue_parts(ax=ax, v=speeds, kphidot=kphidots,
                                hide_zeros=True, colors=['k']*4)
    ax.set_ylim((-10, 10))
    return ax


msg = 'Without rigid rider and balance assist off:'
print(msg)
print("-"*len(msg))
ax = plot_eig(axes[0, 0], model_without)
sax = ax.secondary_xaxis('top', functions=(lambda x: x*MPS2KPH,
                                           lambda x: x*KPH2MPS))
sax.set_xlabel('Speed [km/h]')
ax.set_title('Without Rigid Rider')
ax.set_ylabel('Balance Assist Off\nEigenvalue Components\n[1/s]')
ax.set_xlabel('')

msg = '\nWithout rigid rider and balance assist on:'
print(msg)
print("-"*len(msg))
ax = plot_eig(axes[1, 0], model_without, kphidots=kphidots)
ax.set_ylabel('Balance Assist On\nEigenvalue Components\n[1/s]')
ax.set_xlabel('Speed [m/s]')

msg = '\nWith rigid rider and balance assist off:'
print(msg)
print("-"*len(msg))
ax = plot_eig(axes[0, 1], model_with)
sax = ax.secondary_xaxis('top', functions=(lambda x: x*MPS2KPH,
                                           lambda x: x*KPH2MPS))
sax.set_xlabel('Speed [km/h]')
ax.set_title('With Rigid Rider')
ax.set_ylabel('')
ax.set_xlabel('')

msg = '\nWith rigid rider and balance assist on:'
print(msg)
print("-"*len(msg))
ax = plot_eig(axes[1, 1], model_with, kphidots=kphidots)
ax.set_ylabel('')
ax.set_xlabel('Speed [m/s]')

fig_four.savefig(os.path.join(FIG_DIR, 'balance-assist-eig-vs-speeds.png'),
                 dpi=300)


# FIGURE : Simulate an initial value problem at a low speed under control.
idx = np.argmin(np.abs(speeds - 6.0*KPH2MPS))  # 6 km/h
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
