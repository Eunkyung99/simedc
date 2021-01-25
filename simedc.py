# -*- coding: utf-8 -*-
#!/usr/bin/python
import os, sys
import multiprocessing
import getopt
import random
import numpy.random as nprandom

from lib.simulation import Simulation, ISParms
from lib.regular_simulation import RegularSimulation
from lib.is_simulation import UnifBFBSimulation
from lib.placement import Placement
from lib.smp_data_structures import Weibull
from lib.sim_analysis_functions import Samples
from lib.tracelib.trace import Parser

class Simulate:
    def __init__(self, mission_time,
                 num_racks, nodes_per_rack, disks_per_node, capacity_per_disk,
                 chunk_size, num_stripes,
                 code_type, code_n, code_k, code_l, code_free, 
                 place_type, chunk_rack_config,
                 rack_fail_dists, rack_repair_dist, node_fail_dists,
                 node_transient_fail_dists, node_transient_repair_dists,
                 disk_fail_dists, disk_repair_dists,
                 use_network, network_setting,
                 use_power_outage, power_outage_dist, power_outage_duration,
                 use_trace=False, trace_id=0,
                 sim_type=Simulation.REGULAR, is_parms=None): #add code_free

        # 타입에 맞는 시뮬레이션을 생성하고 init , 디폴트는 Simulation.UNIFBFB
        if sim_type == Simulation.REGULAR:
            # call simulation's __init__
            self.sim = RegularSimulation(mission_time,
                                     num_racks, nodes_per_rack, disks_per_node, capacity_per_disk,
                                     chunk_size, num_stripes,
                                     code_type, code_n, code_k,
                                     place_type, chunk_rack_config,
                                     rack_fail_dists, rack_repair_dist, node_fail_dists,
                                     node_transient_fail_dists, node_transient_repair_dists,
                                     disk_fail_dists, disk_repair_dists,
                                     use_network, network_setting,
                                     use_power_outage, power_outage_dist, power_outage_duration,
                                     code_l,
                                     use_trace, trace_id)

            # call RegularSimulation's init()
            self.sim.init()
        elif sim_type == Simulation.UNIFBFB:
            # call simulation's __init__
            self.sim = UnifBFBSimulation(mission_time,
                                         num_racks, nodes_per_rack, disks_per_node, capacity_per_disk,
                                         chunk_size, num_stripes,
                                         code_type, code_n, code_k,
                                         place_type, chunk_rack_config,
                                         rack_fail_dists, rack_repair_dist, node_fail_dists,
                                         node_transient_fail_dists, node_transient_repair_dists,
                                         disk_fail_dists, disk_repair_dists,
                                         use_network, network_setting,
                                         use_power_outage, power_outage_dist, power_outage_duration,
                                         code_l,
                                         use_trace, trace_id, is_parms)

            # call UnifBFBSimulation's init()
            self.sim.init()
        else:
            print "ERROR: wrong sim_type, which should be of REGULAR or UNIFBFB!"
            sys.exit(2)

    def run_simulation(self, num_iterations=1000):
        rst_list = []
        # print "num_iterations = %d" % num_iterations
        for i in xrange(num_iterations):
            rst_list.append(self.sim.run_iteration(i))
        return rst_list

