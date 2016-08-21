#! /usr/bin/env python
# coding=utf-8
import math
import copy


def Psi(x):
    # x is positive integer
    # it is decreasing function,whose value field is (0, 1]
    return math.exp(-x + 1)


def timeIsEarly(A, B):
    # if A is early than B, return 1
    # else return 0
    pass


class CrowdSourcing(object):
    """docstring for CrowdSourcing"""

    def __init__(self):
        self.worker_skills = None  # 二维list 数字或者字符串
        self.worker_reputation = None  # 一维list 小数
        self.worker_wage = None  # 一维list 小数
        self.rAlpha = []  # Retail Style Alpha
        # 每一个task都有一个id, 从0开始
        self.task_skills = None  # 二维list 数字或者字符串
        self.task_budget = None  # 一维list 小数
        self.task_publishtime = None

    def init_worker_skills(self):
        pass

    def PaymentOfBatch(self, TaskBudget):
        # BatchBudget is a list of budget, which is sorted by publish time
        sum_payment = 0
        for i in range(len(TaskBudget)):
            sum_payment += Psi(i + 1) * TaskBudget[i]
        return sum_payment

    def RetailTaskSkillCoverage(self, taskSkill, workerSkill):
        set_taskSkill = set(taskSkill)
        set_workerSkill = set(workerSkill)
        return len(set_taskSkill & set_workerSkill)

    def getRetailStyleCV(self, tSkill, wSkill, rep, wage):
        t1 = self.RetailTaskSkillCoverage(tSkill, wSkill)
        t2 = rep
        t3 = wage
        return (self.rAlpha[0] * t1 + self.rAlpha[1] * t2) / (self.rAlpha[2] * t3)

    def RetailStyleAllocation(self):
        # return dict
        allocation_dict = {}
        for i in range(len(self.task_skills)):
            max_CV = 0
            max_id = -1
            for j in range(len(self.worker_skills)):
                CV = self.getRetailStyleCV(self.task_skills[i], self.worker_skills[j], self.worker_reputation[j], self.worker_wage[j])
                if max_CV <= CV:
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

    def OverlappingDegreeOfBatch(self, B1, B2):
        set_B1 = []
        for i in range(len(B1)):
            set_B1.extend(B1[i])
        set_B1 = set(B1)
        set_B2 = []
        for i in range(len(B2)):
            set_B2.extend(B2[i])
        set_B2 = set(B2)
        up = set_B1 & set_B2
        down = set_B1 | set_B2
        return len(up) / down(down)

    def BatchMerge(self, B1, B2):
        # accoding publishtime 归并排序
        pass

    def LayeredBatchFormation(self):
        # init, every task is a batch
        BatchList = [[i] for i in range(self.task_skills)]
        Layer = {}
        Layer[i] = BatchList
        i = 1
        c = 0
        if len(Layer[i]) == 1:
            c = 1
        while c == 0:
            Max_O = 0
            x = 0
            y = 0
            for j in range(len(Layer[i])):
                for k in range(len(Layer[i])):
                    if j == k:
                        continue
                    Ojk = self.OverlappingDegreeOfBatch(Layer[i][j], Layer[i][k])
                    if Ojk > Max_O:
                        Max_O = Ojk
                        x = j
                        y = k
            if Max_O == 0:
                c = 1
            else:
                Bnew = self.MergeBatch(Layer[i][x], Layer[i][y])
                temp = []
                for t in range(len(Layer[i])):
                    if t != x and t != y:
                        tt = copy.deepcopy(Layer[i][t])
                        temp.append(tt)
                i += 1
                Layer[i] = temp.append(Bnew)
            if len(Layer[i]) == 1:
                c = 1
        return Layer


if __name__ == "__main__":
    BatchList = [[i] for i in range(10)]
    print BatchList
