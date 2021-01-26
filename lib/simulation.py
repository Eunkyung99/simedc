# -*- coding: utf-8 -*-
##
# Base class for any simulation
#
import sys
from smp_data_structures import Rack, Node, Disk
from network import Network

##
# Container for importance sampling parameters
#
class ISParms:
    def __init__(self, fb_prob=0.5, beta=1.0):
        self.fb_prob = fb_prob
        self.beta = beta


class Simulation:
    REGULAR="regular"
    UNIFBFB = "uniformization_balanced_failure_biasing"
    FAILURE="failure"
    REPAIR="repair"

    def __init__(self, mission_time,
                 num_racks, nodes_per_rack, disks_per_node, capacity_per_disk,
                 chunk_size, num_stripes,
                 code_type, code_n, code_k, code_free, 
                 place_type, chunk_rack_config,
                 rack_fail_dists, rack_repair_dists, node_fail_dists,
                 node_transient_fail_dists, node_transient_repair_dists,
                 disk_fail_dists, disk_repair_dists,
                 use_network, network_setting,
                 use_power_outage, power_outage_dist, power_outage_duration,
                 code_l=0,
                 use_trace=False, trace_id=0,
                 is_parms=None): #add code_free

        # Mission time of the simulation
        self.mission_time = mission_time

        self.num_racks = num_racks
        self.nodes_per_rack = nodes_per_rack
        self.disks_per_node = disks_per_node
        self.capacity_per_disk = capacity_per_disk
        self.num_nodes = num_racks * nodes_per_rack
        # Number of disks in the system
        self.num_disks = self.num_nodes * self.disks_per_node

        self.chunk_size = chunk_size
        self.num_stripes = num_stripes
        self.code_type = code_type
        self.n = code_n
        self.k = code_k
        self.l = code_l # for LRC
        self.free = code_free #add code_free
        self.place_type = place_type
        self.chunk_rack_config = chunk_rack_config
        self.events_queue = None
        self.wait_repair_queue = None
        self.placement = None

        # Disk failure and repair distributions
        self.rack_fail_dists = rack_fail_dists
        self.rack_repair_dists = rack_repair_dists
        self.node_fail_dists = node_fail_dists
        self.node_transient_fail_dists = node_transient_fail_dists
        self.node_transient_repair_dists = node_transient_repair_dists
        self.disk_fail_dists = disk_fail_dists
        self.disk_repair_dists = disk_repair_dists

        self.use_network = use_network
        self.network_setting = network_setting
        self.network = Network(self.num_racks, self.nodes_per_rack, self.network_setting)

        self.use_power_outage = use_power_outage
        self.power_outage_dist = power_outage_dist
        self.power_outage_duration = power_outage_duration

        self.use_trace = use_trace
        self.trace_id = trace_id

        # 예외 처리
        if self.use_power_outage and self.power_outage_dist == None:
            print "Please configure power_outage_dist if using power_outage!"
            sys.exit(2)


        if self.use_power_outage:   # 랙의 실패, 복구 분포 None
            self.racks = [Rack(None, None) for i in xrange(num_racks)]
        else:                       # 랙의 실패, 복구 분포 적용(디폴트)
            self.racks = [Rack(self.rack_fail_dists, self.rack_repair_dists) for i in xrange(self.num_racks)]

        if not use_trace:           # 노드 실패, 일시적 실패, 일시적 복구 분포 적용(디폴트)
            self.nodes = [Node(self.node_fail_dists, self.node_transient_fail_dists ,
                               self.node_transient_repair_dists) for i in xrange(self.num_nodes)]
        else:
            # It will generate in reset() of Regular Simualtion
            self.nodes = [Node(None, None, None) for i in xrange(self.num_nodes)]

        self.disks = [Disk(self.disk_fail_dists, None) for i in xrange(self.num_disks)]

        self.is_parms = is_parms




    ##
    # Init the simulation
    #
    def init(self):
        return None


    ##
    # Reset the simulator
    #
    def reset(self, ite_count=0):
        return None


    ##
    # Get the next event
    #
    def get_next_event(self, curr_time):
        return None


    ##
    # Run an iteration of the simulator
    #
    def run_iteration(self, ite_count=0):
        return None
