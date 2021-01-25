# -*- coding: utf-8 -*-
##
# This module conatins classes and functions used to
# support the simulation of a semi-Markov process.
#
# The underlying failure/repair distributions are assumed
# to be Weibull, which is Exponential when shape=1.
# 기초적인 고장/수리 분포는 Weibull로 가정되며, 이것은 형상=1일 때 지수 분포다.
#
# Kevin Greenan (kmgreen@cs.ucsc.edu)
#
#

import mpmath
from mpmath import mpf
from mpmath import ln
from mpmath import findroot
import random


##
# Set precision used by the MP math lib
# MP math lib에서 사용하는 정밀도 설정
mpmath.mp.prec += 100
mpmath.mp.dps = 100

##
# Contains parameters, distribution functions and hazard rate function
# for a 3-parameter Weibull distribution based on shape, scale and location.
# 베이불 분포 3요소 형상(shape), 척도(scale) and 위치(location)
class Weibull:
    ##
    # Construct a Weibull object by specifying shape, scale and location.
    #
    # Note: when shape == 1, this is an Exponential distribution
    # 형상이 1이면 지수 분포
    #
    def __init__(self, shape=1, scale=1, location=0): 
        self.shape = float(shape)
        self.scale = float(scale)
        self.location = float(location)
    ##
    # Get the probability density of Weibull(shape, scale, location) at x
    #
    # @param x: random variable, most likely a time
    # @return density of Weibull(shape, scale, location) at x
    #
    def pdf_eval(self, x): # 랜덤변수 x로 확률 밀도 얻기
        if x < 0:
            return 0
        elif x < self.location:
            return 0
        else:
            x = float(x)
            a = self.shape/self.scale
            b = (x-self.location)/self.scale
            b = mpmath.power(b, self.shape-1)
            c = mpmath.exp(-mpmath.power(((x-self.location)/self.scale), self.shape))
            return a * b *c

    ##
    # Return the probability P(X <= x) or the probability that a
    # random variable is less than or equal to the parameter x.
    # 확률 P(X <= x) 또는 랜덤 변수가 모수 x보다 작거나 같은 확률을 반환한다.

    # The returned value represents the probability that there is
    # a 'failure' at or before x, which is most likely a time.
    # 반환된 값은 x에 '고장'이 있을 확률

    # @param x: variable, most likely a time
    # @return: probability of failure before or at x
    # 매개변수 x 이전 또는 x에서의 실패 확률 반환
    def cdf_eval(self, x):
        x = float(x)
        if x < self.location:
            return 0
        return float(1) - mpmath.exp(-mpmath.power(((x-self.location)/self.scale), self.shape))

    ##
    # Return the hazard rate at x.  The hazard rate is interpreted
    # as the instantaneous failure rate at x.
    # 위험률을 x로 반환한다. 위험률은 x에서의 순간 고장률로 해석된다.

    # Note: If shape == 1, then this value will be constant for all x
    # 형상 모수가 1이면 이 값은 모든 x에 대해 일정하게 된다.

    # @param x: variable, most likely a time
    # @return instantaneous failure rate at x
    # 매개변수 x에서 순간 실패율 반환
    def hazard_rate(self, x):
        if x < self.location:
            return 0
        elif self.shape == 1:
            return float(1) / self.scale
        else:
            return float(abs(self.pdf_eval(x) / (float(1) - self.cdf_eval(x))))
    ##
    # When the shape parameter is not 1, then the hazard rate will
    # change with time.  When simulating a semi-Markov process using
    # uniformization (which is a method we use), the maximum failure
    # rate for every distribution over all possible times is required.
    # This function evaluates the hazard rate at discrete points and
    # returns the maximum hazard rate for a given mission time (i.e.
    # max simulation time).
    # 형상 모수가 1이 아닌 경우 위험률은 시간에 따라 변경된다. 균일화(우리가 사용하는 방법)를 
    # 사용하여 세미 마르코프 프로세스를 시뮬레이션할 때 가능한 모든 시간에 걸친 모든 분포에 대한 
    # 최대 고장률이 필요하다. 이 함수는 이산형 지점에서 위험률을 평가하고 주어진 임무 시간(즉, 최대 
    # 시뮬레이션 시간)에 대한 최대 위험률을 반환한다.

    # @param mission_time: expected maximum simulation time, 예상 최대 시뮬레이션
    # @return maximum possible hazard rate for [0, mission_time]
    #
    # 0~예상 최대 시뮬레이션 시간에 대해 가능한 최대 위험률을 반환
    def get_max_hazard_rate(self, mission_time):
        max = float(0)

        if self.shape == 1:
            return float(1) / self.scale
        print 0.1 * mission_time
        for i in range(1, int(mission_time), int(float(0.1) * mission_time)):
            curr_h_rate = self.hazard_rate(i)
            if curr_h_rate > max:
                max = curr_h_rate
            elif curr_h_rate == float('nan'):
                break
        return max

    ##
    # Get min hazard rate
    # 최소 위험률 반환
    def get_min_hazard_rate(self, mission_time):
        min = float(1)

        if self.shape == 1:
            return float(1) / self.scale

        for i in range(0, mission_time, int(0.1 * mission_time)):
            curr_h_rate = self.hazard_rate(i)
            if curr_h_rate < min:
                min = curr_h_rate
            elif curr_h_rate == float('nan'):
                break

        return min
    ##
    # Draw a random value from this distribution
    # 분포에서 랜덤 값 그리기
    def draw(self):
        return random.weibullvariate(self.scale, self.shape) + self.location
    ##
    # Draw from a lower truncated Weibull distribution
    # (Reject all samples less than 'lower')
    # 아래쪽 잘린(기준 lower 이하 제거) Weibull 분포에서 그리기
    def draw_truncated(self, lower):
        val = self.draw()
        while val <= lower:
            print "%.2f %.2f" % (lower, val)
            val = self.draw()
        return val
    ##
    # Draw using the inverse transform method.
    # This method draws from the waiting time
    # based on the CDF built from the distribution's
    # hazard rates
    # 분포의 위험률에서 작성된 CDF를 기준으로 대기 시간부터 도출한다.
    # 역변환 함수 그리기
    def draw_inverse_transform(self, curr_time):
        U = random.uniform(0,1)
        while U == 0:
            U = random.uniform(0,1)
        draw = ((-(self.scale**self.shape)*ln(U)+((curr_time)**self.shape))**(1/self.shape) - (curr_time))
        return abs(draw)

