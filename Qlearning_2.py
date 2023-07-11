# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
version 1.0
1、基于Q-Learning框架
2、被测对象：BoundedDequeue.h
BoundedDequeue对象包含一下操作
(1)void pushBottom(int task)    对应操作数3
(2)int popBottom()              对应操作数1
(3)bool isEmpty()               对应操作数0
(4)int popTop()                 对应操作数2
3、operation序列有2，对应两条不同线程，其中一条序列固定 QB = [1, 2, 0, 3, 3, 2](可以为其他长度随机，操作随机)
QA为另一条序列（可变从长，最长长度暂定为6），起始为QA = [3]
4、状态定义为QA当前操作序列抽象而成的四叉树（因为被测并发结构有四种操作，所以为四叉树），由树的高度及偏移量两个维度组成
四叉树中每个结点到跟节点之间路径与操作序列一一对应
5、状态空间，即为高度为6的完全四叉树节点数量->1365

遇到问题：
1、显示头文件出错信息行数是否可以唯一确定一个data-race
2、每训练一次，env发现的并发漏洞不止1个，如何根据结果设置奖励函数
目前解决方案：设置一个列表储存已经发现的并发漏洞，在获得新的结果时比较是否发现新漏洞
（1）R不根据发现新漏洞数量而定：即只要发现新的漏洞且，reward设置为-1；未发现新漏洞，reward设置未-10；发现漏洞但不是新的，reward设置为-5
（2）R根据发现新漏洞数量变化而变化：这种情况下存在问题即为无法知道一次检测报告会存在多少新漏洞，reward最低值如何设置
3、QA初始值设置？ 直接设置为[] or 设置为[3]、[2]、[1]、[0]
4、使用Epsilon_greedy policy时，EPSILON值设置为多少？ 需要实验
5、PERIOD可能会卡住，需要加入控制
6、每幕终止条件如何设置：发现新错误即终止本幕还是QA延长到指定长度再终止
7、建立列表存储已经运行过的控制序列及其结果（即已经测试过的控制序列是否需要重新测试，原因是period运行同样控制序列生成的并发程序结果不同）

