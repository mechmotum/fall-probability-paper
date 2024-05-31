import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from bisect import bisect_left

EXAMPLE_DATA_OFF = os.path.join("data", "example_data_balance_assist_off.parquet")
EXAMPLE_DATA_ON = os.path.join("data", "example_data_balance_assist_on.parquet")
TRACKING_FORCE = 3
DESIRED_FORCES = ["desforce13", "desforce24"]
ALL_FORCES = ["force1", "force2", "force3", "force4"] + DESIRED_FORCES
DURATION_BEFORE = 0.3
DURATION_AFTER = 2.0
DIRECTORY = "figures"
HANLDEBAR_LENGTH = 0.82


def main():
    """Load example time series data from ./data and generate figures."""
    data_on = pd.read_parquet(EXAMPLE_DATA_ON)
    perturbation_dfs_on = get_perturbations(
        data_on, DESIRED_FORCES, DURATION_BEFORE, DURATION_AFTER
    )
    data_off = pd.read_parquet(EXAMPLE_DATA_OFF)
    perturbation_dfs_off = get_perturbations(
        data_off, DESIRED_FORCES, DURATION_BEFORE, DURATION_AFTER
    )
    perturbation_dfs = perturbation_dfs_on + perturbation_dfs_off
    generate_force_torque_plots(perturbation_dfs[:1], DIRECTORY, ALL_FORCES)
    generate_roll_steer_plots(perturbation_dfs, DIRECTORY)


def get_perturbations(
    data,
    DESIRED_FORCES,
    duration_before,
    duration_after,
):
    """Returns each perturbation in a new dataframe. Flips the direction of the
    roll angle and steer rate such that there is no difference between clockwise
    and counterclockwise.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing time series data of the experiment.
    DESIRED_FORCES : List[str]
        Names of the force column headers in the dataframe.
    duration_before : float
        Duration in seconds before the perturbation is applied that should be included.
    duration_after : float
        Duration in seconds after the perurbation has ended that should be included.

    Returns
    -------
    df_list : List[pd.DataFrame]
        List of dataframes where the direction is normalized for the perturbations.
    """
    start_indices, stop_indices = get_perturbation_indices(data, DESIRED_FORCES)
    context_start_indices, context_stop_indices = get_context_around_perturbation(
        data, start_indices, stop_indices, duration_before, duration_after
    )

    perturbation_dfs = []
    for i, _ in enumerate(start_indices):
        start = start_indices[i]
        context_start = context_start_indices[i]
        context_stop = context_stop_indices[i]

        pert_data = pd.DataFrame()
        start_time = data.loc[start, "seconds_since_start"]
        pert_data["seconds_since_start"] = (
            data["seconds_since_start"][context_start:context_stop] - start_time
        )

        for var in data.columns.values:
            if var == "seconds_since_start":
                continue

            if "steer" in var or "roll" in var or "gyro" in var:
                pert_data[var + "_orginal"] = data[var][context_start:context_stop]
                if data["desforce24"][start] > TRACKING_FORCE:
                    pert_data[var] = -data[var][context_start:context_stop]
                else:
                    pert_data[var] = data[var][context_start:context_stop]
            else:
                pert_data[var] = data[var][context_start:context_stop]

        perturbation_dfs.append(pert_data)

    return perturbation_dfs


