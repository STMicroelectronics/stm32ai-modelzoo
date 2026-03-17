import torch 

class SSDExportWrapper(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m
        self.register_buffer("priors", m.priors)

    def forward(self, x):
        conf, loc = self.m(x, decode=False)
        return conf, loc
        #return torch.concatenate([loc, conf], dim =2) 
            
            