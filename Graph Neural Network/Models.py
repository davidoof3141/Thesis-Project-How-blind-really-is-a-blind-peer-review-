import torch.nn as nn
from dgl.nn import GraphConv
import torch.nn.functional as F
import torch
import torch as th

from dgl.nn import SAGEConv

# ----------- 2. create model -------------- #
# build a two-layer GraphSAGE model
class GraphSAGELinkPrediction(nn.Module):
    def __init__(self, in_feats, h_feats):
        super(GraphSAGE, self).__init__()
        self.conv1 = SAGEConv(in_feats, h_feats, 'mean')
        self.conv2 = SAGEConv(h_feats, h_feats, 'mean')

    def forward(self, g, in_feat):
        h = self.conv1(g, in_feat)
        h = F.relu(h)
        h = self.conv2(g, h)
        return h
class GraphClassificationModelCrossEntropy(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super(GraphClassificationModelCrossEntropy, self).__init__()
        self.conv1 = GraphConv(in_dim, out_dim, allow_zero_in_degree=True)
        #self.conv2 = GraphConv(hidden_dim, out_dim, allow_zero_in_degree=True)

    def forward(self, g, features):
        h = self.conv1(g, features)
        #h = F.relu(h)
        #h = self.conv2(g, h)
        return h

    def fit(self, epochs, graph, optimizer):
        train_mask = graph.ndata['train_mask']
        #val_mask = graph.ndata['val_mask']
        labels = graph.ndata['label']
        features = graph.ndata['feat'].float()
        for epoch in range(epochs):
            logits = self(graph, features)
            loss = F.cross_entropy(logits[train_mask].float(), labels[train_mask].float())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if epoch % 10 == 0:
                # Evaluation loop
                with torch.no_grad():
                    logits = self(graph, features)
                    pred = logits.argmax(1)
                    train_acc = (pred[train_mask] == labels[train_mask]).float().mean()
                    #val_acc = (logits[val_mask].argmax(1) == labels[val_mask]).float().mean().item()
                    val_acc = 0
                    print(f'Epoch {epoch}: loss={loss:.4f}, train_acc={train_acc:.4f}, val_acc={val_acc:.4f}')


class GraphClassificationModelBinaryCrossEntropy(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super(GraphClassificationModelBinaryCrossEntropy, self).__init__()
        self.conv1 = GraphConv(in_dim, out_dim, allow_zero_in_degree=True)
        #self.conv2 = GraphConv(hidden_dim, hidden_dim, allow_zero_in_degree=True)
        #self.conv3 = GraphConv(hidden_dim, out_dim, allow_zero_in_degree=True)

    def forward(self, g, features):
        h = self.conv1(g, features)
        #h = F.relu(h)
        #h = self.conv2(g, h)
        #h = self.conv3(g, h)
        return h

    def fit(self, epochs, graph, optimizer):
        train_mask = graph.ndata['train_mask']
        #val_mask = graph.ndata['val_mask']
        labels = graph.ndata['label']
        features = graph.ndata['feat'].float()
        for epoch in range(epochs):
            logits = self(graph, features)
            loss = F.binary_cross_entropy_with_logits(logits[train_mask], labels[train_mask].float())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if epoch % 1 == 0:
                # Evaluation loop
                with torch.no_grad():
                    logits = self(graph, features)
                    train_acc_matches = []
                    for id, index in enumerate(torch.max(logits[train_mask], dim=1)[1]):
                        if labels[train_mask][id][index] == 1:
                            train_acc_matches.append(1)
                        else:
                            train_acc_matches.append(0)
                    train_acc = sum(train_acc_matches) / len(train_acc_matches)
                    """
                    val_acc_matches = []
                    for id, index in enumerate(torch.max(torch.softmax(logits[val_mask], dim=1), dim=1)[1]):
                        if labels[val_mask][id][index] == 1:
                            val_acc_matches.append(1)
                        else:
                            val_acc_matches.append(0)
                    val_acc = sum(val_acc_matches) / len(val_acc_matches)
                    """
                    val_acc = 0
                    print(f'Epoch {epoch}: loss={loss:.4f}, train_acc={train_acc:.4f}, val_acc={val_acc:.4f}')

    def predict(self, graph, nodes_mask):
        features = graph.ndata['feat'].float()
        with torch.no_grad():
            logits = self(graph, features)[nodes_mask]
            return torch.max(torch.softmax(logits, dim=1), dim=1)[1]


