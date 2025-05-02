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

# Arquivo com todas as funcoes e codigos referentes ao preprocessamento

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import pandas as pd
import unicodedata
import re


def agrupar_hda(sintoma):
    if sintoma == "Assintomático":
        return "assintomatica"
    elif sintoma in [
        "Dor precordial",
        "Dispneia",
        "Palpitação",
        "Cianose",
        "Desmaio/tontura",
    ]:
        return "sintomas_cardiacos"
    elif sintoma == "Ganho de peso":
        return "sintomas_gerais"
    else:
        return "outro"


def agrupar_pulsos(sintoma):
    if sintoma == "Normais":
        return "normais"
    elif sintoma in ["Amplos", "Femorais diminuidos", "Diminuídos"]:
        return "alterados"
    else:
        return "outro"


def agrupar_b2(sintoma):
    if sintoma == "Normal":
        return "normal"
    elif sintoma in ["Hiperfonética", "Desdob fixo", "Única"]:
        return "alterado"
    else:
        return "outro"


def agrupar_motivo1(motivo):
    if motivo in [
        "1 - Cardiopatia já estabelecida",
        "6 - Suspeita de cardiopatia",
        "5 - Parecer cardiológico",
    ]:
        return "condicao_cardiaca"
    elif motivo == "2 - Check-up":
        return "check_up"
    else:
        return "outro"


def agrupar_ppa(ppa):
    if ppa == "Normal":
        return "normal"
    elif ppa == "Não Calculado":
        return "nao_calculado"
    elif ppa in ["Pre-Hipertensão PAD", "Pre-Hipertensão PAS"]:
        return "pre_hipertensao"
    elif ppa in ["HAS-2 PAS", "HAS-2 PAD", "HAS-1 PAS", "HAS-1 PAD"]:
        return "hipertensao"
    else:
        return "outro"


to_replace_map = {
    "sexo": {
        "F": "feminino",
        "M": "masculino",
        "Feminino": "feminino",
        "Masculino": "masculino",
        "Indeterminado": "indeterminado",
    },
    "sopro": {
        "Sistólico": "sistolico",
        "Contínuo": "continuo",
        "contínuo": "continuo",
        "sistólico": "sistolico",
        "diastólico": "diastolico",
        "Sistolico e diastólico": "sistolico",
    },
}

to_apply_map = {
    "hda_1": agrupar_hda,
    "pulsos": agrupar_pulsos,
    "b2": agrupar_b2,
    "motivo1": agrupar_motivo1,
    "ppa": agrupar_ppa,
}


def clean_column_names(df):
    df.columns = [normalize_string(col) for col in df.columns]
    return df


def normalize_string(text):
    text = unicodedata.normalize("NFD", text)
    text = "".join([char for char in text if unicodedata.category(char) != "Mn"])
    text = text.lower()
    return re.sub(r"[^a-z0-9]+", "_", text)


def remove_outliers(df):
    df = df.drop(df[df["peso"] <= 0].index)
    df = df.drop(df[(df["idade"] <= 0) | (df["idade"] >= 22)].index)
    df = df.drop(df[df["imc"] > 100].index)
    df = df.drop(df[df["fc"] > 480].index)

    return df


def numerical_imputer(df):
    imputer = IterativeImputer(max_iter=200, initial_strategy="median")

    df_num = df.select_dtypes(include=["float64", "int64"]).drop(columns=["id"])

    original_std = df_num.std()
    original_mean = df_num.mean()

    df_num_norm = (df_num - original_mean) / original_std
    df_num_norm = pd.DataFrame(
        imputer.fit_transform(df_num_norm),
        columns=df_num_norm.columns,
        index=df_num.index,
    )

    df_num = df_num_norm * original_std + original_mean

    assert all(df_num.index == df.index)
    df.loc[:, df_num.columns] = df_num

    return df


def preprocess(df, test=False):
    columns_to_drop = [
        "atendimento",
        "convenio",
        "altura",
        "dn",
        "pa_sistolica",
        "pa_diastolica",
        "hda2",
        "motivo2",
    ]

    df = clean_column_names(df)
    if not test:
        df = remove_outliers(df)
    df = df.drop(columns=columns_to_drop)
    df = numerical_imputer(df)

    df = df.fillna({"sexo": "Indeterminado"})

    for column, dict in to_replace_map.items():
        df[column] = df[column].replace(dict)

    for column, transform_fn in to_apply_map.items():
        df[column] = df[column].apply(transform_fn)

    df = pd.get_dummies(
        df,
        columns=["sexo", "sopro", "hda_1", "pulsos", "b2", "motivo1", "ppa"],
        dtype=int,
    )

    if not test:
        df = df.dropna(
            subset=["classe"],
        )
        df["classe"] = df["classe"].apply(lambda x: 0 if x == "Normal" else 1)

    return df
