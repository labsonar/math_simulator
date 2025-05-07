""" Example of use of scenario module
"""
import os
import time

import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib as tikz
import scipy.io.wavfile as sci_wave
import scipy.signal as sci_sig

import lps_utils.quantities as lps_qty
import lps_synthesis.scenario.dynamic as lps_dynamic
import lps_synthesis.scenario.scenario as lps_scenario
import lps_synthesis.scenario.sonar as lps_sonar
import lps_synthesis.environment.environment as lps_env
import lps_synthesis.propagation.channel as lps_channel

lps_channel.DEFAULT_DIR = "./lps_libraries/acoustic_synthesis/result/propagation"


def main() -> None:

    output_dir = "./plot/scenario_1"
    os.makedirs(output_dir, exist_ok=True)

    values = []
    # for sea_value in [lps_env.Sea.STATE_0, lps_env.Sea.STATE_2, lps_env.Sea.STATE_4]:
    #     values.append([sea_value, lps_env.Rain.NONE, str(sea_value)])

    for rain_value in lps_env.Rain:
        values.append([lps_env.Sea.STATE_0, rain_value, str(rain_value)])

    for sea_value, rain_value, label in values:

        environment = lps_env.Environment(rain_value=rain_value,
                                        sea_value=sea_value,
                                        shipping_value=lps_env.Shipping.LEVEL_2)
        channel = lps_channel.PredefinedChannel.BASIC.get_channel()
        sample_frequency = lps_qty.Frequency.khz(16)

        scenario = lps_scenario.Scenario(channel = channel,
                                        environment = environment)

        sonar = lps_sonar.Sonar.hidrofone(
                sensitivity=lps_qty.Sensitivity.db_v_p_upa(-165),
                initial_state=lps_dynamic.State(
                        position = lps_dynamic.Displacement(
                                lps_qty.Distance.m(0),
                                lps_qty.Distance.m(0)))
        )

        scenario.add_sonar("main", sonar)


        ship1 = lps_scenario.Ship(
                        ship_id="Navio 1",
                        propulsion=lps_scenario.CavitationNoise(
                            ship_type=lps_scenario.ShipType.PASSENGER,
                            n_blades=4,
                            n_shafts=1,
                        ),
                        max_speed=lps_qty.Speed.kt(15),
                        draft=lps_qty.Distance.m(100),
                        initial_state=lps_dynamic.State(
                                position = lps_dynamic.Displacement(
                                        lps_qty.Distance.km(-0.05),
                                        lps_qty.Distance.km(0.8)),
                                velocity = lps_dynamic.Velocity(
                                        lps_qty.Speed.kt(15),
                                        lps_qty.Speed.kt(0))
                        )
                )

        scenario.add_noise_container(ship1)

        scenario.simulate(lps_qty.Time.s(1), 10)

        scenario.geographic_plot(os.path.join(output_dir,"geographic.png"))
        scenario.geographic_plot(os.path.join(output_dir,"geographic.tex"))
        scenario.relative_distance_plot(os.path.join(output_dir,"distance.png"))
        scenario.relative_distance_plot(os.path.join(output_dir,"distance.tex"))
        scenario.velocity_plot(os.path.join(output_dir,"velocity.png"))
        scenario.velocity_plot(os.path.join(output_dir,"velocity.tex"))
        scenario.relative_velocity_plot(os.path.join(output_dir,"relative_velocity.png"))
        scenario.relative_velocity_plot(os.path.join(output_dir,"relative_velocity.tex"))


        output_wav = os.path.join(output_dir, f"{label}.wav")

        if os.path.exists(output_wav):
            _, signal = sci_wave.read(output_wav)

        else:
            start_time = time.time()
            signal = scenario.get_sonar_audio("main", fs=sample_frequency)
            end_time = time.time()
            print("Get audio time: ", end_time-start_time)

            sci_wave.write(output_wav, int(sample_frequency.get_hz()), signal)

        float_signal = signal.astype(np.float32) / (2**15 -1)
        if len(float_signal.shape) != 1:
            float_signal = float_signal[:,0]
        f, t, s = sci_sig.spectrogram(float_signal, fs=sample_frequency.get_hz(), nperseg=2048)

        aux = 20 * np.log10(np.clip(s, 1e-10, None))
        aux = aux - np.max(aux)
        plt.figure(figsize=(10, 6))
        plt.pcolormesh(t, f/1e3, aux, shading='gouraud')
        plt.ylabel('Frequência (kHz)')
        plt.xlabel('Tempo (s)')
        cbar = plt.colorbar(label="Intensidade (dB)")
        cbar.ax.yaxis.set_label_position('left')
        plt.savefig(os.path.join(output_dir, f"{label}.png"))
        tikz.save(os.path.join(output_dir, f"{label}.tex"))
        plt.close()


if __name__ == "__main__":
    main()
