#! /usr/bin/env python
# coding=utf-8
import math
import copy
import time as tc


def Psi(x):  # ok
    # x is positive integer
    # it is decreasing function,whose value field is (0, 1]
    return math.exp((-x + 1) * 0.5)


def timeIsEarly(A, B):
    # if A is early than B, return 1
    # else return 0
    if float(A) < float(B):
        return 1
    else:
        return 0


class CrowdSourcing(object):
    """docstring for CrowdSourcing"""

    def __init__(self):
        self.worker_skills = None  # 二维list 数字或者字符串
        self.worker_reputation = None  # 一维list 小数
        self.worker_wage = None  # 一维list 小数
        self.worker_distance = None  # 二维list 数字 两点之间的距离
        self.rAlpha = []  # Retail Style Alpha
        self.lAlpha = []  # Layered Batch Alpha
        self.lBeta = []  # Layered Batch Beta
        self.cAlpha = []  # Core-Based Batch Alpha
        self.cBeta = []  # Core-Based Batch Beta
        # 每一个task都有一个id, 从0开始
        self.task_skills = None  # 二维list 数字或者字符串
        self.task_budget = None  # 一维list 小数
        self.task_publishtime = None
        self.task_due_date = None
        self.worker_task_estimated_completed_time = None  #二维数组，worker id / task id

    def PaymentOfBatch(self, taskidSet):  # ok
        # BatchBudget is a list of budget, which is sorted by publish time
        sum_payment = 0
        for i in range(len(taskidSet)):
            tid = taskidSet[i]
            sum_payment += Psi(i + 1) * self.task_budget[tid]
        return sum_payment

    def RetailTaskSkillCoverage(self, tid, wid):  # ok
        set_taskSkill = set(self.task_skills[tid])
        set_workerSkill = set(self.worker_skills[wid])
        return len(set_taskSkill & set_workerSkill)

    def getRetailStyleCV(self, tid, wid):  # ok
        t1 = self.RetailTaskSkillCoverage(tid, wid)
        t2 = self.worker_reputation[wid]
        t3 = self.worker_wage[wid]
        return (self.rAlpha[0] * t1 + self.rAlpha[1] * t2) / (self.rAlpha[2] * t3)

    def RetailStyleAllocation(self):  # ok
        # return dict
        allocation_dict = {}
        for i in range(len(self.task_skills)):
            max_CV = -1
            max_id = -1
            for j in range(len(self.worker_skills)):
                CV = self.getRetailStyleCV(i, j)
                if max_CV < CV:
                    max_CV = CV
                    max_id = j
            if max_id != -1:
                if max_id in allocation_dict:
                    allocation_dict[max_id].append(i)
                else:
                    allocation_dict[max_id] = [i]
            else:
                print 'error', i
        return allocation_dict

    def argMaxRetailStyleCV(self, Wtemp, tid):
        max_CV = -1
        max_id = -1
        for wid in Wtemp:
            CV = self.getRetailStyleCV(tid, wid)
            if CV > max_CV:
                max_CV = CV
                max_id = wid
        return max_id

    def RetailStyleAllocation2(self):  # ok
        # return dict
        start = tc.clock()
        allocation_dict = {}
        W = [i for i in range(len(self.worker_skills))]
        T = [i for i in range(len(self.task_skills))]
        # 按照截止时间排序
        listLength = len(T)
        while listLength > 0:
            for i in range(listLength - 1):
                if timeIsEarly(self.task_due_date[T[i + 1]], self.task_due_date[T[i]]):
                    T[i] = T[i] + T[i + 1]
                    T[i + 1] = T[i] - T[i + 1]
                    T[i] = T[i] - T[i + 1]
            listLength -= 1
        # 按照截止时间排序
        Wtime = [0 for i in range(len(self.worker_skills))]
        i = 0
        while i < len(T):
            tid = T[i]
            c1 = 0
            Wtemp = copy.copy(W)
            while c1 == 0:
                wid = self.argMaxRetailStyleCV(Wtemp, tid)
                c2 = 0
                if self.task_budget[tid] < self.worker_wage[wid] and Wtime[wid] + self.worker_task_estimated_completed_time[wid][tid] < self.task_due_date[tid]:
                    c2 = 1
                    Wtime[wid] += self.worker_task_estimated_completed_time[wid][tid]
                if c2 == 0:
                    if wid in allocation_dict:
                        allocation_dict[wid].append(tid)
                    else:
                        allocation_dict[wid] = [tid]
                    c1 = 1
                Wtemp.remove(wid)
                if len(Wtemp) == 0:
                    c1 = 1
            i += 1
        end = tc.clock()
        print end - start
        return allocation_dict

    def OverlappingDegreeOfBatch(self, B1, B2):  # ok
        set_B1 = []
        for i in range(len(B1)):
            set_B1.extend(self.task_skills[B1[i]])
        set_B1 = set(set_B1)
        set_B2 = []
        for i in range(len(B2)):
            set_B2.extend(self.task_skills[B2[i]])
        set_B2 = set(set_B2)
        up = set_B1 & set_B2
        down = set_B1 | set_B2
        return float(len(up)) / len(down)

    def BatchMerge(self, B1, B2):  # ok
        # accoding publishtime 归并排序
        i = 0
        j = 0
        newBatch = []
        while i < len(B1) and j < len(B2):
            if timeIsEarly(self.task_publishtime[B1[i]], self.task_publishtime[B2[j]]):
            # if timeIsEarly(self.task_due_date[B1[i]], self.task_due_date[B2[j]]):
                newBatch.append(B1[i])
                i += 1
            else:
                newBatch.append(B2[j])
                j += 1
        while i < len(B1):
            newBatch.append(B1[i])
            i += 1
        while j < len(B2):
            newBatch.append(B2[j])
            j += 1
        return newBatch

    def LayeredBatchFormation(self):   # ok
        # init, every task is a batch
        BatchList = [[i] for i in xrange(len(self.task_skills))]
        i = 1
        Layer = {}
        Layer[i] = BatchList
        c = 0
        if len(Layer[i]) == 1:
            c = 1
        while c == 0:
            Max_O = -1
            x = 0
            y = 0
            for j in xrange(len(Layer[i])):
                for k in xrange(len(Layer[i])):
                    if j == k:
                        continue
                    Ojk = self.OverlappingDegreeOfBatch(Layer[i][j], Layer[i][k])
                    if Ojk > Max_O:
                        Max_O = Ojk
                        x = j
                        y = k
            if Max_O == -1:
                c = 1
            else:
                Bnew = self.BatchMerge(Layer[i][x], Layer[i][y])
                temp = []
                for t in xrange(len(Layer[i])):
                    if t != x and t != y:
                        tt = copy.deepcopy(Layer[i][t])
                        temp.append(tt)
                i += 1
                temp.append(Bnew)
                Layer[i] = temp
            if len(Layer[i]) == 1:
                c = 1
        return Layer

    def getBatchLayeredCVOfSingleWorker(self, workerid, Batch):  # ok
        skill_set = set(self.worker_skills[workerid])
        up = 0
        down = 0
        for tid in Batch:
            task_skill_set = set(self.task_skills[tid])
            down += len(self.task_skills[tid])
            up += len(skill_set & task_skill_set)
        CB = float(up) / down
        sum_Occ_up = 0
        for i in xrange(len(Batch)):
            sum_Occ_up += (float(self.worker_wage[workerid]) / (Psi(i + 1) * self.task_budget[Batch[i]]))
        Occ = 0
        if len(Batch) != 0:
            Occ = sum_Occ_up / float(len(Batch))
        sum_Est = 0
        for tid in Batch:
            sum_Est += float(self.worker_task_estimated_completed_time[workerid][tid])
        R = float(self.worker_reputation[workerid])
        avg_Est = 0
        if len(Batch) != 0:
            avg_Est = sum_Est / float(len(Batch))
        result = (self.lBeta[0] * CB + self.lBeta[1] * R) / (self.lBeta[2] * Occ + self.lBeta[3] * avg_Est)
        return result

    def getBatchLayeredCV(self, workerid, Batch):  # ok
        result = self.getBatchLayeredCVOfSingleWorker(workerid, Batch)
        sum = 0
        for wid in xrange(len(self.worker_skills)):
            if wid != workerid:
                sum += (self.getBatchLayeredCVOfSingleWorker(wid, Batch) / float(self.worker_distance[wid][workerid]))
        return self.lAlpha[0] * result + self.lAlpha[1] * sum

    def argMaxBatchLayeredCV(self, Wset, Batch):  # ok
        max_wid = -1
        max_CV = -1
        for wid in Wset:
            CV = self.getBatchLayeredCV(wid, Batch)
            if CV > max_CV:
                max_CV = CV
                max_wid = wid
        return max_wid

    def BatchLayeredAllocation(self, L):  # ok
        Layer = copy.deepcopy(L)
        i = len(Layer)
        c1 = 0
        allocation_dict = {}
        W = [v for v in xrange(len(self.worker_skills))]
        start = tc.clock()
        while i > 0 and c1 == 0:
            j = 0
            while j < len(Layer[i]):
                batch = Layer[i][j]
                c2 = 0
                Wtemp = copy.copy(W)
                while c2 == 0:
                    wid = self.argMaxBatchLayeredCV(Wtemp, batch)
                    time = 0
                    c3 = 0
                    for t in xrange(len(batch)):
                        tid = batch[t]
                        time = time + self.worker_task_estimated_completed_time[wid][tid]
                        if time > self.task_due_date[tid]:
                            c3 = 1
                        if Psi(t + 1) * self.task_budget[tid] < self.worker_wage[wid]:
                            c3 = 1
                    if c3 == 0:
                        allocation_dict[wid] = batch
                        W.remove(wid)
                        c2 = 1
                        Layer[i].remove(batch)
                        for k in xrange(1, i):
                            e = 0
                            while e < len(Layer[k]):
                                b = Layer[k][e]
                                relation = set(b).difference(batch)
                                if len(relation) == 0:  # b 被包含于 batch
                                    Layer[k].remove(b)
                                    e -= 1
                                e += 1
                        j -= 1
                    Wtemp.remove(wid)
                    if len(Wtemp) == 0:
                        c2 = 1
                j += 1
            i -= 1
            if i > 0:
                if len(Layer[i]) == 0:
                    c1 = 1
        end = tc.clock()
        print end - start, 'time'
        return allocation_dict

    # core-based batch formation and allocation
    def OverlappingDegreeOfTask(self, tid1, tid2):  # ok
        set_T1 = set(self.task_skills[tid1])
        set_T2 = set(self.task_skills[tid2])
        up = set_T1 & set_T2
        down = set_T1 | set_T2
        return float(len(up)) / len(down)

    def argMaxSumOfSimilaritiesWithOtherTasks(self, TidSet):  # ok
        # TidSet
        max_sum = -1
        core_tid = -1
        for tid_i in TidSet:
            sum_similarity = 0
            for tid_j in TidSet:
                if tid_i != tid_j:
                    sum_similarity += self.OverlappingDegreeOfTask(tid_i, tid_j)
            if max_sum < sum_similarity:
                max_sum = sum_similarity
                core_tid = tid_i
        return core_tid

    def getCoreBasedCVOfSingleWorker(self, workerid, taskid):  # ok
        up = len(set(self.worker_skills[workerid]) & set(self.task_skills[taskid]))
        down = len(set(self.worker_skills[workerid]) | set(self.task_skills[taskid]))
        CB = float(up) / down
        R = float(self.worker_reputation[workerid])
        Occ = float(self.worker_wage[workerid]) / self.task_budget[taskid]
        Est = float(self.worker_task_estimated_completed_time[workerid][taskid])
        result = (self.cBeta[0] * CB + self.cBeta[1] * R) / (self.cBeta[2] * Occ + self.cBeta[3] * Est)
        return result

    def getCoreBasedCV(self, workerid, taskid):  # ok
        result = self.getCoreBasedCVOfSingleWorker(workerid, taskid)
        sum = 0
        for wid in xrange(len(self.worker_skills)):
            if wid != workerid:
                sum += (self.getCoreBasedCVOfSingleWorker(wid, taskid) / float(self.worker_distance[wid][workerid]))
        return self.cAlpha[0] * result + self.cAlpha[1] * sum

    def argMaxCoreBasedCV(self, Wset, taskid):  # ok
        max_wid = -1
        max_CV = -1
        for wid in Wset:
            CV = self.getCoreBasedCV(wid, taskid)
            if CV > max_CV:
                max_CV = CV
                max_wid = wid
        return max_wid

    def argMaxCoreBasedSimilarTask(self, core_tid, TidSet):  # ok
        max_id = -1
        max_theta = -1
        for tid in TidSet:
            if tid != core_tid:
                theta = self.OverlappingDegreeOfTask(core_tid, tid)
                if max_theta < theta:
                    max_theta = theta
                    max_id = tid
        return max_id

    def CoreBasedBatchAllocation(self):  # ok
        c1 = 0
        TidSet = [i for i in xrange(len(self.task_skills))]
        W = [i for i in xrange(len(self.worker_skills))]
        allocation_dict = {}
        while c1 == 0:
            core_tid = self.argMaxSumOfSimilaritiesWithOtherTasks(TidSet)
            k = 1
            c2 = 1
            Wtemp = copy.copy(W)
            c3 = 1
            time = 0
            while c2 == 1:
                wid = self.argMaxCoreBasedCV(Wtemp, core_tid)
                if self.worker_task_estimated_completed_time[wid][core_tid] <= self.task_due_date[core_tid] and Psi(1) * self.task_budget[core_tid] >= self.worker_wage[wid]:
                    time += self.worker_task_estimated_completed_time[wid][core_tid]
                    TidSet.remove(core_tid)
                    c2 = 0
                    c3 = 0
                    allocation_dict[wid] = [core_tid]
                    W.remove(wid)
                Wtemp.remove(wid)
            TidSetTemp = copy.copy(TidSet)
            if len(TidSetTemp) == 0:
                c3 = 1
            while c3 == 0:
                tb = self.argMaxCoreBasedSimilarTask(core_tid, TidSetTemp)
                if tb != -1:
                    if time + self.worker_task_estimated_completed_time[wid][tb] <= self.task_due_date[tb] and Psi(k + 1) * self.task_budget[tb] >= self.worker_wage[wid]:
                        time += self.worker_task_estimated_completed_time[wid][tb]
                        k += 1
                        allocation_dict[wid].append(tb)
                        TidSet.remove(tb)
                    TidSetTemp.remove(tb)
                if len(TidSetTemp) == 0:
                    c3 = 1
            if len(TidSet) == 0:
                c1 = 1
        return allocation_dict