def usage(arg): # 오작동시 가이드 출력
    print arg, ": -h [--help]"
    print "-A <sim_type> [--sim_type <sim_type>]"
    print "-f <fb_prob> [--fb_prob <fb_prob>]"
    print "-b <beta> [--beta <beta>]"
    print "-i <total_iterations> [--total_iterations <total_iterations>]"
    print "-p <num_processes> [--num_processes <num_processes>]"
    print "-m <mission_time> [--mission_time <mission_time>]"
    print "-u <rseed_plus> [--rseed_plus <rseed_plus>]"
    print "-R <num_racks> [--num_racks <num_racks>]"
    print "-N <nodes_per_rack> [--nodes_per_rack <nodes_per_rack>]"
    print "-D <disks_per_node> [--disks_per_node <disks_per_node>]"
    print "-C <capacity_per_disk> [--capacity_per_disk <capacity_per_disk>]"
    print "-K <chunk_size> [--chunk_size <chunk_size>]"
    print "-S <num_stripes> [--num_stripes <num_stripes>]"
    print "-t <code_type> [--code_type <code_type>]"
    print "-n <code_n> [--code_n <code_n>]"
    print "-k <code_k> [--code_k <code_k>]"
    print "-l <code_l> [--code_l <code_l>]"
    print "-T <place_type> [--place_type <place_type>]"
    print "-g <chunk_rack_config [--chunk_rack_config <chunk_rack_config>]"
    print "-W <use_network> [--use_network <use_network>]"
    print "-s <network_setting> [--network_setting <network_setting>]"
    print "-O <use_power_outage> [--use_power_outage <use_power_outage>]"
    print "-F <use_trace> [--use_trace <use_trace>]"
    print "-d <trace_id> [--trace_id <trace_id>]"
    print "-E <code_free> [--code_free <code_free>]"
    print ""
    print "Detail:"
    print "sim_type =  \"regular\" (Regular), \"unifbfb\" (Enable importance sampling)"
    print "fb_prob = probability of failure biasing"
    print "beta = a value that is close to the average repair rate"
    print "total_iterations = total number of simulation runs."
    print "num_processes = number of running processes."
    print "mission_time = simulation end time in hours."
    print "rseed_plus = number of random seed"
    print "chunk_size = size (MiB) of each chunk."
    print "num_stripes = number of stripes."
    print "code_type = \"rs\" (Reed-Solomon Codes), \"lrc\" (Locally Repairable Codes), \"drc\" (Double Regenerating Codes)."
    print "code_n = number of data chunks and parity chunks for each stripe."
    print "code_k = number of data chunks for each stripe."
    print "code_l = number of groups in LRC."
    print "place_type = \"flat\" (Flat), \"hie\" (Hierachical)."
    print "chunk_rack_config = number of chunks in each rack. This must agree with the erasure code."
    print "use_network = False / True. If using network, network_setting = [cross_rack_repair_bwth, intra_rack_repair_bwth]"
    print "use_trace = False / True. If using trace, trace_id is in (4~11, 13~18)."
    print "code_free = number of free chunks" #add
    print ""
    print "Samples:"
    print arg, "-n 9 -k 6 -t rs -T flat"
    print arg, "-n 9 -k 6 -t rs -T hie -g 3,3,3"

