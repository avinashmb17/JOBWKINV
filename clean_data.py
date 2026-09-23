import pandas as pd


def clean_data(df, df_mst, df_dsgctg, df_con):

    # =========================================================
    # REMOVE UNWANTED COLUMNS
    # =========================================================

    df = df.copy()
    df_mst = df_mst.copy()
    df_dsgctg = df_dsgctg.copy()
    df_con = df_con.copy()

    df.drop(df.columns[[1, 3]], axis=1, inplace=True)


    # =========================================================
    # REMOVE TOP ROWS
    # =========================================================

    df = df.iloc[3:].copy()


    # =========================================================
    # SET HEADER
    # =========================================================

    df.columns = df.iloc[0]

    # Remove header row
    df = df[1:].copy()

    # Reset index
    df = df.reset_index(drop=True)


    # =========================================================
    # CLEAN COLUMN NAMES
    # =========================================================

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df_mst.columns = (
        df_mst.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df_dsgctg.columns = (
        df_dsgctg.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df_con.columns = (
        df_con.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )


    # =========================================================
    # EXPORT REF
    # =========================================================

    a1_cell = df.iloc[0, 0]

    df['exp_ref'] = a1_cell


    # =========================================================
    # CLEAN DESIGN
    # =========================================================

    df['design'] = (
        df['design']
        .fillna('')
        .astype(str)
        .str.strip()
    )


    # =========================================================
    # CLEAN ORDER NO
    # =========================================================

    df['order no'] = (
        df['order no']
        .fillna('')
        .astype(str)
        .str.strip()
    )


    # =========================================================
    # EXTRACT LAST 4 DIGITS OF ORDER NO
    # =========================================================

    df['order_last4'] = (
        df['order no']
        .astype(str)
        .str.strip()
        .str.split('/')
        .str[-1]
        .str.strip()
        .str[-4:]
    )


    # =========================================================
    # CREATE NEW DESIGN
    # =========================================================

    df['design'] = (
        df['design']
        + df['order_last4']
    )


    # =========================================================
    # MERGE MASTER DATA
    # =========================================================

    df = df.merge(
        df_mst[
            ['ctg', 'desc', 'ctg_sort', 'category']
        ].drop_duplicates(),
        on='ctg',
        how='left'
    )


    # =========================================================
    # CLEAN CONVERSION MASTER
    # =========================================================

    df_con = df_con[
        ['ctg', 'karatage', 'conversion']
    ].drop_duplicates()


    # =========================================================
    # MERGE CONVERSION MASTER
    # =========================================================

    df = df.merge(
        df_con[
            ['ctg', 'karatage', 'conversion']
        ],
        on=['ctg', 'karatage'],
        how='left'
    )


    # =========================================================
    # CONVERT NUMERIC COLUMNS
    # =========================================================

    num_cols = [
        'inv rm wt',
        'conversion',
        'inv pure wt',
        'inv rate',
        'inv value'
    ]

    for col in num_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors='coerce'
            )


    # =========================================================
    # APPLY CONVERSION
    # =========================================================

    mask = (
        df['conversion'].notna()
        & ~df['category'].fillna('').isin(['D'])
    )


    # =========================================================
    # UPDATE INV PURE WT
    # =========================================================

    df.loc[mask, 'inv pure wt'] = (
        df.loc[mask, 'inv rm wt']
        * df.loc[mask, 'conversion']
    ).round(3)


    # =========================================================
    # UPDATE INV VALUE
    # =========================================================

    df.loc[mask, 'inv value'] = (
        df.loc[mask, 'inv pure wt']
        * df.loc[mask, 'inv rate']
    ).round(2)


    # =========================================================
    # FILL MISSING MASTER DATA
    # =========================================================

    df['desc'] = (
        df['desc']
        .fillna(df['ctg'])
    )

    df['ctg_sort'] = (
        pd.to_numeric(
            df['ctg_sort'],
            errors='coerce'
        )
        .fillna(99)
    )


    # =========================================================
    # MERGE DESIGN CATEGORY
    # =========================================================

    df = df.merge(
        df_dsgctg[
            ['dsgctg', 'dsgctg_desc']
        ].drop_duplicates(),
        on='dsgctg',
        how='left'
    )


    # =========================================================
    # DESC_1
    # =========================================================

    def new_desc1(row):

        # Clean description
        desc = (
            str(row['desc']).strip()
            if pd.notna(row['desc'])
            else ''
        )

        # Clean karatage
        if pd.notna(row['karatage']):

            karatage = str(
                row['karatage']
            ).strip()

            # Prevent nan / None text
            if karatage.lower() in [
                'nan',
                'none',
                ''
            ]:
                karatage = ''

        else:
            karatage = ''


        # -----------------------------------------------------
        # GOLD
        # -----------------------------------------------------

        if desc.lower() == 'gold':

            if karatage:
                return 'Gold-' + karatage
            else:
                return 'Gold'


        # -----------------------------------------------------
        # SILVER
        # -----------------------------------------------------

        elif desc.lower() == 'silver':

            if karatage:
                return 'Silver-' + karatage
            else:
                return 'Silver'

        # -----------------------------------------------------
        # Platinum
        # -----------------------------------------------------
        #    print("desc:", desc)
        #elif desc.lower() == '950PT':
        elif desc.lower() == 'plantinium':
            if karatage:
                return 'Plantinium-' + karatage
            else:
                return 'Plantinium'
        
        # -----------------------------------------------------
        # RUBBER
        # -----------------------------------------------------

        elif desc.lower() == 'rubber':

            return 'Rubber'


        # -----------------------------------------------------
        # CORD
        # -----------------------------------------------------

        elif desc.lower() == 'cord':

            return 'Cord'


        # -----------------------------------------------------
        # CARFIBER
        # -----------------------------------------------------

        elif desc.lower() == 'carfiber':

            return 'Carfiber'
        
        # -----------------------------------------------------
        # Nithinol
        # -----------------------------------------------------
        
        elif desc.lower() == 'nithinol':

            return 'Nithinol'

        # -----------------------------------------------------
        # Steel
        # -----------------------------------------------------
        
        elif desc.lower() == 'steel':

            return 'Steel'

        # -----------------------------------------------------
        # Titanium
        # -----------------------------------------------------
        
        elif desc.lower() == 'titanium':

            return 'Titanium'



        # -----------------------------------------------------
        # STUDDED MATERIALS
        # -----------------------------------------------------

        elif desc in [
            'Studded Diamond',
            'Studded Color Stone',
            'Studded Color Precious Stone',
            'Studded Color Synthetic Stone',
            'Studded Color Pearl Stone',
            'Studded Semi  Precious Color Stone'
        ]:

            return desc


        # -----------------------------------------------------
        # OTHER
        # -----------------------------------------------------

        else:

            if karatage:
                return karatage
            else:
                return desc


    df['desc_1'] = df.apply(
        new_desc1,
        axis=1
    )


    # =========================================================
    # COLUMN HEADER
    # =========================================================

    def col_header(row):

        if row['desc_1'] == 'Studded Diamond':

            return 'Dia'

        elif row['desc_1'] == 'Studded Color Stone':

            return 'Col Stn'

        elif row['desc_1'] == 'Studded Color Precious Stone':

            return 'Col Pr Stn'

        elif row['desc_1'] == 'Studded Semi  Precious Color Stone':

            return 'Col Semi Pr Stn'

        elif row['desc_1'] == 'Studded Color Synthetic Stone':

            return 'Col Synthetic Stn'

        elif row['desc_1'] == 'Studded Color Pearl Stone':

            return 'Col Pearl Stn'

        else:

            return str(row['desc_1'])


    df['col_head'] = df.apply(
        col_header,
        axis=1
    )


    # =========================================================
    # SORT
    # =========================================================

    df = (
        df
        .sort_values(
            ['ctg_sort', 'design']
        )
        .reset_index(drop=True)
    )


    # =========================================================
    # FINAL DESCRIPTION
    # =========================================================

    result = []


    grp = df.groupby(
        [
            'design',
            'dsgctg',
            'inv exp no'
        ],
        dropna=False
    )


    # =========================================================
    # COMBINATION MATERIALS
    # =========================================================

    combination_materials = {
        'gold',
        'silver',
        '950pt',
        'plantinium'
    }


    # =========================================================
    # PROCESS EACH GROUP
    # =========================================================

    for keys, data in grp:

        unique_desc = []


        # -----------------------------------------------------
        # GET UNIQUE DESCRIPTIONS
        # -----------------------------------------------------

        for val in data['desc_1']:

            if pd.isna(val):
                continue

            val = str(val).strip()

            # Ignore blank / nan
            if not val:
                continue

            if val.lower() in [
                'nan',
                'none'
            ]:
                continue

            if val not in unique_desc:

                unique_desc.append(val)


        # -----------------------------------------------------
        # CHECK MATERIAL COUNT
        # -----------------------------------------------------

        material_found = set()


        for val in unique_desc:

            val_lower = val.lower().strip()


            for material in combination_materials:

                # Examples:
                #
                # Gold
                # Gold-14KT
                # Silver
                # Silver-925
                #
                if (
                    val_lower == material
                    or val_lower.startswith(
                        material + '-'
                    )
                ):

                    material_found.add(material)

                    break


        # Number of different metals/materials
        material_count = len(material_found)


        # -----------------------------------------------------
        # CREATE DESCRIPTION
        # -----------------------------------------------------

        description_text = '-'.join(
            unique_desc
        )


        # -----------------------------------------------------
        # COMBINATION JEWELLERY
        # -----------------------------------------------------

        if material_count > 1: 
            final_desc = ( description_text + '-Combination Jewellery' )
        

        # -----------------------------------------------------
        # NORMAL JEWELLERY
        # -----------------------------------------------------

        else:

            final_desc = (
                description_text
                + '-Jewellery'
            )


        # -----------------------------------------------------
        # APPEND RESULT
        # -----------------------------------------------------

        result.append(
            [
                keys[0],
                keys[1],
                keys[2],
                final_desc
            ]
        )


    # =========================================================
    # CREATE FINAL DESCRIPTION DATAFRAME
    # =========================================================

    df_final = pd.DataFrame(
        result,
        columns=[
            'design',
            'dsgctg',
            'inv exp no',
            'final_desc'
        ]
    )


    # =========================================================
    # MERGE FINAL DESCRIPTION
    # =========================================================

    df = df.merge(
        df_final,
        on=[
            'design',
            'dsgctg',
            'inv exp no'
        ],
        how='left'
    )


    # =========================================================
    # RETURN
    # =========================================================

    return df
