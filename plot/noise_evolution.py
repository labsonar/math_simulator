""" Script to explore noise evolution through the process chain
"""
import argparse
import os
import tqdm

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tikzplotlib as tikz

import lps_utils.quantities as lps_qty
import lps_sp.acoustical.broadband as lps_bb
import lps_sp.signal as lps_signal
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

    for i, speed_factor in enumerate(tqdm.tqdm(speed_factors, desc="Speed test", ncols=120)):
        ship.ref_state.velocity.x = cruise_speed * (speed_factor/100)

        ship.move(lps_qty.Time.s(1), 120)

        bb_noise, speeds = ship.propulsion.generate_broadband_noise(fs)

        if i == 0:
            lps_signal.save_normalized_wav(
                bb_noise,
                fs,
                os.path.join(output_dir, f"{ship.get_id()}_speed_bb_noise.wav"))

        modulated_noise, _ = ship.propulsion.modulate_noise(broadband=bb_noise,
                                                         speeds=speeds,
                                                         fs=fs)


        lps_signal.save_normalized_wav(
            modulated_noise,
            fs,
            os.path.join(output_dir, f"{ship.get_id()}_speed_{speed_factor:.0f}%.wav"))

        ship.reset()


        f_bb, i_bb = lps_bb.psd(modulated_noise, fs=fs.get_hz())

        label = f"{speed_factor:.1f}% cruise speed"
        plt.plot(f_bb[:-2], i_bb[:-2], label=label, color=cmap(i))


    ship.ref_state = ref_state

    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD [dB]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{ship.get_id()}_speed_psd_comparison.png"), dpi=300)
    tikz.save(os.path.join(output_dir, f"{ship.get_id()}_speed_psd_comparison.tex"))
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

    for n_blades in tqdm.tqdm(range(3, 7), desc="Blade test", ncols=120):
        ship.propulsion.n_blades = n_blades

        ship.move(lps_qty.Time.s(1), 120)

        noise = ship.propulsion.generate_noise(fs)

        lps_signal.save_normalized_wav(
            noise,
            fs,
            os.path.join(output_dir, f"{ship.get_id()}_{n_blades}_blades.wav"))

        ship.reset()

    ship.propulsion.n_blades = ref_blade
    ship.ref_state = ref_state

def _get_complete_name(args, add_str: str = "") -> str:

    env_label = "_env" if args.with_environment else ""

    if args.step_duration != 1.0 or args.n_steps != 40:
        comp = f"_[{args.step_duration}:{args.n_steps}]"
    else:
        comp = ""

    return f"out{env_label}{comp}{add_str}.wav"

def _parse_args():
    parser = argparse.ArgumentParser(description="Simulate and export ship noise evolution")

    parser.add_argument("--with-environment", action="store_true",
                        help="Use a random environment (default: False)")
    parser.add_argument("--run_speed_test", action="store_true",
                        help="Export noise varying ship speed")
    parser.add_argument("--run_blade_test", action="store_true",
                        help="Export noise varying number of blades")
    parser.add_argument("--run_channel_test", action="store_true",
                        help="Export with variable channel estimation resolution")
    parser.add_argument("--run_ss_test", action="store_true",
                        help="Run export sound speed test")
    parser.add_argument("--run_depth_test", action="store_true",
                        help="Export with multiple source depths")
    parser.add_argument("--vary-depth", action="store_true",
                        help="Export with multiple depths")
    parser.add_argument("--vary-seabed", action="store_true",
                        help="Export with multiple seabeds")
    parser.add_argument("--each-ship-signal", action="store_true",
                        help="Export hydrophone noise per ship")
    parser.add_argument("--both-ship-signals", action="store_true",
                        help="Export hydrophone noise for both ships")
    parser.add_argument("--export-trajectories", action="store_true",
                        help="Plot trajectories and distances")
    parser.add_argument("--export-trajectories-tex", action="store_true",
                        help="Plot trajectories and distances")
    parser.add_argument("--export-complete", action="store_true",
                        help="Export complete signal from all ships")
    parser.add_argument("--use-sonar", action="store_true",
                        help="Use circular sonar instead of hydrophone")
    parser.add_argument("--output-dir", type=str, default="./result/noise_evolution",
                        help="Output directory")
    parser.add_argument("--step-duration", type=float, default=1.0,
                        help="Duration of each simulation step in seconds (default: 1.0)")
    parser.add_argument("--n-steps", type=int, default=40,
                        help="Number of simulation steps (default: 40)")

    return parser.parse_args()