def get_parms(): # 입력 매개변수 추출
    total_iterations = 4
    num_processes = 4
    mission_time = 87600  # 87600h = 10y
    rseed_plus = 10
    num_racks = 32
    nodes_per_rack = 32
    disks_per_node = 1
    capacity_per_disk = 2 ** 20  # 2^20 MiB = 1 TiB

    chunk_size = 256  # MiB
    num_stripes = 349524
    code_type = Placement.CODE_TYPE_RS
    code_n = 9  # number of chunks in total per stripe
    code_k = 6  # number of data chunks
    code_l = 2  # number of groups in LRC
    code_free = 0 #add number of free chunk
    place_type = Placement.PLACE_TYPE_FLAT # PLACE_TYPE_HIERARCHICAL
    chunk_rack_config = None

    use_network = True
    cross_rack_repair_bwth = 125  # 125MB/s = 1Gb/s
    intra_rack_repair_bwth = 125
    network_setting = [cross_rack_repair_bwth, intra_rack_repair_bwth]

    use_power_outage = False
    use_trace = False
    trace_id = 9

    # sim_type = Simulation.REGULAR
    sim_type = Simulation.UNIFBFB
    is_fb_prob = float(0.5)
    is_beta = float(.61)


    try:
        # getopt, C-style parser for command line options
        (opts, args) = getopt.getopt(sys.argv[1:], "hi:p:m:u:R:N:D:C:K:S:t:n:k:l:E:T:g:W:s:O:F:d:A:f:b:",
                                     ["help",
                                      "total_iterations", "num_processes", "mission_time", "rseed_plus",
                                      "num_racks", "nodes_per_rack", "disks_per_node", "capacity_per_disk",
                                      "chunk_size", "num_stripes",
                                      "code_type", "code_n", "code_k", "code_l", "code_free", 
                                      "place_type", "chunk_rack_config",
                                      "use_network", "network_setting",
                                      "use_power_outage",
                                      "use_trace", "trace_id",
                                      "sim_type","fb_prob", "beta"]) #add code_free
        # opts = [('-n', '9'), ('-k', '6'), ('-t', 'rs'), ('-T', 'flat')] / args = []
    except:
        usage(sys.argv[0])
        print "getopts excepted"
        sys.exit(1)

    if len(opts) == 0 :
        print "Please specify at least one parameter!\n"
        usage(sys.argv[0])
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            print usage(sys.argv[0])
            sys.exit(0)
        elif o in ("-i", "--iterations"):
            total_iterations = int(a)
        elif o in ("-p", "--num_processes"):
            num_processes = int(a)
        elif o in ("-m", "--mission_time"):
            mission_time = int(a)
        elif o in ("-u", "--rseed_plus"):
            rseed_plus = int(a)
        elif o in ("-R", "--num_racks"):
            num_racks = int(a)
        elif o in ("-N", "--nodes_per_rack"):
            nodes_per_rack = int(a)
        elif o in ("-D", "--disks_per_node"):
            disks_per_node = int(a)
        elif o in ("-C", "--capacity_per_disk"):
            capacity_per_disk = int(a)
        elif o in ("-K", "--chunk_size"):
            chunk_size = int(a)
        elif o in ("-S", "--num_stripes"):
            num_stripes = int(a)
        elif o in ("-t", "--code_type"):
            if a == "rs":
                code_type = Placement.CODE_TYPE_RS
            elif a == "lrc":
                code_type = Placement.CODE_TYPE_LRC
            elif a == "drc":
                code_type = Placement.CODE_TYPE_DRC
            else:
                print "Please set right code_type(-t)!"
                sys.exit(2)
        elif o in ("-n","--code_n"):
            code_n = int(a)
        elif o in ("-k", "-code_k"):
            code_k = int(a)
        elif o in ("-l", "-code_l"):
            code_l = int(a)
        elif o in ("-E", "-code_free"):
            code_free = int(a)
        elif o in ("-T", "--place_type"):
            if a == "flat":
                place_type = Placement.PLACE_TYPE_FLAT
            elif a == "hie":
                place_type = Placement.PLACE_TYPE_HIERARCHICAL
            else:
                print "Please set right code_type(-T)!"
                sys.exit(2)
        elif o in ("-g", "--chunk_rack_config"):
            chunk_rack_config = a.split(",")
            chunk_rack_config = [int(item) for item in chunk_rack_config]
        elif o in ("-W", "--use_network"):
            if a == "true" or a == "True" or a == "TRUE":
                use_network = True
            elif a == "false" or a == "False" or a == "FALSE":
                use_network = False
        elif o in ("-s", "--network_setting"):
            network_setting = a.split(",")
            network_setting = [float(item) for item in network_setting]
        elif o in ("-O", "--use_power_outage"):
            if a == "true" or a == "True" or a == "TRUE":
                use_power_outage = True
            elif a == "false" or a == "False" or a == "FALSE":
                use_power_outage = False
        elif o in ("-F", "--use_trace"):
            if a == "true" or a == "True" or a == "TRUE":
                use_trace = True
            elif a == "false" or a == "False" or a == "FALSE":
                use_trace = False
        elif o in("-d", "--trace_id"):
            trace_id = int(a)
        elif o in("-A", "--sim_type"):
            if a == "regular":
                sim_type = Simulation.REGULAR
            elif a == "unifbfb":
                sim_type = Simulation.UNIFBFB
        elif o in("-f", "fb_prob"):
            is_fb_prob = float(a)
        elif o in("-b", "beta"):
            is_beta = float(a)

    return (total_iterations, num_processes, mission_time, rseed_plus,
            num_racks, nodes_per_rack, disks_per_node, capacity_per_disk,
            chunk_size, num_stripes,
            code_type, code_n, code_k, code_l, code_free, 
            place_type, chunk_rack_config,
            use_network, network_setting,
            use_power_outage,
            use_trace, trace_id,
            sim_type, is_fb_prob, is_beta)