if __name__ == "__main__":
    crowds = CrowdSourcing()
    crowds.task_budget = [18, 17, 18, 18, 19, 19]
    #print crowds.PaymentOfBatch([i for i in range(6)])
    crowds.rAlpha = [0.1, 0.1, 0.8]
    crowds.task_skills = [[1, 5, 4], [1, 3], [2, 4], [5, 3], [1, 2], [2, 3, 5, 4]]
    crowds.worker_wage = [5, 3, 6, 7, 4, 4]
    crowds.worker_skills = [[2, 3], [1, 8], [2, 4], [1, 3, 5], [4, 3, 1], [2]]
    for i in range(len(crowds.task_skills)):
        for j in range(len(crowds.worker_skills)):
            print i, j, crowds.task_skills[i], crowds.worker_skills[j], crowds.RetailTaskSkillCoverage(i, j)
    crowds.worker_reputation = [1, 3, 5, 4, 4, 2]
    for i in range(len(crowds.task_skills)):
        for j in range(len(crowds.worker_skills)):
            print i, j, crowds.getRetailStyleCV(i, j)
    print crowds.RetailStyleAllocation()
    B1 = [0, 3, 4]
    B2 = [1, 2, 5]
    print crowds.OverlappingDegreeOfBatch(B1, B2)
    print B1
    print B2
    crowds.task_publishtime = [0, 4, 2, 2, 3, 3]
    layer = crowds.LayeredBatchFormation()
    print layer
    crowds.worker_task_estimated_completed_time = [[1, 4, 6, 5, 7, 2],
                                                   [2, 3, 4, 3, 5, 1],
                                                   [1, 4, 5, 2, 7, 2],
                                                   [0, 5, 6, 4, 7, 2],
                                                   [1, 4, 3, 2, 6, 3],
                                                   [2, 3, 5, 3, 7, 2]]
    crowds.lBeta = [0.3, 0.2, 0.3, 0.2]
    for i in range(1, 7):
        print i, Psi(i)
    print crowds.getBatchLayeredCVOfSingleWorker(3, B1)
    crowds.worker_distance = [[0, 1, 2, 3, 4, 5],
                              [1, 0, 1, 2, 3, 4],
                              [2, 1, 0, 1, 2, 3],
                              [3, 2, 1, 0, 1, 2],
                              [4, 3, 2, 1, 0, 1],
                              [5, 4, 3, 2, 1, 0]]
    crowds.lAlpha = [1.0, 0.0]
    print crowds.getBatchLayeredCV(3, B1)
    print crowds.argMaxBatchLayeredCV([i for i in range(6)], B1)
    crowds.task_due_date = [30, 31, 30, 35, 40, 36]
    print crowds.BatchLayeredAllocation(layer)
    #print layer
    start = tc.clock()
    print crowds.RetailStyleAllocation()
    end = tc.clock()
    print end - start
    print crowds.OverlappingDegreeOfTask(0, 5)
    core_id = crowds.argMaxSumOfSimilaritiesWithOtherTasks([i for i in range(6)])
    crowds.cBeta = [0.3, 0.2, 0.3, 0.2]
    print crowds.getCoreBasedCVOfSingleWorker(2, 5)
    crowds.cAlpha = [0.5, 0.5]
    print crowds.getCoreBasedCV(1, 5)
    print crowds.argMaxCoreBasedCV([i for i in range(6)], 5)
    print 'core_id'
    print core_id
    print crowds.argMaxCoreBasedSimilarTask(core_id, [i for i in range(6)])
    print crowds.CoreBasedBatchAllocation()
    print crowds.RetailStyleAllocation2()