def main():
    """App main's function. """
    args = _parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    fs = lps_qty.Frequency.khz(16)
    seed_base = 42

    ships = [
        lps_noise.Ship.by_type(lps_noise.ShipType.BULKER, seed_base),
        lps_noise.Ship.by_type(lps_noise.ShipType.FISHING, seed_base)
    ]
    ships[0].draft = lps_qty.Distance.m(9)
    ships[-1].draft = lps_qty.Distance.m(6)

    for ship in ships:
        print("ship: ", ship.get_id())
        print("\tn_blades: ", ship.propulsion.n_blades)
        print("\tcruise_speed: ", ship.propulsion.cruise_speed.get_kt())
        print("\tcruise_rpm: ", ship.propulsion.cruise_rotacional_frequency.get_rpm())
        print("\tdraft: ", ship.draft)

    if args.run_speed_test:
        for ship in ships:
            ship_dir = os.path.join(args.output_dir, "speed_test", ship.get_id())
            os.makedirs(ship_dir, exist_ok=True)
            _eval_speed_conditions(ship, fs, ship_dir)

    if args.run_blade_test:
        for ship in ships:
            blade_dir = os.path.join(args.output_dir, "blade_test", ship.get_id())
            os.makedirs(blade_dir, exist_ok=True)
            _eval_modulation_conditions(ship, fs, blade_dir)

    if args.use_sonar:
        sensor = lps_sonar.Sonar.cylindrical(
            n_staves=36,
            radius=lps_qty.Distance.m(1),
            sensitivity=lps_qty.Sensitivity.db_v_p_upa(-150),
            signal_conditioner=lps_sonar.IdealAmplifier(60)
        )
    else:
        sensor = lps_sonar.Sonar.hydrophone(
            sensitivity=lps_qty.Sensitivity.db_v_p_upa(-150),
            signal_conditioner=lps_sonar.IdealAmplifier(40)
        )

    for ship, x, y in zip(ships, [-120, -180], [50, -50]):
        ship.ref_state.position.x = lps_qty.Distance.m(x)
        ship.ref_state.position.y = lps_qty.Distance.m(y)

    sensor.ref_state.velocity.x = lps_qty.Speed.kt(0)

    sensor.move(lps_qty.Time.s(args.step_duration), args.n_steps)
    for ship in ships:
        ship.move(lps_qty.Time.s(args.step_duration), args.n_steps)

    env = lps_env.Environment.random(seed=seed_base + 2) if args.with_environment else None
    depths = [20, 30, 40, 80] if args.vary_depth else [30]
    seabeds = list(lps_layer.SeabedType) if args.vary_seabed else [lps_layer.SeabedType.SAND]
    env_label = "_env" if env else ""

    if args.each_ship_signal or args.both_ship_signals:
        for depth in depths:
            for seabed in seabeds:
                print("seabed: ", seabed)
                channel = channel_allocator.get_channel(
                        lps_qty.Distance.m(depth),
                        seabed,
                        seed=seed_base
                    )

                if args.each_ship_signal:
                    for ship in ships:
                        noise = sensor.get_data(lps_noise.NoiseCompiler([ship], fs), channel, env)
                        out_dir = os.path.join(args.output_dir, "seabed_test")
                        os.makedirs(out_dir, exist_ok=True)

                        lps_signal.save_wav(
                            noise,
                            fs,
                            os.path.join(out_dir,
                                         f"{ship.get_id()}_{depth}_{seabed}{env_label}.wav"))

                if args.both_ship_signals:

                    noise = sensor.get_data(lps_noise.NoiseCompiler(ships, fs), channel, env)
                    out_dir = os.path.join(args.output_dir, "seabed_test")
                    os.makedirs(out_dir, exist_ok=True)

                    lps_signal.save_wav(
                        noise,
                        fs,
                        os.path.join(out_dir,
                                     f"{depth}_{seabed}{env_label}.wav"))

    if args.export_trajectories:
        lps_dynamic.Element.plot_trajectories(
            [sensor, *ships],
            os.path.join(args.output_dir, "trajectories.png")
        )
        lps_dynamic.Element.relative_distance_plot(
            sensor,
            ships,
            os.path.join(args.output_dir, "relative_distance.png")
        )
        lps_dynamic.Element.relative_speed_plot(
            sensor,
            ships,
            os.path.join(args.output_dir,"relative_speed.png")
        )

    if args.export_trajectories_tex:
        lps_dynamic.Element.plot_trajectories(
            [sensor, *ships],
            os.path.join(args.output_dir, "trajectories.tex")
        )
        lps_dynamic.Element.relative_distance_plot(
            sensor,
            ships,
            os.path.join(args.output_dir,"relative_distance.tex")
        )
        lps_dynamic.Element.relative_speed_plot(
            sensor,
            ships,
            os.path.join(args.output_dir, "relative_speed.tex")
        )

    if args.run_channel_test:
        for n_points in [4, 40, 400, 4000]:
            channel = channel_allocator.get_channel(
                    lps_qty.Distance.m(depths[0]),
                    seabeds[0],
                    n_points,
                    seed=seed_base
                )
            noise = sensor.get_data(lps_noise.NoiseCompiler(ships, fs), channel, env)
            out_dir = os.path.join(args.output_dir, "channel_resolution")
            os.makedirs(out_dir, exist_ok=True)
            lps_signal.save_wav(noise,
                                fs,
                                os.path.join(out_dir, _get_complete_name(args, f"_{n_points}pts")))

    if args.run_ss_test:
        for sweep in [-50, 50]:
            channel = channel_allocator.get_channel(
                    lps_qty.Distance.m(depths[0]),
                    seabeds[0],
                    seed=seed_base,
                    speed_sweep = lps_qty.Speed.m_s(sweep)
                )
            noise = sensor.get_data(lps_noise.NoiseCompiler(ships, fs), channel, env)
            out_dir = os.path.join(args.output_dir, "ss_test")
            os.makedirs(out_dir, exist_ok=True)
            lps_signal.save_wav(noise,
                                fs,
                                os.path.join(out_dir, _get_complete_name(args, f"_{sweep}")))

    if args.export_complete:
        channel = channel_allocator.get_channel(
                lps_qty.Distance.m(depths[0]),
                seabeds[0],
                seed=seed_base
            )

        noise = sensor.get_data(lps_noise.NoiseCompiler(ships, fs), channel, env)
        out_dir = os.path.join(args.output_dir, "complete")
        os.makedirs(out_dir, exist_ok=True)
        lps_signal.save_wav(noise, fs, os.path.join(out_dir, _get_complete_name(args)))

    if args.run_depth_test:

        for depth in range(3,21,3):

            ships[-1].draft = lps_qty.Distance.m(depth)

            # sensor.reset()
            # sensor.move(lps_qty.Time.s(args.step_duration), args.n_steps)
            # for ship in ships:
            #     ship.reset()
            #     ship.move(lps_qty.Time.s(args.step_duration), args.n_steps)

            channel = channel_allocator.get_channel(
                    lps_qty.Distance.m(depths[0]),
                    seabeds[0],
                    seed=seed_base,
                )
            noise = sensor.get_data(lps_noise.NoiseCompiler(ships, fs), channel, env)
            out_dir = os.path.join(args.output_dir, "source_depth_test")
            os.makedirs(out_dir, exist_ok=True)
            lps_signal.save_wav(noise,
                                fs,
                                os.path.join(out_dir, f"at_{depth}m.wav"))


if __name__ == "__main__":
    main()
