import docker
q1 = [0,0,0,0,0,0,0,0]
q2 = [0,0,0,0,0,0,0,0]

class stealQueue(object):
    def __init__(self):
        super(stealQueue, self).__init__()
        self.queue1 = q1
        self.queue2 = q2
        self.action_space = [0,1,2,3,4,5,6,7]
        self.n_actions = len(self.action_space)
        self.n_features = len(q1) * 2  # state/observation 里的特征数目
        self.max_step = 10
        self.steps = 0
        client = docker.from_env()
        containerId = "ef22199e51c69421943234a98110001fa6ac37a94521367b4621554b3846e0f9"
        self.container = client.containers.get(containerId)
        self.someReword = {}
        self.max_action = 3

    def step(self, action):
        self.steps += 1
        self.queue2[action] = (self.queue2[action] + 1)%self.max_action
        #当前状态 归一化
        state = (self.queue1 + self.queue2) 
        state_ = [item/self.max_action for item in state]
        tupleS = tuple(state_)
        if self.someReword.get(tupleS) is not None:
            reward = self.someReword[tupleS]
        else :
            reward = self.getReward()
            self.someReword[tupleS] = reward
        end = False
        if self.steps >= self.max_step :
            end = True
            self.steps = 0
        return state_, reward, end
    
    def reset(self) :
        self.queue1 = q1
        self.queue2 = q2
        self.steps = 0
        state = (self.queue1 + self.queue2)
        state_ = [item/self.max_action for item in state]
        return state_
    
    def getReward(self) :
        #defult: python dockerTest.py --suffix_labels1=\"1,0;1,0;0,0;1,0;0,0;0,0\" --suffix_labels2=\"0,0;1,0;0,0;1,0;1,0;1,0\"
        run = "python /workdir/PERIOD/test/mars/test.py --suffix_labels1=\""
        for i in range(int(self.n_features/2)) :
            run += str(self.queue1[i])
            run += ",0"
            if i < self.n_features/2 - 1 :
                run += ";"
            else :
                run += "\""
        run += "--suffix_labels2=\""
        for i in range(int(self.n_features/2)) :
            run += str(self.queue2[i])
            run += ",0"
            if i < self.n_features/2 - 1 :
                run += ";"
            else :
                run += "\""
        #docker run period
        ping = self.container.exec_run(run)
        lines = ping.output.decode("utf-8").split("\n")
        reward = 0
        for line in lines :
            print (line)
            if line.find("Error")>=0 and line.find("Interleavings")>=0 :
                nums = line.split(" ")
                reward = nums[3]
                break
        return int(reward)
    
    def getReward_rasn(self) :
        #defult: python dockerTest.py --suffix_labels1=\"1,0;1,0;0,0;1,0;0,0;0,0\" --suffix_labels2=\"0,0;1,0;0,0;1,0;1,0;1,0\"
        run = "python /workdir/PERIOD/test/mars/test.py --suffix_labels1=\""
        for i in range(int(self.n_features/2)) :
            run += str(self.queue1[i])
            run += ",0"
            if i < self.n_features/2 - 1 :
                run += ";"
            else :
                run += "\""
        run += "--suffix_labels2=\""
        for i in range(int(self.n_features/2)) :
            run += str(self.queue2[i])
            run += ",0"
            if i < self.n_features/2 - 1 :
                run += ";"
            else :
                run += "\""
        #docker run period
        ping = self.container.exec_run(run)
        lines = ping.output.decode("utf-8").split("\n")
        reward = 0
        for line in lines :
            print (line)
            if line.find("Error")>=0 and line.find("Interleavings")>=0 :
                nums = line.split(" ")
                reward = nums[3]
                break
        return int(reward)

'''
if __name__ == "__main__":
    testQ = stealQueue()
    reward = testQ.getReward()
    print(type(reward))
    print(reward)
'''