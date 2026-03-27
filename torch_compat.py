"""
Aureum PyTorch Compatibility Layer
Minimal PyTorch-like API for migration path

Usage:
    import aureum.torch_compat as torch
    # or
    from aureum import Tensor, nn

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

from typing import List, Union, Optional
from .numpy_compat import AureumArray, array as aureum_array
from .frontend.aureum_stdlib import AureumModel

class Tensor(AureumArray):
    """PyTorch-like Tensor backed by Aureum"""
    
    def __init__(self, data):
        super().__init__(data)
        self.requires_grad = False
    
    def __repr__(self):
        return f"Tensor({self._data})"
    
    def size(self):
        """Return shape (simplified for 1D)"""
        return (len(self._data),)
    
    def item(self):
        """Get scalar value"""
        if len(self._data) == 1:
            return self._data[0]
        raise ValueError("Only one element tensors can be converted to scalars")


class Module:
    """Base class for neural network modules"""
    
    def __init__(self):
        self._parameters = {}
    
    def forward(self, x):
        raise NotImplementedError
    
    def __call__(self, x):
        return self.forward(x)


class Linear(Module):
    """Linear layer using Aureum kernel"""
    
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = None  # Will be ternary weights
        self.bias = None
        
        # Initialize with Aureum model
        self._model = AureumModel(
            input_dim=in_features,
            num_classes=out_features
        ).random_weights()
    
    def forward(self, x: Union[Tensor, List]) -> Tensor:
        """Forward pass using BitNet kernel"""
        if isinstance(x, Tensor):
            x = x.tolist()
        
        # Use Aureum classify for linear transformation
        result = self._model.classify(x)
        return Tensor([result.score])


class Sequential(Module):
    """Sequential container for layers"""
    
    def __init__(self, *layers):
        super().__init__()
        self.layers = layers
    
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


# Neural network module namespace
class nn:
    Module = Module
    Linear = Linear
    Sequential = Sequential


# Optimizer namespace (placeholder)
class optim:
    """Optimizer namespace (not implemented - Aureum uses ternary weights)"""
    
    class SGD:
        def __init__(self, *args, **kwargs):
            pass
        
        def step(self):
            pass
        
        def zero_grad(self):
            pass