1、PERIOD增加控制
ps -ef 显示全部
ps -ef | grep PERIOD 显示某一个
2、reward选择T/n+1
3、增加read or write
4、初始值设置为[]
"""
import numpy as np
import pandas as pd
import time
import signal
import subprocess
# import docker

np.random.seed(2)  # reproducible

N_STATES = 1365                         # 状态空间大小，即为高度为6的完全四叉树上节点数量
ACTIONS = [0, 1, 2, 3]                  # 动作空间大小，0、1、2、3分别对应isEmpty()、popBottom()、popTop()、pushBottom(int task)
EPSILON = 0.8                           # greedy police，80%概率根据Q表来选择行为，20%概率随机选择行为
ALPHA = 0.1                             # learning rate
GAMMA = 0.9                             # discount factor
MAX_EPISODES = 10                       # maximum episodes
QA = [3]                                # QA初始状态
QB = [1, 2, 0, 3, 3, 2]                 # QB为固定状态
Error_set = []                          # 记录已经发现的并发漏洞


# 超时信号处理函数
def handle_timeout(signum, frame):
    raise Exception('代码执行超时')


# 创建Q表
def build_q_table(n_states, actions):
    table = pd.DataFrame(
        np.zeros((n_states, len(actions))),     # q_table initial values
        columns=actions,                        # actions's name
    )
    return table


# 选择action
def choose_action(QA, q_table):
    # 显示q_table前几行
    # top_rows = q_table.head(5)
    # print(top_rows)

    # This is how to choose an action
    state = getnum(QA)
    state_actions = q_table.iloc[state, :]                                  # iloc[state, :]表示访问Q表中第state行的所有列。
                                                                            # 这样做可以得到当前状态下所有动作的Q值。其中，:表示访问该行的所有列，相当于省略了列号。
    if (np.random.uniform() > EPSILON) or ((state_actions == 0).all()):     # act non-greedy or state-action have no value
        action_name = np.random.choice(ACTIONS)
    else:   # act greedy
        action_name = state_actions.idxmax()    # replace argmax to idxmax as argmax means a different function in newer version of pandas
    return action_name


# 将QA当前序列转化为树中对应节点，返回值为树的高度及在当前高度的偏移量
def getstate(QueueA):
    Height = len(QueueA)    # 树高
    offset = 0              # 偏移量
    x = 1
    # 先计算出高度为Height-1的完全n叉树节点数量
    for i in range(Height):
        if i < Height - 2:
            offset += x
            x *= len(ACTIONS)
    offset += x
    # 再计算（最低层）偏移量
    for i in range(Height):
        if (i != 0) & (i < Height - 1):
            # print("+", Queue[i] * k * n_actions, Queue[i], k , n_actions)
            offset += QueueA[i] * x
            x = int(x / len(ACTIONS))
    offset += QueueA[len(QueueA) - 1] + 1
    return Height, offset


# 将QA当前序列转化为树中对应节点，返回值在树中的节点序号
def getnum(QueueA):
    Height = len(QueueA)    # 树高
    if Height == 1:
        return 0
    else:
        num = 0              # 偏移量
        x = 1
        # 先计算出高度为Height-1的完全n叉树节点数量
        for i in range(Height):
            if i < Height - 2:
                num += x
                x *= len(ACTIONS)
        num += x
        # 再计算（最低层）偏移量
        for i in range(Height):
            if (i != 0) & (i < Height - 1):
                # print("+", Queue[i] * k * n_actions, Queue[i], k , n_actions)
                num += QueueA[i] * x
                x = int(x / len(ACTIONS))
        num += QueueA[len(QueueA) - 1]
        return num


# 从environment获得反馈并解析，给出本次发现的并发漏洞
def get_env_feedback(S_):
    # run Mars
    run1 = "python /workdir/mars/main_BD.py --suffix_labels1=\""
    for i in range(len(S_)):
        run1 += str(S_[i])
        run1 += ",0"
        if i < len(S_) - 1:
            run1 += ";"
        else:
            run1 += "\" --suffix_labels2=\""
    for i in range(len(QB)):
        run1 += str(QB[i])
        run1 += ",0"
        if i < len(QB) - 1:
            run1 += ";"
        else:
            run1 += "\""
    # res1 = subprocess.Popen(run1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)      # 使用管道
    timeout = 30                                    # 设置超时时间为20秒
    signal.signal(signal.SIGALRM, handle_timeout)   # 注册信号处理函数
    signal.alarm(timeout)                           # 启动定时器
    try:
        # 需要监测时间的代码行
        res1 = subprocess.Popen(run1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)      # 使用管道
    except Exception as e:
        # 如果捕获到异常，则说明代码执行超时
        print("mars延时")
        # 跳过当前行代码，接着执行下一行
        pass
    # 取消定时器
    signal.alarm(0)
    # print(res.stdout.read())                                                                      # 标准输出
    # lines = res1.stdout.read().decode().splitlines()
    res1.stdout.close()
    # for line in lines:
    #     print(line)

    # run PERIOD
    run2 = "/workdir/PERIOD/run.sh"
    # res2 = subprocess.Popen(run2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)      # 使用管道
    timeout = 30                                    # 设置超时时间为20秒
    signal.signal(signal.SIGALRM, handle_timeout)   # 注册信号处理函数
    signal.alarm(timeout)                           # 启动定时器
    try:
        # 需要监测时间的代码行
        res2 = subprocess.Popen(run2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)      # 使用管道
    except Exception as e:
        # 如果捕获到异常，则说明代码执行超时
        print("PERIOD延时")
        # 跳过当前行代码，接着执行下一行
        pass
    # 取消定时器
    signal.alarm(0)

    # print(res.stdout.read())                                                                      # 标准输出
    lines = res2.stdout.read().decode().splitlines()
    res2.stdout.close()
    # for line in lines:
    #     print(line)

    # 解析PERIOD输出结果
    find_error = False                  # 记录是否period每层深度下是否发现漏洞
    error_info = []                     # 记录漏洞信息
    error_path = "Found no data-race error_info"  # 记录保存出错信息的文件名
    singleerr = False
    singlepre = False
    single_err = []
    single_pre = []
    for line in lines:
        # print(line)
        if line.find("error_path:") >= 0:
            find_error = True
            error_path = "BoundedDequeue.h"
        if line.find("Error info:") >= 0 and find_error:
            singleerr = True
            singlepre = False
        if find_error and singleerr and line.find(error_path) >= 0:
            single_err.append(line)
        if line.find("Pre_info:") >= 0 and find_error:
            singleerr = False
            singlepre = True
        if find_error and singlepre and line.find(error_path) >= 0:
            single_pre.append(line)
        if line.find("another error") >= 0:
            # error_info.append(single_err, "+", single_pre)
            # print(single_err, "+", single_pre)
            ifexists = True
            for i in error_info:
                if i == (single_err, single_pre):
                    ifexists = False
            if ifexists:
                error_info.append((single_err, single_pre))
            single_err = []
            single_pre = []
        if line == "End of ErrorInfo":
            find_error = False
            singlepre = False
    return error_info


# 获得reward
def get_reward(error_info):
    R = -10                     # 奖励值
    new_error_num = 0           # 记录新发现的并发漏洞总数
    # 未发现并发漏洞
    if len(error_info) == 0:
        R = -10
    # 发现并发漏洞后要检查是否有重复发现的并发漏洞
    for i in error_info:
        if i not in Error_set:
            print("new error_info: ", i)
            Error_set.append(i)
            new_error_num += 1
    # R += new_error_num
    if new_error_num == 0:
        R = -5
    else:
        R = -1
    return R


# Agent模块
def rl():
    # main part of RL loop
    q_table = build_q_table(N_STATES, ACTIONS)
    episode_num = 0                             # 记录总幕数
    run_num = 0                                 # 记录总运行次数
    for episode in range(MAX_EPISODES):
        episode_num += 1
        print("NUM of EPSILON: ", episode_num)
        is_terminated = False                   # 每幕训练终止标志，终止有两种情况：发现并发漏洞 or QA长度延长到6
        QA = [3]                                # 每次重新训练时将QA重新置为[3]
        S = QA
        while not is_terminated:
            run_num += 1
            A = choose_action(S, q_table)      # 选择action
            S_ = []
            for i in S:
                S_.append(i)
            S_.append(A)
            print("S_: ", S_)

            error_info = get_env_feedback(S_)   # 得到env输出的漏洞报告
            # timeout = 30                                    # 设置超时时间为20秒
            # signal.signal(signal.SIGALRM, handle_timeout)   # 注册信号处理函数
            # signal.alarm(timeout)                           # 启动定时器
            # try:
            #     # 需要监测时间的代码行
            #     error_info = get_env_feedback(S_)   # 得到env输出的漏洞报告
            # except Exception as e:
            #     # 如果捕获到异常，则说明代码执行超时
            #     print("get_env_feedback延时")
            #     # 跳过当前行代码，接着执行下一行
            #     pass
            # # 取消定时器
            # signal.alarm(0)

            R = get_reward(error_info)          # 根据漏洞报告得到本次训练的奖励
            # S_, R = get_env_feedback(S, A)    # take action & get next state and reward
            q_predict = q_table.loc[getnum(S), A]
            # if S_ != 'terminal':
            # if len(S_) == 6:                    # 当QA长度延长到6时
            if len(S_) == 6 or R == -1:         # 当发现新并发漏洞(即R==-1)或QA长度延长到6时
                q_target = R                    # next state is terminal
                is_terminated = True            # terminate this episode
            else:
                q_target = R + GAMMA * q_table.iloc[getnum(S_), :].max()   # next state is not terminal

            # print("getnum(S): ", getnum(S))
            # print("pre: ", q_table.loc[getnum(S), :])
            q_table.loc[getnum(S), A] += ALPHA * (q_target - q_predict)  # update
            # print("post: ", q_table.loc[getnum(S), :])
            S = S_                              # 更新state

    # return q_table
    return Error_set, run_num


if __name__ == "__main__":
    # print(getstate([3, 3, 3, 3, 3]))
    # QA = [3, 2, 1]
    # print(get_env_feedback(QA))

    Error_set, run_num = rl()
    print("Total run times: ", run_num)
    new_list = []
    for i in Error_set:
        if i not in new_list:
            new_list.append(i)
    if len(new_list) == len(Error_set):
        print("没有重复元素")
    print("Number of total error: ", len(Error_set))
    print("Error_set: ")
    for i in Error_set:
        print(i)
