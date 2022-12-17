import torch

class Loss(object):
    """A simple wrapper class for loss calculation"""

    def __init__(self, model, device):
        self.model = model
        self.device = device
        self.criterion = torch.nn.CTCLoss(reduction='sum').to(self.device)

    def calculate_loss(self, inputs, input_sizes, targets, target_sizes):
        """Calculate CTC loss.
        Args:
            logits: N x T x C, score before softmax
            logits_sizes: number of timesteps of logits 
            targets: N x T
            target_sizes: number of timesteps of targets
        """
        print(inputs)
        print(input_sizes)
        print(targets)
        print(target_sizes)
        inputs = inputs.to(self.device)
        input_sizes = input_sizes.to(self.device)
        targets = targets.to(self.device)
        target_sizes = target_sizes.to(self.device)

        logits, logit_sizes = self.model(inputs, input_sizes) # THIS IS THE ACTUAL FORWARD PASS -- Goes to main forward pass function
        out = logits.transpose(0, 1)  # TxNxC
        out = out.log_softmax(-1)

        print("Output size is: ")
        print(out.size())
        print(out)
    
        out = out.float()  # ensure float32 for loss
        loss = self.criterion(out, targets, logit_sizes, target_sizes) # CALCULATION OF CTC LOSS
        print("Loss is: ")
        print(loss)
        loss = loss / logits.size(0)  # average the loss by minibatch
        print(loss)

        if loss.item() == float("inf") or loss.item() == float("-inf"):
            raise Exception("WARNING: received an inf loss")
        if torch.isnan(loss).sum() > 0:
            raise Exception('WARNING: received a nan loss')
        if loss.item() < 0:
            raise Exception("WARNING: received a negative loss")
        print("Loss is: ")
        print(loss)
        return loss