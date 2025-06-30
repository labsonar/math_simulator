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
import lps_synthesis.environment.environment as lps_env
import lps_synthesis.scenario.noise_source as lps_noise


def main(ship_type = lps_noise.ShipType.BULKER) -> None:
    """App main's function. """

    output_dir = f"./result/noise_evolution/{ship_type}"
    os.makedirs(output_dir, exist_ok=True)

    fs = lps_qty.Frequency.khz(16)

    speed_factors = [20, 80, 100, 120]

    n_blades = ship_type.draw_n_blades(42)
    n_shafts = ship_type.draw_n_shafts(42)
    length = ship_type.draw_length(42)
    cruise_speed = ship_type.draw_cruising_speed(42)
    cruise_rotacional_frequency = ship_type.draw_cruising_rotacional_frequency(42)
    max_speed = cruise_speed * 1.5

    print("\tcruise_speed: ", cruise_speed)
    print("\tcruise_rotacional_frequency: ", cruise_rotacional_frequency)

    noise_source = lps_noise.CavitationNoise(
            ship_type=ship_type,
            n_blades = n_blades,
            n_shafts = n_shafts,
            length = length,
            cruise_speed = cruise_speed,
            cruise_rotacional_frequency = cruise_rotacional_frequency,
            max_speed = max_speed
        )

    container = lps_noise.Ship(ship_id=str(lps_noise.ShipType.RECREATIONAL),
                               propulsion=noise_source)

    plt.figure(figsize=(10, 6))
    cmap = cm.get_cmap("viridis", len(speed_factors))

    for i, speed_factor in enumerate(speed_factors):
        container.ref_state.velocity.x = cruise_speed * (speed_factor/100)

        container.reset()
        container.move(lps_qty.Time.s(1), 15)

        bb_noise, speeds = noise_source.generate_broadband_noise(fs)

        if i == 0:
            lps_signal.save_normalized_wav(bb_noise,
                                        fs,
                                        os.path.join(output_dir, f"speed_{speed_factor}.wav"))

        f_bb, i_bb = lps_bb.psd(bb_noise, fs=fs.get_hz())

        label = f"{speed_factor:.1f}% cruise speed"
        plt.plot(f_bb, i_bb, label=label, color=cmap(i))


        modulated_noise, _ = noise_source.modulate_noise(broadband=bb_noise,
                                                         speeds=speeds,
                                                         fs=fs)

        lps_signal.save_normalized_wav(modulated_noise,
                                    fs,
                                    os.path.join(output_dir, f"mod_speed_{speed_factor}.wav"))

    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD [dB]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "speed_psd_comparison.png"), dpi=300)
    plt.close()

if __name__ == "__main__":

    for ship_type in [lps_noise.ShipType.BULKER, lps_noise.ShipType.FISHING]:
        print("ship_type: ", ship_type)
        main(ship_type)
