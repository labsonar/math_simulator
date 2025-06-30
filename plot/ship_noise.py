""" Ship Noise expected vs simulated. """
import os

import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

import lps_utils.quantities as lps_qty
import lps_sp.acoustical.broadband as lps_bb
import lps_synthesis.scenario.noise_source as lps_noise


def main() -> None:
    """App main's function. """

    output_dir = "./result/ship_noise"
    os.makedirs(output_dir, exist_ok=True)

    fs = lps_qty.Frequency.khz(16)
    duration = lps_qty.Time.s(300)
    speed = lps_qty.Speed.kt(5)
    n_samples = int(duration * fs)

    fig1, ax1 = plt.subplots(figsize=(12, 6))
    fig2, ax2 = plt.subplots(figsize=(12, 6))


    for ship in lps_noise.ShipType:

        freqs, psd = ship.to_psd(fs=fs, speed=speed)
        freqs_hz = [f.get_hz() for f in freqs]

        audio_signal = lps_bb.generate(
            frequencies=np.array(freqs_hz),
            psd_db=psd,
            n_samples=n_samples,
            fs=fs.get_hz()
        )

        est_freqs, est_psd = lps_bb.psd(signal=audio_signal,
                                        fs=fs.get_hz(),
                                        window_size=2048,
                                        overlap=0.9)

        log_freqs = np.logspace(np.log10(est_freqs[0]), np.log10(est_freqs[-2]), 500)
        simulated_psd = np.interp(log_freqs, est_freqs, est_psd)
        expected_psd = np.interp(log_freqs, freqs_hz, psd)


        label=str(ship).capitalize().replace("_", " ")
        ax1.semilogx(log_freqs, expected_psd, label=label)
        ax2.semilogx(log_freqs, simulated_psd, label=label)


    for ax in [ax1, ax2]:
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Power Spectral Density (dB ref 1 µPa @ 1m / √Hz)")
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid()


    fig1.tight_layout(rect=[0, 0, 0.75, 1])
    fig1.savefig(os.path.join(output_dir, "ships_psd.png"), bbox_inches='tight')
    tikzplotlib.save(os.path.join(output_dir, "ships_psd.tex"))

    fig2.tight_layout(rect=[0, 0, 0.75, 1])
    fig2.savefig(os.path.join(output_dir, "ships_psd_simulated.png"), bbox_inches='tight')
    tikzplotlib.save(os.path.join(output_dir, "ships_psd_simulated.tex"))

    plt.close(fig1)
    plt.close(fig2)

if __name__ == "__main__":
    main()