def do_it(job_description):
    # get the values for each parameter via get_parms()
    (iter_num, rseed, mission_time,
     num_racks, nodes_per_rack, disks_per_node, capacity_per_disk,
     chunk_size, num_stripes,
     code_type, code_n, code_k, code_l, code_free, 
     place_type, chunk_rack_config,
     use_network, network_setting,
     use_power_outage,
     use_trace, trace_id,
     sim_type, is_fb_prob, is_beta) = job_description #add code_free

    # 시드값을 맞춘다 = 동일한 셋트의 난수 발생
    nprandom.seed(rseed)
    random.seed(rseed)

    # disk failure distribution ,Weibull 분포(신뢰도 데이터를 모형화하기 위해 가장 일반적으로 사용)
    # 설정값에 따라 랙, 노드, 디스크의 분포값을 생성
    disk_fail_dists = Weibull(shape=1.12, scale=87600.)
    if use_network:     # 디폴트
        disk_repair_dists = None
    else:
        disk_repair_dists = Weibull(shape=3.0, scale=0.03, location=0.01)

    power_outage_rate = float(365 * 24) # power 정전 률 ?
    power_outage_duration = float(15)   # power 정전 지속시간 ?

    if use_power_outage:    
        rack_fail_dists = None
        rack_repair_dists = None
        power_outage_dist = Weibull(shape=1.0, scale=power_outage_rate, location=0.0)
    else:   # 디폴트
        rack_fail_dists = Weibull(shape=1.0, scale=87600.)
        rack_repair_dists = Weibull(shape=1.0, scale=24., location=10.)
        power_outage_dist = None

    if use_trace:
        node_fail_dists = None
        node_transient_fail_dists = None
        node_transient_repair_dists = None
    else:   # 디폴트
        node_fail_dists = Weibull(shape=1.0, scale=91250.)
        node_transient_fail_dists = Weibull(shape=1.0, scale=2890.8, location = 0.0)
        node_transient_repair_dists = Weibull(shape=1.0, scale=0.25, location=0.0)

    is_parms = None
    if sim_type == Simulation.UNIFBFB:  # 디폴트
        is_parms = ISParms(is_fb_prob, is_beta) # 0.5 / 0.61

    # init Simulate
    simulation = Simulate(mission_time,
                          num_racks, nodes_per_rack, disks_per_node, capacity_per_disk,
                          chunk_size, num_stripes,
                          code_type, code_n, code_k, code_l, code_free, 
                          place_type, chunk_rack_config,
                          rack_fail_dists, rack_repair_dists,
                          node_fail_dists, node_transient_fail_dists, node_transient_repair_dists,
                          disk_fail_dists, disk_repair_dists,
                          use_network, network_setting,
                          use_power_outage, power_outage_dist, power_outage_duration,
                          use_trace, trace_id,
                          sim_type, is_parms)

    return simulation.run_simulation(iter_num)


def get_output(result_simulation, total_iterations, num_stripes, code_n):
    run_samples = []
    avg_num_lost_chunks = float(0)
    avg_br = float(0)
    avg_single_chunk_repair_ratio = float(0)

    # print "len_results = %d" % len(result_simulation)
    for each in result_simulation:
        print each
        (sample, ori_pattern) = each
        run_samples.append(sample)
        (num_failed_stripes, num_lost_chunks, blocked_ratio, single_chunk_repair_ratio) = eval(ori_pattern)
        avg_num_lost_chunks += num_lost_chunks
        avg_br += blocked_ratio
        avg_single_chunk_repair_ratio += single_chunk_repair_ratio

    samples = Samples(run_samples)
    mean = samples.calcMean()
    relative_error = 100. * float(samples.calcRE("0.95"))

    avg_num_lost_chunks /= total_iterations
    NOMDL = avg_num_lost_chunks / (num_stripes * code_n)
    avg_br /= total_iterations
    avg_single_chunk_repair_ratio /= total_iterations

    print "*************** Result ***************"
    print "num_zeroes = %d" % samples.get_num_zeroes()
    print "PDL(데이터 손실 확률) = %e" % mean
    print "RE(상대적 에러 비율) =", "{0:.1f}%".format(relative_error)
    #print "NOMDL (bytes/byte) = %.12f" % NOMDL
    print "NOMDL(표준화 데이터 손실 규모) (bytes/byte) = %e" % NOMDL
    #print "BR = %.12f" % avg_br
    print "BR(차단 비율) = %e" % avg_br
    print "Single-chunk repair ratio = %.6f" % avg_single_chunk_repair_ratio
    print "***************************************"


