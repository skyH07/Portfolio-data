"""Génère le jeu de données fictif de « L'Atelier Vert » (boutique de plantes imaginaire)."""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)

produits = [
    # id, nom, catégorie, prix, coût
    ("P01", "Monstera Deliciosa", "Plantes d'intérieur", 29.90, 12.00),
    ("P02", "Ficus Lyrata", "Plantes d'intérieur", 39.90, 16.50),
    ("P03", "Pothos Doré", "Plantes d'intérieur", 14.90, 5.20),
    ("P04", "Sansevieria", "Plantes d'intérieur", 19.90, 7.50),
    ("P05", "Calathea Orbifolia", "Plantes d'intérieur", 24.90, 10.10),
    ("P06", "Zamioculcas", "Plantes d'intérieur", 27.90, 11.20),
    ("P07", "Olivier En Pot", "Plantes d'extérieur", 59.90, 26.00),
    ("P08", "Lavande", "Plantes d'extérieur", 8.90, 3.20),
    ("P09", "Rosier Grimpant", "Plantes d'extérieur", 19.90, 7.80),
    ("P10", "Hortensia", "Plantes d'extérieur", 22.90, 9.00),
    ("P11", "Citronnier", "Plantes d'extérieur", 49.90, 22.00),
    ("P12", "Bambou Nain", "Plantes d'extérieur", 17.90, 7.00),
    ("P13", "Pot Terre Cuite 20 Cm", "Pots & cache-pots", 9.90, 3.50),
    ("P14", "Pot Terre Cuite 35 Cm", "Pots & cache-pots", 19.90, 7.00),
    ("P15", "Cache-Pot Céramique Blanc", "Pots & cache-pots", 24.90, 9.00),
    ("P16", "Jardinière Balcon 60 Cm", "Pots & cache-pots", 16.90, 6.00),
    ("P17", "Terreau Universel 40 L", "Terreaux & engrais", 11.90, 5.50),
    ("P18", "Terreau Plantes Vertes 20 L", "Terreaux & engrais", 9.90, 4.20),
    ("P19", "Engrais Liquide 1 L", "Terreaux & engrais", 8.90, 3.10),
    ("P20", "Billes D'Argile 10 L", "Terreaux & engrais", 7.90, 2.80),
    ("P21", "Sécateur Pro", "Outils", 29.90, 13.00),
    ("P22", "Arrosoir 10 L", "Outils", 14.90, 5.80),
    ("P23", "Gants De Jardinage", "Outils", 9.90, 3.00),
    ("P24", "Pulvérisateur 1 L", "Outils", 6.90, 2.20),
    ("P25", "Bougie Parfumée Figuier", "Décoration", 19.90, 6.50),
    ("P26", "Terrarium En Verre", "Décoration", 34.90, 13.00),
    ("P27", "Guirlande Lumineuse", "Décoration", 24.90, 8.00),
    ("P28", "Coffret Cadeau Plante", "Décoration", 44.90, 18.00),
]
dp = pd.DataFrame(produits, columns=["ID_Produit", "Produit", "Catégorie", "Prix_Unitaire", "Coût_Unitaire"])

categories = dp["Catégorie"].unique().tolist()
cat_share = {"Plantes d'intérieur": .30, "Plantes d'extérieur": .20, "Pots & cache-pots": .15,
             "Terreaux & engrais": .14, "Outils": .09, "Décoration": .12}
#            J    F    M    A    M    J    J    A    S    O    N    D
mods = {
    "Plantes d'intérieur": [1.0, 1.0, 1.0, 1.0, 0.9, 0.8, 0.8, 0.8, 1.0, 1.1, 1.2, 1.3],
    "Plantes d'extérieur": [0.3, 0.4, 1.2, 2.0, 2.1, 1.5, 0.9, 0.6, 0.9, 0.6, 0.4, 0.3],
    "Pots & cache-pots":   [0.7, 0.8, 1.2, 1.5, 1.5, 1.2, 0.9, 0.8, 1.0, 0.9, 0.8, 0.8],
    "Terreaux & engrais":  [0.5, 0.6, 1.4, 1.8, 1.7, 1.2, 0.9, 0.7, 1.0, 0.8, 0.5, 0.4],
    "Outils":              [0.6, 0.7, 1.2, 1.5, 1.4, 1.1, 0.9, 0.8, 1.0, 1.0, 0.9, 1.5],
    "Décoration":          [0.6, 0.7, 0.6, 0.6, 0.7, 0.6, 0.6, 0.6, 0.7, 0.9, 1.7, 3.2],
}
month_w = [0.65, 0.70, 1.00, 1.35, 1.40, 1.15, 0.95, 0.80, 0.95, 0.90, 1.05, 1.50]
weekday_w = [0.8, 0.85, 0.9, 0.95, 1.1, 1.5, 0.9]  # lun..dim