class Rack:

    ##
    # Three possible states of rack
    #
    STATE_RACK_NORMAL = "rack is normal"
    STATE_RACK_UNAVAILABLE = "rack is unavailable"
    STATE_RACK_CRASHED = "rack is crashed"

    ##
    # Possible failure events
    #
    EVENT_RACK_FAIL = "transient rack failure"
    EVENT_RACK_REPAIR = "repair for transient rack failure"


    def __init__(self, rack_fail_distr, rack_repair_distr):
        # Current state
        self.state = self.STATE_RACK_NORMAL
        # Transient failure distribution
        self.rack_fail_distr = rack_fail_distr
        # Repair distribution for transient rack failure
        self.rack_rapair_distr = rack_repair_distr


    def init_state(self):
        self.state = self.STATE_RACK_NORMAL


    ##
    # Transient rack failure
    #
    def fail_rack(self, curr_time):
        self.state = self.STATE_RACK_UNAVAILABLE


    ##
    # Repair for transient rack failure
    #
    def repair_rack(self):
        self.state = self.STATE_RACK_NORMAL


    ##
    # Get current state of this rack
    #
    def get_curr_state(self):
        return self.state



class Node:

    ##
    # Three possible states
    #
    STATE_NODE_NORMAL = "node is normal"
    STATE_NODE_UNAVAILABLE = "node is unavailable"
    STATE_NODE_CRASHED = "node is crashed"

    ##
    # Possible failure events
    #
    EVENT_NODE_FAIL = "node failure"
    EVENT_NODE_REPAIR = "node repair"
    EVENT_NODE_TRANSIENT_FAIL = "node transient failure"
    EVENT_NODE_TRANSIENT_REPAIR = "node transient repair"


    def __init__(self, node_fail_distr, node_transient_fail_distr, node_transient_repair_distr,
                 node_fail_trace=None, node_transient_fail_trace=None, node_transient_repair_trace=None):
        # Current state
        self.state = self.STATE_NODE_NORMAL

        # Failure distribution
        self.node_fail_distr = node_fail_distr
        self.node_transient_fail_distr = node_transient_fail_distr
        self.node_transient_repair_distr = node_transient_repair_distr

        # Add node fail events for trace
        self.node_fail_trace = node_fail_trace
        # Add node transient failure events from trace
        self.node_transient_fail_trace = node_transient_fail_trace
        self.node_transient_repair_trace = node_transient_repair_trace

        # The following is for importance sampling
        self.last_time_update = mpf(0)
        # Global begin time of this disk
        self.begin_time = mpf(0)
        # Local (relative) clock of this disk
        self.clock = mpf(0)
        # Local repair time of this disk
        self.repair_clock = mpf(0)
        self.repair_start = mpf(0)


    def init_clock(self, curr_time):
        self.last_time_update = curr_time
        self.begin_time = curr_time
        self.clock = mpf(0)
        self.repair_clock = mpf(0)
        self.repair_start = mpf(0)


    def init_state(self):
        self.state = self.STATE_NODE_NORMAL


    ##
    # Update node clocks.  There are three main clocks to update:
    #   the node clock
    #   the repair clock (if there is an ongoing repair)
    #   the time of the last clock update (used to update the node clock)
    #
    # The clock member variable is used to get instantaneous failure
    # rate, while the repair clock is used to get the instantaneous "repair" rate.
    # 클락 멤버 변수는 실패율을 얻기위해, repair clock는 복구율을 얻기 위해 사용
    # @param curr_time: current simulation time
    #
    def update_clock(self, curr_time):
        self.clock += (curr_time - self.last_time_update) #마지막 업데이트로 부터 지난 시간
        if self.state == self.STATE_NODE_CRASHED:
            self.repair_clock = (curr_time - self.repair_start)
        else:
            self.repair_clock = mpf(0)

        self.last_time_update = curr_time


    ##
    # Get this node's current time
    #
    # @return current node clock reading
    #
    def read_clock(self):
        return self.clock


    ##
    # Get this node's current repair time
    #
    # @return current node repair clock reading
    #
    def read_repair_clock(self):
        return self.repair_clock


    ##
    # Permanent node failure
    #
    def fail_node(self, curr_time):
        self.state = self.STATE_NODE_CRASHED
        self.repair_clock = mpf(0)
        self.repair_start = curr_time


    ##
    # Repair for permanent node failure
    #
    def repair_node(self):
        self.begin_time = self.last_time_update
        self.clock = mpf(0)  # this is considered as brand-new after repair
        self.repair_clock = mpf(0)
        self.state = self.STATE_NODE_NORMAL


    ##
    # Update the normal node as unavailable
    #
    def offline_node(self):
        if self.state == self.STATE_NODE_NORMAL:
            self.state = self.STATE_NODE_UNAVAILABLE


    ##
    # Update the unavailable disk as normal
    #
    def online_node(self):
        if self.state == self.STATE_NODE_UNAVAILABLE:
            self.state = self.STATE_NODE_NORMAL


    ##
    # Get current state of this node
    #
    def get_curr_state(self):
        return self.state

    ##
    # Get instantaneous failure rate of this node
    #
    # @return instantaneous whole-component failure rate
    #
    def curr_node_fail_rate(self):
        if self.state == self.STATE_NODE_CRASHED:
            return float(0)

        return self.node_fail_distr.hazard_rate(self.clock)


