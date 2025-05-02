# ################################################################
# PROJETO FINAL
#
# Universidade Federal de Sao Carlos (UFSCAR)
# Departamento de Computacao - Sorocaba (DComp-So)
# Disciplina: Aprendizado de Maquina
# Prof. Tiago A. Almeida
#
#
# Nome: Vinícius Henrique de Proença Cavalcanti
# RA: 839901
# ################################################################

# Arquivo com todas as funcoes e codigos referentes aos experimentos


class ModelTrain:
    def __init__(self, model):
        self.__model = model

    def train(self, X, y):
        self.__model.fit(X, y)
        print(self.__model.best_params_)

    def get_model(self):
        return self.__model

    def get_model_name(self):
        return self.__model.estimator.__class__.__name__