def generate_force_torque_plots(perturbation_dfs, directory, force_column_names):
    """Generates a plot showing the four forces on the handlebars and the torque
    applied by these four forces as a function of time.

    Parameters
    ----------
    perturbation_dfs : List[pandas.DataFrame]
        A list of dataframes that contain the data to be plotted.
    directory : str
        Name of the directory in which to store the generated images.
    force_column_names : List[str]
        A list containing the names of the columns to include in the plot.
    """
    if not os.path.isdir(directory):
        os.mkdir(directory)

    for i, df in enumerate(perturbation_dfs):
        fig, axs = plt.subplots(2, 1, sharex=True, layout='constrained')
        fig.set_size_inches(140/25.4, 80/25.4)

        df.plot(x="seconds_since_start", y=force_column_names, ax=axs[0],
                grid=True)

        actual_torque, desired_torque = calculate_torque_on_handlebars(df)
        axs[1].plot(
            df["seconds_since_start"],
            actual_torque,
            label="Measured net torque on handlebars",
        )
        axs[1].plot(
            df["seconds_since_start"],
            desired_torque,
            label="Desired net torque on handlebars",
        )

        fig.suptitle(get_figure_title(df))
        axs[0].set_ylabel("Force [N]")
        axs[0].legend(
            [
                "Motor 1",
                "Motor 2",
                "Motor 3",
                "Motor 4",
                "Desired motor 1 and 3",
                "Desired motor 2 and 4",
            ],
            fontsize='x-small'
        )
        axs[1].set_xlabel("Time relative to start of perturbation [s]")
        axs[1].set_ylabel("Torque [Nm]")
        axs[1].legend(fontsize='x-small')
        axs[1].grid()

        filename = os.path.join(directory, "perturbation_" + str(i))
        fig.savefig(fname=filename, dpi=300, bbox_inches="tight")
        print(f"Saved plot with name {filename}")
        plt.close()


def generate_roll_steer_plots(perturbation_dfs, directory):
    """Plots all the perturbations in one plot.

    Parameters
    ----------
    data : List[pd.DataFrame]
        List of dataframes that should be plotted.
    directory : str
        Name of the directory in which to store the generated images.
    """
    if not os.path.isdir(directory):
        os.mkdir(directory)

    fig, axs = plt.subplots(2, 1, sharex=True)
    fig.set_size_inches(10, 6)

    for df in perturbation_dfs:
        if "motor_current" in df.columns:
            color = "lightsteelblue"
        else:
            color = "lightcoral"

        if pd.Series.max(abs(df["roll_angle"])) < 500:
            df.plot(
                x="seconds_since_start",
                y="roll_angle",
                color=color,
                ax=axs[0],
                alpha=0.5,
            )
            df.plot(
                x="seconds_since_start",
                y="steer_rate",
                color=color,
                ax=axs[1],
                alpha=0.5,
                legend=False,
            )

    legend_elements = [
        Line2D([0], [0], color="lightsteelblue", lw=4, label="Balance-assist ON"),
        Line2D([0], [0], color="lightcoral", lw=4, label="Balance-assist OFF"),
    ]
    axs[0].legend(handles=legend_elements)

    for i in [0, 1]:
        axs[i].axvline(x=0, color="k")
        axs[i].axvline(x=0.3, color="k")
        axs[i].grid()

    axs[0].set_ylabel("Roll angle [deg]")
    axs[1].set_ylabel("Steer rate [deg/s]")
    axs[1].set_xlabel("Time relative to start of perturbation [s]")
    fig.suptitle(
        "Roll angle and steer rate for all perturbations applied to one participant."
    )

    filename = os.path.join(directory, "roll_steer_overlay")
    fig.savefig(fname=filename, dpi=300, bbox_inches="tight")
    print(f"Saved plot with name {filename}")
    plt.close()


def calculate_torque_on_handlebars(data):
    """Calculates the torque on the handlebars applied by the bumpem system.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing the force data.

    Returns
    -------
    actual_torque : pd.Series
        Net torque that the bump'em system applies to the handlebars.
    desired_torque : pd.Series
        Net torque that should be applied to the handlebars.
    """
    desired_torque = (
        (data["desforce24"] - data["desforce13"]) * 2 * (HANLDEBAR_LENGTH / 2)
    )

    force_right = data["force2"] - data["force3"]
    force_left = data["force4"] - data["force1"]

    net_force = force_right + force_left
    actual_torque = net_force * (HANLDEBAR_LENGTH / 2)
    return actual_torque, desired_torque


