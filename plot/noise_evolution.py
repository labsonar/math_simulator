""" Example of evolution of noise
"""
import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tikzplotlib

import lps_utils.quantities as lps_qty
import lps_sp.acoustical.broadband as lps_bb
import lps_sp.signal as lps_signal
import lps_sp.acoustical.analysis as lps_acoustic
import lps_synthesis.scenario.dynamic as lps_dynamic
import lps_synthesis.scenario.noise_source as lps_noise
import lps_synthesis.scenario.sonar as lps_sonar
import lps_synthesis.propagation.layers as lps_layer
import lps_synthesis.environment.environment as lps_env

import channel_allocator

def _eval_speed_conditions(ship: lps_noise.Ship, fs: lps_qty.Frequency, output_dir: str) -> None:

    speed_factors = [20, 80, 100, 120]
    cruise_speed = ship.propulsion.cruise_speed
    ref_state = ship.ref_state
    ship.ref_state.velocity.y = lps_qty.Speed.kt(0)
    ship.ref_state.acceleration.x = lps_qty.Acceleration.m_s2(0)
    ship.ref_state.acceleration.y = lps_qty.Acceleration.m_s2(0)

    plt.figure(figsize=(10, 6))
    cmap = cm.get_cmap("viridis", len(speed_factors))

    for i, speed_factor in enumerate(speed_factors):
        ship.ref_state.velocity.x = cruise_speed * (speed_factor/100)

        ship.move(lps_qty.Time.s(1), 15)

        bb_noise, speeds = ship.propulsion.generate_broadband_noise(fs)

        if i == 0:
            lps_signal.save_normalized_wav(bb_noise,
                                        fs,
                                        os.path.join(output_dir, f"speed_{speed_factor}.wav"))

        f_bb, i_bb = lps_bb.psd(bb_noise, fs=fs.get_hz())

        label = f"{speed_factor:.1f}% cruise speed"
        plt.plot(f_bb, i_bb, label=label, color=cmap(i))


        modulated_noise, _ = ship.propulsion.modulate_noise(broadband=bb_noise,
                                                         speeds=speeds,
                                                         fs=fs)

        lps_signal.save_normalized_wav(modulated_noise,
                                    fs,
                                    os.path.join(output_dir, f"mod_speed_{speed_factor}.wav"))

        ship.reset()

    ship.ref_state = ref_state

    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD [dB]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "speed_psd_comparison.png"), dpi=300)
    plt.close()

def _eval_modulation_conditions(ship: lps_noise.Ship,
                               fs: lps_qty.Frequency,
                               output_dir: str) -> None:

    ref_blade = ship.propulsion.n_blades
    ref_state = ship.ref_state
    ship.ref_state.velocity.x = ship.propulsion.cruise_speed
    ship.ref_state.velocity.y = lps_qty.Speed.kt(0)
    ship.ref_state.acceleration.x = lps_qty.Acceleration.m_s2(0)
    ship.ref_state.acceleration.y = lps_qty.Acceleration.m_s2(0)

    for n_blades in range(3, 7):
        ship.propulsion.n_blades = n_blades

        ship.move(lps_qty.Time.s(1), 15)

        noise = ship.propulsion.generate_noise(fs)

        lps_signal.save_normalized_wav(noise,
                                    fs,
                                    os.path.join(output_dir, f"n_blades_{n_blades}.wav"))

        ship.reset()

    ship.propulsion.n_blades = ref_blade
    ship.ref_state = ref_state