if __name__ == "__main__":
    # Get the configuration, 초기 환경값 설정
    (total_iterations, num_processes, mission_time, rseed_plus,
     num_racks, nodes_per_rack, disks_per_node, capacity_per_disk,
     chunk_size, num_stripes,
     code_type, code_n, code_k, code_l, code_free,
     place_type, chunk_rack_config,
     use_network, network_setting,
     use_power_outage,
     use_trace, trace_id,
     sim_type, is_fb_prob, is_beta) = get_parms()

    # Check the configured storage capacity is valid, 저장 용량 확인
    # 전체 디스크 용량 (2^20 MiB(1 TiB) * 32 * 32 * 1)
    total_cap = float(capacity_per_disk * num_racks * nodes_per_rack * disks_per_node)
    # 실제 사용 용량 (9 * 349524 * 256 MiB) stripe당 청크 수 * stripe 수 * 청크 크기
    real_cap = float(code_n * num_stripes * chunk_size)


    if total_cap < real_cap:
        print "The storage capacity is NOT enough in current configuration!"
        sys.exit(2)

    # Cross-rack 대역폭은 intra-rack 대역폭보다 작아야 함
    if network_setting[0] > network_setting[1]:
        print "Cross-rack bandwidth must be less than intra-rack bandwidth."
        sys.exit(2)

    # 환경설정 값 출력
    print "\n*********** Configuration ***********"
    print "total_iterations(총 시뮬레이션 실행 수) = %d\nnum_processes(실행중인 프로세스 수) = %d\nmission_time(hours)(시뮬레이션 종료 시간) = %d" % \
          (total_iterations, num_processes, mission_time)
    print "rseed_plus(랜덤 시드 수) = %d" % rseed_plus
    print "num_racks(랙 수) = %d\nnodes_per_rack(랙당 노드 수) = %d\ndisks_per_node(노드당 디스크 수) = %d\ncapacity_per_disk = %d" % \
          (num_racks, nodes_per_rack, disks_per_node, capacity_per_disk)
    print "chunk_size(MiB)(각 청크 크기) = %d\nnum_stripes(stripe 수) = %d" % (chunk_size, num_stripes)
    print "code_type(코드 타입) = %s\ncode_n(각 stripe의 데이터 청크+패리티 청크 수) = %d\ncode_k(각 stripe의 데이터 청크 수) = %d" % (code_type, code_n, code_k)
    print "total_capacity (PiB)(전체 디스크 용량) = %.6f" % (total_cap/float(2 ** 30))
    print "usage_ratio(디스크 사용 비율) = %.6f" % (real_cap/total_cap)
    print "place_type(배치 유형) = %s\nchunk_rack_config(각 랙의 청크 수) = %s" % (place_type, chunk_rack_config)
    if use_network:
        print "network_setting[cross_rack_repair_bwth, intra_rack_repair_bwth] =", network_setting #byte/s
    if use_power_outage:
        print "use_power_outage =", use_power_outage
    if use_trace:
        print "use_trace =", use_trace, "\ntrace_id =", trace_id
    print "Simulation type(시뮬레이션 유형) = %s" % sim_type
    if sim_type == Simulation.UNIFBFB:
        print "is_fb_prob(실패 편향 확률) = %.3f, is_beta(평균 repair rate에 가까운 값) = %.3f" % (is_fb_prob, is_beta)
    print "number of free chunks(Free chunk) = %d" % code_free #add
    print "***************************************\n"

    # Check whether the parsed traces exist, 트레이스가 존재할 경우 체크
    trace_transient_path = "./lib/tracelib/transient_events/s" + str(trace_id) + 'n0.txt'
    trace_failure_path = "./lib/tracelib/failure_events/s" + str(trace_id) + 'n0.txt'
    trace_transient_repair_path = "./lib/tracelib/transient_repair/s" + str(trace_id) + 'n0.txt'

    # 디폴트는 무시
    if use_trace and not (os.path.exists(trace_transient_path) and os.path.exists(trace_failure_path)
                          and os.path.exists(trace_transient_repair_path)):
        parser = Parser(trace_id, mission_time)
        sum_nodes = parser.get_sum_nodes()
        if sum_nodes != num_racks * nodes_per_rack:
            print "The number of nodes should be equal to nodes_num in trace!"
            sys.exit(2)
        parser.parse_traces()

    # 프로세스 풀 생성
    pool = multiprocessing.Pool(num_processes)
    n = num_processes * 1

    # total_iterations는 프로세스 수의 배수여야함
    if total_iterations % n != 0:
        print "total_iterations should be divided by n!"
        sys.exit(2)

    # 프로세스당 시뮬레이션 횟수
    iterations_per_job = [total_iterations / n] * n     # [1, 1, 1, 1] -> iter_num
    enumerates = range(0+rseed_plus, n+rseed_plus)      # [10, 11, 12, 13] -> rseed
    jobs = zip(iterations_per_job, enumerates)          # [(1, 10), (1, 11), (1, 12), (1, 13)]

    # add params_tuple
    params_tuple = (mission_time,
     num_racks, nodes_per_rack, disks_per_node, capacity_per_disk,
     chunk_size, num_stripes,
     code_type, code_n, code_k, code_l,
     place_type, chunk_rack_config,
     use_network, network_setting,
     use_power_outage,
     use_trace, trace_id,
     sim_type, is_fb_prob, is_beta)

    # 위에서 만든 튜플을 jobs 요소마다 붙여줌
    for idx in xrange(len(jobs)):
        jobs[idx] += params_tuple

    results_list = pool.map(do_it, jobs)
    
    results = []
    for each in results_list:
        results += each

    get_output(results, total_iterations, num_stripes, code_n)
