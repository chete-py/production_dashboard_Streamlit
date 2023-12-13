import pandas as pd
import streamlit as st
import plotly as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_vizzu import VizzuChart, Data, Config, Style
import base64
import io
import hydralit_components as hc

#can apply customisation to almost all the properties of the card, including the progress bar
theme_bad = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-times-circle'}
theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange','icon_color': 'orange', 'icon': 'fa fa-question-circle'}
theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}

st.sidebar.image('corplogo.PNG', use_column_width=True)

uploaded_file = st.sidebar.file_uploader("Upload Production Listing",  type=['csv', 'xlsx', 'xls'], kwargs=None,)




if uploaded_file is not None:
    try:
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            data_types = {'Policy No': str}
            df = pd.read_excel(uploaded_file, dtype = data_types, header=6)
                      
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file, header=6)

    except Exception as e:    
        st.write("Error:", e)

if uploaded_file is not None:

    view = st.sidebar.radio('Select',['Company', 'Branch', 'Territorial Manager'])
    df2 = df[["TRANSACTION DATE", "BRANCH", "INTERMEDIARY TYPE", "INTERMEDIARY", "PRODUCT", "SALES TYPE", "STAMP DUTY", "SUM INSURED", "GROSS PREMIUM", "NET BALANCE", "RECEIPTS", "TM"]]    
    df2['STAMP DUTY'] = df2['STAMP DUTY'].astype(str) 
    total_motor_produce = df2[df2['STAMP DUTY'].str.contains('MOTOR')] 
    thedf = df2.dropna(subset='TRANSACTION DATE')
    thedf['TRANSACTION DATE'] = pd.to_datetime(thedf['TRANSACTION DATE'], format='%m/%d/%Y')
    # Extract the month name for each date in the 'date_column'
    thedf['MONTH NAME'] = thedf['TRANSACTION DATE'].dt.strftime('%B')
    thedf['MONTH NAME'] = thedf['MONTH NAME'].str.upper()
    
    lastdf = pd.read_csv('agency_accounts.csv')

    newdf = pd.merge(thedf, lastdf, on='INTERMEDIARY', how='left')
    newdf.loc[newdf['INTERMEDIARY'].str.contains('REIN', case=False, na=False), 'NEW TM'] = 'REINSURANCE'
    newdf = newdf[["TRANSACTION DATE", "BRANCH", "INTERMEDIARY TYPE", "INTERMEDIARY", "PRODUCT", "SALES TYPE", "SUM INSURED", "GROSS PREMIUM", "NET BALANCE", "RECEIPTS", "NEW TM", "MONTH NAME"]]
    cancellations = newdf[newdf['SUM INSURED'] < 0]
    #preview = newdf.groupby('INTERMEDIARY')['GROSS PREMIUM'].sum()

    # Group by and sum with additional text columns
    preview = newdf.groupby('INTERMEDIARY').agg({
        'GROSS PREMIUM': 'sum',
        'BRANCH': 'first',  
        'NEW TM': 'first',  
     
    })
    
    # Sort the results from highest to lowest and take the top 5 rows
    preview_sorted = preview.sort_values(by='GROSS PREMIUM', ascending=False).head(5)

    if view == 'Company':

        motor = total_motor_produce[total_motor_produce['STAMP DUTY'] == 'MOTOR']
        nonmotor = total_motor_produce[total_motor_produce['STAMP DUTY'] == 'NON-MOTOR']
        motorproduce = motor['GROSS PREMIUM'].sum()
        nonmotorproduce = nonmotor['GROSS PREMIUM'].sum()
        cancelled = cancellations['GROSS PREMIUM'].sum()
        amount_cancelled = "Ksh. {:,.0f}".format(cancelled)

        totalmix = (motorproduce+nonmotorproduce)
        total_mix_result = "{:,.0f}".format(totalmix)
        mix = (motorproduce/ totalmix)*100
        mix_result = "{:.0f}".format(mix)

        chart = VizzuChart()
        
        bar = newdf.groupby('BRANCH')['GROSS PREMIUM'].sum().reset_index()

        data = Data()

        bar['Percentage'] = (bar['GROSS PREMIUM']/(bar['GROSS PREMIUM'].sum()) * 100)
        
            
        gp = newdf['GROSS PREMIUM'].sum()
        total_gp = "Ksh. {:,.0f}".format(gp)

        receipted = newdf['RECEIPTS'].sum()
        total_receipted = "Ksh. {:,.0f}".format(receipted)

        credit = newdf['NET BALANCE'].sum()
        total_credit = "Ksh. {:,.0f}".format(credit)

        cc = st.columns(5)

        with cc[0]:
        # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
            hc.info_card(title='Production', content= f'Ksh. {total_mix_result}', sentiment='good',bar_value=77, content_text_size = 'small', title_text_size='small')

        with cc[1]:
            hc.info_card(title='Receipted', content=f'{total_receipted}',bar_value=12, sentiment='good', content_text_size = 'small', title_text_size='small')

        with cc[2]:
            hc.info_card(title='Credit', content=f'{total_credit}', sentiment='neutral',bar_value=55, content_text_size = 'small', title_text_size='small')

        with cc[3]:
            hc.info_card(title='Cancelled', content=f'{amount_cancelled}',bar_value=2, title_text_size='small', content_text_size = 'small', theme_override=theme_bad)

        with cc[4]:
            hc.info_card(title='Portfolio Mix',content= f'{mix_result}% Motor',key='sec',bar_value=5, content_text_size = 'small', sentiment='good', title_text_size='small')
            
       
        data.add_df(bar)
        
        # Animate the data
        chart.animate(data)

        chart.animate(Config({"x": "BRANCH", "y": "GROSS PREMIUM", "title": "PRODUCTION PER BRANCH", "color": "BRANCH",  "label":"GROSS PREMIUM"}), delay=2)

       
        if st.checkbox("Swap"):
            chart.animate(Config({"x":"GROSS PREMIUM", "y": "BRANCH", "title": "PRODUCTION PER BRANCH", "color": "BRANCH",  "label":"GROSS PREMIUM"}))

        

        output = chart.show()

        
        st.markdown("")

        sorted_prev = pd.DataFrame(preview_sorted)

        st.markdown("**INTERMEDIARIES WITH THE HIGHEST PRODUCTION**")

        st.dataframe(sorted_prev)


    if view == 'Branch':
        unique = newdf['BRANCH'].unique()

        selected_branch =st.sidebar.selectbox("Choose Branch", unique)

        # Filter the DataFrame based on the selected branch
        filtered_df = newdf[newdf['BRANCH'] == selected_branch]
        for_cancellation =  cancellations[cancellations['BRANCH'] == selected_branch]

        nonmotordf = filtered_df[~filtered_df['PRODUCT'].str.contains('Motor')]
        motordf = filtered_df[filtered_df['PRODUCT'].str.contains('Motor')]
        nonmotor = nonmotordf['GROSS PREMIUM'].sum()
        motor = motordf['GROSS PREMIUM'].sum()
        cancelled = for_cancellation['GROSS PREMIUM'].sum()
        amount_cancelled = "Ksh. {:,.0f}".format(cancelled)
        total_mix = (motor+nonmotor)
        total_mix_result = "{:,.0f}".format(total_mix)
        mix = (motor/total_mix)*100
        mix_result = "{:.0f}".format(mix)

        bar = filtered_df.groupby('NEW TM')['GROSS PREMIUM'].sum().reset_index()

        gp = filtered_df['GROSS PREMIUM'].sum()
        total_gp = "Ksh. {:,.0f}".format(gp)

        receipted = filtered_df['RECEIPTS'].sum()
        total_receipted = "Ksh. {:,.0f}".format(receipted)

        credit = filtered_df['NET BALANCE'].sum()
        total_credit = "Ksh. {:,.0f}".format(credit)

        cc = st.columns(5)

        with cc[0]:
        # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
            hc.info_card(title='Production', content= f'Ksh. {total_mix_result}', content_text_size = 'small',sentiment='good',bar_value=77, title_text_size='small')

        with cc[1]:
            hc.info_card(title='Receipted', content=f'{total_receipted}',bar_value=12, content_text_size = 'small', sentiment='good', title_text_size='small')

        with cc[2]:
            hc.info_card(title='Credit', content=f'{total_credit}', sentiment='neutral', content_text_size = 'small', bar_value=55, title_text_size='small')

        with cc[3]:
            hc.info_card(title='Cancelled', content=f'{amount_cancelled}',bar_value=2, title_text_size='small', content_text_size = 'small', theme_override=theme_bad)

        with cc[4]:
            hc.info_card(title='Portfolio Mix',content=f'{mix_result}% Motor ',key='sec', bar_value=5, content_text_size = 'small', sentiment='good', title_text_size='small')

        chart = VizzuChart()        
    
        data = Data()

        bar['Percentage'] = (bar['GROSS PREMIUM']/(bar['GROSS PREMIUM'].sum()) * 100)

        data.add_df(bar)
        
        # Animate the data
        chart.animate(data)

        chart.animate(Config({"x": "NEW TM", "y": "GROSS PREMIUM", "title": "TERRITORIAL MANAGERS PRODUCTION", "color": "NEW TM",  "label":"GROSS PREMIUM"}), delay=2)

       
        if st.checkbox("Swap"):
            chart.animate(Config({"x":"GROSS PREMIUM", "y": "NEW TM", "title": "TERRITORIAL MANAGERS PRODUCTION", "color": "NEW TM",  "label":"GROSS PREMIUM"}))

        

        output = chart.show()


    if view == 'Territorial Manager':
        unique = newdf['NEW TM'].unique()
              
        target = pd.read_csv('targets.csv')

        target['NEW TM'] = target['NEW TM'].str.strip()
        target['MONTH'] = target['MONTH'].str.strip() 
        target['RENEWALS'] = target['RENEWALS'].str.strip() 
        target['NEW TM'] = target['NEW TM'].str.strip() 
        # Get the current date
        current_date = datetime.now()

        # Create a pandas Timestamp object
        timestamp = pd.Timestamp(current_date)

        # Extract the month name
        current_month = timestamp.strftime('%B')
        
        current_month_name = current_month.upper()


        selected_manager =st.sidebar.selectbox("Choose TM", unique)

        for_cancellation =  cancellations[(cancellations['NEW TM'] == selected_manager) & (cancellations['MONTH NAME'] == current_month_name)]
      

        # Filter the DataFrame based on the selected branch
        filtered_df = newdf[(newdf['NEW TM'] == selected_manager) & (newdf['MONTH NAME'] == current_month_name)]
        filtered_target = target[(target['NEW TM'] == selected_manager) & (target['MONTH'] == current_month_name)]
        total = int(filtered_target['TOTAL'].sum())
        target_total = "{:,.0f}".format(total)
        target_renewal = filtered_target['RENEWALS'].sum()
        target_newbizz = filtered_target['NEW TM'].sum()
        daily = (total/20)
        weekly = (total/4)
        target_daily = "{:,.0f}".format(daily)
        target_weekly = "{:,.0f}".format(weekly)
        
        month_premium = filtered_df['GROSS PREMIUM'].sum()
        fom_month_premium = "Ksh. {:,.0f}".format(month_premium)
        month_receipts = filtered_df['RECEIPTS'].sum()
        fom_month_receipts = "Ksh. {:,.0f}".format(month_receipts)
        month_credit = filtered_df['NET BALANCE'].sum()
        fom_month_credit = "Ksh. {:,.0f}".format(month_credit)

        most_current_date = newdf['TRANSACTION DATE'].max()
        most_recent = filtered_df[filtered_df['TRANSACTION DATE'] == most_current_date]

        daily_cancellation =  cancellations[(cancellations['NEW TM'] == selected_manager) & (cancellations['TRANSACTION DATE'] == most_current_date)]

        day_premium = most_recent['GROSS PREMIUM'].sum()
        fom_day_premium = "Ksh. {:,.0f}".format(day_premium)
        day_receipts = most_recent['RECEIPTS'].sum()
        fom_day_receipts = "Ksh. {:,.0f}".format(day_receipts)
        day_credit = most_recent['NET BALANCE'].sum()
        fom_day_credit = "Ksh. {:,.0f}".format(day_credit)

        monthly_cancelled = for_cancellation['GROSS PREMIUM'].sum()
        amount_cancelled = "Ksh. {:,.0f}".format(monthly_cancelled)

        daily_cancelled = daily_cancellation['GROSS PREMIUM'].sum()
        amount_daily_cancelled = "Ksh. {:,.0f}".format(daily_cancelled)

        filtered_df['TRANSACTION DATE'] = pd.to_datetime(filtered_df['TRANSACTION DATE'])

      
        # Ensure 'TRANSACTION DATE' is a datetime object
        if pd.api.types.is_datetime64_any_dtype(filtered_df['TRANSACTION DATE']):
            # Calculate the start date of the current week (Monday)
            start_of_week = most_current_date - timedelta(days=most_current_date.dayofweek)

            # Filter data for payments from Monday of the current week to the most recent date
            filtered_data = filtered_df[(filtered_df['TRANSACTION DATE'] >= start_of_week) & (filtered_df['TRANSACTION DATE'] <= most_current_date)]


        else:
            print("The 'TRANSACTION DATE' column is not in datetime format.")
            
        week_premium = filtered_data['GROSS PREMIUM'].sum()
        fom_week_premium = "Ksh. {:,.0f}".format(week_premium)
        week_receipts = filtered_data['RECEIPTS'].sum()
        fom_week_receipts = "Ksh. {:,.0f}".format(week_receipts)
        week_credit = filtered_data['NET BALANCE'].sum()
        fom_week_credit = "Ksh. {:,.0f}".format(week_credit)   
        week_cancelled = filtered_data[filtered_data['SUM INSURED'] < 0]
        total_cancelled = week_cancelled['GROSS PREMIUM'].sum()
        week_total_cancelled = "Ksh. {:,.0f}".format(total_cancelled)   


        # Create a DataFrame without an index
        table_data = pd.DataFrame({
            ' ': [f'{selected_manager} TARGETS'],
            'MONTHLY': [f'Ksh. {target_total}'],
            'WEEKLY': [f'Ksh. {target_weekly}'],
            'DAILY': [f'Ksh. {target_daily}']
        })
        
        # Display the table 
        st.write(table_data.style.set_properties(**{'text-align': 'center'}).to_html(index=False, escape=False), unsafe_allow_html=True)
                
        st.markdown("")
        
        cc= st.columns(4)

        with cc[0]:
        # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
            hc.info_card(title= 'Month To Date Production', content= f'{fom_month_premium}', sentiment='good',  title_text_size='small', bar_value=77, content_text_size='small')

        with cc[1]:
            hc.info_card(title='Month To Date Receipted', content=f'{fom_month_receipts}',bar_value=12,  title_text_size='small', sentiment='good', content_text_size='small')

        with cc[2]:
            hc.info_card(title='Month To Date On Credit', content=f'{fom_month_credit}', sentiment='neutral',  title_text_size='small', bar_value=55, content_text_size='small')

        with cc[3]:
            hc.info_card(title='Month To Date Cancellations', content=f'{amount_cancelled}',bar_value=2, title_text_size='small', content_text_size = 'small', theme_override=theme_bad)

        cc_row1 = st.columns(4)

        with cc_row1[0]:
        # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
            hc.info_card(title= 'Week To Date Production', content= f'{fom_week_premium}', key = 'week_premium', sentiment='good',bar_value=77, content_text_size='small', title_text_size='small')

        with cc_row1[1]:
            hc.info_card(title='Week To Date Receipted', content=f'{fom_week_receipts}', key='week_receipt', bar_value=12, sentiment='good', content_text_size='small',title_text_size='small')

        with cc_row1[2]:
            hc.info_card(title='Week To Date On Credit', content=f'{fom_week_credit}', key='week_credit', sentiment='neutral',bar_value=55, content_text_size='small', title_text_size='small')

        with cc_row1[3]:
            hc.info_card(title='Week To Date Cancellations', content=f'{week_total_cancelled}', key='week_cancelled', sentiment='bad',bar_value=55, content_text_size='small',title_text_size='small')
        
        
        
        cc_row2 = st.columns(4)

        with cc_row2[0]:
        # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
            hc.info_card(title='Yesterday Production', content= f'{fom_day_premium}', sentiment='good',bar_value=77, key='day_premium', content_text_size='small', title_text_size='small')

        with cc_row2[1]:
            hc.info_card(title='Yesterday Receipted', content= f'{fom_day_receipts}',bar_value=12, key='day_receipts', sentiment='good',  content_text_size='small', title_text_size='small')

        with cc_row2[2]:
            hc.info_card(title='Yesterday On Credit', content=f'{fom_day_credit}', key='day_credit', sentiment='neutral', bar_value=55, content_text_size='small', title_text_size='small')

        with cc_row2[3]:
            hc.info_card(title='Yesterday Cancellations', content=f'{amount_daily_cancelled}',bar_value=2, key='cancelled', title_text_size='small', content_text_size = 'small', theme_override=theme_bad)



