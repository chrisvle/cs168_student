from dns import *
from rtts import *
#print get_average_times("3/dns_output_2.json")

# assert(count_different_dns_responses("jin/dns_output_1.json", "jin/dns_output_2.json"), [8, 32])
assert count_different_dns_responses("../jin/dns_output_1.json", "../jin/dns_output_other_server.json") == [8, 34]




# assert count_different_dns_responses("jin/dns_output_2.json", "examples/dig_sample_output.json") == [8, 9]
assert count_different_dns_responses("../examples/dig_sample_output.json", "../examples/dig_sample_output.json") == [1, 1]
# assert(count_different_dns_responses("jin/dns_output_other_server.json", "examples/dig_sample_output.json"), [0, 1])
# assert(count_different_dns_responses("jin/dns_output_other_server.json", "jin/dns_output_2.json"), [0, 0])
# assert(count_different_dns_responses("jin/dns_output_other_server.json", "jin/dns_output_1.json"), [0, 34])
# assert(count_different_dns_responses("jin/dns_output_other_server.json", "jin/dns_output_other_server.json"), [0, 0])

# assert(get_average_times("jin/dns_output_2.json") ==[5119.1854838709678, 144.91229032258064])


# assert get_average_times("../jin/dns_output_1.json") == [361.28658536585368, 108.51829268292683]
assert get_average_ttls("../jin/dns_output_1.json") == [508989.16463414632, 172800.0, 122042.04430379746, 8066.1585365853662]
# assert(get_average_ttls("jin/dns_output_2.json"), [384691.94199999998, 172800.0, 125154.38588574392, 7979.0500000000002])
assert get_average_ttls("../examples/dig_sample_output.json") == [478634.6, 172800.0, 172800.0, 300.0]
assert get_average_times("../examples/dig_sample_output.json") == [206.19999999999999, 45.200000000000003]










