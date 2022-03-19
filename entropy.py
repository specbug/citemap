import pandas as pd
from typing import List, Optional, Set, Tuple


def debloat(edges: set, nodes: int, threshold: tuple = (0.95, 0.95)) -> Set[Tuple[str, str]]:
    """Remove nodes with inflow and/or ourflow > threshold"""
    df = pd.DataFrame(list(edges), columns=["source", "target"])
    checkpoint_shape = df.shape[0]
    df_inflow = df.groupby("target").count().reset_index().rename(columns={"source": "inflow"})
    df_outflow = df.groupby("source").count().reset_index().rename(columns={"target": "outflow"})
    df = df.merge(df_inflow, on="target", how="left")
    df = df.merge(df_outflow, on="source", how="left")
    df["inflow_ratio"] = df["inflow"] / nodes
    df["outflow_ratio"] = df["outflow"] / nodes
    df = df[(df["inflow_ratio"] <= threshold[0]) & (df["outflow_ratio"] <= threshold[1])]
    print(f"{checkpoint_shape - df.shape[0]} edges removed")
    df.drop(["outflow", "inflow", "outflow_ratio", "inflow_ratio"], axis=1, inplace=True)
    return set(tuple(i) for i in df.values.tolist())
