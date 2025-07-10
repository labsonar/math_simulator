import argparse
import time
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib as tikz

import lps_utils.quantities as lps_qty
import lps_synthesis.propagation.channel as lps_channel
import lps_synthesis.propagation.channel_description as lps_desc
import lps_synthesis.propagation.layers as lps_layer

def get_channel(depth: lps_qty.Distance,
                seabed: lps_layer.SeabedType,
                source_depths = [lps_qty.Distance.m(d) for d in np.arange(3, 21, 3)],
                n_points: int = 400,
                seed = None,
                speed_sweep = lps_qty.Speed.m_s(0)) -> lps_channel.Channel:
    desc = lps_desc.Description()

    desc.add(lps_qty.Distance.m(0), lps_qty.Speed.m_s(1500))
    desc.add(depth - lps_qty.Distance.m(1), lps_qty.Speed.m_s(1500) + speed_sweep)
    if seabed is None:
        desc.add(depth, lps_layer.AcousticalLayer())
    else:
        desc.add(depth, lps_layer.Seabed(seabed, seed=seed))

    return lps_channel.Channel(description = desc,
                    sensor_depth = depth - lps_qty.Distance.m(5),
                    source_depths = source_depths,
                    max_distance = lps_qty.Distance.m(200),
                    max_distance_points = (n_points + 1),
                    sample_frequency = lps_qty.Frequency.khz(16))


if __name__ == "__main__":
    seabed_choices = [e.name.lower() for e in lps_layer.SeabedType]

    parser = argparse.ArgumentParser(
            description="Gera um canal acústico com profundidade especificada."
        )
    parser.add_argument("depth", type=float, help="Profundidade do canal em metros")
    parser.add_argument(
        "--seabed",
        type=str,
        choices=seabed_choices,
        default=None,
        help=f"Tipo de fundo marinho opcional: {', '.join(seabed_choices)}"
    )
    parser.add_argument("--performance_test", action="store_true",
                    help="print the time to get the channel response along the number of points")

    args = parser.parse_args()

    seabed_enum = lps_layer.SeabedType[args.seabed.upper()] if args.seabed is not None else None
    depth = lps_qty.Distance.m(args.depth)


    if args.performance_test:
        point_list = [1, 5, 10, 50, 100, 500, 1000]
        times = []

        print("Benchmarking tempo de execução para diferentes valores de n_points:")
        for n in point_list:
            start = time.time()
            get_channel(depth,
                        seabed_enum,
                        n_points=n,
                        speed_sweep = lps_qty.Speed.m_s(0.2),
                        source_depths=[lps_qty.Distance.m(3)])
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"n_points = {n:4d} | tempo = {elapsed:.4f} segundos")

        point_array = np.array(point_list)
        times_array = np.array(times)
        relative_times = times_array / times_array.min()

        np.savez("./result/channel_allocator_data.npz",
             point_list=point_array,
             times=times_array,
             relative_times=relative_times)


        plt.figure()
        plt.plot(point_array, relative_times, marker='o', linestyle='-')
        plt.xlabel("n_points")
        plt.ylabel("Fator de tempo (relativo)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("./result/channel_allocator.png")
        tikz.save("./result/channel_allocator.tex")
        plt.close()

    else:
        get_channel(depth, seabed_enum)
