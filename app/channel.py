import lps_utils.quantities as lps_qty
import lps_synthesis.propagation.layers as lps_layer
import lps_synthesis.propagation.models as lps_model
import lps_synthesis.propagation.channel_description as lps_desc
import lps_synthesis.propagation.channel as lps_channel


lps_channel.TEMP_DEFAULT_DIR = "./lps_libraries/acoustic_synthesis/result/propagation"

desc = lps_desc.Description()
desc.add(lps_qty.Distance.m(0), lps_qty.Speed.m_s(1500))
desc.add(lps_qty.Distance.m(30), lps_qty.Speed.m_s(1420))
desc.add(lps_qty.Distance.m(50), lps_layer.BottomType.CHALK)

# ch = lps_channel.Channel(description = desc,
#                 sensor_depth = lps_qty.Distance.m(40),
#                 source_depths = [lps_qty.Distance.m(10)],
#                 max_distance = lps_qty.Distance.km(1),
#                 max_distance_points = 128,
#                 sample_frequency = lps_qty.Frequency.khz(16),
#                 frequency_range=[lps_qty.Frequency.khz(5), lps_qty.Frequency.khz(5.05)],
#                 model = lps_model.Model.OASES)

# ch.propagate(input_data: np.array,
#              source_depth: lps_qty.Distance,
#              distance: typing.List[lps_qty.Distance])

# print(ch.description)

desc.save("test.json")

print(desc)

desc2 = lps_desc.Description.load("test.json")
print(desc2)