##
# This class encapsulates the state of a disk (i.e., disk) under simulation.
# Each disk is given failure and repair distributions for the entire disk.
#
# A disk may be in one of three states:
# NORMAL (operational, no failures) or
# UNAVAILABLE (unavailable due to transient failures) or
# CRASHED (entire disk is failed)
#
class Disk:

    ##
    # The three possible states
    #
    STATE_NORMAL = "state normal"
    STATE_UNAVAILABLE = "state unavailable"
    STATE_CRASHED = "state crashed"

    ##
    # Possible failure events
    #
    EVENT_DISK_FAIL = "disk failure"
    EVENT_DISK_REPAIR = "disk repair"


    ##
    # A disk is constructed by specifying the appropriate failure/repair distributions.
    # The disk fail/repair distributions must be specified.
    # This function will set the disk state to NORMAL and set all clocks to 0.
    # init_clock *must* first be called in order to use this object in simulation.
    #
    def __init__(self, disk_fail_distr, disk_repair_distr):
        # Current state
        self.state = self.STATE_NORMAL

        # keep record of the unavailable time of this disk
        self.unavail_start = mpf(0)
        self.unavail_clock = mpf(0)

        # Failure and repair distributions
        self.disk_fail_distr = disk_fail_distr
        self.disk_repair_distr = disk_repair_distr

        # The following clocks are mainly for importance sampling
        # Last "global" clock update
        self.last_time_update = mpf(0)
        # Global begin time of this disk
        self.begin_time = mpf(0)
        # Local (relative) clock of this disk
        self.clock = mpf(0)
        # Local repair time of this disk
        self.repair_clock = mpf(0)
        self.repair_start = mpf(0)


    ##
    # Set the last clock update to the current simulation time and initialize
    # t_0 for this disk (begin_time).
    #
    # @param curr_time: t_0 of this disk
    #
    def init_clock(self, curr_time):
        self.unavail_start = float(0)
        self.unavail_clock = float(0)
        self.last_time_update = curr_time
        self.begin_time = curr_time
        self.clock = mpf(0)
        self.repair_clock = mpf(0)
        self.repair_start = mpf(0)


    ##
    # Set the state of this disk to NORMAL
    #
    def init_state(self):
        self.state = self.STATE_NORMAL


    ##
    # Update disk clocks.  There are three main clocks to update:
    # the disk clock, the repair clock (if there is an ongoing repair)
    # and the time of the last clock update (used to update the disk clock)
    #
    # The clock member variable is used to get instantaneous failure
    # rate, while the repair clock is used to get the instantaneous "repair" rate.
    #
    # @param curr_time: current simulation time
    #
    def update_clock(self, curr_time):
        self.clock += (curr_time - self.last_time_update)
        if self.state == self.STATE_CRASHED:
            self.repair_clock = (curr_time - self.repair_start)
        else:
            self.repair_clock = float(0)
        self.last_time_update = curr_time


    ##
    # Get this disk's current time
    #
    # @return current disk clock reading
    #
    def read_clock(self):
        return self.clock


    ##
    # Get this disk's current repair time
    #
    # @return current disk repair clock reading
    #
    def read_repair_clock(self):
        return self.repair_clock


    ##
    # Get disk state
    #
    # @return disk state
    #
    def get_curr_state(self):
        return self.state


    ##
    # Fail this disk.  Reset list of failed sub-disks
    #
    def fail_disk(self, curr_time):
        if self.state == self.STATE_NORMAL:
            self.unavail_start = curr_time
        self.state = self.STATE_CRASHED
        self.repair_clock = float(0)
        self.repair_start = curr_time


    ##
    # Repair this disk.
    #
    def repair_disk(self, curr_time):
        self.state = self.STATE_NORMAL
        self.unavail_clock += curr_time - self.unavail_start
        self.begin_time = self.last_time_update
        self.clock = float(0)
        self.repair_clock = float(0)


    ##
    # Update the normal disk as unavailable
    #
    def offline_disk(self, curr_time):
        if self.state == self.STATE_NORMAL:
            self.state = self.STATE_UNAVAILABLE
            self.unavail_start = curr_time


    ##
    # Update the unavailable disk as normal
    #
    def online_disk(self, curr_time):
        if self.state == self.STATE_UNAVAILABLE:
            self.state = self.STATE_NORMAL
            self.unavail_clock += curr_time - self.unavail_start


    ##
    # Return the unavailable time of this disk
    #
    def get_unavail_time(self, curr_time):
        if self.state == self.STATE_NORMAL:
            return self.unavail_clock
        else:
            return self.unavail_clock + (curr_time - self.unavail_start)


    ##
    # Get instantaneous failure rate of this disk
    #
    # @return instantaneous whole-disk failure rate
    #
    def curr_disk_fail_rate(self):
        if self.state == self.STATE_CRASHED:
            return float(0)

        return self.disk_fail_distr.hazard_rate(self.clock)


    ##
    # Get instantaneous repair rate of this disk
    #
    # @return instantaneous whole-disk repair rate
    #
    def curr_disk_repair_rate(self):
        if self.state == self.STATE_NORMAL:
            return float(0)

        return self.disk_repair_distr.hazard_rate(self.repair_clock)


    ##
    # Return sum of instantaneous fail/repair rates
    #
    def inst_rate_sum(self):
        return self.curr_disk_fail_rate() + self.curr_disk_repair_rate()


def test():
    # Basic test of the Weibull functions
    w = Weibull(shape=float(2.0), scale=float(12), location=6)

    print "Weibull(%s,%s,%s): " % (w.shape, w.scale, w.location)

    sum = 0

    for i in range(10000):
        sum += w.draw_truncated(6)

    print "MEAN: ", float(sum) / 10000.

    print w.draw_inverse_transform(0)
    print w.draw_inverse_transform(0)
    print w.draw_inverse_transform(0)
    print w.draw_inverse_transform(0)

    print "Max hazard rate is %e\n" % w.get_max_hazard_rate(100)

    for i in range(0,200,5):
        print "CDF at time %d is %f\n" % (i, w.cdf_eval(i))

    w = Weibull(shape=float(1.0), scale=float(120000))

    print "Bunch of draws:"
    for i in range(10):
        print w.draw_inverse_transform(1000000)

    print "Weibull(%s,%s,%s): " % (w.shape, w.scale, w.location)

    print "Max hazard rate is %e\n" % w.get_max_hazard_rate(1000)

    for i in range(0,1000,100):
        print "Hazard rate at time %d is %e\n" % (i, w.hazard_rate(i))


if __name__ == "__main__":
    test()