def main() -> None:
    """App main's function. """

    output_dir = "./result/noise_evolution"
    os.makedirs(output_dir, exist_ok=True)

    fs = lps_qty.Frequency.khz(16)
    seed = 42

    ships = []

    for ship_type in [lps_noise.ShipType.BULKER, lps_noise.ShipType.FISHING]:

        ships.append(lps_noise.Ship.by_type(ship_type, seed))

    #     ship_dir = os.path.join(output_dir, "speed", str(ship_type))
    #     os.makedirs(ship_dir, exist_ok=True)
    #     _eval_speed_conditions(ships[-1], fs, ship_dir)

    # blade_dir = os.path.join(output_dir, "n_blades")
    # os.makedirs(blade_dir, exist_ok=True)
    # _eval_modulation_conditions(ships[0], fs, blade_dir)

    ships[0].ref_state.position.x = lps_qty.Distance.m(-120)
    ships[0].ref_state.position.y = lps_qty.Distance.m(50)
    ships[-1].ref_state.position.x = lps_qty.Distance.m(-180)
    ships[-1].ref_state.position.y = lps_qty.Distance.m(-50)

    hydrophone = lps_sonar.Sonar.hydrophone(
            sensitivity = lps_qty.Sensitivity.db_v_p_upa(-150),
            signal_conditioner = lps_sonar.IdealAmplifier(40),
        )
    hydrophone.ref_state.velocity.x = lps_qty.Speed.kt(0)

    sonar = lps_sonar.Sonar.cylindrical(
        n_staves = 36,
        radius = lps_qty.Distance.m(1),
        sensitivity = lps_qty.Sensitivity.db_v_p_upa(-150),
        signal_conditioner = lps_sonar.IdealAmplifier(60),
    )
    sonar.ref_state.velocity.x = lps_qty.Speed.kt(0)

    # depths = [20, 30, 40, 50, 100]
    depths = [30]
    # seabeds = list(lps_layer.SeabedType)
    seabeds = [lps_layer.SeabedType.SAND]
    env = lps_env.Environment.random(seed=seed)
    # env = None

    if env is None:
        env_label = ""
    else:
        env_label = "_env"

    hydrophone.move(lps_qty.Time.s(1), 40)
    sonar.move(lps_qty.Time.s(1), 40)
    for ship in ships:
        ship.move(lps_qty.Time.s(1), 40)

        # for depth in depths:
        #     for seabed in seabeds:

        #         channel = channel_allocator.get_channel(lps_qty.Distance.m(depth),
        #                                                 seabed)

        #         noise = hydrophone._calculate_sensor_signal(
        #                 sensor = hydrophone.sensors[0],
        #                 noise_compiler = lps_noise.NoiseCompiler([ship], fs),
        #                 channel = channel,
        #                 environment = env,
        #                 without_digitalization=True
        #             )

        #         com_dir = os.path.join(output_dir, "depth", str(seabed), ship.get_id())
        #         os.makedirs(com_dir, exist_ok=True)
        #         lps_signal.save_normalized_wav(
        #                 noise,
        #                 fs,
        #                 os.path.join(com_dir, f"{depth}{env_label}.wav")
        #             )

        #         lps_acoustic.SpectralAnalysis.LOFAR.plot(
        #                 filename = os.path.join(com_dir, f"{depth}{env_label}.png"),
        #                 data = noise,
        #                 fs = int(fs.get_hz()),
        #                 params = lps_acoustic.Parameters(
        #                         n_spectral_pts = 4096,
        #                     ),
        #                 integration = lps_acoustic.TimeIntegration(True, 1, 0.5),
        #                 frequency_in_x_axis = True,
        #                 # colormap: color.Colormap = plt.get_cmap('jet')
        #             )

        #         # lps_bb.plot_psd(filename=os.path.join(depth_dir, f"{label}_psd.png"),
        #         #                 noise=noise,
        #         #                 fs=fs)


    channel = channel_allocator.get_channel(lps_qty.Distance.m(depths[0]),
                                            seabeds[0])

    # lps_dynamic.Element.plot_trajectories([hydrophone, *ships],
    #                                       os.path.join(output_dir, "scenario_trajetorie.png"))

    # lps_dynamic.Element.relative_distance_plot(hydrophone, ships,
    #                                       os.path.join(output_dir, "scenario_rel_distance.png"))


    # noise = hydrophone._calculate_sensor_signal(
    #         sensor = hydrophone.sensors[0],
    #         noise_compiler = lps_noise.NoiseCompiler(ships, fs),
    #         channel = channel,
    #         environment = env,
    #         without_digitalization=True
    #     )

    # com_dir = os.path.join(output_dir, "compiled")
    # os.makedirs(com_dir, exist_ok=True)
    # lps_signal.save_normalized_wav(
    #         noise,
    #         fs,
    #         os.path.join(com_dir, f"hydrophone{env_label}.wav")
    #     )

    # lps_acoustic.SpectralAnalysis.LOFAR.plot(
    #         filename = os.path.join(com_dir, f"hydrophone{env_label}.png"),
    #         data = noise,
    #         fs = int(fs.get_hz()),
    #         params = lps_acoustic.Parameters(
    #                 n_spectral_pts = 4096,
    #             ),
    #         integration = lps_acoustic.TimeIntegration(True, 1, 0.5),
    #         frequency_in_x_axis = True,
    #         # colormap: color.Colormap = plt.get_cmap('jet')
    #     )


    noise = sonar.get_data(
            noise_compiler = lps_noise.NoiseCompiler(ships, fs),
            channel = channel,
            environment = env,
        )

    sonar_dir = os.path.join(output_dir, "sonar")
    os.makedirs(sonar_dir, exist_ok=True)
    lps_signal.save_wav(
            noise,
            fs,
            os.path.join(sonar_dir, f"sonar{env_label}.wav")
        )


if __name__ == "__main__":
    main()
