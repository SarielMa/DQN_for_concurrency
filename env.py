import os
#import commands //python3已删除
import subprocess

class stealQueue(object):
    def __init__(self):
        super(stealQueue, self).__init__()
        self.queue1 = [1,1,0,1,0,0]
        self.queue2 = [0,1,0,1,0,0]
        self.action_space = [0,1,2,3,4,5]
        self.n_actions = len(self.action_space)
        self.n_features = 12  # state/observation 里的特征数目
        self.max_step = 100
        self.steps = 0

    def step(self, action):
        self.steps += 1
        max_action = 2
        self.queue1[action] = (self.queue1[action] + 1)%max_action
        self.queue2[action] = (self.queue2[action] + 1)%max_action
        #当前状态 归一化
        state = (self.queue1 + self.queue2)/max_action 
        reward = self.getReward()
        end = False
        if self.steps >= self.max_step :
            end = True
            self.steps = 0
        return state, reward, end
    
    def reset(self) :
        self.queue1 = [1,1,0,1,0,0]
        self.queue2 = [0,1,0,1,0,0]
        self.steps = 0
    
    def getReward(self) :
        #defult: python dockerTest.py --suffix_labels1=\"1,0;1,0;0,0;1,0;0,0;0,0\" --suffix_labels2=\"0,0;1,0;0,0;1,0;1,0;1,0\"
        run = "python dockerTest.py --suffix_labels1=\""
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
        #调用period
        #os.system(run)
        #output = commands.getouput(run)
        output = subprocess.getoutput(run)
        return output


if __name__ == "__main__":
    testQ = stealQueue()
    reward = testQ.getReward()
    print(reward)
