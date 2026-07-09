import pandas as pd

def inv_sum(df):
    print(df.columns.tolist())
    # Grouping Sum
    group_cols = ['inv exp no', 'final_desc','dsgctg_desc']

    #Summary
    df_summary = df.groupby(group_cols,as_index= False).agg({
         'qty':'sum',
         'gross wt':'sum',
        }) 
   
   # rename columns
    df_summary.rename(columns={
    'qty': 'no. & kind of pkgs',
    'gross wt': 'gross wt (gms)'
    }, inplace=True) 

# ---------------- GOLD DATA ----------------
# inv rm wt only for desc = Gold

    gold_rm = (
        df[df['desc'] == 'Gold']
        .groupby(group_cols, as_index=False)['inv rm wt']
        .sum()
        .rename(columns={'inv rm wt': 'Gold Wt'})
        )

    gold_pure = (
        df[df['desc'] == 'Gold']
        .groupby(group_cols, as_index=False)['inv pure wt']
        .sum()
        .rename(columns={'inv pure wt': 'Pure Gold Wt'})
        )

    dia_rm = (
        df[df['desc'] == 'Studded Diamond']
        .groupby(group_cols, as_index=False)[['inv rm wt','inv value']]
        .sum()
        )
    # Add new column
    #dia_rm['Dia Rate'] = dia_rm['inv value'] / dia_rm['inv rm wt']

    dia_rm['Dia Rate'] = (
    dia_rm['inv value']
    .div(dia_rm['inv rm wt'].replace(0, pd.NA))
    .fillna(0)
    .round(4)
    .map('{:.3f}'.format)
    )
    
    dia_rm = dia_rm.rename(columns={'inv rm wt': 'Dia Cts','inv value': 'Dia Val'})
    
    
    dia_rm = dia_rm[
    group_cols + ['Dia Cts', 'Dia Rate', 'Dia Val']
    ]        
    
    col_stn = (
    df[df['desc'].isin(['Studded Semi  Precious Color Stone','Studded Color Precious Stone','Studded Color Synthetic Stone','Studded Color Pearl Stone','Studded Color Stone'])]
    .groupby(group_cols, as_index=False)[['inv rm wt', 'inv value']]
    .sum()
)
    
    col_stn['Col Stn Rate'] = (
        col_stn['inv value']
        .div(col_stn['inv rm wt'].replace(0, pd.NA))
        .fillna(0)
        .round(4)
        .map('{:.3f}'.format)
    )
    
    col_stn = col_stn.rename(columns={'inv rm wt': 'Col stn Cts','inv value': 'Col stn Val'})    
    
    col_stn = col_stn[
    group_cols + ['Col stn Cts', 'Col Stn Rate', 'Col stn Val']
    ]        
 
   # rename columns
    df_summary.rename(columns={
    'qty': 'no. & kind of pkgs',
    'gross wt': 'gross wt (gms)'
    }, inplace=True) 

   
    labour=(
         df.groupby(group_cols,as_index=False)[['labour','inv value']]
        .sum()
        .round(4)
    )

    # less Dia Value
    labour = labour.merge(
        dia_rm[group_cols + ['Dia Val']],
        on=group_cols,
        how='left'
    )

    # less Color Stone Value
    labour = labour.merge(
        col_stn[group_cols + ['Col stn Val']],
        on=group_cols,
        how='left'
    )

    # fill null
    labour[['Dia Val', 'Col stn Val']] = (
        labour[['Dia Val', 'Col stn Val']]
        .fillna(0)
    )
    # final inv value calculation
    labour['inv value'] = (
                            labour['inv value']
                            - labour['Dia Val']
                            - labour['Col stn Val']
                        )

    # round values
    labour[['labour', 'inv value']] = (
                                        labour[['labour', 'inv value']]
                                        .round(4)
                                     )

    # optional remove extra columns
    labour = labour.drop(columns=['Dia Val', 'Col stn Val'])


    # rename columns
    labour.rename(columns={
    'inv value': 'Metal Amt',
    }, inplace=True) 

    #New Metal Amt Calculation
    m_amt = (
    df[df['category'] == 'M']
    .groupby(group_cols, as_index=False)[['labour', 'inv value']]
    .sum()
    .round(4)
    )
    
    # Create M_Amt Usd 
    m_amt['metal_New_amt'] = m_amt['inv value'] + m_amt['labour']
   

    amt = (
       df.groupby(group_cols, as_index=False)[['labour' ,'inv value']]
    .sum()
    .round(4)
    )
        
    amt['Amt Usd'] = amt['labour']+amt['inv value']

    # merge
    df_summary = df_summary.merge(
        gold_rm,
        on=group_cols,
        how='left'
        )
    df_summary = df_summary.merge(
        gold_pure,
        on=group_cols,
        how='left'
        )
    df_summary = df_summary.merge(
        dia_rm,
        on=group_cols,
        how='left'
    )

    df_summary = df_summary.merge(
        col_stn,
        on=group_cols,
        how='left'
    )

    df_summary = df_summary.merge(
        labour,
        on=group_cols,
        how='left'
    )

    df_summary = df_summary.merge(
        amt[group_cols + ['Amt Usd']],
        on=group_cols,
        how='left'
        )
    
    # ---------------- DYNAMIC COL_HEAD SUM ----------------

    pivot_df = (
        df.pivot_table(
        index=group_cols,
        columns='col_head',
        values=['inv pure wt','inv rm wt', 'inv value'],
        aggfunc='sum',
        fill_value=0
        )
        .round(4)
        )
    
    # flatten multi-index columns
    pivot_df.columns = [
        f"{col_head}_{'Wt' if value == 'inv pure wt' 
        else 'RmWt' if value == 'inv rm wt'
        else 'Amt'}"
        for value, col_head in pivot_df.columns
    ]

    # convert index to columns
    pivot_df = pivot_df.reset_index()

