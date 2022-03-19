import pandas as pd
from typing import List, Optional, Set, Tuple


def debloat(edges: set, nodes: int, threshold: float = 0.95) -> Set[Tuple[str, str]]:
    """Remove nodes with outflow and/or inflow > threshold"""
    df = pd.DataFrame(list(edges), columns=["source", "target"])
    df["outflow"] = df.groupby("source")["target"].transform("count")
    df["inflow"] = df.groupby("target")["source"].transform("count")
    df["outflow_ratio"] = df["outflow"] / nodes
    df["inflow_ratio"] = df["inflow"] / nodes
    df = df[(df["outflow_ratio"] <= threshold) & (df["inflow_ratio"] <= threshold)]
    df.drop(["outflow", "inflow", "outflow_ratio", "inflow_ratio"], axis=1, inplace=True)
    return set(tuple(i) for i in df.values.tolist())
