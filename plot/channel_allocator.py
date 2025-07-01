import argparse
import numpy as np

import lps_utils.quantities as lps_qty
import lps_synthesis.propagation.channel as lps_channel
import lps_synthesis.propagation.channel_description as lps_desc
import lps_synthesis.propagation.layers as lps_layer

def get_channel(depth: lps_qty.Distance, seabed: lps_layer.SeabedType) -> lps_channel.Channel:
    desc = lps_desc.Description()

    desc.add(lps_qty.Distance.m(0), lps_qty.Speed.m_s(1500))
    desc.add(depth - lps_qty.Distance.m(1), lps_qty.Speed.m_s(1500))
    if seabed is None:
        desc.add(depth, lps_layer.AcousticalLayer())
    else:
        desc.add(depth, lps_layer.Seabed(seabed))

    return lps_channel.Channel(description = desc,
                    sensor_depth = depth - lps_qty.Distance.m(5),
                    source_depths = [lps_qty.Distance.m(d) for d in np.arange(3, 21, 3)],
                    max_distance = lps_qty.Distance.m(200),
                    max_distance_points = 41,
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

    args = parser.parse_args()

    seabed_enum = lps_layer.SeabedType[args.seabed.upper()] if args.seabed is not None else None
    get_channel(lps_qty.Distance.m(args.depth), seabed_enum)