# remove column index name
    pivot_df.columns.name = None

#    pivot_df = (
#        df.pivot_table(
#        index=group_cols,
#        columns='col_head',
#        values='inv value',
#        aggfunc='sum',
#        fill_value=0
#        )
#        .reset_index()
#        .round(4)
#    )

    # remove multi index name
 #   pivot_df.columns.name = None
    
    # drop columns if exist
    pivot_df = pivot_df.drop(columns=['Dia', 'Col Stn','Dia_Amt','Col Stn_Amt'], errors='ignore')
    
#    pivot_df.rename(
#    columns={
#        col: f"{col}_Amt"
#        for col in pivot_df.columns
#        if col not in group_cols
#    },
#    inplace=True
#)


# ---------------- FINAL MERGE ----------------

    result = df_summary.merge(
        pivot_df,
        on= group_cols,
        how='left'
    )

# ---------------- REMOVE SPECIFIED COLUMNS ----------------

    remove_columns = [
        'Gold Wt',
        'Pure Gold Wt',
        'Dia Rate',
        'Dia_RmWt',
        'Col Semi Pr Stn_RmWt',
        'Col Stn Rate',
        'Gold-18KT_Amt',
        'Gold-18KT-1_Amt',
        'Gold-22KT_Amt',
        'Gold-22KT-1_Amt'
        'Gold-14KT_Amt',
        'Gold-14KT-1_Amt',
    ]

    result = result.drop(columns=remove_columns, errors='ignore')



#    pivot_df1 = (
#        df.pivot_table(
#        index=group_cols,
#        columns='col_head',
#        values='inv pure wt',
#        aggfunc='sum',
#        fill_value=0
#        )
#        .reset_index()
#        .round(4)
#    )

    # remove multi index name
#    pivot_df1.columns.name = None
    
 #   pivot_df1.rename(
 #   columns={
 #       col: f"{col}_Wt"
 #       for col in pivot_df1.columns
 #       if col not in group_cols
 #   },
 #   inplace=True
 #   )
    
  
  
    # merge second pivot
  #  result = result.merge(
  #      pivot_df1,
  #      on=group_cols,
  #      how='left'
  #  )
   
   
   
    result = result.loc[
    :,
    ~((result.fillna(0) == 0).all())
    ]

    result = result.fillna(0)

    # ---------------- ROUND 4 DECIMAL ----------------

    num_cols = result.select_dtypes(include='number').columns

    result[num_cols] = result[num_cols].round(4)


   # create empty dict
    total_data = {}

    for col in result.columns:

        # numeric columns
        if pd.api.types.is_numeric_dtype(result[col]):
            total_data[col] = result[col].sum()

        # first group column
        elif col == 'inv exp no':
            total_data[col] = 'TOTAL'

        # other text columns
        else:
            total_data[col] = ''

    # create dataframe
    total_row = pd.DataFrame([total_data])

    # append
    result = pd.concat([result, total_row], ignore_index=True)
   
    
# ---------------- OPTIONAL ----------------
    result = result.fillna(0)

    return result