regions = {
    "Auvergne-Rhône-Alpes": 0, "Île-de-France": 19, "Nouvelle-Aquitaine": 9, "Occitanie": 9,
    "Hauts-de-France": 8, "Grand Est": 8, "Provence-Alpes-Côte d'Azur": 8, "Pays de la Loire": 6,
    "Bretagne": 5, "Normandie": 5, "Bourgogne-Franche-Comté": 4, "Centre-Val de Loire": 4, "Corse": 1,
}
reg_names = list(regions)
reg_p = np.array([regions[r] for r in reg_names], float); reg_p /= reg_p.sum()

clients = []          # dicts
lignes = []
order_no = 10000

def new_client(date):
    cid = f"C{len(clients) + 1:05d}"
    local = rng.random() < 0.55
    region = "Auvergne-Rhône-Alpes" if local else rng.choice(reg_names, p=reg_p)
    loyalty = rng.gamma(1.2, 1.0)  # propension à revenir
    churn_after = date + pd.Timedelta(days=int(rng.exponential(420)))
    pref = "Magasin" if local and rng.random() < 0.8 else ("Site web" if rng.random() < 0.72 else "Marketplace")
    c = dict(ID_Client=cid, Région=region, loyalty=loyalty, churn=churn_after, pref=pref, Date_Inscription=date)
    clients.append(c)
    return c

dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
for d in dates:
    growth = 1.0 if d.year == 2024 else 1.13
    lam = 8.6 * month_w[d.month - 1] * weekday_w[d.weekday()] * growth
    n_orders = rng.poisson(lam)
    for _ in range(n_orders):
        active = [c for c in clients[-1500:] if c["churn"] > d] if clients else []
        if active and rng.random() < 0.55:
            w = np.array([c["loyalty"] for c in active]); w /= w.sum()
            c = active[rng.choice(len(active), p=w)]
        else:
            c = new_client(d)
        canal = c["pref"] if rng.random() < 0.85 else rng.choice(["Magasin", "Site web", "Marketplace"])
        if canal == "Magasin" and c["Région"] != "Auvergne-Rhône-Alpes":
            canal = "Site web"
        order_no += 1
        n_lines = rng.choice([1, 2, 3, 4], p=[.45, .30, .17, .08])
        cw = np.array([cat_share[k] * mods[k][d.month - 1] for k in categories]); cw /= cw.sum()
        chosen = set()
        for _ in range(n_lines):
            cat = rng.choice(categories, p=cw)
            pool = dp[dp["Catégorie"] == cat]
            pw = 1 / pool["Prix_Unitaire"].values ** 0.6; pw /= pw.sum()
            pid = pool["ID_Produit"].values[rng.choice(len(pool), p=pw)]
            if pid in chosen:
                continue
            chosen.add(pid)
            row = dp[dp["ID_Produit"] == pid].iloc[0]
            q = 1 if cat in ("Plantes d'extérieur", "Plantes d'intérieur", "Décoration", "Outils") else rng.choice([1, 2, 3], p=[.6, .3, .1])
            if cat == "Plantes d'extérieur" and row["Prix_Unitaire"] < 10:
                q = rng.choice([1, 3, 6], p=[.5, .35, .15])
            remise = 0.0
            if d.month in (1, 7) and rng.random() < 0.35:
                remise = 0.20
            elif canal == "Site web" and rng.random() < 0.12:
                remise = 0.10
            elif canal == "Magasin" and rng.random() < 0.08:
                remise = 0.05
            lignes.append(dict(ID_Commande=f"CMD{order_no}", Date=d.date(), ID_Client=c["ID_Client"],
                               Région=c["Région"], Canal=canal, ID_Produit=pid, Produit=row["Produit"],
                               Catégorie=cat, Quantité=int(q), Prix_Unitaire=row["Prix_Unitaire"],
                               Remise=remise, Coût_Unitaire=row["Coût_Unitaire"]))

df = pd.DataFrame(lignes)
df["CA_HT"] = (df["Quantité"] * df["Prix_Unitaire"] * (1 - df["Remise"])).round(2)
df["Coût_Total"] = (df["Quantité"] * df["Coût_Unitaire"]).round(2)
df["Marge"] = (df["CA_HT"] - df["Coût_Total"]).round(2)

dc = pd.DataFrame(clients)[["ID_Client", "Région", "Date_Inscription"]]
dc["Date_Inscription"] = pd.to_datetime(dc["Date_Inscription"]).dt.date

df.to_csv(OUT / "ventes_atelier_vert_2024_2025.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
dp.to_csv(OUT / "produits.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
dc.to_csv(OUT / "clients.csv", index=False, sep=";", encoding="utf-8-sig")

print(len(df), "lignes", df["ID_Commande"].nunique(), "commandes", dc.shape[0], "clients")
print(df.groupby(pd.to_datetime(df["Date"]).dt.year)[["CA_HT", "Marge"]].sum().round(0))
print(df.groupby("Canal")["CA_HT"].sum().round(0))
print(df.groupby("Catégorie")["CA_HT"].sum().round(0))
