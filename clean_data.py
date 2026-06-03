import pandas as pd

def clean_data(df, df_mst, df_dsgctg,df_con):

    # Remove unwanted columns
    df.drop(df.columns[[1, 3]], axis=1, inplace=True)

    # Remove top rows
    df = df.iloc[3:]

    # Set header
    df.columns = df.iloc[0]

    # Remove header row
    df = df[1:]

    # Reset index
    df = df.reset_index(drop=True)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    df_mst.columns = df_mst.columns.str.strip().str.lower()

    df_dsgctg.columns = (
        df_dsgctg.columns.str.strip().str.lower()
    )

    # Export Ref
    a1_cell = df.iloc[0, 0]

    df['exp_ref'] = a1_cell

    # Merge master
    df = df.merge(
        df_mst[['ctg', 'desc', 'ctg_sort','category']],
        on='ctg',
        how='left'
    )
    # remove duplicate mapping rows
    df_con = df_con[['ctg', 'karatage', 'conversion']].drop_duplicates()
    
    df = df.merge(
        df_con[['ctg','karatage', 'conversion']],
        on=['ctg','karatage'],
        how='left'
    )
    
    # update inv pure wt and inv value which is map to master data coversion sheet
    num_cols = ['inv rm wt', 'conversion', 'inv pure wt', 'inv rate']

    

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # apply conversion ONLY for Gold category
    mask = (
        df['conversion'].notna()) & (~df['category'].isin(['D'])
                )        

   # update inv pure wt
    df.loc[mask, 'inv pure wt'] = (
    df.loc[mask, 'inv rm wt'] *
    df.loc[mask, 'conversion']
    ).round(3)

    # update inv value
    df.loc[mask, 'inv value'] = (
    df.loc[mask, 'inv pure wt'] *
    df.loc[mask, 'inv rate']
    ).round(2) 
    
    # Fill missing
    df['desc'] = df['desc'].fillna(df['ctg'])

    df['ctg_sort'] = df['ctg_sort'].fillna(99)
    
    
    # Merge dsgctg
    df = df.merge(
        df_dsgctg[['dsgctg', 'dsgctg_desc']],
        on='dsgctg',
        how='left'
    )

    # desc_1
    def new_desc1(row):

        if row['desc'] == 'Gold':

            return 'Gold-' + str(row['karatage'])

        elif row['desc'] == 'Silver':

            return 'Silver-' + str(row['karatage'])

        elif row['desc'] == 'Studded Semi  Precious Color Stone':
            
            return row['desc']
            #return 'Studded Semi  Precious Color Stone-' + str(row['karatage'])

        elif row['desc'] == 'Studded Color Stone':
            
             return row['desc'] 
         
        if row['desc'] == 'Studded Color Precious Stone':
            
             return row['desc'] 

        if row['desc'] == 'Studded Color Synthetic Stone':
            
             return row['desc'] 
        
        if row['desc'] == 'Studded Color Pearl Stone':
            
             return row['desc']  
    
    
            
        elif row['desc'] in [
            'Studded Diamond',
            #'Studded Color Stone'
            #'Studded Color Precious Stone'
        ]:

            return row['desc']

        else:

            return str(row['karatage'])

    df['desc_1'] = df.apply(
        new_desc1,
        axis=1
    )

    # col_head
    def col_header(row):

        if row['desc_1'] == 'Studded Diamond':

            return 'Dia'

        elif row['desc_1'] == 'Studded Color Stone':

            return 'Col Stn'
        
        elif row['desc_1'] == 'Studded Color Precious Stone':

            return 'Col Pr Stn'
        
        elif row['desc_1'] == 'Studded Semi  Precious Color Stone':
            
            return 'Col Semi Pr Stn'
        
        
        else:
            
            return str(row['desc_1'])

    df['col_head'] = df.apply(
        col_header,
        axis=1
    )

    # Sort
    df = df.sort_values('ctg_sort')

    # Final Desc
    result = []

    grp = df.groupby([
        'design',
        'dsgctg',
        'inv exp no'
    ])

    for keys, data in grp:

        unique_desc = []

        for val in data['desc_1']:

            if pd.notna(val):

                if val not in unique_desc:

                    unique_desc.append(val)

        dsgctg_desc = str(
            data['dsgctg_desc'].iloc[0]
        )

        final_desc = (
            #dsgctg_desc
            '-'.join(unique_desc)
            + '-Jewellery'
        )

        result.append([
            keys[0],
            keys[1],
            keys[2],
            final_desc
        ])

    df_final = pd.DataFrame(
        result,
        columns=[
            'design',
            'dsgctg',
            'inv exp no',
            'final_desc'
        ]
    )

    # Merge final desc
    df = df.merge(
        df_final,
        on=[
            'design',
            'dsgctg',
            'inv exp no'
        ],
        how='left'
    )

    return df
