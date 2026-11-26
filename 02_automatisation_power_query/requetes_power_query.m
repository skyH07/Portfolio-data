// =====================================================================
//  L'Atelier Vert (données fictives) : consolidation automatique
//  des 12 exports mensuels du logiciel de caisse avec Power Query
// =====================================================================
//  Crée chaque bloc ci-dessous comme une requête séparée dans Power Query
//  (Accueil > Nouvelle source > Autres sources > Requête vide > Éditeur avancé),
//  en lui donnant exactement le nom indiqué.
// ---------------------------------------------------------------------


// ---------------------------------------------------------------------
// 1) Paramètre « DossierExports »
//    Accueil > Gérer les paramètres > Nouveau, type Texte.
//    Valeur : chemin complet du dossier qui contient UNIQUEMENT les exports, par ex.
//    C:\Portfolio\02_automatisation_power_query\exports_caisse
// ---------------------------------------------------------------------

// 2) Paramètre « CheminReferentiel »
//    Valeur : chemin complet du fichier reference_produits.csv, par ex.
//    C:\Portfolio\02_automatisation_power_query\reference_produits.csv
// ---------------------------------------------------------------------


// ---------------------------------------------------------------------
// 3) Requête « Référentiel produits »
// ---------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(CheminReferentiel), [Delimiter = ";", Encoding = 65001, QuoteStyle = QuoteStyle.None]),
    Entetes = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    // Clé de rapprochement : nom sans espaces superflus, en majuscules
    Cle = Table.AddColumn(Entetes, "Cle_Produit", each Text.Upper(Text.Trim([Produit])), type text)
in
    Cle


// ---------------------------------------------------------------------
// 4) Fonction « fxNettoyerExport » : nettoie UN fichier d'export
// ---------------------------------------------------------------------
(contenu as binary) as table =>
let
    // Columns = 7 : force 7 colonnes même si les premières lignes (titre) en ont moins
    Brut = Csv.Document(contenu, [Delimiter = ";", Columns = 7, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
    // Les 3 premières lignes sont un titre et une période ajoutés par le logiciel
    SansLignesTitre = Table.Skip(Brut, 3),
    AvecEntetes = Table.PromoteHeaders(SansLignesTitre, [PromoteAllScalars = true]),
    // Depuis septembre, le logiciel a renommé deux colonnes : on harmonise
    NomsHarmonises = Table.RenameColumns(
        AvecEntetes,
        {{"Qte", "Quantité"}, {"Montant_HT", "Montant"}},
        MissingField.Ignore
    ),
    // Supprime les lignes vides et la ligne TOTAL en bas de fichier
    LignesUtiles = Table.SelectRows(
        NomsHarmonises,
        each [N_Ticket] <> null
            and Text.Trim([N_Ticket]) <> ""
            and not Text.StartsWith(Text.Upper(Text.Trim([N_Ticket])), "TOTAL")
    )
in
    LignesUtiles


// ---------------------------------------------------------------------
// 5) Requête principale « Ventes 2025 »
// ---------------------------------------------------------------------
let
    Source = Folder.Files(DossierExports),
    FichiersCsv = Table.SelectRows(Source, each Text.Lower([Extension]) = ".csv"),
    // Applique la fonction de nettoyage à chaque fichier, puis empile tout
    Nettoyes = Table.AddColumn(FichiersCsv, "Donnees", each fxNettoyerExport([Content])),
    Combine = Table.Combine(Nettoyes[Donnees]),
    Colonnes = Table.SelectColumns(Combine, {"N_Ticket", "Date", "Canal", "Produit", "Quantité", "Prix_Unitaire", "Montant"}),

    // Deux formats de date selon la version du logiciel : 31/03/2025 ou 2025-07-15
    DatesConverties = Table.TransformColumns(
        Colonnes,
        {{"Date", each
            if Text.Contains(_, "/")
            then Date.FromText(_, [Format = "dd/MM/yyyy", Culture = "fr-FR"])
            else Date.FromText(_, [Format = "yyyy-MM-dd", Culture = "fr-FR"]),
          type date}}
    ),

    // Nombres au format français (virgule décimale)
    NombresConvertis = Table.TransformColumns(
        DatesConverties,
        {
            {"Quantité", each Number.FromText(_, "fr-FR"), Int64.Type},
            {"Prix_Unitaire", each Number.FromText(_, "fr-FR"), Currency.Type},
            {"Montant", each Number.FromText(_, "fr-FR"), Currency.Type}
        }
    ),

    // Noms de produits incohérents (majuscules, espaces en trop) : clé normalisée
    AvecCle = Table.AddColumn(NombresConvertis, "Cle_Produit", each Text.Upper(Text.Trim([Produit])), type text),

    // Certains mois ont été exportés deux fois : on retire les lignes en double
    SansDoublons = Table.Distinct(AvecCle),

    // Rapprochement avec le référentiel pour récupérer l'ID, le nom propre et la catégorie
    Fusion = Table.NestedJoin(SansDoublons, {"Cle_Produit"}, #"Référentiel produits", {"Cle_Produit"}, "Ref", JoinKind.LeftOuter),
    Developpe = Table.ExpandTableColumn(Fusion, "Ref", {"ID_Produit", "Produit", "Catégorie"}, {"ID_Produit", "Produit_Ref", "Catégorie"}),
    Selection = Table.SelectColumns(Developpe, {"N_Ticket", "Date", "Canal", "ID_Produit", "Produit_Ref", "Catégorie", "Quantité", "Prix_Unitaire", "Montant"}),
    Renomme = Table.RenameColumns(Selection, {{"Produit_Ref", "Produit"}}),
    Trie = Table.Sort(Renomme, {{"Date", Order.Ascending}, {"N_Ticket", Order.Ascending}})
in
    Trie
