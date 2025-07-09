""" Script to explore noise evolution through the process chain
"""
import argparse
import os
import tqdm
import random
import string

import numpy as np
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

def main():
    output_dir = "./result/test"

    os.makedirs(output_dir, exist_ok=True)
    fs = lps_qty.Frequency.khz(16)
    duration = lps_qty.Time.s(10)
    seed_base = 42


    rng = np.random.default_rng(seed_base)

    rng.normal()

    # noise = rng.normal(0, 1, int(duration*fs))


    ships = [
        lps_noise.Ship.by_type(lps_noise.ShipType.BULKER, seed_base),
        # lps_noise.Ship.by_type(lps_noise.ShipType.FISHING, seed_base)
    ]

    # env = lps_env.Environment.random(seed=seed_base + 2)
    env = None
    depths = [30]
    seabeds = [lps_layer.SeabedType.SAND]

    sensor = lps_sonar.Sonar.hydrophone(
        sensitivity=lps_qty.Sensitivity.db_v_p_upa(-150),
        signal_conditioner=lps_sonar.IdealAmplifier(40)
    )

    channel = channel_allocator.get_channel(lps_qty.Distance.m(depths[0]), seabeds[0], 40, seed_base)

    # for signal, depth, _ in compiler:
        # propag_noise = channel.propagate(
        #     input_data=signal,
        #     source_depth=depth,
        #     distance=[lps_qty.Distance.m(-100), lps_qty.Distance.m(100)]
        # )
        # random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        # lps_signal.save_wav(propag_noise, fs, os.path.join(output_dir, f"{random_string}.wav"))

    sensor.move(lps_qty.Time.s(1), 25)
    for ship in ships:
        ship.move(lps_qty.Time.s(1), 25)

    last = None
    while True:

        out_noise = sensor.get_data(lps_noise.NoiseCompiler(ships, fs), channel, env)

        # out_noise = channel.propagate(
        #     input_data=out_noise,
        #     source_depth=lps_qty.Distance.m(5),
        #     distance=[lps_qty.Distance.m(-100), lps_qty.Distance.m(100)]
        # )

        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        lps_signal.save_wav(out_noise, fs, os.path.join(output_dir, f"{random_string}.wav"))

        if last is None:
            last = out_noise

        if not np.allclose(last, out_noise, rtol=1e-5, atol=1e-8):
            print("noise change")
            break

        print("loop")

if __name__ == "__main__":
    main()
