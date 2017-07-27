from operators.base import Operator


class SelectTopConformer(Operator):
    def __call__(self, *args, **kwargs):
        kwargs.update ( {'pdb': kwargs['pdbs'].pdbs[0]} )
        return kwargs