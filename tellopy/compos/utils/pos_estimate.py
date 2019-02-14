#!/usr/bin/python3

import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from sklearn.preprocessing import MinMaxScaler

import pandas as pd
import numpy as np

torch.set_default_tensor_type('torch.cuda.FloatTensor')
class Net(torch.nn.Module):
    def __init__(self, n_feature, n_hidden, n_output):
        super(Net, self).__init__()
        self.features_x = self._make_layers(n_feature-3,n_hidden)
        self.predict_x_2 = nn.Linear(n_hidden[-1],n_output)
        self.predict_x_1 = nn.Sequential(
                            nn.Linear(3,n_hidden[-1]),
                            nn.LeakyReLU(0.01),
                            nn.BatchNorm1d(n_hidden[-1]),
                            )
        self.hidden_x_2 = nn.Sequential(
                            nn.Linear(n_hidden[-1],n_hidden[-1]),
                            nn.LeakyReLU(0.01),
                            nn.BatchNorm1d(n_hidden[-1]),
                            nn.Linear(n_hidden[-1],n_hidden[-1]),
                            nn.LeakyReLU(0.01),
                            nn.BatchNorm1d(n_hidden[-1]),
                            nn.Linear(n_hidden[-1],n_hidden[-1]),
                            nn.LeakyReLU(0.01),
                            nn.BatchNorm1d(n_hidden[-1]),
                            )
        
        
        self.features_y = self._make_layers(n_feature-3,n_hidden)
        self.predict_y_2 = nn.Linear(n_hidden[-1],n_output)
        self.predict_y_1 = nn.Sequential(
                            nn.Linear(3,n_hidden[-1]),
                            nn.LeakyReLU(0.01),
                            nn.BatchNorm1d(n_hidden[-1]),
                            )
        self.hidden_y_2 = nn.Sequential(
                            nn.Linear(n_hidden[-1],n_hidden[-1]),
                            nn.LeakyReLU(0.01),
                            nn.BatchNorm1d(n_hidden[-1]),
                            nn.Linear(n_hidden[-1],n_hidden[-1]),
                            nn.LeakyReLU(0.01),
                            nn.BatchNorm1d(n_hidden[-1]),
                            nn.Linear(n_hidden[-1],n_hidden[-1]),
                            nn.LeakyReLU(0.01),
                            nn.BatchNorm1d(n_hidden[-1]),
                            )

    def forward(self, inputs):
        outx = self.features_x(inputs[:,3:])
        outx2 = self.predict_x_1(inputs[:,:3])       
        outx += outx2
        outx = self.hidden_x_2(outx)
        outx = self.predict_x_2(outx)
        
        outy = self.features_y(inputs[:,3:])
        outy2 = self.predict_y_1(inputs[:,:3])       
        outy += outy2
        outy = self.hidden_y_2(outy)
        outy = self.predict_y_2(outy)
        return outx ,outy

    def _make_layers(self, n_feature, n_hidden):
        layers = []
        
        in_channels = n_feature
        for x in n_hidden:
            layers += [nn.Linear(in_channels, x),
                       nn.LeakyReLU(0.01),
                       nn.BatchNorm1d(x),
                       #nn.Dropout(0.5)
                      ]
            in_channels = x
        #layers += [nn.Dropout(0.5)]
        return nn.Sequential(*layers)



class PosEstimate:
    def __init__(self, path_to_model, path_to_dataset):
        self.alldata = pd.read_csv(path_to_dataset, index_col=0)
        mat_ = pd.concat([self.alldata['tposx'],self.alldata['tposy']],axis=1)
        self.mat_targ = np.array(mat_).reshape((self.alldata.shape[0],2))

        self.mat_features =\
                    np.matrix(self.alldata.drop(['tposx','tposy','tposz','tvelx','tvely','tvelz'],axis=1))
        self.prepro = MinMaxScaler(feature_range=(-1,1))
        self.prepro.fit(self.mat_features)
        self.prepro_targ = MinMaxScaler(feature_range=(-1,1))
        self.prepro_targ.fit(self.mat_targ)


        self.col_train_bis = list(self.alldata.columns)
        self.col_train_bis.remove('tposx')
        self.col_train_bis.remove('tposy')
        self.col_train_bis.remove('tposz')
        self.col_train_bis.remove('tvelx')
        self.col_train_bis.remove('tvely')
        self.col_train_bis.remove('tvelz')
        self.FEATURES = np.array(self.col_train_bis)
        self.TARGETS = np.array(['tposx','tposy'])

        self.model = torch.load(path_to_model)
        self.model.eval()

    def model_eval(self,model, features):
        mm = np.array([features])
        inputs = torch.from_numpy(mm).float()
        inputs = inputs.to('cuda')
        output = model(inputs)
        return output

    def estimate(self,features):
        '''
        Args:
            features (list): 15 drone state
        '''
        data_features = pd.DataFrame(self.prepro.transform([features]), columns = self.FEATURES)
        data_features = list(data_features.loc[0])

        outputs = pd.DataFrame([],columns=['tposx','tposy'])

        modelOutputs = self.model_eval(self.model, data_features)
        for m,n in zip(modelOutputs[0],modelOutputs[1]):
                outputs = outputs.append({'tposx':m.data[0],'tposy':n.data[0]},ignore_index=True)

        predection = pd.DataFrame(self.prepro_targ.inverse_transform(outputs))

        return float(predection[0]), float(predection[1])







if __name__ == "__main__":
    test = PosEstimate("../model/bestmodel_bothxy.pth","../model/alldata.csv")