def get_figure_title(data):
    """Generate a title based on the direction and magnitude of the perturbation.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing the data for which to generate the figure.

    Returns
    -------
    str
        Generated title for the figure.
    """
    max13 = data["desforce13"].max()
    max24 = data["desforce24"].max()
    if max13 > max24:
        direction = "Clockwise"
        max = max13
    else:
        direction = "Counterclockwise"
        max = max24

    return direction + " perturbation of " + str(max) + " N"


def get_perturbation_indices(data, column_names):
    """Returns the beginning and end indices of blocks of data that are above the tracking
    force.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing the data in which to find the start and stop indices.
    column_name : str
        Column of the dataframe that should be analysed.

    Returns
    -------
    start_indices : List[int]
        List containing start indices.
    stop_indices : List[int]
        List containing stop indicies.
    """
    start_indices = []
    stop_indices = []

    for column_name in column_names:
        start_index = 0
        while True:
            df_shortened = data[start_index:]
            if df_shortened[df_shortened[column_name] > TRACKING_FORCE].empty:
                break

            tmp_start_index = (
                df_shortened[df_shortened[column_name] > TRACKING_FORCE].iloc[0].name
            )
            df_shortened = data[tmp_start_index:]

            try:
                tmp_stop_index = (
                    df_shortened[df_shortened[column_name] == TRACKING_FORCE]
                    .iloc[0]
                    .name
                )
            except Exception as e:
                print(e)
                tmp_stop_index = df_shortened.tail(1).index.values[0]
                break

            start_index = tmp_stop_index
            if tmp_stop_index - tmp_start_index > 30:  # filter logging errors
                start_indices.append(tmp_start_index)
                stop_indices.append(tmp_stop_index)

    start_indices.sort()
    stop_indices.sort()

    return start_indices, stop_indices


def get_context_around_perturbation(
    data,
    start_indices,
    stop_indices,
    duration_before,
    duration_after,
):
    """Returns the indices of the dataframe for `duration` seconds before and after the
    perturbation.

    Parameters
    ----------
    start_indices : List[int]
        List containing the indices of the dataframe at which a perturbation starts.
    stop_indices : List[int]
        List containing the indices of the dataframe at which a perturbation stops.
    duration_before : float
        Amount of time that should be between the original start indice and the new start indice
    duration_after : float
        Amount of time that should be between the original stop indice and the new stop indice

    Returns
    -------
    new_start_indices : List[int]
        List containing the start indices that are `duration` before the perturbation.
    new_stop_indices : List[int]
        List containing the stop indices that are `duration` after the perturbation.
    """
    new_start_indices = []
    new_stop_indices = []

    for i, value in enumerate(start_indices):
        pert_start_time = data["seconds_since_start"][start_indices[i]]
        pert_stop_time = data["seconds_since_start"][stop_indices[i]]
        context_start = find_closest_timestamp(
            pert_start_time - duration_before, data["seconds_since_start"]
        )
        context_stop = find_closest_timestamp(
            pert_stop_time + duration_after, data["seconds_since_start"]
        )

        new_start_indices.append(
            data[data["seconds_since_start"] == context_start].index.values[0]
        )
        new_stop_indices.append(
            data[data["seconds_since_start"] == context_stop].index.values[0]
        )

    return new_start_indices, new_stop_indices


def find_closest_timestamp(time: float, series: pd.Series) -> float:
    """Returns the closest time to `time` in `series`.

    Parameters
    ----------
    time : float
        Time to search for.
    series: pandas.Series
        Series containing timestamps.

    Returns
    -------
    float
        Closest time to `time` in `series`.
    """
    index = bisect_left(series, time)
    if index == 0:
        return series.head(1).values[0]

    if index == len(series):
        return series.tail(1).values[0]

    before = series[index - 1]
    after = series[index + 1]

    if after - time < time - before:
        return after
    else:
        return before


if __name__ == "__main__":
    main()
